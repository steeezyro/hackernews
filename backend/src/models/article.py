from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Article:
    title: str
    url: str
    screenshot_path: Optional[str] = None
    status: str = "pending"
    summary: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "screenshot": f"/screenshots/{self.screenshot_path}" if self.screenshot_path else None,
            "status": self.status,
            "summary": self.summary or "Summary not available.",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }