from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    provider: str = "bedrock"
    # Google Gemini settings
    gemini_api_key: str = ""
    gemini_model_name: str = "gemini-1.5-flash"

    # AWS Bedrock settings
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region_name: str = "eu-west-1"
    aws_profile_name: str = "dev"
    bedrock_model_name: str = "eu.anthropic.claude-sonnet-4-20250514-v1:0"


settings = Settings()
