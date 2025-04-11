from x_api_client import x_client
from database import Database
from utils import logger
from datetime import datetime, timedelta

def track_performance():
    try:
        db = Database()
        # Get posts from the last 24 hours
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        posts = db.db.posts.find({"created_at": {"$gt": one_day_ago}})
        
        for post in posts:
            tweet_id = post['tweet_id']
            tweet = x_client.client.get_tweet(id=tweet_id, tweet_fields=['public_metrics'])
            metrics = tweet.data['public_metrics']
            
            # Update the post with new metrics
            db.db.posts.update_one(
                {"tweet_id": tweet_id},
                {
                    "$set": {
                        "impressions": metrics['impression_count'],
                        "likes": metrics['like_count'],
                        "retweets": metrics['retweet_count'],
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        
        logger.info("Updated analytics for recent posts")
    except Exception as e:
        logger.error(f"Error updating analytics: {e}")