import pytest
from unittest.mock import Mock, patch
from content_generator import ContentGenerator
from config import settings

@pytest.fixture
def content_generator():
    return ContentGenerator()

def test_generate_content(content_generator):
    """Test content generation."""
    with patch.object(content_generator, '_make_request') as mock_request:
        mock_request.return_value = "Test tweet content"
        content = content_generator.generate_content("Test prompt")
        assert content is not None
        assert len(content) <= settings.MAX_TWEET_LENGTH
        mock_request.assert_called_once()

def test_generate_hashtags(content_generator):
    """Test hashtag generation."""
    with patch.object(content_generator, '_make_request') as mock_request:
        mock_request.return_value = "#test #ai #technology"
        hashtags = content_generator.generate_hashtags("Test content")
        assert len(hashtags) <= 5
        assert all(tag.startswith('#') for tag in hashtags)

def test_generate_reply(content_generator):
    """Test reply generation."""
    with patch.object(content_generator, '_make_request') as mock_request:
        mock_request.return_value = "Test reply"
        reply = content_generator.generate_reply("Original tweet")
        assert reply is not None
        assert len(reply) <= settings.MAX_TWEET_LENGTH

def test_rate_limiting(content_generator):
    """Test rate limiting functionality."""
    # Test rate limiting
    for _ in range(settings.GROK_RATE_LIMIT):
        content_generator.generate_content("Test prompt") 