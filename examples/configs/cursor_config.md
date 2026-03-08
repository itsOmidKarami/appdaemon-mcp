# Cursor / VS Code Configuration

To use the AppDaemon MCP server in Cursor or VS Code, follow these steps:

## 1. Open MCP Settings
In Cursor, go to **Settings** -> **Cursor Settings** -> **General** -> **MCP**.

## 2. Add New Server
Click on **+ Add Server**.

## 3. Enter Configuration
- **Name**: `AppDaemon`
- **Type**: `command`
- **Command**: `uvx appdaemon-mcp`

## 4. Set Environment Variables
You may need to set these in your system environment or using a tool that can provide them to Cursor. Alternatively, if Cursor supports direct env input for MCP:

- `AD_URL`: `http://192.168.1.20:5050`
- `AD_API_KEY`: `your_api_password`

## Alternative: Local Development
If you want to run the server from source:
- **Command**: `uv run --directory /path/to/appdaemon-mcp appdaemon-mcp`
