"""End-to-end tests for MCP streamable-http transport.

Tests the full MCP session lifecycle (initialize → initialized → tools/call)
against a live server. Requires the server to be running at the target URL.

Usage:
    # Against local server
    uv run pytest tests/test_e2e_streamable_http.py -v

    # Against remote server
    MCP_SERVER_URL=https://passage-of-time-mcp.tae0y.net/mcp uv run pytest tests/test_e2e_streamable_http.py -v
"""

import os
import json
import pytest
import httpx

MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8000/mcp")

TOOL_ARGS = {
    "current_datetime": {"timezone": "Asia/Seoul"},
    "time_difference": {
        "timestamp1": "2026-03-01 00:00:00",
        "timestamp2": "2026-03-07 00:00:00",
    },
    "time_since": {"timestamp": "2026-03-01 00:00:00"},
    "parse_timestamp": {"timestamp": "2026-04-01 09:00:00"},
    "add_time": {
        "timestamp": "2026-03-07 00:00:00",
        "duration": 25,
        "unit": "days",
    },
    "timestamp_context": {"timestamp": "2026-04-01 09:00:00"},
    "format_duration": {"seconds": 2160000},
}


class MCPSession:
    """Minimal MCP streamable-http client for testing."""

    def __init__(self, url: str, accept: str = "application/json, text/event-stream"):
        self.url = url
        self.accept = accept
        self.session_id = None
        self.client = httpx.Client(timeout=15)
        self._next_id = 1

    def _headers(self):
        h = {
            "Content-Type": "application/json",
            "Accept": self.accept,
        }
        if self.session_id:
            h["mcp-session-id"] = self.session_id
        return h

    def _next_request_id(self):
        rid = self._next_id
        self._next_id += 1
        return rid

    @staticmethod
    def _parse_sse_response(text: str):
        """Extract JSON-RPC result from SSE event stream."""
        for line in text.strip().splitlines():
            if line.startswith("data: "):
                return json.loads(line[6:])
        return json.loads(text)

    def initialize(self):
        resp = self.client.post(
            self.url,
            headers=self._headers(),
            json={
                "jsonrpc": "2.0",
                "id": self._next_request_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "e2e-test", "version": "1.0"},
                },
            },
        )
        assert resp.status_code == 200, f"initialize failed: {resp.status_code} {resp.text}"
        self.session_id = resp.headers.get("mcp-session-id")
        assert self.session_id, "No mcp-session-id in response"
        return self._parse_sse_response(resp.text)

    def send_initialized(self):
        resp = self.client.post(
            self.url,
            headers=self._headers(),
            json={
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
            },
        )
        assert resp.status_code == 202, f"initialized notification failed: {resp.status_code}"

    def call_tool(self, name: str, arguments: dict):
        resp = self.client.post(
            self.url,
            headers=self._headers(),
            json={
                "jsonrpc": "2.0",
                "id": self._next_request_id(),
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            },
        )
        assert resp.status_code == 200, f"tools/call {name} failed: {resp.status_code} {resp.text}"
        return self._parse_sse_response(resp.text)

    def close(self):
        if self.session_id:
            self.client.delete(self.url, headers=self._headers())
        self.client.close()


@pytest.fixture
def mcp_session():
    """Create an initialized MCP session."""
    session = MCPSession(MCP_SERVER_URL)
    session.initialize()
    session.send_initialized()
    yield session
    session.close()


@pytest.fixture
def mcp_session_wildcard_accept():
    """Create an MCP session using Accept: */* (simulates Claude.ai behavior)."""
    session = MCPSession(MCP_SERVER_URL, accept="*/*")
    session.initialize()
    session.send_initialized()
    yield session
    session.close()


def _is_server_running():
    try:
        httpx.get(MCP_SERVER_URL.replace("/mcp", "/"), timeout=3)
        return True
    except Exception:
        return False


requires_server = pytest.mark.skipif(
    not _is_server_running(),
    reason=f"MCP server not running at {MCP_SERVER_URL}",
)


@requires_server
class TestMCPSessionLifecycle:
    def test_initialize(self):
        session = MCPSession(MCP_SERVER_URL)
        result = session.initialize()
        assert result["result"]["serverInfo"]["name"] == "Perception of Passage of Time"
        assert result["result"]["protocolVersion"] == "2024-11-05"
        session.close()

    def test_initialize_wildcard_accept(self):
        """Claude.ai sends Accept: */* — verify the middleware rewrites it."""
        session = MCPSession(MCP_SERVER_URL, accept="*/*")
        result = session.initialize()
        assert result["result"]["serverInfo"]["name"] == "Perception of Passage of Time"
        session.close()


@requires_server
class TestToolCalls:
    @pytest.mark.parametrize("tool_name", TOOL_ARGS.keys())
    def test_tool_call(self, mcp_session, tool_name):
        result = mcp_session.call_tool(tool_name, TOOL_ARGS[tool_name])
        assert "result" in result
        assert result["result"]["isError"] is False
        content = result["result"]["content"]
        assert len(content) > 0
        assert content[0]["type"] == "text"
        assert len(content[0]["text"]) > 0

    @pytest.mark.parametrize("tool_name", TOOL_ARGS.keys())
    def test_tool_call_wildcard_accept(self, mcp_session_wildcard_accept, tool_name):
        """Verify all tools work with Accept: */* (Claude.ai compat)."""
        result = mcp_session_wildcard_accept.call_tool(
            tool_name, TOOL_ARGS[tool_name]
        )
        assert "result" in result
        assert result["result"]["isError"] is False


@requires_server
class TestTimestampContextNullSafety:
    def test_relative_day_never_null(self, mcp_session):
        """relative_day must never be None — was causing output validation errors."""
        result = mcp_session.call_tool(
            "timestamp_context",
            {"timestamp": "2020-01-01 12:00:00"},
        )
        content = json.loads(result["result"]["content"][0]["text"])
        assert content["relative_day"] is not None
        assert isinstance(content["relative_day"], str)
