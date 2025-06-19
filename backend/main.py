from api import app
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hackernews-1.onrender.com",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")

@app.get("/")
def root():
    return {"message": "Hacker News Summarizer is live!"}

@app.get("/api/results")
def get_results():
    if os.path.exists("output.json"):
        with open("output.json", "r") as f:
            data = json.load(f)
        return data
    return {"error": "output.json not found"}

@app.get("/run")
def run_scraper():
    if os.path.exists("screenshots"):
        shutil.rmtree("screenshots")
    os.makedirs("screenshots", exist_ok=True)

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
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
                page = browser.new_page()
                page.goto(url, timeout=30000)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_load_state("networkidle")
                screenshot_path = f"screenshots/{idx}.png"
                page.screenshot(path=screenshot_path, full_page=True)
                result["screenshot"] = screenshot_path
                result["status"] = "success"
                page.close()
            except Exception as e:
                print(f"⚠️ Screenshot failed: {e}", flush=True)

            try:
                response = model.generate_content(f"Summarize this article in 2-3 lines: {url}")
                result["summary"] = response.text.strip()
            except Exception as e:
                print(f"⚠️ Summary failed: {e}", flush=True)

            results.append(result)

        browser.close()

    with open("output.json", "w") as f:
        json.dump(results, f, indent=2)

    return {"status": "completed", "results": results}
