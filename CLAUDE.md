# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

An MCP (Model Context Protocol) server that gives LLMs temporal awareness — current time, time differences, duration formatting, and human-context annotations (business hours, weekday/weekend, typical activities). Built with FastMCP and deployed via Docker + Cloudflare Tunnel.

Single-file server: all tools live in `passage_of_time_mcp.py`. There is no package structure.

**Infrastructure:** Source code lives on a Windows home server. Development is done from a Mac client via SSH. Git for version control, Docker Desktop on the home server for serving.

## Common Commands

```bash
# Install dependencies (uv is the primary package manager)
uv sync

# Run the server locally (port 8000, streamable-http transport)
uv run python passage_of_time_mcp.py

# Run tests
uv run pytest tests/ -v

# Run a single test class or method
uv run pytest tests/test_passage_of_time_mcp.py::TestTimeDifference -v
uv run pytest tests/test_passage_of_time_mcp.py::TestTimeDifference::test_simple_difference -v

# Docker build & run (from repo root)
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml up
```

Legacy `pipenv` commands (`pipenv run server`, `pipenv run test`) also work but `uv` is preferred.

## Architecture

**Server entry point:** `passage_of_time_mcp.py`
- Creates a `FastMCP` instance with optional GitHub OAuth (via env vars `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `MCP_BASE_URL`)
- Registers 7 MCP tools: `current_datetime`, `time_difference`, `time_since`, `parse_timestamp`, `add_time`, `timestamp_context`, `format_duration`
- `__main__` block builds a Starlette app with streamable-http transport, adds OAuth well-known endpoints and debug logging middleware, then runs via uvicorn on port 8000

**Timestamp contract:** All tools accept timestamps in `YYYY-MM-DD HH:MM:SS` or `YYYY-MM-DD` format only. The shared `parse_standard_timestamp()` function enforces this. Default timezone is `America/New_York`.

**Docker deployment:** `docker/Dockerfile` uses a multi-stage uv build. `docker/docker-compose.yml` pairs the MCP service with a Cloudflare Tunnel sidecar. The build runs `patch_mcp_register.py` at image build time to patch upstream MCP/FastMCP libraries for Claude.ai OAuth compatibility (scope filtering, grant_type relaxation).

**Tests:** `tests/test_passage_of_time_mcp.py` mocks `FastMCP` at import time to test tool functions directly. Uses `unittest.mock.patch` on `passage_of_time_mcp.datetime` for time-dependent tests.

## Environment Variables

| Variable | Purpose |
|---|---|
| `GITHUB_CLIENT_ID` | GitHub OAuth app client ID (optional, enables auth) |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth app client secret |
| `MCP_BASE_URL` | Public base URL for OAuth endpoints |
| `PORT` | Server port (default: 8000) |
| `CLOUDFLARE_TUNNEL_TOKEN` | Cloudflare Tunnel token (docker-compose only) |

## Key Constraints

- Python 3.12+ required
- `patch_mcp_register.py` is a build-time-only file that monkey-patches upstream MCP libs inside the Docker image. It is tightly coupled to specific upstream code — changes to `mcp` or `fastmcp` versions may break it.
- The test file mocks `sys.modules['fastmcp']` before importing the server module. New test files must follow the same pattern or the `FastMCP` constructor will fail.

---

### Rule Hierarchy

When rules from different files apply to the same response, use this priority order:

- Non-code responses: `thinking-guidelines` > `CLAUDE.md`
- Code tasks: `coding-guidelines` > `CLAUDE.md`
- When rules conflict: prefer thinking (surface trade-offs, ask) over acting (proceed and fix later)
