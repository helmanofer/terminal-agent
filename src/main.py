import asyncio
import sys

from plumbum import local
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
            bash = local["bash"]
            retcode, stdout, stderr = bash["-c", shell_command.command].run()
            if stdout:
                print(f"\nOutput:\n{stdout}")
            if stderr:
                print(f"\nErrors:\n{stderr}")
        else:
            print("Execution cancelled.")
    except FileNotFoundError:
        print("bash command not found. Please ensure bash is in your PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
