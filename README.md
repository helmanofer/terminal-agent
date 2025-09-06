# GitHub Copilot Authentication Client

A Python client for authenticating with GitHub Copilot using OAuth device flow, based on SST OpenCode authentication patterns.

## Features

- **OAuth Device Flow Authentication** - User-friendly authentication without requiring manual token creation
- **Secure Token Storage** - Uses system keyring and file fallback for token persistence
- **Automatic Token Refresh** - Handles token expiration and refresh automatically
- **Multiple Model Support** - Access to GPT-4, Claude, and other models through Copilot
- **SST OpenCode Compatible** - Follows the same authentication patterns as SST OpenCode

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd terminal-assistant
```

2. Install dependencies:
```bash
uv sync
# or with pip:
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from src.github_copilot_client import GitHubCopilotClient

# Create client
client = GitHubCopilotClient()

# Authenticate (will prompt for device code if needed)
if client.authenticate():
    print("Authentication successful!")
    
    # Send a chat completion request
    messages = [
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Write a Python function to calculate factorial."}
    ]
    
    response = client.chat_completion(messages, model="gpt-4")
    print(response)
else:
    print("Authentication failed")
```

### Run the Example

```bash
# Using virtual environment
.venv/bin/python example.py

# Or activate venv first
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
python example.py
```

## Authentication Flow

The client uses GitHub's OAuth device flow for authentication:

1. **Device Code Request** - Client requests a device code from GitHub
2. **User Authorization** - User visits GitHub and enters the device code
3. **Token Exchange** - Client polls for and receives the access token
4. **Copilot Token** - GitHub token is exchanged for a Copilot API token
5. **Secure Storage** - Tokens are stored securely using system keyring

### First Time Setup

When you run the client for the first time:

1. The client will display a URL and device code
2. Visit the URL in your browser
3. Enter the device code when prompted
4. Authorize the application
5. The client will automatically receive and store the tokens

## API Usage

### Chat Completion

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain Python decorators."}
]

response = client.chat_completion(
    messages=messages,
    model="gpt-4",
    temperature=0.7,
    max_tokens=500
)
```

### List Available Models

```python
models = client.list_models()
for model in models:
    print(f"Model: {model['id']}")
```

### Check Authentication Status

```python
if client.is_authenticated():
    print("Ready to use Copilot API")
else:
    print("Authentication required")
```

### Logout

```python
client.logout()  # Clears all stored tokens
```

## Configuration

### Token Storage

Tokens are stored securely using:

1. **System Keyring** (preferred) - Uses OS-native secure storage
2. **File Fallback** - `~/.local/share/opencode/auth.json`

### Environment Variables

You can also set tokens via environment variables:

```bash
export GITHUB_TOKEN="your_github_token"
```

## Requirements

- Python 3.12+
- Active GitHub Copilot subscription
- Required packages:
  - `requests>=2.31.0`
  - `keyring>=24.0.0`
  - `python-dotenv>=1.0.0`

## Security Considerations

⚠️ **Important Security Notes:**

- This implementation uses **unofficial, reverse-engineered** GitHub Copilot APIs
- GitHub doesn't provide an official public API for Copilot
- This may violate GitHub's Terms of Service
- APIs can change without notice, potentially breaking the implementation
- Use at your own risk and consider official alternatives for production

### Official Alternatives

For production use, consider:

- **GitHub Models** (when available)
- **Direct OpenAI API**
- **Azure OpenAI Service**

## Troubleshooting

### Authentication Issues

If authentication fails:

1. Ensure you have an active GitHub Copilot subscription
2. Check that Copilot is enabled in your GitHub settings
3. Try logging out and re-authenticating: `client.logout()` then `client.authenticate(force_refresh=True)`

### Import Errors

If you get import errors:

1. Ensure you're using the virtual environment: `.venv/bin/python`
2. Check that dependencies are installed: `uv sync`
3. Verify you're importing from the correct path

### Token Expiration

Tokens are automatically refreshed, but if you experience issues:

```python
# Force re-authentication
client.authenticate(force_refresh=True)
```

## Development

### Testing

Run the test script to verify everything works:

```bash
.venv/bin/python test_copilot.py
```

### File Structure

```
src/
├── __init__.py                    # Package initialization
├── github_copilot_auth_device.py  # OAuth device flow implementation
├── github_copilot_client.py       # Main client with token management
└── github_copilot_auth.py         # CLI entry point

example.py                         # Usage example
test_copilot.py                   # Test script
pyproject.toml                    # Project configuration
```

## Contributing

This implementation is based on reverse engineering and may need updates as GitHub's APIs change. Contributions are welcome!

## License

MIT License - see LICENSE file for details.

## Disclaimer

This project is not affiliated with GitHub or Microsoft. Use at your own risk and ensure compliance with GitHub's Terms of Service.