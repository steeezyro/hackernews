import pytest
import time
from src.utils.rate_limiter import RateLimiter

def test_rate_limiter_allows_under_limit():
    """Test rate limiter allows requests under limit"""
    limiter = RateLimiter(max_requests=5, window_seconds=60)
    
    # Should allow up to 5 requests
    for i in range(5):
        assert limiter.is_allowed("client1") == True
    
    # 6th request should be denied
    assert limiter.is_allowed("client1") == False

def test_rate_limiter_different_clients():
    """Test rate limiter tracks different clients separately"""
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    
    # Each client should have their own limit
    assert limiter.is_allowed("client1") == True
    assert limiter.is_allowed("client2") == True
    assert limiter.is_allowed("client1") == True
    assert limiter.is_allowed("client2") == True
    
    # Both clients should now be at limit
    assert limiter.is_allowed("client1") == False
    assert limiter.is_allowed("client2") == False

def test_rate_limiter_remaining_requests():
    """Test getting remaining requests"""
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    
    assert limiter.get_remaining_requests("client1") == 3
    
    limiter.is_allowed("client1")
    assert limiter.get_remaining_requests("client1") == 2
    
    limiter.is_allowed("client1")
    assert limiter.get_remaining_requests("client1") == 1
    
    limiter.is_allowed("client1")
    assert limiter.get_remaining_requests("client1") == 0