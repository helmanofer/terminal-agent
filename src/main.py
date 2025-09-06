import asyncio

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from src.settings import settings


async def main():
    """
    This is the main function that runs the Pydantic AI agent.
    """
    provider = GoogleProvider(api_key=settings.gemini_api_key)
    model = GoogleModel(settings.gemini_model_name, provider=provider)
    ai = Agent(model)
    response = await ai.run("hello")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
