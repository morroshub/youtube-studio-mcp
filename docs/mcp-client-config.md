# MCP Client Configuration

Use this server with any MCP client that supports stdio servers.

## Generic MCP config

From the repository root:

```json
{
  "mcpServers": {
    "youtube-studio": {
      "command": "python3",
      "args": ["./scripts/server.py"],
      "cwd": "/absolute/path/to/youtube-studio-mcp",
      "env": {
        "YOUTUBE_CLIENT_SECRETS": "./secrets/client_secret.json",
        "YOUTUBE_TOKEN_FILE": "./secrets/token.json"
      }
    }
  }
}
```

Replace `/absolute/path/to/youtube-studio-mcp` with the folder where you cloned this repo.

## Codex plugin config

The repository includes:

- `.codex-plugin/plugin.json`
- `.mcp.json`

Clone the repo into your Codex plugins folder, add your local credentials under `secrets/`, authenticate, and restart Codex.
