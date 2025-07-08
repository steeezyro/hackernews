import json
import sqlite3
import os
import glob
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from ..models.article import Article

logger = logging.getLogger(__name__)

class ArticleCache:
    def __init__(self, db_path: str = "articles.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    screenshot_path TEXT,
                    status TEXT NOT NULL,
                    summary TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at)
            """)
            conn.commit()

    def save_articles(self, articles: List[Article]) -> bool:
        """Save articles to database"""
        try:
            # Ensure database is initialized
            self._init_db()
            
            with sqlite3.connect(self.db_path) as conn:
                # Clear old articles (keep only latest batch)
                conn.execute("DELETE FROM articles")
                
                for article in articles:
                    conn.execute("""
                        INSERT OR REPLACE INTO articles 
                        (title, url, screenshot_path, status, summary, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        article.title,
                        article.url,
                        article.screenshot_path,
                        article.status,
                        article.summary,
                        article.created_at,
                        article.updated_at
                    ))
                
                conn.commit()
                logger.info(f"Saved {len(articles)} articles to database")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save articles: {e}")
            return False

    def get_articles(self) -> List[Article]:
        """Get articles from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM articles 
                    ORDER BY created_at ASC
                """)
                
                articles = []
                for row in cursor.fetchall():
                    article = Article(
                        title=row['title'],
                        url=row['url'],
                        screenshot_path=row['screenshot_path'],
                        status=row['status'],
                        summary=row['summary'],
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                        updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                    )
                    articles.append(article)
                
                return articles
                
        except Exception as e:
            logger.error(f"Failed to get articles: {e}")
            return []

    def is_cache_fresh(self, max_age_minutes: int = 5) -> bool:
        """Check if cache is fresh enough"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT MAX(created_at) as latest_update 
                    FROM articles
                """)
                row = cursor.fetchone()
                
                if not row or not row[0]:
                    return False
                
                latest_update = datetime.fromisoformat(row[0])
                age = datetime.now() - latest_update
                
                return age < timedelta(minutes=max_age_minutes)
                
        except Exception as e:
            logger.error(f"Failed to check cache freshness: {e}")
            return False

    def get_cache_status(self) -> dict:
        """Get cache status information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_articles,
                        MAX(created_at) as latest_update,
                        COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_articles
                    FROM articles
                """)
                row = cursor.fetchone()
                
                return {
                    "total_articles": row[0] if row else 0,
                    "latest_update": row[1] if row and row[1] else None,
                    "successful_articles": row[2] if row else 0,
                    "is_fresh": self.is_cache_fresh()
                }
                
        except Exception as e:
            logger.error(f"Failed to get cache status: {e}")
            return {
                "total_articles": 0,
                "latest_update": None,
                "successful_articles": 0,
                "is_fresh": False
            }

