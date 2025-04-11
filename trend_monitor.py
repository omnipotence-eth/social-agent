from serpapi import search
from config import settings
from utils import logger

def get_trending_topics():
    """Get trending topics from Google Trends."""
    try:
        params = {
            "engine": "google_trends",
            "q": "technology, ai, fashion, architecture, design",
            "api_key": settings.SERPAPI_API_KEY
        }
        results = search(params)
        trending_searches = results.get('trending_searches', [])
        return [search['title'] for search in trending_searches[:5]] or ["technology"]
    except Exception as e:
        logger.error(f"Error getting trending topics: {e}")
        return ["technology"]

def get_trending_hashtags():
    """Get trending hashtags from Google Trends and convert them to hashtags."""
    try:
        # Use the same trending topics but format them as hashtags
        topics = get_trending_topics()
        hashtags = [f"#{topic.lower().replace(' ', '')}" for topic in topics]
        return hashtags or ["#technology", "#ai"]
    except Exception as e:
        logger.error(f"Error getting trending hashtags: {e}")
        return ["#technology", "#ai"]