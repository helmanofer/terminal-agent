from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    # Google Gemini settings
    gemini_api_key: str = ""
    gemini_model_name: str = "gemini-1.5-flash"

    # AWS Bedrock settings
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region_name: str = ""
    aws_profile_name: str = ""
    bedrock_model_name: str = "anthropic.claude-3-sonnet-20240229-v1:0"


settings = Settings()
