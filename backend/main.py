from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import os
import shutil
import json
import google.generativeai as genai

# Load .env variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

app = FastAPI()

# 🔒 CORS config (in prod, restrict to your frontend URL)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or: ["https://hackernews-1.onrender.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔗 Serve screenshots folder statically
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")


@app.get("/")
def root():
    return {"message": "Hacker News Summarizer is live!"}


@app.get("/api/results")
def run_scraper():
    # Clean and prepare screenshots folder
    if os.path.exists("screenshots"):
        shutil.rmtree("screenshots")
    os.makedirs("screenshots", exist_ok=True)

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Grab top 10 links
        page = browser.new_page()
        page.goto("https://news.ycombinator.com/")
        items = page.query_selector_all('tr.athing')[:10]

        links = []
        for item in items:
            title_el = item.query_selector('.titleline a')
            title = title_el.inner_text()
            url = title_el.get_attribute('href')
            if url.startswith("item?"):
                url = "https://news.ycombinator.com/" + url
            links.append((title, url))
        page.close()

        # Screenshot and summarize
        for idx, (title, url) in enumerate(links, 1):
            print(f"{idx}. {title} ({url})", flush=True)
            result = {
                "title": title,
                "url": url,
                "screenshot": None,
                "status": "failed",
                "summary": "Summary not available."
            }

            try:
                # Screenshot
                page = browser.new_page()
                print(f"📍 Navigating to {url}", flush=True)
                page.goto(url, timeout=30000)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_load_state("networkidle")

                screenshot_path = f"screenshots/{idx}.png"
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"✅ Screenshot saved to {screenshot_path}", flush=True)

                result["screenshot"] = screenshot_path
                result["status"] = "success"
                page.close()

            except Exception as e:
                print(f"⚠️ Screenshot failed for '{title}': {e}", flush=True)

            try:
                # Gemini summarization
                print(f"🤖 Summarizing {url} ...", flush=True)
                response = model.generate_content(f"Summarize this article in 2-3 lines: {url}")
                result["summary"] = response.text.strip()
                print("✅ Summary complete", flush=True)

            except Exception as e:
                print(f"⚠️ Gemini summarization failed for '{title}': {e}", flush=True)

            results.append(result)

        browser.close()

    # Output JSON (optional for logging)
    with open("output.json", "w") as f:
        json.dump(results, f, indent=2)

    return {"status": "completed", "results": results}
