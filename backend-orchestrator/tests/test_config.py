"""Test config module."""
import os
import pytest
from unittest.mock import patch, MagicMock

os.environ["GEMINI_API_KEY"] = "test-key"
os.environ["DEBUG"] = "true"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/testdb"


def test_settings_defaults():
    """Test that settings have correct defaults."""
    # Clear cached settings
    from app.config import get_settings
    get_settings.cache_clear()
    
    with patch.dict(os.environ, {
        "GEMINI_API_KEY": "test-key",
        "DEBUG": "true",
    }, clear=True):
        get_settings.cache_clear()
        settings = get_settings()
        
        assert settings.APP_NAME == "SupportSight Live"
        assert settings.DEBUG is True
        assert settings.GEMINI_API_KEY == "test-key"


def test_settings_production():
    """Test production settings."""
    from app.config import get_settings
    get_settings.cache_clear()
    
    with patch.dict(os.environ, {
        "GEMINI_API_KEY": "prod-key",
        "ENVIRONMENT": "production",
        "DEBUG": "false",
    }, clear=True):
        get_settings.cache_clear()
        settings = get_settings()
        
        assert settings.ENVIRONMENT == "production"
        assert settings.DEBUG is False


def test_settings_database_url():
    """Test database URL configuration."""
    from app.config import get_settings
    get_settings.cache_clear()
    
    test_url = "postgresql+asyncpg://user:pass@host:5432/db"
    with patch.dict(os.environ, {
        "GEMINI_API_KEY": "test-key",
        "DATABASE_URL": test_url,
    }, clear=True):
        get_settings.cache_clear()
        settings = get_settings()
        
        assert settings.DATABASE_URL == test_url


def test_settings_cors_origins():
    """Test CORS origins configuration."""
    from app.config import get_settings
    get_settings.cache_clear()
    
    with patch.dict(os.environ, {
        "GEMINI_API_KEY": "test-key",
        "ALLOWED_ORIGINS": "https://example.com,https://app.example.com",
    }, clear=True):
        get_settings.cache_clear()
        settings = get_settings()
        
        assert "https://example.com" in settings.ALLOWED_ORIGINS
