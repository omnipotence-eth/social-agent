import os
import json
import requests
import modal
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
from PIL import Image
from io import BytesIO
import logging
from dotenv import load_dotenv
import aiohttp
from config import settings
from utils import retry_with_backoff

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modal configuration
stub = modal.Stub("social-agent-image-generator")
image = modal.Image.debian_slim().pip_install("Pillow", "requests", "python-dotenv", "torch", "diffusers", "transformers")

class ImageGenerator:
    """Handles image generation using Modal."""
    
    def __init__(self):
        """Initialize the image generator."""
        self.api_key = settings.MODAL_API_KEY
        self.base_url = "https://api.x.ai/v1/images/generations"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.image_dir = Path("data/images")
        self.image_dir.mkdir(parents=True, exist_ok=True)
        
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
            
    @stub.function(image=image)
    def download_image(self, url: str, filename: Optional[str] = None) -> Optional[str]:
        """
        Download an image from a URL and save it locally.
        
        Args:
            url (str): The URL of the image to download
            filename (Optional[str]): Custom filename (default: timestamp-based)
            
        Returns:
            Optional[str]: Path to the downloaded image or None if download failed
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"image_{timestamp}.png"
                
            filepath = self.image_dir / filename
            
            with open(filepath, "wb") as f:
                f.write(response.content)
                
            return str(filepath)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading image: {str(e)}")
            return None
            
    @stub.function(image=image)
    def process_image(self, image_path: str, size: tuple = (1080, 1080)) -> Optional[str]:
        """
        Process an image (resize, format) for social media.
        
        Args:
            image_path (str): Path to the image file
            size (tuple): Target size for the image (default: (1080, 1080))
            
        Returns:
            Optional[str]: Path to the processed image or None if processing failed
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != "RGB":
                    img = img.convert("RGB")
                    
                # Resize image
                img = img.resize(size, Image.Resampling.LANCZOS)
                
                # Save processed image
                processed_path = str(Path(image_path).with_suffix("_processed.jpg"))
                img.save(processed_path, "JPEG", quality=95)
                
                return processed_path
                
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return None
            
    def generate_and_process(self, prompt: str, size: str = "1024x1024") -> Optional[Dict[str, Any]]:
        """
        Generate and process an image in one step.
        
        Args:
            prompt (str): The text prompt to generate the image from
            size (str): The size of the image to generate (default: "1024x1024")
            
        Returns:
            Optional[Dict[str, Any]]: Dictionary containing image information or None if failed
        """
        try:
            # Generate image
            image_url = self.generate_image(prompt)
            if not image_url:
                return None
                
            # Download image
            image_path = self.download_image(image_url)
            if not image_path:
                return None
                
            # Process image
            processed_path = self.process_image(image_path)
            if not processed_path:
                return None
                
            return {
                "original_url": image_url,
                "original_path": image_path,
                "processed_path": processed_path,
                "prompt": prompt
            }
            
        except Exception as e:
            logger.error(f"Error in generate_and_process: {str(e)}")
            return None

# Create global instance
image_generator = ImageGenerator()

# Example usage
if __name__ == "__main__":
    generator = ImageGenerator()
    result = generator.generate_and_process(
        "A futuristic cityscape at sunset with flying cars",
        size="1024x1024"
    )
    
    if result:
        print(f"Generated image saved at: {result['processed_path']}")
    else:
        print("Failed to generate and process image") 