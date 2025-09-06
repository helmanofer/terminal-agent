import asyncio
import sys
from dataclasses import dataclass
from typing import Annotated, Any

from plumbum import ProcessExecutionError, local
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, RunUsage, UsageLimits
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from rich import print

from src.settings import settings


class ShellResult(BaseModel):
    """Result from executing a shell command"""

    command: str
    output: str
    success: bool


class TaskComplete(BaseModel):
    """Indicates the task has been completed successfully"""

    result: str
    summary: str


class TaskContinue(BaseModel):
    """Indicates more exploration is needed"""

    next_step: str
    reason: str


class TaskFailed(BaseModel):
    """Indicates the task failed"""

    error: str
    attempted_steps: list[str]


@dataclass
class ShellContext:
    """Context for tracking shell operations"""

    query: str
    steps_taken: list[str]
    discoveries: dict[str, str]
    max_iterations: int = 10


async def create_shell_agent(
    model: Any,
) -> Agent[None, TaskComplete | TaskContinue | TaskFailed]:
    """Create a single agent for handling complex shell queries"""
    search_tool = duckduckgo_search_tool()

    system_prompt = """
    You are an intelligent shell assistant that can handle complex,
    multi-stage queries.

    Your approach:
    1. EXPLORE FIRST: Use discovery commands to understand the system state
    2. BE METHODICAL: Break complex queries into logical steps
    3. LEARN AND ADAPT: Use previous command results to inform next steps
    4. BE SPECIFIC: When you find what you're looking for, provide exact
       commands

    For ambiguous queries like "show container logs":
    - First run 'docker ps' to see running containers
    - Then run 'kubectl get pods' to check k8s pods
    - Finally get logs from the most relevant container/pod

    For queries about "something" or partial names:
    - Use grep, find, or ps to search for matches
    - Try multiple discovery approaches
    - Present findings clearly

    IMPORTANT:
    - return TaskComplete ONLY when you've successfully answered the
      user's query
    - Return TaskContinue if you need to explore more
    - Return TaskFailed only if you've exhausted reasonable options
    """

    agent = Agent(  # type: ignore[call-overload]
        model,
        tools=[search_tool],
        system_prompt=system_prompt,
        output_type=TaskComplete | TaskContinue | TaskFailed,
    )

    @agent.tool
    def run_shell_command(
        ctx: RunContext[None],
        command: Annotated[
            str,
            Field(
                description="Valid shell command to execute. Use discovery "
                "commands like 'docker ps', 'kubectl get pods', 'ps aux', "
                "'ls', 'find' to explore first."
            ),
        ],
        read_only: Annotated[
            bool,
            Field(
                description="True for read-only commands (ls, ps, docker ps, "
                "etc.), False for commands that modify state."
            ),
        ],
        timeout: Annotated[
            int,
            Field(
                default=30,
                description="Timeout in seconds for command execution. "
                "Default is 30 seconds. Use longer timeouts for commands "
                "that may take time (e.g., large file operations, "
                "network requests).",
                ge=1,
                le=300,
            ),
        ] = 30,
    ) -> ShellResult:
        """
        Execute a shell command on the local system.

        Use for:
        - System exploration: ps, ls, find, docker ps, kubectl get
        - Log viewing: tail, cat, journalctl, docker logs
        - Status checking: systemctl status, df -h, top
        - File operations: grep, sed, awk
        """
        print(f"\n[bold blue]▶️  Executing:[/bold blue] [yellow]`{command}`[/yellow] with timeout {timeout} seconds")

        try:
            execute = False
            if read_only:
                execute = True
            else:
                confirm = input("  Execute modifying command? (y/n): ").lower()
                execute = confirm == "y"

            if execute:
                bash = local["bash"]
                retcode, stdout, stderr = bash["-c", command].run(
                    retcode=None, timeout=timeout)

                # Display output to user immediately
                if stdout.strip():
                    print(f"[green]📄 Output:[/green]\n{stdout}")
                if stderr.strip():
                    print(f"[yellow]⚠️  Stderr:[/yellow]\n{stderr}")
                if retcode != 0:
                    print(f"[red]❌ Exit code: {retcode}[/red]")

                # Determine success based on return code
                success = retcode == 0
                output = f"Exit code: {retcode}\nStdout:\n{stdout}\n"
                f"Stderr:\n{stderr}"

                return ShellResult(command=command, output=output, success=success)
            else:
                return ShellResult(
                    command=command,
                    output="Command execution cancelled by user.",
                    success=False,
                )

        except ProcessExecutionError as e:
            # Display error output to user immediately
            if e.stdout.strip():
                print(f"[green]📄 Output:[/green]\n{e.stdout}")
            if e.stderr.strip():
                print(f"[yellow]⚠️  Stderr:[/yellow]\n{e.stderr}")
            print(f"[red]❌ Exit code: {e.retcode}[/red]")

            output = (
                f"Command failed with exit code {e.retcode}\n"
                f"Stdout:\n{e.stdout}\nStderr:\n{e.stderr}"
            )
            return ShellResult(command=command, output=output, success=False)
        except Exception as e:
            return ShellResult(
                command=command,
                output=f"Unexpected error: {e}",
                success=False,
            )

    return agent  # type: ignore[no-any-return]


