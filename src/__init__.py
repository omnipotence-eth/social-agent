"""
Social Agent - An automated social media content generation and posting system.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .content_generator import ContentGenerator
from .image_generator import ImageGenerator
from .x_api_client import XAPIClient
from .database import MongoDB
from .utils import logger, rate_limit, retry_with_backoff
from .config import settings

__all__ = [
    'ContentGenerator',
    'ImageGenerator',
    'XAPIClient',
    'MongoDB',
    'logger',
    'rate_limit',
    'retry_with_backoff',
    'settings'
] 