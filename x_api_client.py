from typing import List, Optional, Dict, Any
import tweepy
from config import settings
from utils import logger, rate_limit, retry_with_backoff, sanitize_text, RateLimiter

class XAPIClient:
    """X (Twitter) API Client with rate limiting and error handling."""
    
    def __init__(self):
        """Initialize the X API client with authentication."""
        self.auth = tweepy.OAuth1UserHandler(
            settings.X_API_KEY,
            settings.X_API_SECRET,
            settings.X_ACCESS_TOKEN,
            settings.X_ACCESS_TOKEN_SECRET
        )
        self.api = tweepy.API(self.auth)
        self.client = tweepy.Client(
            consumer_key=settings.X_API_KEY,
            consumer_secret=settings.X_API_SECRET,
            access_token=settings.X_ACCESS_TOKEN,
            access_token_secret=settings.X_ACCESS_TOKEN_SECRET
        )
        self.rate_limiter = RateLimiter({
            '15m': {'max_requests': settings.X_RATE_LIMIT_PER_15M, 'time_window': 900},
            '1d': {'max_requests': settings.X_RATE_LIMIT_PER_DAY, 'time_window': 86400},
            '30d': {'max_requests': settings.X_RATE_LIMIT_PER_MONTH, 'time_window': 2592000}
        })

    @retry_with_backoff(max_retries=settings.MAX_RETRIES)
    def post_tweet(self, text: str, media: Optional[str] = None, in_reply_to_tweet_id: Optional[str] = None) -> Optional[str]:
        """Post a tweet with rate limiting."""
        if not self.rate_limiter.acquire():
            logger.warning("Rate limit exceeded, waiting for next window")
            return None
            
        try:
            # Sanitize and validate text
            clean_text = sanitize_text(text, settings.MAX_TWEET_LENGTH)
            
            if media:
                media_id = self.api.media_upload(media).media_id
                response = self.client.create_tweet(
                    text=clean_text,
                    media_ids=[media_id],
                    in_reply_to_tweet_id=in_reply_to_tweet_id
                )
            else:
                response = self.client.create_tweet(
                    text=clean_text,
                    in_reply_to_tweet_id=in_reply_to_tweet_id
                )
                
            if response and response.data:
                tweet_id = response.data['id']
                logger.info(f"Posted tweet: {tweet_id}")
                return tweet_id
            else:
                logger.error("Failed to get tweet ID from response")
                return None
                
        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
            return None

    @rate_limit(max_requests=settings.X_RATE_LIMIT)
    @retry_with_backoff(max_retries=settings.MAX_RETRIES)
    def search_tweets(self, query: str, count: int = 10) -> List[Dict[str, Any]]:
        """
        Search for recent tweets.
        
        Args:
            query: Search query
            count: Number of tweets to return
            
        Returns:
            List of tweet data
        """
        try:
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(count, 100)  # API limit is 100
            )
            return tweets.data if tweets.data else []
        except Exception as e:
            logger.error(f"Error searching tweets: {str(e)}")
            raise

    @rate_limit(max_requests=settings.X_RATE_LIMIT)
    @retry_with_backoff(max_retries=settings.MAX_RETRIES)
    def like_tweet(self, tweet_id: str) -> None:
        """Like a tweet."""
        try:
            self.client.like(tweet_id)
            logger.info(f"Liked tweet: {tweet_id}")
        except Exception as e:
            logger.error(f"Error liking tweet {tweet_id}: {str(e)}")
            raise

    @rate_limit(max_requests=settings.X_RATE_LIMIT)
    @retry_with_backoff(max_retries=settings.MAX_RETRIES)
    def retweet(self, tweet_id: str) -> None:
        """Retweet a tweet."""
        try:
            self.client.retweet(tweet_id)
            logger.info(f"Retweeted: {tweet_id}")
        except Exception as e:
            logger.error(f"Error retweeting {tweet_id}: {str(e)}")
            raise

    @rate_limit(max_requests=settings.X_RATE_LIMIT)
    @retry_with_backoff(max_retries=settings.MAX_RETRIES)
    def reply_to_tweet(self, tweet_id: str, text: str) -> None:
        """Reply to a tweet."""
        try:
            clean_text = sanitize_text(text, settings.MAX_TWEET_LENGTH)
            self.client.create_tweet(
                text=clean_text,
                in_reply_to_tweet_id=tweet_id
            )
            logger.info(f"Replied to tweet: {tweet_id}")
        except Exception as e:
            logger.error(f"Error replying to tweet {tweet_id}: {str(e)}")
            raise

# Create global instance
x_client = XAPIClient()