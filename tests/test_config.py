import os
from unittest.mock import patch

from app.config import Settings, settings


def test_settings_default_values(monkeypatch):
    """Test that Settings class has correct default values."""
    for name in ("APP_NAME", "APP_ENV", "DEBUG", "HOST", "PORT", "LOG_LEVEL"):
        monkeypatch.delenv(name, raising=False)
    test_settings = Settings(_env_file=None)
    assert test_settings.APP_NAME == "FastAPI Starter"
    assert test_settings.APP_ENV == "development"
    assert test_settings.DEBUG is False
    assert test_settings.HOST == "0.0.0.0"
    assert test_settings.PORT == 8000
    assert test_settings.LOG_LEVEL == "info"


def test_settings_from_env_vars():
    """Test that Settings can be overridden by environment variables."""
    with patch.dict(os.environ, {
        'APP_NAME': 'Test App',
        'APP_ENV': 'production',
        'DEBUG': 'true',
        'HOST': '127.0.0.1',
        'PORT': '9000',
        'LOG_LEVEL': 'debug'
    }):
        test_settings = Settings()
        assert test_settings.APP_NAME == "Test App"
        assert test_settings.APP_ENV == "production"
        assert test_settings.DEBUG is True
        assert test_settings.HOST == "127.0.0.1"
        assert test_settings.PORT == 9000
        assert test_settings.LOG_LEVEL == "debug"


def test_settings_instance_exists():
    """Test that the settings instance is properly instantiated."""
    assert settings is not None
    assert isinstance(settings, Settings)


def test_settings_model_config():
    """Test that the Settings class has proper model configuration."""
    test_settings = Settings()
    model_config = test_settings.model_config
    
    assert model_config['env_file'] == ".env"
    assert model_config['env_file_encoding'] == "utf-8"
    assert model_config['extra'] == "ignore"


def test_settings_port_type():
    """Test that PORT setting is properly typed as integer."""
    test_settings = Settings()
    assert isinstance(test_settings.PORT, int)


def test_settings_debug_type():
    """Test that DEBUG setting is properly typed as boolean."""
    test_settings = Settings()
    assert isinstance(test_settings.DEBUG, bool)


def test_settings_with_unknown_env_vars():
    """Test Settings with unknown environment variables are ignored."""
    with patch.dict(os.environ, {
        'APP_ENV': 'test',
        'UNKNOWN_VAR': 'should_be_ignored'
    }):
        test_settings = Settings()
        assert test_settings.APP_ENV == "test"
        # Should not raise an error due to extra="ignore"
        assert not hasattr(test_settings, 'UNKNOWN_VAR')
