# In Jesus name, amen. All glory to God!

import signal
import sys
from typing import Optional
from datetime import datetime
import schedule
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from content_generator import ContentGenerator
from image_generator import ImageGenerator
from x_api_client import x_client
from trend_monitor import get_trending_topics
from interaction_module import handle_interactions
from analytics import track_performance
from database import db
from utils import logger, sanitize_text, rate_limit, retry_with_backoff
from config import settings
from monitoring import metrics_collector
from cache import cache
import os
import logging
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

class SocialAgent:
    """Main social agent class handling scheduling and coordination."""
    
    def __init__(self):
        """Initialize the social agent."""
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self.setup_signal_handlers()
        self.x_client = x_client
        self.db = db
        self.image_generator = ImageGenerator()
        self.content_generator = ContentGenerator()

    def setup_signal_handlers(self):
        """Set up handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def handle_shutdown(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully."""
        logger.info("Received shutdown signal, stopping gracefully...")
        self.stop()
        sys.exit(0)

    def create_and_post_content(self) -> None:
        """Create and post high-quality content."""
        try:
            # Get trending topics from cache or generate new ones
            cache_key = "trending_topics"
            topics = cache.get(cache_key)
            if not topics:
                topics = get_trending_topics()
                cache.set(cache_key, topics)
            
            if not topics:
                logger.warning("No trending topics found")
                return

            # Get current hour to determine post type
            current_hour = datetime.now().hour
            
            # Strategic timing:
            # - Morning (6-9): Informative threads (when engagement is high)
            # - Afternoon (12-15): Single tweets (lunch break engagement)
            # - Evening (18-21): Single tweets (after work engagement)
            # - Night (0-3): Informative threads (global audience)
            
            is_thread = (
                (6 <= current_hour <= 9) or  # Morning threads
                (0 <= current_hour <= 3)     # Night threads
            )
            
            # Get recent posts (last 24 hours only)
            recent_posts = self.db.get_recent_posts(limit=5)
            
            # Try each topic until we find one that works
            for topic in topics:
                # Only skip if we posted about this exact topic in the last 24 hours
                if any(topic.lower() == post['text'].lower() for post in recent_posts):
                    logger.info(f"Skipping exact topic match: {topic}")
                    continue
                    
                if is_thread:
                    # Generate and post a thread
                    tweets = self.content_generator.generate_thread(topic)
                    if not tweets:
                        logger.warning("Failed to generate thread")
                        continue
                        
                    # Post the thread
                    success = True
                    for i, tweet in enumerate(tweets):
                        if i == 0:
                            # First tweet
                            tweet_id = self.x_client.post_tweet(tweet)
                        else:
                            # Reply to previous tweet
                            tweet_id = self.x_client.post_tweet(tweet, in_reply_to_tweet_id=tweet_id)
                            
                        if tweet_id:
                            # Save to database
                            self.db.insert_post(tweet_id, tweet)
                            logger.info(f"Successfully posted thread tweet {i+1}/{len(tweets)}")
                            metrics_collector.log_api_call("twitter", "post_tweet", "success")
                        else:
                            logger.error(f"Failed to post thread tweet {i+1}")
                            metrics_collector.log_api_call("twitter", "post_tweet", "error")
                            success = False
                            break
                            
                    if success:
                        break
                        
                else:
                    # Generate and post a single tweet
                    tweet = self.content_generator.generate_tweet(topic)
                    if not tweet:
                        logger.warning("Failed to generate tweet")
                        continue
                        
                    # Post the tweet
                    tweet_id = self.x_client.post_tweet(tweet)
                    if tweet_id:
                        # Save to database
                        self.db.insert_post(tweet_id, tweet)
                        logger.info(f"Successfully posted tweet: {tweet_id}")
                        metrics_collector.log_api_call("twitter", "post_tweet", "success")
                        break
                    else:
                        logger.error("Failed to post tweet")
                        metrics_collector.log_api_call("twitter", "post_tweet", "error")
            
        except Exception as e:
            logger.error(f"Error in create_and_post_content: {str(e)}")
            metrics_collector.log_error(e, "create_and_post_content")
            metrics_collector.log_api_call("twitter", "post_tweet", "error")

    def schedule_jobs(self) -> None:
        """Schedule content creation jobs for optimal virality."""
        # Content creation jobs - 4 times per day at strategic times
        self.scheduler.add_job(
            self.create_and_post_content,
            CronTrigger(hour='6,12,18,0'),  # 6 AM, 12 PM, 6 PM, 12 AM
            id='content_creation'
        )
        
        # Health check job - every 15 minutes
        self.scheduler.add_job(
            self.health_check,
            CronTrigger(minute='*/15'),
            id='health_check'
        )

    def health_check(self) -> None:
        """Perform health check of all components."""
        try:
            # Check database connection
            self.db.get_recent_posts(limit=1)
            
            # Check X API
            self.x_client.search_tweets("test", count=1)
            
            # Check cache
            cache.set("health_check", "ok")
            if cache.get("health_check") != "ok":
                raise Exception("Cache health check failed")
            
            logger.info("Health check passed")
            metrics_collector.log_api_call("health", "check", "success")
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            metrics_collector.log_error(e, "health_check")
            metrics_collector.log_api_call("health", "check", "error")

    def start(self) -> None:
        """Start the social agent."""
        try:
            logger.info("Starting social agent...")
            self.is_running = True
            self.schedule_jobs()
            self.scheduler.start()
            
            # Run initial content creation
            self.create_and_post_content()
            
            # Keep the main thread alive
            while self.is_running:
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Error starting social agent: {str(e)}")
            metrics_collector.log_error(e, "start")
            self.stop()

    def stop(self) -> None:
        """Stop the social agent gracefully."""
        try:
            logger.info("Stopping social agent...")
            self.is_running = False
            self.scheduler.shutdown()
            self.db.close()
            cache.clear()
            metrics_collector.save_metrics()
            logger.info("Social agent stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping social agent: {str(e)}")
            metrics_collector.log_error(e, "stop")

def main():
    """Main entry point."""
    agent = SocialAgent()
    agent.start()

if __name__ == "__main__":
    main()