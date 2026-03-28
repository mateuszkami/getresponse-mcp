# GetResponse MCP Server

An MCP (Model Context Protocol) server that connects [GetResponse](https://www.getresponse.com/) email marketing platform to AI assistants like Claude.

## Features

- **Account Info** - Get account details and plan information
- **Campaigns** - List mailing lists with real subscriber counts
- **Contacts** - List, search, and get detailed contact information
- **Newsletters** - View newsletters with open/click rates
- **Autoresponders** - Monitor automated email sequences
- **Subscriber Stats** - Aggregated statistics across all campaigns

## Quick Start

### Install

```bash
pip install getresponse-mcp
```

### Configure

Add to your Claude Code MCP config (`.mcp.json`):

```json
{
  "mcpServers": {
    "getresponse": {
      "type": "stdio",
      "command": "getresponse-mcp",
      "env": {
        "GETRESPONSE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Get your API key from [GetResponse API settings](https://app.getresponse.com/api).

### Run directly

```bash
GETRESPONSE_API_KEY=your-key getresponse-mcp
```

## Available Tools

| Tool | Description |
|------|-------------|
| `get_account_info` | Account details (name, email, plan) |
| `list_campaigns` | All mailing lists with subscriber counts |
| `list_contacts` | Contacts with optional campaign/email filter |
| `get_contact` | Detailed info for a specific contact |
| `list_newsletters` | Newsletters with delivery stats |
| `get_newsletter_stats` | Detailed stats for a specific newsletter |
| `list_autoresponders` | Automated email sequences |
| `search_contacts` | Search by email, name, or date |
| `get_subscriber_stats` | Aggregated subscriber breakdown |

## Requirements

- Python 3.10+
- GetResponse account with API access

## License

MIT
