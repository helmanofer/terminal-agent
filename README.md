# Terminal Agent

An AI-powered terminal assistant that can execute shell commands and search the web to help you with various tasks.

## Features

- **AI-Powered Command Execution** - Uses AI to understand and execute shell commands
- **Web Search Integration** - Can search DuckDuckGo for information
- **Interactive Shell Tool** - Executes commands with user confirmation for safety
- **Google Gemini Integration** - Powered by Google's Gemini AI model

## Installation & Setup

1. Clone this repository:
```bash
git clone https://github.com/helmanofer/terminal-agent.git
cd terminal-agent
```

2. Run the setup script:
```bash
./setup.sh
```

This will automatically:
- Add the `q()` function to your shell configuration (.bashrc or .zshrc)
- Allow you to run the terminal agent from anywhere using `q <your query>`

3. Restart your terminal or run:
```bash
source ~/.bashrc  # or ~/.zshrc for zsh users
```

## Quick Start

### Using the `q` Command

After setup, you can use the terminal agent from anywhere:

```bash
# Ask questions
q "How do I list all files in a directory?"

# Get help with commands  
q "What's the difference between rm and rm -rf?"

# Ask for system information
q "Show me my disk usage"

# Search for information
q "What's the latest version of Python?"
```

### Manual Usage

You can also run it manually:

```bash
# From the project directory
uvx --from . my-terminal-agent "your query here"

# Or install locally first
pip install -e .
my-terminal-agent "your query here"
```

## Configuration

### Environment Variables

You need to set your Google Gemini API key:

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

Or create a `.env` file in the project directory:

```
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_NAME=gemini-1.5-flash  # Optional, defaults to gemini-1.5-flash
```

### How It Works

1. **Query Processing** - The AI agent analyzes your natural language query
2. **Tool Selection** - Chooses between shell commands or web search based on your request
3. **Safety Confirmation** - For non-read-only commands, asks for confirmation before execution
4. **Result Display** - Shows the output and provides a final answer

## Requirements

- Python 3.12+
- Google Gemini API key
- Required packages:
  - `pydantic-ai`
  - `google-generativeai`
  - `plumbum`
  - `ddgs`
  - `rich`

## Safety Features

- **Command Confirmation** - Non-read-only commands require user confirmation
- **Read-only Auto-execution** - Safe commands like `ls`, `cat`, `grep` run automatically
- **Error Handling** - Graceful handling of command failures and exceptions

## Troubleshooting

### API Key Issues

If you get authentication errors:

1. Ensure your `GEMINI_API_KEY` is set correctly
2. Verify your API key is active and has quota remaining
3. Check that you're using a valid Gemini model name

### Command Not Found

If `q` command is not found after setup:

1. Restart your terminal
2. Or run: `source ~/.bashrc` (or `~/.zshrc` for zsh)
3. Verify the function was added to your shell config

### Permission Errors

If you get permission errors:

1. Make sure the setup script is executable: `chmod +x setup.sh`
2. Check file permissions in the project directory

## Examples

```bash
# File operations
q "Show me all Python files in this directory"
q "What's in my home directory?"
q "Find files larger than 100MB"

# System information  
q "How much disk space do I have?"
q "Show running processes"
q "What's my IP address?"

# Web search
q "What's the latest version of Node.js?"
q "How to install Docker on Ubuntu?"
```

## File Structure

```
├── src/
│   ├── main.py           # Main application entry point
│   └── settings.py       # Configuration settings
├── setup.sh              # Shell setup script
├── pyproject.toml        # Project configuration
└── README.md            # This file
```

## License

MIT License - see LICENSE file for details.