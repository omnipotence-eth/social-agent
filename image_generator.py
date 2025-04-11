"""
Image generation module using Modal.
"""

import os
import requests
from typing import Optional
from config import settings
from utils import logger, retry_with_backoff
from modal import Image, Stub, web_endpoint

stub = Stub("image-generator")
image = Image.debian_slim().pip_install("torch", "diffusers", "transformers")

class ImageGenerator:
    """Handles image generation using Modal."""
    
    def __init__(self):
        """Initialize the image generator."""
        self.api_key = settings.MODAL_API_KEY
        
    @retry_with_backoff(max_retries=settings.MAX_RETRIES)
    def generate_image(self, prompt: str) -> Optional[str]:
        """
        Generate an image using Modal's Stable Diffusion.
        
        Args:
            prompt: Text description of the image to generate
            
        Returns:
            URL of the generated image or None if generation failed
        """
        try:
            # Call Modal endpoint for image generation
            response = requests.post(
                "https://modal.com/api/v1/stable-diffusion",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"prompt": prompt}
            )
            response.raise_for_status()
            return response.json()["image_url"]
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return None

# Create global instance
image_generator = ImageGenerator()

if __name__ == "__main__":
    import asyncio
    # Test the image generation
    async def test():
        # Deploy the app first
        print("Deploying Modal app...")
        await stub.deploy()
        print("Modal app deployed, generating image...")
        result = await image_generator.generate_image("a beautiful sunset over mountains")
        print(f"Generated image: {result}")
    
    asyncio.run(test())