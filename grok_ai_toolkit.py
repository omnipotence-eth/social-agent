"""
GrokAI Toolkit for interacting with the Grok API.
"""

import requests
from typing import Dict, List, Optional
from config import settings
from utils import logger

class GrokAI:
    """GrokAI API client."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize GrokAI client."""
        self.api_key = api_key or settings.GROK_API_KEY
        self.base_url = "https://api.x.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.9,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0
    ) -> str:
        """
        Generate text using GrokAI.
        
        Args:
            prompt: The prompt to generate text from
            system_prompt: Optional system prompt to guide the model's behavior
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (0.0-1.0)
            top_p: Controls diversity via nucleus sampling (0.0-1.0)
            frequency_penalty: Penalizes frequent tokens (-2.0-2.0)
            presence_penalty: Penalizes repeated tokens (-2.0-2.0)
            
        Returns:
            Generated text
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": "grok-beta",
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "frequency_penalty": frequency_penalty,
                "presence_penalty": presence_penalty
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error generating text with GrokAI: {e}")
            return ""
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text."""
        try:
            messages = [
                {"role": "system", "content": "Analyze the sentiment of the following text."},
                {"role": "user", "content": text}
            ]
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": "grok-beta",
                    "messages": messages,
                    "temperature": 0.2,
                    "max_tokens": 50
                }
            )
            response.raise_for_status()
            
            # Parse sentiment from response
            sentiment_text = response.json()["choices"][0]["message"]["content"].lower()
            sentiment = {
                "positive": 0.0,
                "negative": 0.0,
                "neutral": 1.0
            }
            
            if "positive" in sentiment_text:
                sentiment["positive"] = 0.8
                sentiment["neutral"] = 0.2
            elif "negative" in sentiment_text:
                sentiment["negative"] = 0.8
                sentiment["neutral"] = 0.2
                
            return sentiment
        except Exception as e:
            logger.error(f"Error analyzing sentiment with GrokAI: {e}")
            return {"positive": 0.0, "negative": 0.0, "neutral": 1.0}
    
    def generate_hashtags(self, text: str, max_hashtags: int = 5) -> List[str]:
        """Generate relevant hashtags for text."""
        try:
            messages = [
                {"role": "system", "content": f"Generate {max_hashtags} relevant hashtags for the following text."},
                {"role": "user", "content": text}
            ]
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": "grok-beta",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 50
                }
            )
            response.raise_for_status()
            
            # Parse hashtags from response
            hashtags_text = response.json()["choices"][0]["message"]["content"]
            hashtags = [tag.strip() for tag in hashtags_text.split() if tag.startswith("#")]
            return hashtags[:max_hashtags]
        except Exception as e:
            logger.error(f"Error generating hashtags with GrokAI: {e}")
            return [] 