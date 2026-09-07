import importlib.util
import io
import json
import sys
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("youtube_server", ROOT / "scripts" / "server.py")
server = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = server
assert SPEC.loader is not None
SPEC.loader.exec_module(server)


def test_oauth_scopes_are_read_only():
    assert server.SCOPES == [
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/yt-analytics.readonly",
    ]


def test_mcp_exposes_only_read_operations(monkeypatch, tmp_path):
    monkeypatch.setenv("YOUTUBE_CLIENT_SECRETS", str(tmp_path / "client_secret.json"))
    monkeypatch.setenv("YOUTUBE_TOKEN_FILE", str(tmp_path / "token.json"))

    names = {tool["name"] for tool in server.McpServer().tools}

    assert names == {
        "youtube_auth_status",
        "youtube_start_auth",
        "youtube_channel_overview",
        "youtube_list_videos",
        "youtube_get_video",
        "youtube_channel_analytics",
        "youtube_video_analytics",
        "youtube_list_comments",
    }
    assert not any(word in name for name in names for word in ("update", "upload", "post", "delete"))


def test_start_auth_does_not_return_an_unusable_authorization_url(monkeypatch, tmp_path):
    client_file = tmp_path / "client_secret.json"
    client_file.write_text(
        '{"installed":{"client_id":"test-client","client_secret":"test-secret"}}',
        encoding="utf-8",
    )
    monkeypatch.setenv("YOUTUBE_CLIENT_SECRETS", str(client_file))
    monkeypatch.setenv("YOUTUBE_TOKEN_FILE", str(tmp_path / "token.json"))

    payload = server.McpServer()._start_auth_payload()

    assert "authorization_url" not in payload


def test_hidden_write_tool_cannot_be_called(monkeypatch, tmp_path):
    monkeypatch.setenv("YOUTUBE_CLIENT_SECRETS", str(tmp_path / "client_secret.json"))
    monkeypatch.setenv("YOUTUBE_TOKEN_FILE", str(tmp_path / "token.json"))
    mcp = server.McpServer()

    try:
        mcp._call_tool("youtube_update_video", {"video_id": "abc"})
    except RuntimeError as exc:
        assert "disabled in read-only mode" in str(exc)
    else:
        raise AssertionError("write tool was callable")


def test_mcp_accepts_json_lines_framing(monkeypatch):
    message = {"jsonrpc": "2.0", "id": 1, "method": "ping"}
    monkeypatch.setattr(
        server.sys,
        "stdin",
        SimpleNamespace(buffer=io.BytesIO((json.dumps(message) + "\n").encode())),
    )
    mcp = object.__new__(server.McpServer)

    assert mcp._read_message() == message
    assert mcp._json_lines is True


def test_mcp_replies_with_json_lines_when_client_uses_it(monkeypatch):
    output = io.BytesIO()
    monkeypatch.setattr(server.sys, "stdout", SimpleNamespace(buffer=output))
    mcp = object.__new__(server.McpServer)
    mcp._json_lines = True

    mcp._write_message({"jsonrpc": "2.0", "id": 1, "result": {}})

    assert json.loads(output.getvalue().decode()) == {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {},
    }
