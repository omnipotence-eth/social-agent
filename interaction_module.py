from x_api_client import x_client
from content_generator import content_generator
from textblob import TextBlob
from utils import logger

def handle_interactions():
    try:
        query = "from:verified (technology OR ai OR fashion OR architecture OR design)"
        tweets = x_client.search_tweets(query, count=5)
        for tweet in tweets:
            sentiment = TextBlob(tweet['text']).sentiment.polarity
            prompt = (
                f"Reply positively to this tweet: {tweet['text']}"
                if sentiment > 0
                else f"Reply encouragingly to this tweet: {tweet['text']}"
            )
            reply_text = content_generator.generate_reply(tweet['text'])
            x_client.reply_to_tweet(tweet['id'], reply_text)
            x_client.like_tweet(tweet['id'])
            x_client.retweet(tweet['id'])
    except Exception as e:
        logger.error(f"Error in handle_interactions: {e}")