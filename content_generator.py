from typing import Optional, List
import requests
from config import settings
from utils import logger, rate_limit, retry_with_backoff, sanitize_text
from grok_ai_toolkit import GrokAI

class ContentGenerator:
    """Handles content generation using Grok's API."""
    
    def __init__(self):
        """Initialize the content generator."""
        self.grok = GrokAI(api_key=settings.GROK_API_KEY)
        self.max_tokens = 280  # Maximum tweet length

    @rate_limit(max_requests=settings.GROK_RATE_LIMIT)
    @retry_with_backoff(max_retries=settings.MAX_RETRIES)
    def _make_request(self, prompt: str, system_prompt: str = None) -> str:
        """Make a request to the Grok API."""
        try:
            response = self.grok.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=self.max_tokens,
                temperature=0.7,
                top_p=0.9,
                frequency_penalty=0.5,
                presence_penalty=0.5
            )
            return response
        except Exception as e:
            logger.error(f"Error making Grok request: {str(e)}")
            raise

    def generate_tweet(self, topic: str) -> Optional[str]:
        """Generate an inspiring and informative tweet about a topic."""
        try:
            prompt = (
                f"Create a complete, natural tweet about {topic}. "
                "The tweet should:"
                "\n1. Be a complete thought (under 140 characters)"
                "\n2. Share one clear, interesting fact or insight"
                "\n3. Use simple, everyday language"
                "\n4. Focus on technology, AI, or science"
                "\n5. Be factually accurate"
                "\n6. Sound like a friend sharing something cool"
                "\n7. End with a complete sentence"
                "\n8. Avoid technical terms unless explained simply"
            )
            
            tweet = self._make_request(prompt)
            if not tweet:
                logger.error("Failed to generate tweet")
                return None
                
            # Ensure tweet is under 140 characters and complete
            tweet = tweet[:140]
            if not tweet.endswith(('.', '!', '?')):
                tweet = tweet.rsplit('.', 1)[0] + '.'
            return tweet
            
        except Exception as e:
            logger.error(f"Error generating tweet: {str(e)}")
            return None

    def generate_thread(self, topic: str) -> List[str]:
        """Generate an informative thread about a topic."""
        try:
            prompt = (
                f"Create a natural, educational thread about {topic}. "
                "The thread should:"
                "\n1. Have 3-4 complete tweets"
                "\n2. Each tweet should be under 140 characters"
                "\n3. Start with an interesting fact or question"
                "\n4. Each tweet should be a complete thought"
                "\n5. Build knowledge step by step"
                "\n6. End with a meaningful conclusion"
                "\n7. Use simple, clear language"
                "\n8. Explain complex ideas in everyday terms"
            )
            
            thread_text = self._make_request(prompt)
            if not thread_text:
                logger.error("Failed to generate thread")
                return []
                
            # Split into individual tweets and ensure completeness
            tweets = [t.strip() for t in thread_text.split('\n') if t.strip()]
            tweets = [t[:140] for t in tweets]
            
            # Ensure each tweet is a complete thought
            processed_tweets = []
            for tweet in tweets[:4]:  # Limit to 4 tweets
                if not tweet.endswith(('.', '!', '?')):
                    tweet = tweet.rsplit('.', 1)[0] + '.'
                processed_tweets.append(tweet)
            
            return processed_tweets
            
        except Exception as e:
            logger.error(f"Error generating thread: {str(e)}")
            return []

    def generate_hashtags(self, content: str) -> List[str]:
        """
        Generate relevant hashtags for the content.
        
        Args:
            content: The content to generate hashtags for
            
        Returns:
            List of generated hashtags
        """
        try:
            prompt = f"Generate 3-5 relevant hashtags for this content: {content}"
            system_prompt = "You are a hashtag generator."
            
            response = self._make_request(prompt, system_prompt)
            hashtags = response.strip().split()
            # Clean and format hashtags
            hashtags = [f"#{tag.strip('#')}" for tag in hashtags if tag.strip('#')]
            return hashtags[:5]  # Return at most 5 hashtags
            
        except Exception as e:
            logger.error(f"Error generating hashtags: {str(e)}")
            return []

    def generate_reply(self, tweet_text: str) -> Optional[str]:
        """
        Generate a reply to a tweet.
        
        Args:
            tweet_text: The tweet to reply to
            
        Returns:
            Generated reply or None if generation failed
        """
        try:
            prompt = (
                f"Generate a positive and engaging reply to this tweet: {tweet_text}\n"
                "Keep it concise and relevant."
            )
            system_prompt = "You are a friendly and engaging social media user."
            
            reply = self._make_request(prompt, system_prompt)
            return sanitize_text(reply, settings.MAX_TWEET_LENGTH)
            
        except Exception as e:
            logger.error(f"Error generating reply: {str(e)}")
            raise

# Create global instance
content_generator = ContentGenerator()