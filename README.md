# PromptLane SDK

Official Python SDK for PromptLane, a modern prompt engineering and management platform.

## Installation

```bash
pip install promptlane-sdk
```

## Features

- Multi-connection support:
  - Direct database access
  - API-based connectivity
  - Mixed mode (read from DB, write via API)
- Comprehensive access to PromptLane resources:
  - Projects
  - Prompts
  - Teams
  - Users
  - Activities

## Quick Start

```python
from promptlane_sdk import PromptLaneClient

# Using API connection (recommended)
client = PromptLaneClient(
    connection_type="api",
    base_url="https://api.example.com",
    api_key="your_api_key"
)

# Direct database connection (for advanced users)
client = PromptLaneClient(
    connection_type="database",
    db_connection_string="postgresql://user:password@localhost:5432/promptlane"
)

# Mixed mode (read from DB, write via API)
client = PromptLaneClient(
    connection_type="mixed",
    base_url="https://api.example.com",
    api_key="your_api_key",
    db_connection_string="postgresql://user:password@localhost:5432/promptlane"
)

# Get all projects
projects = client.projects.list()

# Get a specific prompt
prompt = client.prompts.get("prompt-key")

# Create a new prompt
new_prompt = client.prompts.create(
    name="My New Prompt",
    key="my-new-prompt",
    system_prompt="You are a helpful assistant.",
    user_prompt="Answer the following: {{query}}",
    project_id="project-id-here"
)
```

## Connection Types

### API Connection

The recommended approach for most users. All operations are performed via HTTP requests to the PromptLane API.

### Direct Database Connection

For advanced use cases where you need direct database access, such as:
- Deployment within the same infrastructure as PromptLane
- Bulk operations requiring higher performance
- Read-only analytical queries

### Mixed Mode

Combines the best of both worlds:
- Read operations use direct database access for better performance
- Write operations go through the API to ensure data validation and business logic

## Documentation

For complete documentation, visit [docs.promptlane.ai](https://docs.promptlane.ai).

## License

MIT 