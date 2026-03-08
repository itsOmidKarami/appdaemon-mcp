# AppDaemon MCP Server

An [MCP](https://modelcontextprotocol.io/) server that wraps the [AppDaemon](https://appdaemon.readthedocs.io/) REST API, letting AI assistants (Claude, Cursor, etc.) observe and manage AppDaemon home-automation apps.

```
AI Client ──MCP protocol──▶ appdaemon-mcp ──REST API──▶ AppDaemon
```

---

## Requirements

- Python 3.10+
- [`uv`](https://github.com/astral-sh/uv) (recommended) or `pip`
- A running AppDaemon instance with the HTTP component enabled

---

## Installation

```bash
# Clone / enter the project
cd appdaemon-mcp

# Install with uv (creates a virtual env automatically)
uv sync
```

---

## Configuration

All configuration is done via environment variables:

| Variable        | Required | Default | Description                                                |
| --------------- | -------- | ------- | ---------------------------------------------------------- |
| `AD_URL`        | **Yes**  | —       | AppDaemon base URL, e.g. `http://192.168.1.20:5050`        |
| `AD_API_KEY`    | No       | —       | API password (if `api_password` is set in AD config)       |
| `AD_APPS_DIR`   | No       | —       | Path to AppDaemon `apps/` directory (enables dev tools)    |
| `AD_CONFIG_DIR` | No       | —       | Path to AD config directory (enables config resources)     |
| `AD_VERIFY_SSL` | No       | `true`  | Set to `false` to skip SSL verification                    |
| `MCP_TRANSPORT` | No       | `stdio` | `stdio` for IDE integrations, `streamable-http` for remote |

---

## Running

### stdio (Claude Desktop / Cursor)

```bash
AD_URL=http://192.168.1.20:5050 AD_API_KEY=secret uv run appdaemon-mcp
```

### Development / MCP Inspector

```bash
AD_URL=http://192.168.1.20:5050 uv run mcp dev src/appdaemon_mcp/server.py
# Then open http://localhost:5173
```

---

## Claude Desktop configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "appdaemon": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/appdaemon-mcp", "appdaemon-mcp"],
      "env": {
        "AD_URL": "http://192.168.1.20:5050",
        "AD_API_KEY": "your-secret"
      }
    }
  }
}
```

---

## Available Tools

| Tool            | Description                                         |
| --------------- | --------------------------------------------------- |
| `ad_get_info`   | AppDaemon version, timezone, and runtime info       |
| `ad_list_apps`  | All apps with status (running / stopped / disabled) |
| `ad_get_state`  | Entity state across an entire namespace             |
| `ad_get_entity` | State of a single entity                            |
| `ad_get_logs`   | Recent AppDaemon log entries                        |

More tools will be added (app management, service calls, dev tools).

---

## Development

```bash
# Run tests
uv run pytest

# Lint
uv run ruff check src/ tests/

# Syntax check
python -m py_compile src/appdaemon_mcp/server.py src/appdaemon_mcp/client.py
```

---

## Architecture

See [`implementation_plan.md`](./implementation_plan.md) for the full design document.