async def run_shell_workflow(query: str, model: Any) -> None:
    """Main workflow for handling shell queries with conversation continuity"""
    print(f"[bold cyan]🔍 Starting shell workflow for:[/bold cyan] [white]{query}[/white]")

    context = ShellContext(query=query, steps_taken=[], discoveries={})

    # Create the agent
    agent = await create_shell_agent(model)

    # Initialize conversation state
    message_history: list[ModelMessage] | None = None
    usage = RunUsage()
    usage_limits = UsageLimits(request_limit=20)

    iteration = 0

    while iteration < context.max_iterations:
        iteration += 1
        print(f"\n[bold magenta]📋 Iteration {iteration}[/bold magenta]")

        try:
            # Construct the prompt for this iteration
            if iteration == 1:
                prompt = f"Handle this query: {query}"
            else:
                prompt = "Continue with the next step based on previous results."

            # Run the agent
            result = await agent.run(
                prompt,
                message_history=message_history,
                usage=usage,
                usage_limits=usage_limits,
            )

            output = result.output
            context.steps_taken.append(f"Iteration {iteration}")

            if isinstance(output, TaskComplete):
                print("\n[bold green]✅ Task completed successfully![/bold green]")
                print(f"[green]Result:[/green] {output.result}")
                print(f"[green]Summary:[/green] {output.summary}")
                print(f"[blue]Total iterations:[/blue] {iteration}")
                print(f"[blue]Usage:[/blue] {usage}")
                return

            elif isinstance(output, TaskContinue):
                print(f"[yellow]🔄 Continuing:[/yellow] {output.next_step}")
                print(f"[yellow]Reason:[/yellow] {output.reason}")
                # Update message history to maintain conversation context
                message_history = result.all_messages()

            elif isinstance(output, TaskFailed):
                print(f"\n[bold red]❌ Task failed:[/bold red] {output.error}")
                print(f"[red]Attempted steps:[/red] {', '.join(output.attempted_steps)}")
                return

        except Exception as e:
            print(f"\n[bold red]💥 Error in iteration {iteration}:[/bold red] {e}")
            if iteration >= 3:  # Give up after 3 errors
                print("[red]Too many errors, giving up.[/red]")
                return
            continue

    print(f"\n[yellow]⏰ Reached maximum iterations ({context.max_iterations})[/yellow]")
    print(f"[blue]Steps taken:[/blue] {', '.join(context.steps_taken)}")


async def async_main() -> None:
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python -m src.main3 <your query>")
        print("Examples:")
        print("  python -m src.main3 'show me docker container logs'")
        print("  python -m src.main3 'find processes using port 8080'")
        print("  python -m src.main3 'check disk usage and find large files'")
        return

    query = " ".join(sys.argv[1:])

    provider = GoogleProvider(api_key=settings.gemini_api_key)
    model = GoogleModel(settings.gemini_model_name, provider=provider)

    print(f"[bold cyan]🎯 Goal:[/bold cyan] [white]{query}[/white]\n")

    await run_shell_workflow(query, model)


def main() -> None:
    """Console script entry point"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
