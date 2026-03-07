FROM ghcr.io/astral-sh/uv:0.7-python3.12-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --frozen --no-install-project

COPY passage_of_time_mcp.py ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --frozen


FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    XDG_DATA_HOME="/app/.local/share"

RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --no-create-home appuser \
    && mkdir -p /app/.local/share \
    && chown -R appuser:appuser /app/.local

COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY patch_mcp_register.py ./
COPY --chown=appuser:appuser passage_of_time_mcp.py ./

# Patch MCP register handler to accept authorization_code-only grant_types (Claude.ai compat)
RUN python patch_mcp_register.py && rm patch_mcp_register.py

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/.well-known/oauth-authorization-server')" || exit 1

CMD ["python", "passage_of_time_mcp.py"]
