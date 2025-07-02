import pytest
from datetime import datetime
from src.models.article import Article

def test_article_creation():
    """Test basic article creation"""
    article = Article(
        title="Test Article",
        url="https://example.com",
        status="success"
    )
    
    assert article.title == "Test Article"
    assert article.url == "https://example.com"
    assert article.status == "success"
    assert article.screenshot_path is None
    assert article.summary is None

def test_article_to_dict():
    """Test article serialization"""
    now = datetime.now()
    article = Article(
        title="Test Article",
        url="https://example.com",
        screenshot_path="1.png",
        status="success",
        summary="Test summary",
        created_at=now,
        updated_at=now
    )
    
    result = article.to_dict()
    
    assert result["title"] == "Test Article"
    assert result["url"] == "https://example.com"
    assert result["screenshot"] == "/screenshots/1.png"
    assert result["status"] == "success"
    assert result["summary"] == "Test summary"
    assert result["created_at"] == now.isoformat()
    assert result["updated_at"] == now.isoformat()

def test_article_to_dict_no_screenshot():
    """Test article serialization without screenshot"""
    article = Article(
        title="Test Article",
        url="https://example.com",
        status="failed"
    )
    
    result = article.to_dict()
    
    assert result["screenshot"] is None
    assert result["summary"] == "Summary not available."