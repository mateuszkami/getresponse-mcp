# GetResponse MCP Server

An MCP (Model Context Protocol) server that connects [GetResponse](https://www.getresponse.com/) email marketing platform to AI assistants like Claude.

## Features

**Read Operations:**
- **Account Info** - Get account details and plan information
- **Campaigns** - List mailing lists with real subscriber counts
- **Contacts** - List, search, and get detailed contact information
- **Newsletters** - View newsletters with open/click rates
- **Autoresponders** - Monitor automated email sequences
- **Subscriber Stats** - Aggregated statistics across all campaigns

**Write Operations:**
- **Contacts** - Create, update, and delete contacts
- **Campaigns** - Create, update, and delete mailing lists
- **Tags** - List, create, assign, and remove tags from contacts
- **Custom Fields** - List and create custom fields

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

### Read

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

### Write

| Tool | Description |
|------|-------------|
| `create_contact` | Add a new contact to a campaign |
| `update_contact` | Update contact details or move to another list |
| `delete_contact` | Delete a contact permanently |
| `create_campaign` | Create a new mailing list |
| `update_campaign` | Update campaign settings |
| `delete_campaign` | Delete a mailing list permanently |
| `list_tags` | List all tags |
| `create_tag` | Create a new tag |
| `assign_tag_to_contact` | Assign a tag to a contact |
| `remove_tag_from_contact` | Remove a tag from a contact |
| `list_custom_fields` | List all custom fields |
| `create_custom_field` | Create a new custom field |

## Requirements

- Python 3.10+
- GetResponse account with API access

## License

MIT
