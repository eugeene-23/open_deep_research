FROM ghcr.io/astral-sh/uv:python3.11-bookworm

WORKDIR /app

# Copy only what we need to install dependencies first.
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY tests ./tests
COPY langgraph.json langgraph.local.json ./

# Install project + deps into a dedicated venv.
RUN uv sync --frozen

EXPOSE 2024

CMD ["uv", "run", "langgraph", "dev", "--config", "langgraph.local.json", "--host", "0.0.0.0", "--port", "2024", "--allow-blocking", "--no-browser"]
