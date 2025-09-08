from unittest.mock import MagicMock, patch

import pytest
from plumbum import ProcessExecutionError
from pydantic_ai import RunContext, RunUsage

from src.main import run_shell_command


@pytest.mark.asyncio
async def test_run_shell_command_readonly_success():
    """Test successful execution of a read-only command."""
    ctx = RunContext(deps=None, model=MagicMock(), usage=RunUsage())

    with patch("src.main.local") as mock_local:
        mock_bash = mock_local.__getitem__.return_value
        mock_runnable = mock_bash.__getitem__.return_value
        mock_runnable.run.return_value = (0, "some output", "")

        result = await run_shell_command(
            ctx, command="ls -l", read_only=True
        )

        assert result.success is True
        assert "some output" in result.output
        mock_local.__getitem__.assert_called_with("bash")
        mock_bash.__getitem__.assert_called_with(("-c", "ls -l"))
        mock_runnable.run.assert_called_once()


@pytest.mark.asyncio
async def test_run_shell_command_modifying_confirmed():
    """Test successful execution of a modifying command with confirmation."""
    ctx = RunContext(deps=None, model=MagicMock(), usage=RunUsage())

    with patch("src.main.local") as mock_local, \
         patch("builtins.input", return_value="y"):
        mock_bash = mock_local.__getitem__.return_value
        mock_runnable = mock_bash.__getitem__.return_value
        mock_runnable.run.return_value = (0, "file created", "")

        result = await run_shell_command(
            ctx, command="touch new_file", read_only=False
        )

        assert result.success is True
        assert "file created" in result.output


@pytest.mark.asyncio
async def test_run_shell_command_modifying_cancelled():
    """Test cancellation of a modifying command."""
    ctx = RunContext(deps=None, model=MagicMock(), usage=RunUsage())

    with patch("builtins.input", return_value="n"):
        result = await run_shell_command(
            ctx, command="rm -rf /", read_only=False
        )

        assert result.success is False
        assert "cancelled by user" in result.output


@pytest.mark.asyncio
async def test_run_shell_command_failure():
    """Test a command that fails with a non-zero exit code."""
    ctx = RunContext(deps=None, model=MagicMock(), usage=RunUsage())

    with patch("src.main.local") as mock_local:
        mock_bash = mock_local.__getitem__.return_value
        mock_runnable = mock_bash.__getitem__.return_value
        mock_runnable.run.return_value = (1, "", "error message")

        result = await run_shell_command(
            ctx, command="cat non_existent_file", read_only=True
        )

        assert result.success is False
        assert "error message" in result.output
        assert "Exit code: 1" in result.output


@pytest.mark.asyncio
async def test_run_shell_command_process_execution_error():
    """Test handling of ProcessExecutionError."""
    ctx = RunContext(deps=None, model=MagicMock(), usage=RunUsage())

    with patch("src.main.local") as mock_local:
        mock_bash = mock_local.__getitem__.return_value
        mock_runnable = mock_bash.__getitem__.return_value
        mock_exception = ProcessExecutionError(
            argv=["bash", "-c", "some_command"],
            retcode=127,
            stdout="some stdout",
            stderr="command not found"
        )
        mock_runnable.run.side_effect = mock_exception

        result = await run_shell_command(
            ctx, command="some_command", read_only=True
        )

        assert result.success is False
        assert "command not found" in result.output
        assert "some stdout" in result.output
        assert "Command failed with exit code 127" in result.output
