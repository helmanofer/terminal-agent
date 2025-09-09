from abc import ABC, abstractmethod
from typing import Any

from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from pydantic_ai.models.bedrock import BedrockConverseModel
from pydantic_ai.providers.bedrock import BedrockProvider

from src.settings import Settings


class LLMService(ABC):
    @abstractmethod
    def get_model(self) -> Any:
        ...


class GoogleService(LLMService):
    def __init__(self, settings: Settings):
        self.settings = settings

    def get_model(self) -> GoogleModel:
        provider = GoogleProvider(api_key=self.settings.gemini_api_key)
        return GoogleModel(self.settings.gemini_model_name, provider=provider)


class BedrockService(LLMService):
    def __init__(self, settings: Settings):
        self.settings = settings

    def get_model(self) -> BedrockConverseModel:
        provider = BedrockProvider(
            profile_name=self.settings.aws_profile_name,
            region_name=self.settings.aws_region_name,
            aws_access_key_id=self.settings.aws_access_key_id,
            aws_secret_access_key=self.settings.aws_secret_access_key,
        )

        return BedrockConverseModel(self.settings.bedrock_model_name, provider=provider)


def get_llm_service(settings: Settings) -> LLMService:
    if settings.provider == "google":
        return GoogleService(settings)
    elif settings.provider == "bedrock":
        return BedrockService(settings)
    else:
        raise ValueError(
            "No LLM provider configured. Please set either Google or AWS "
            "Bedrock credentials."
        )
