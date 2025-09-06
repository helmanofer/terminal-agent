import asyncio
import subprocess
import sys

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from src.settings import settings


class ShellCommand(BaseModel):
    """Represents a shell command to be executed."""

    command: str = Field(..., description="The shell command to execute.")
    reasoning: str = Field(
        ..., description="A brief explanation of why this command was chosen."
    )


async def main():
    """
    This is the main function that runs the Pydantic AI agent.
    """
    if len(sys.argv) < 2:
        print("Usage: python -m src.main <your query>")
        return

    query = " ".join(sys.argv[1:])

    provider = GoogleProvider(api_key=settings.gemini_api_key)
    model = GoogleModel(settings.gemini_model_name, provider=provider)
    ai = Agent(model, output_type=ShellCommand)

    print(f"Query: {query}")
    print("Thinking...")

    result = await ai.run(query)
    shell_command: ShellCommand = result.output

    print(f"\nReasoning: {shell_command.reasoning}")
    print(f"Command: {shell_command.command}")

    try:
        confirm = input("\nExecute? (y/n): ").lower()
        if confirm == "y":
            process = subprocess.run(
                shell_command.command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if process.stdout:
                print(f"\nOutput:\n{process.stdout}")
            if process.stderr:
                print(f"\nErrors:\n{process.stderr}")
        else:
            print("Execution cancelled.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        if e.stdout:
            print(f"\nOutput:\n{e.stdout}")
        if e.stderr:
            print(f"\nErrors:\n{e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
