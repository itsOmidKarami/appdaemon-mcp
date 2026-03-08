# AppDaemon MCP - Developer Guide

Welcome to the AppDaemon MCP project! This guide explains how to set up your local development environment, run tests, and contribute.

## Prerequisites

- **Python 3.12+** (We strongly suggest 3.12 due to a documented `dataclasses` compatibility issue with Python 3.14).
- **[uv](https://docs.astral.sh/uv/)**: We use `uv` for lightning-fast dependency management and environment isolation.

## 1. Setting Up the Virtual Environment

We use a standard virtual environment managed by `uv`.

1. Clone the repository (if you haven't already and are working in the `appdaemon-mcp` submodule).
2. Install dependencies:

```bash
cd appdaemon-mcp
uv sync
```

This will automatically create a `.venv` folder, resolve the lockfile, and install all dependencies (including dev constraints like `pytest`, `ruff`, and `mypy`).

## 2. Setting Up Pre-commit Hooks

To maintain code quality, we use `pre-commit` to run formatting (`ruff-format`), linting (`ruff`), and static type checking (`mypy`) before every commit.

Install the git hooks:

```bash
uv run pre-commit install
```

You can optionally run it manually across all files:

```bash
uv run pre-commit run --all-files
```

## 3. Running the Server Locally

To start the MCP server in development mode, you can use the `mcp dev` command (provided by the `@modelcontextprotocol/sdk`).

```bash
# Set your AppDaemon URL and run the inspector
AD_URL=https://appdaemon.my-home-lab.link uv run mcp dev src/appdaemon_mcp/server.py
```

This launches the standard MCP GUI Inspector at `http://localhost:5173`.

## 4. Running Tests

We use `pytest` with `pytest-asyncio` for our testing framework. We mock external HTTP calls to the AppDaemon API using `aioresponses`.

Run the test suite:

```bash
uv run pytest
```

To run with coverage reporting:

```bash
uv run pytest --cov=src/appdaemon_mcp
```

## 5. Submitting Changes (Conventional Commits)

We enforce **Conventional Commits** to automate Semantic Versioning and changelog generation.

When making a commit, follow this format:

- `feat: added a new tool for x`
- `fix: resolved crashing issue on y`
- `docs: updated readme`
- `chore: bumped dependencies`

You can use the `commitizen` CLI (installed via dev dependencies) to guide you through this interactively:

```bash
uv run cz commit
```

If your commit does not match the conventional format, the `pre-commit` hook (`commitizen` stage) will block it and ask you to reformat.
