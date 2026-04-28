FROM ghcr.io/astral-sh/uv:python3.11-bookworm

WORKDIR /app

# Copy only what we need to install dependencies first.
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY tests ./tests
COPY langgraph.json ./

# Explicit uv cache dir to keep build tool wheels inside the image.
ENV UV_CACHE_DIR=/app/.uv-cache

# Install project + deps into a dedicated venv.
# Build isolation is OK here because the build host has internet access.
RUN uv sync --frozen

# Pre-install build tools into the runtime venv so that any later
# offline build (e.g. triggered by langgraph serve) can find them.
# Must match the versions specified in pyproject.toml [build-system].requires
RUN uv pip install "setuptools>=73.0.0" wheel

# Disable PEP 517 build isolation: when uv needs to build a package it
# will reuse the setuptools/wheel already present in the active venv
# instead of trying to download them from PyPI.
ENV UV_NO_BUILD_ISOLATION=1

EXPOSE 2024

CMD ["uv", "run", "langgraph", "dev", "--config", "langgraph.json", "--host", "0.0.0.0", "--port", "2024", "--allow-blocking", "--no-browser"]
