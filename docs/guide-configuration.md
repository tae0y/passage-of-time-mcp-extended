# Configure the Server

This page describes the available configuration options for the MCP server.

## Timezone Support

The server defaults to `Asia/Seoul` but supports all standard timezone names:

| Example | Zone |
|---------|------|
| `Asia/Seoul` | KST (default) |
| `UTC` | UTC |
| `US/Pacific` | PST/PDT |
| `Europe/London` | GMT/BST |
| `Asia/Tokyo` | JST |

Pass the `timezone` parameter to any tool to override the default.

## Timestamp Formats

All timestamps must use one of these formats:

| Format | Example |
|--------|---------|
| Full | `2024-01-15 14:30:45` |
| Date only | `2024-01-15` |

This strict formatting prevents ambiguity and ensures reliable calculations.
