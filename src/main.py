import asyncio
import sys
from typing import Annotated

from plumbum import ProcessExecutionError, local
from pydantic import Field
from pydantic_ai import Agent, Tool
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.run import AgentRunResult

from src.settings import settings


class ShellTool(Tool):
    def __init__(self):
        super().__init__(self.run)

    def run(
        self,
        command: Annotated[
            str,
            Field(
                ...,
                description="The valid, executable shell command to run. Do not include explanations or context.",
            ),
        ],
        read_only: Annotated[
            bool,
            Field(
                ...,
                description="Is the command read-only? (e.g., 'ls', 'cat', 'grep'). Set to false for commands that modify state (e.g., 'rm', 'mkdir', 'mv').",
            ),
        ],
    ) -> str:
        """
        Executes a shell command on the user's local machine.
        Use this for tasks involving file system operations (ls, find, du), process management (ps, kill),
        or other command-line interactions. Do NOT use this for general knowledge questions; use the search tool for that.
        Returns the stdout and stderr of the command.
        """
        print(f"\n▶️  Command: {command}")
        try:
            execute = False
            if read_only:
                execute = True
            else:
                confirm = input("  Execute? (y/n): ").lower()
                if confirm == "y":
                    execute = True

            if execute:
                bash = local["bash"]
                retcode, stdout, stderr = bash["-c", command].run(retcode=None)
                output = f"Stdout:\n{stdout}\nStderr:\n{stderr}\n"
                # print(f"  Output:\n{output}")
                return output
            else:
                return "User cancelled execution."

        except ProcessExecutionError as e:
            error_output = f"An error occurred.\nStdout:\n{e.stdout}\nStderr:\n{e.stderr}\n"
            print(f"  {error_output}")
            return error_output
        except Exception as e:
            error_output = f"An unexpected error occurred: {e}"
            print(f"  {error_output}")
            return error_output


async def main():
    """
    The main function for the terminal agent.
    """
    if len(sys.argv) < 2:
        print("Usage: python -m src.main <your query>")
        return

    query = " ".join(sys.argv[1:])

    provider = GoogleProvider(api_key=settings.gemini_api_key)
    model = GoogleModel(settings.gemini_model_name, provider=provider)

    search_tool = duckduckgo_search_tool()
    shell_tool = ShellTool()

    ai = Agent(model, tools=[shell_tool, search_tool])

    print(f"Goal: {query}\n")
    print("🤔 Thinking...")

    # The agent will now handle the conversation and tool calls automatically
    response: AgentRunResult = await ai.run(query)
    print(f"\n✅ Final Answer: {response.output}")



if __name__ == "__main__":
    asyncio.run(main())
