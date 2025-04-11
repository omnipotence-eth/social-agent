from typing import Dict, List, Optional, Any
from datetime import datetime
import pymongo
from pymongo.errors import PyMongoError, ConnectionFailure, ServerSelectionTimeoutError
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from config import settings
from utils import logger, retry_with_backoff

class Database:
    """Database handler for MongoDB operations."""
    
    def __init__(self):
        """Initialize database connection with connection pooling."""
        self.client = None
        self.db = None
        self._connect()
        self._setup_indexes()

    def _connect(self) -> None:
        """Establish database connection with retry mechanism."""
        try:
            if not self.client:
                self.client = MongoClient(
                    settings.MONGODB_URI,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000,
                    socketTimeoutMS=45000,
                    maxPoolSize=50,
                    minPoolSize=10,
                    server_api=ServerApi('1')
                )
                # Force a connection to verify it works
                self.client.admin.command('ping')
                self.db = self.client[settings.MONGODB_DB]
                logger.info("Database connection established")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            self.client = None
            self.db = None
            raise

    def _setup_indexes(self) -> None:
        """Set up database indexes with error handling."""
        try:
            if self.db is None:
                self._connect()
                
            # Posts collection indexes
            self.db.posts.create_index([("tweet_id", pymongo.ASCENDING)], unique=True)
            self.db.posts.create_index([("created_at", pymongo.DESCENDING)])
            
            # Analytics collection indexes
            self.db.analytics.create_index([("date", pymongo.DESCENDING)])
            
            # Interactions collection indexes
            self.db.interactions.create_index([
                ("tweet_id", pymongo.ASCENDING),
                ("type", pymongo.ASCENDING)
            ])
            
            logger.info("Database indexes created")
        except PyMongoError as e:
            logger.error(f"Failed to create indexes: {str(e)}")
            raise

    def _ensure_connection(self) -> None:
        """Ensure database connection is active."""
        try:
            if self.client is None or self.db is None:
                self._connect()
            self.client.admin.command('ping')
        except (ConnectionFailure, ServerSelectionTimeoutError):
            self._connect()

    @retry_with_backoff()
    def insert_post(self, tweet_id: str, text: str, media_path: Optional[str] = None) -> str:
        """
        Insert a new post into the database.
        
        Args:
            tweet_id: The ID of the tweet
            text: The tweet text
            media_path: Optional path to media file
            
        Returns:
            The inserted document ID
        """
        try:
            post = {
                "tweet_id": tweet_id,
                "text": text,
                "media_path": media_path,
                "created_at": datetime.utcnow(),
                "metrics": {
                    "likes": 0,
                    "retweets": 0,
                    "replies": 0
                }
            }
            result = self.db.posts.insert_one(post)
            logger.info(f"Inserted post with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Failed to insert post: {str(e)}")
            raise

    @retry_with_backoff()
    def update_post_metrics(self, tweet_id: str, metrics: Dict[str, int]) -> None:
        """Update post metrics."""
        try:
            self.db.posts.update_one(
                {"tweet_id": tweet_id},
                {"$set": {"metrics": metrics}}
            )
            logger.info(f"Updated metrics for tweet: {tweet_id}")
        except PyMongoError as e:
            logger.error(f"Failed to update post metrics: {str(e)}")
            raise

    @retry_with_backoff(max_retries=3)
    def get_recent_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent posts with connection check."""
        self._ensure_connection()
        try:
            return list(
                self.db.posts.find()
                .sort("created_at", pymongo.DESCENDING)
                .limit(limit)
            )
        except PyMongoError as e:
            logger.error(f"Failed to get recent posts: {str(e)}")
            raise

    @retry_with_backoff(max_retries=3)
    def save_analytics(self, data: Dict[str, Any]) -> str:
        """Save analytics data with connection check."""
        self._ensure_connection()
        try:
            data["date"] = datetime.utcnow()
            result = self.db.analytics.insert_one(data)
            logger.info(f"Saved analytics with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Failed to save analytics: {str(e)}")
            raise

    @retry_with_backoff(max_retries=3)
    def log_interaction(self, tweet_id: str, interaction_type: str, 
                       user_id: Optional[str] = None) -> str:
        """Log user interaction with connection check."""
        self._ensure_connection()
        try:
            interaction = {
                "tweet_id": tweet_id,
                "type": interaction_type,
                "user_id": user_id,
                "timestamp": datetime.utcnow()
            }
            result = self.db.interactions.insert_one(interaction)
            logger.info(f"Logged interaction with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Failed to log interaction: {str(e)}")
            raise

    def close(self) -> None:
        """Close database connection."""
        try:
            if self.client:
                self.client.close()
                self.client = None
                self.db = None
                logger.info("Database connection closed")
        except PyMongoError as e:
            logger.error(f"Error closing database connection: {str(e)}")
            raise

# Create global database instance
db = Database()