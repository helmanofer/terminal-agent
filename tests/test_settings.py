import os
from unittest.mock import patch

from src.settings import Settings


def test_settings_loading_from_env_file():
    """Test that settings are correctly loaded from a .env file."""
    # Create a dummy .env file
    with open(".env", "w") as f:
        f.write("GEMINI_API_KEY=test_key_from_file\n")
        f.write("GEMINI_MODEL_NAME=test_model_from_file\n")

    settings = Settings()
    assert settings.gemini_api_key == "test_key_from_file"
    assert settings.gemini_model_name == "test_model_from_file"

    # Clean up the dummy .env file
    os.remove(".env")


def test_settings_loading_from_env_variables():
    """Test that settings are correctly loaded from environment variables."""
    with patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "test_key_from_env",
            "GEMINI_MODEL_NAME": "test_model_from_env",
        },
    ):
        settings = Settings()
        assert settings.gemini_api_key == "test_key_from_env"
        assert settings.gemini_model_name == "test_model_from_env"


def test_settings_defaults():
    """Test that default settings are used when no other source is available."""
    # Ensure no .env file exists
    if os.path.exists(".env"):
        os.remove(".env")

    # Ensure no relevant environment variables are set
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings()
        assert settings.gemini_api_key == ""
        assert settings.gemini_model_name == "gemini-1.5-flash"
