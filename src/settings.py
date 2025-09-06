from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    gemini_api_key: str = ""
    gemini_model_name: str = "gemini-1.5-flash"


settings = Settings()
