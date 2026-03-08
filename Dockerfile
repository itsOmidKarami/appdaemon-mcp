# Use an official Python base image
FROM python:3.12-slim

# Install uv for dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (without the package itself)
RUN uv sync --no-dev --no-install-project

# Copy source code
COPY src/ src/
COPY README.md ./

# Install the project
RUN uv sync --no-dev

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV MCP_TRANSPORT=stdio

# Use the appdaemon-mcp command provided in pyproject.toml
ENTRYPOINT ["appdaemon-mcp"]
