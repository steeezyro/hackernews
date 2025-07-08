import asyncio
import logging
from typing import List, Tuple
from playwright.async_api import async_playwright, Page, Browser
from concurrent.futures import ThreadPoolExecutor
import google.generativeai as genai
from datetime import datetime
import os

from ..models.article import Article

logger = logging.getLogger(__name__)

class HackerNewsScraper:
    def __init__(self, gemini_api_key: str):
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
        self.max_concurrent = 5

    async def scrape_top_stories(self) -> List[Article]:
        """Scrape top 10 HackerNews stories with parallel processing"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                
                # Get top story links
                links = await self._get_story_links(browser)
                logger.info(f"Found {len(links)} stories to process")
                
                # Process stories in parallel
                articles = await self._process_stories_parallel(browser, links)
                
                await browser.close()
                return articles
                
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise

    async def _get_story_links(self, browser: Browser) -> List[Tuple[str, str]]:
        """Extract top 10 story links from HackerNews front page"""
        page = await browser.new_page()
        try:
            await page.goto("https://news.ycombinator.com/", wait_until="networkidle")
            
            items = await page.query_selector_all('tr.athing')
            links = []
            
            for item in items[:10]:
                title_el = await item.query_selector('.titleline a')
                if title_el:
                    title = await title_el.inner_text()
                    url = await title_el.get_attribute('href')
                    
                    # Handle relative URLs
                    if url and url.startswith("item?"):
                        url = "https://news.ycombinator.com/" + url
                    elif url and url.startswith("/"):
                        url = "https://news.ycombinator.com" + url
                    elif url and not url.startswith("http"):
                        # Skip invalid URLs
                        continue
                    
                    if url:  # Only add if we have a valid URL
                        links.append((title, url))
            
            return links
            
        finally:
            await page.close()

    async def _process_stories_parallel(self, browser: Browser, links: List[Tuple[str, str]]) -> List[Article]:
        """Process stories in parallel with rate limiting"""
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def process_single_story(idx: int, title: str, url: str) -> Article:
            async with semaphore:
                return await self._process_single_story(browser, idx + 1, title, url)
        
        tasks = [
            process_single_story(idx, title, url) 
            for idx, (title, url) in enumerate(links)
        ]
        
        articles = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        valid_articles = []
        for i, article in enumerate(articles):
            if isinstance(article, Exception):
                logger.error(f"Failed to process story {i+1}: {article}")
                # Create failed article
                title, url = links[i] if i < len(links) else ("Unknown", "")
                valid_articles.append(Article(
                    title=title,
                    url=url,
                    status="failed",
                    created_at=datetime.now()
                ))
            else:
                valid_articles.append(article)
        
        return valid_articles

    async def _process_single_story(self, browser: Browser, idx: int, title: str, url: str) -> Article:
        """Process a single story: screenshot + summary"""
        logger.info(f"Processing story {idx}: {title}")
        
        article = Article(
            title=title,
            url=url,
            status="processing",
            created_at=datetime.now()
        )
        
        page_content = None
        
        # Try screenshot and extract content with better error handling
        try:
            screenshot_success, content = await self._take_screenshot_and_extract_content(browser, idx + 1, url)
            if screenshot_success:
                article.screenshot_path = f"{idx + 1}.png"
                article.status = "success"
                page_content = content
            else:
                article.status = "screenshot_failed"
        except Exception as e:
            logger.error(f"Screenshot processing failed for {title}: {e}")
            article.status = "screenshot_failed"
        
        # Try summary with better error handling
        try:
            summary = await self._generate_summary(title, page_content)
            article.summary = summary
        except Exception as e:
            logger.warning(f"Summary generation failed for {title}: {e}")
            article.summary = "AI summary temporarily unavailable (API key issue)."
        
        article.updated_at = datetime.now()
        return article

    async def _take_screenshot_and_extract_content(self, browser: Browser, idx: int, url: str) -> tuple[bool, str]:
        """Take screenshot of a single article and extract page content"""
        page = await browser.new_page()
        try:
            # Set viewport for consistent screenshots
            await page.set_viewport_size({"width": 1200, "height": 800})
            
            logger.info(f"Taking screenshot of {url}")
            
            # Navigate with shorter timeout and better error handling
            await page.goto(url, timeout=15000, wait_until="domcontentloaded")
            
            # Wait a bit for page to load
            await asyncio.sleep(2)
            
            # Extract page content for summary
            page_content = ""
            try:
                # Try to extract readable text from the page
                content = await page.evaluate("""
                    () => {
                        // Remove script and style elements
                        const scripts = document.querySelectorAll('script, style');
                        scripts.forEach(el => el.remove());
                        
                        // Get text content and clean it up
                        const text = document.body.innerText || document.body.textContent || '';
                        
                        // Clean up whitespace and limit length
                        return text.replace(/\\s+/g, ' ').trim().substring(0, 3000);
                    }
                """)
                page_content = content or ""
                logger.info(f"Extracted {len(page_content)} characters of content")
            except Exception as e:
                logger.warning(f"Failed to extract content from {url}: {e}")
                page_content = ""
            
            # Scroll to capture more content
            await page.evaluate("window.scrollTo(0, Math.min(document.body.scrollHeight / 3, 1000))")
            await asyncio.sleep(1)
            
            screenshot_path = f"screenshots/{idx}.png"
            os.makedirs("screenshots", exist_ok=True)
            
            await page.screenshot(
                path=screenshot_path,
                full_page=False,
                type='png'
            )
            
            # Verify file was created
            if os.path.exists(screenshot_path):
                logger.info(f"Screenshot saved successfully: {screenshot_path}")
                return True, page_content
            else:
                logger.warning(f"Screenshot file not created: {screenshot_path}")
                return False, page_content
            
        except Exception as e:
            logger.warning(f"Screenshot failed for {url}: {type(e).__name__}: {e}")
            return False, ""
        finally:
            await page.close()

    async def _generate_summary(self, title: str, page_content: str | None) -> str:
        """Generate AI summary for an article"""
        try:
            # If no content was extracted, use title-based summary
            if not page_content or len(page_content.strip()) < 50:
                logger.info(f"No content extracted, using title-based summary for: {title}")
                prompt = f"Based on this HackerNews article title: '{title}', provide a brief 2-3 sentence summary about what this article is likely about. Focus on the main topic and key points."
            else:
                # Use extracted content for summary
                prompt = f"Please provide a 2-3 sentence summary of this article titled '{title}'. Here is the article content: {page_content[:2000]}..."
            
            # Use ThreadPoolExecutor for blocking Gemini API call
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(
                    executor,
                    lambda: self.model.generate_content(prompt)
                )
            
            if response and hasattr(response, 'text') and response.text:
                return response.text.strip()
            else:
                logger.warning(f"Empty response from Gemini for {title}")
                return "Summary not available - API returned empty response."
            
        except Exception as e:
            logger.warning(f"Summary generation failed for {title}: {e}")
            # Fallback to basic title-based summary
            return f"This article discusses {title.lower()}. Please visit the link for more details."