import time
from collections import defaultdict, deque
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client"""
        now = time.time()
        client_requests = self.requests[client_id]
        
        # Remove old requests outside the window
        while client_requests and client_requests[0] <= now - self.window_seconds:
            client_requests.popleft()
        
        # Check if under limit
        if len(client_requests) < self.max_requests:
            client_requests.append(now)
            return True
        
        logger.warning(f"Rate limit exceeded for client {client_id}")
        return False

    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client"""
        now = time.time()
        client_requests = self.requests[client_id]
        
        # Remove old requests
        while client_requests and client_requests[0] <= now - self.window_seconds:
            client_requests.popleft()
        
        return max(0, self.max_requests - len(client_requests))

    def get_reset_time(self, client_id: str) -> float:
        """Get time when rate limit resets for client"""
        client_requests = self.requests[client_id]
        if not client_requests:
            return time.time()
        
        return client_requests[0] + self.window_seconds