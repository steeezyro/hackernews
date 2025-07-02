import os
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from src.services.scraper import HackerNewsScraper
from src.services.cache import ArticleCache
from src.utils.rate_limiter import RateLimiter
from src.utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger()

# Global instances
scraper = None
cache = None
rate_limiter = RateLimiter(max_requests=5, window_seconds=300)  # 5 requests per 5 minutes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global scraper, cache
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable is required")
        raise ValueError("GEMINI_API_KEY is required")
    
    scraper = HackerNewsScraper(api_key)
    cache = ArticleCache()
    
    # Create screenshots directory
    os.makedirs("screenshots", exist_ok=True)
    
    logger.info("Application started successfully")
    yield
    
    # Shutdown
    logger.info("Application shutting down")

app = FastAPI(
    title="HackerNews Analysis API",
    description="Real-time HackerNews story analysis with screenshots and AI summaries",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hackernews-1.onrender.com",
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "HackerNews Analysis API v2.0",
        "status": "healthy",
        "cache_status": cache.get_cache_status() if cache else None
    }

@app.get("/api/articles")
async def get_articles():
    """Get cached articles"""
    try:
        articles = cache.get_articles()
        cache_status = cache.get_cache_status()
        
        return {
            "articles": [article.to_dict() for article in articles],
            "cache_status": cache_status,
            "total": len(articles)
        }
        
    except Exception as e:
        logger.error(f"Failed to get articles: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve articles")

@app.post("/api/refresh")
async def refresh_articles(request: Request, background_tasks: BackgroundTasks):
    """Refresh articles from HackerNews"""
    client_ip = request.client.host
    
    # Rate limiting
    if not rate_limiter.is_allowed(client_ip):
        remaining = rate_limiter.get_remaining_requests(client_ip)
        reset_time = rate_limiter.get_reset_time(client_ip)
        
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "remaining_requests": remaining,
                "reset_time": reset_time
            }
        )
    
    # Check if cache is fresh
    if cache.is_cache_fresh(max_age_minutes=2):
        logger.info("Cache is fresh, returning cached results")
        articles = cache.get_articles()
        return {
            "status": "cached",
            "articles": [article.to_dict() for article in articles],
            "message": "Returned cached results (updated within last 2 minutes)"
        }
    
    # Start background refresh
    background_tasks.add_task(refresh_articles_background)
    
    return {
        "status": "refreshing",
        "message": "Article refresh started in background. Check back in 30-60 seconds.",
        "estimated_completion": "30-60 seconds"
    }

async def refresh_articles_background():
    """Background task to refresh articles"""
    try:
        logger.info("Starting background article refresh")
        articles = await scraper.scrape_top_stories()
        cache.save_articles(articles)
        logger.info(f"Successfully refreshed {len(articles)} articles")
        
    except Exception as e:
        logger.error(f"Background refresh failed: {e}")

@app.get("/api/status")
async def get_status():
    """Get system status"""
    try:
        cache_status = cache.get_cache_status()
        
        return {
            "system_status": "healthy",
            "cache_status": cache_status,
            "rate_limit_info": {
                "max_requests": rate_limiter.max_requests,
                "window_seconds": rate_limiter.window_seconds
            }
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {
            "system_status": "degraded",
            "error": str(e)
        }

# Legacy endpoint for backwards compatibility
@app.get("/api/results")
async def get_results_legacy():
    """Legacy endpoint - redirects to /api/articles"""
    try:
        articles = cache.get_articles()
        return [article.to_dict() for article in articles]
        
    except Exception as e:
        logger.error(f"Legacy endpoint failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve articles")

# Legacy endpoint for backwards compatibility
@app.get("/run")
async def run_legacy(request: Request, background_tasks: BackgroundTasks):
    """Legacy endpoint - redirects to POST /api/refresh"""
    return await refresh_articles(request, background_tasks)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)