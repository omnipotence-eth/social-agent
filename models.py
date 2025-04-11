from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, validator
from config import settings

class TweetData(BaseModel):
    """Model for tweet data validation."""
    text: str = Field(..., max_length=settings.MAX_TWEET_LENGTH)
    media_path: Optional[str] = None
    hashtags: Optional[List[str]] = Field(default_factory=list)

    @validator('hashtags', each_item=True)
    def validate_hashtags(cls, v):
        if not v.startswith('#'):
            return f"#{v}"
        return v

class PostMetrics(BaseModel):
    """Model for post metrics validation."""
    likes: int = Field(default=0, ge=0)
    retweets: int = Field(default=0, ge=0)
    replies: int = Field(default=0, ge=0)
    impressions: Optional[int] = Field(default=0, ge=0)

class Post(BaseModel):
    """Model for database post validation."""
    tweet_id: str
    text: str = Field(..., max_length=settings.MAX_TWEET_LENGTH)
    media_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metrics: PostMetrics = Field(default_factory=PostMetrics)

class Interaction(BaseModel):
    """Model for user interaction validation."""
    tweet_id: str
    type: str = Field(..., regex='^(like|retweet|reply)$')
    user_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AnalyticsData(BaseModel):
    """Model for analytics data validation."""
    date: datetime = Field(default_factory=datetime.utcnow)
    metrics: Dict[str, Any]
    interactions: Dict[str, int]
    performance_score: float = Field(ge=0, le=1.0)

class APIMetrics(BaseModel):
    """Model for API metrics validation."""
    total_calls: int = Field(default=0, ge=0)
    success_calls: int = Field(default=0, ge=0)
    error_calls: int = Field(default=0, ge=0)
    average_response_time: float = Field(default=0.0, ge=0)

class SystemMetrics(BaseModel):
    """Model for system metrics validation."""
    cpu_percent: float = Field(ge=0, le=100)
    memory_percent: float = Field(ge=0, le=100)
    disk_percent: float = Field(ge=0, le=100)
    uptime_seconds: float = Field(ge=0) 