# MCP Chat with Amazon Bedrock

This guide explains how to run MCP Chat using Claude models through Amazon Bedrock. No Anthropic API key is required. Requests are authenticated with your AWS credentials.

## Prerequisites

- Python 3.10+
- AWS account with access to Claude models enabled in Amazon Bedrock
- AWS credentials configured locally (AWS CLI profile, SSO, or environment variables)

## Setup

### Step 1: Set the configuration values

The settings are documented here and are not read from `.env`. Set them in the same terminal session before running the app.

PowerShell (Windows):

```powershell
$env:CLAUDE_MODEL = "au.anthropic.claude-haiku-4-5-20251001-v1:0"  # Bedrock model ID (inference profile)
$env:AWS_PROFILE = "NP-DP-SysAccounts-AllPlatforms"  # AWS CLI profile with Bedrock access
$env:AWS_REGION = "ap-southeast-2"  # Region where the Bedrock model is enabled
```

bash (macOS/Linux):

```bash
export CLAUDE_MODEL="au.anthropic.claude-haiku-4-5-20251001-v1:0"
export AWS_PROFILE="NP-DP-SysAccounts-AllPlatforms"
export AWS_REGION="ap-southeast-2"
```

If you use AWS SSO, sign in before running the app:

```bash
aws sso login --profile NP-DP-SysAccounts-AllPlatforms
```

### Step 2: Install dependencies

#### Option 1: Setup with uv (Recommended)

1. Install uv, if not already installed:

```bash
pip install uv
```

2. Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
uv sync
```

4. Run the project

```bash
uv run main.py
```

#### Option 2: Setup without uv

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install "anthropic[bedrock]" python-dotenv prompt-toolkit "mcp[cli]==1.8.0"
```

3. Run the project

```bash
python main.py
```

## How it works

- `core/claude.py` creates a `bedrock-runtime` client with boto3 and calls the Bedrock Converse API. `temperature` and `maxTokens` are sent in `inferenceConfig`.
- The client reads AWS credentials from `AWS_PROFILE` or the default AWS credential chain.
- `CLAUDE_MODEL` must be a Bedrock model ID, not an Anthropic model name.

## Troubleshooting

- **Credentials error or expired token:** run `aws sso login --profile <name>` again, or check that `AWS_PROFILE` matches a profile in `~/.aws/config`.
- **`AccessDeniedException` or model not found:** confirm the model is enabled in the Bedrock console for `AWS_REGION`, and that `CLAUDE_MODEL` is the exact model ID or inference profile ID.
- **`boto3` not found:** reinstall dependencies so the `anthropic[bedrock]` extra is installed.
