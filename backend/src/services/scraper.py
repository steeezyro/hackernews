import asyncio
import logging
from typing import List, Tuple
from playwright.async_api import async_playwright, Page, Browser
from concurrent.futures import ThreadPoolExecutor
import google.generativeai as genai
from datetime import datetime
import os
import glob

from ..models.article import Article

logger = logging.getLogger(__name__)

class HackerNewsScraper:
    def __init__(self, gemini_api_key: str):
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
        self.max_concurrent = 3  # Reduced for better stability

    async def scrape_top_stories(self) -> List[Article]:
        """Scrape top 10 HackerNews stories"""
        try:
            # Clear old screenshots first
            self._clear_old_screenshots()
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-web-security']
                )
                
                # Get top story links
                links = await self._get_story_links(browser)
                logger.info(f"Found {len(links)} stories to process")
                
                # Process stories sequentially to ensure proper numbering
                articles = await self._process_stories_sequentially(browser, links)
                
                await browser.close()
                return articles
                
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise

    def _clear_old_screenshots(self):
        """Remove all old screenshot files"""
        screenshot_dir = "screenshots"
        if os.path.exists(screenshot_dir):
            for file in glob.glob(f"{screenshot_dir}/*.png"):
                try:
                    os.remove(file)
                    logger.info(f"Removed old screenshot: {file}")
                except Exception as e:
                    logger.warning(f"Failed to remove {file}: {e}")

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
                        continue
                    
                    if url:
                        links.append((title, url))
            
            return links
            
        finally:
            await page.close()

    async def _process_stories_sequentially(self, browser: Browser, links: List[Tuple[str, str]]) -> List[Article]:
        """Process stories one by one maintaining HackerNews ranking order"""
        articles = []
        
        for idx, (title, url) in enumerate(links):
            article_number = idx + 1  # Keep original order: 1, 2, 3, ..., 10
            logger.info(f"Processing HackerNews article #{article_number}: {title}")
            
            try:
                article = await self._process_single_story(browser, article_number, title, url)
                articles.append(article)
            except Exception as e:
                logger.error(f"Failed to process article #{article_number}: {e}")
                # Create failed article
                failed_article = Article(
                    title=title,
                    url=url,
                    status="failed",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                articles.append(failed_article)
        
        return articles

    async def _process_single_story(self, browser: Browser, article_number: int, title: str, url: str) -> Article:
        """Process a single story: screenshot + summary"""
        article = Article(
            title=title,
            url=url,
            status="processing",
            created_at=datetime.now()
        )
        
        # Take screenshot
        screenshot_success = await self._take_screenshot(browser, article_number, url)
        if screenshot_success:
            article.screenshot_path = f"/screenshots/{article_number}.png"
            article.status = "success"
        else:
            article.status = "screenshot_failed"
        
        # Generate summary
        try:
            summary = await self._generate_summary(title)
            article.summary = summary
        except Exception as e:
            logger.error(f"Summary generation failed for {title}: {e}")
            if "429" in str(e) and "quota" in str(e).lower():
                article.summary = f"AI summary temporarily unavailable due to API quota limits."
            else:
                article.summary = f"Unable to generate AI summary. Content analysis temporarily unavailable."
        
        article.updated_at = datetime.now()
        return article

    async def _take_screenshot(self, browser: Browser, article_number: int, url: str) -> bool:
        """Take a clean screenshot of a single article"""
        # Create new context for each screenshot to ensure isolation
        context = await browser.new_context(
            viewport={'width': 1200, 'height': 800},
            ignore_https_errors=True
        )
        
        page = await context.new_page()
        
        try:
            logger.info(f"Taking screenshot #{article_number} of {url}")
            
            # Navigate to page
            await page.goto(url, timeout=30000, wait_until="networkidle")
            
            # Wait for page to fully load
            await asyncio.sleep(3)
            
            # Scroll slightly to capture more content
            await page.evaluate("window.scrollTo(0, Math.min(document.body.scrollHeight / 4, 500))")
            await asyncio.sleep(1)
            
            # Take screenshot
            screenshot_path = f"screenshots/{article_number}.png"
            os.makedirs("screenshots", exist_ok=True)
            
            await page.screenshot(
                path=screenshot_path,
                full_page=False,
                type='png'
            )
            
            # Verify file was created
            if os.path.exists(screenshot_path):
                logger.info(f"Screenshot #{article_number} saved successfully")
                return True
            else:
                logger.warning(f"Screenshot #{article_number} file not created")
                return False
                
        except Exception as e:
            logger.warning(f"Screenshot #{article_number} failed for {url}: {e}")
            return False
        finally:
            await context.close()

    async def _generate_summary(self, title: str) -> str:
        """Generate AI summary for an article"""
        try:
            prompt = f"Based on this HackerNews article title: '{title}', provide a brief 2-3 sentence summary about what this article is likely about. Focus on the main topic and key points."
            
            logger.info(f"Generating AI summary for: {title}")
            
            # Use ThreadPoolExecutor for blocking Gemini API call
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(
                    executor,
                    lambda: self.model.generate_content(prompt)
                )
            
            if response and hasattr(response, 'text') and response.text:
                summary = response.text.strip()
                logger.info(f"Generated AI summary for {title}: {summary[:60]}...")
                return summary
            else:
                logger.warning(f"Empty response from Gemini for {title}")
                return "Summary not available - API returned empty response."
            
        except Exception as e:
            logger.error(f"Summary generation failed for {title}: {e}")
            if "429" in str(e) and "quota" in str(e).lower():
                return f"AI summary temporarily unavailable due to API quota limits."
            return f"Unable to generate AI summary. Content analysis temporarily unavailable."