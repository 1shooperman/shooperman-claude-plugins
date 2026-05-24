import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "publish" / "scripts"))
from publish_markdown_to_slack import (
    _parse_dotenv,
    convert_inline,
    load_slack_token,
    main,
    markdown_to_slack,
    resolve_channel_id,
)


# --- convert_inline ---

def test_convert_inline_link():
    assert convert_inline("[Claude](https://claude.ai)") == "<https://claude.ai|Claude>"


def test_convert_inline_bold_double_star():
    assert convert_inline("**hello**") == "*hello*"


def test_convert_inline_bold_double_underscore():
    assert convert_inline("__hello__") == "*hello*"


def test_convert_inline_italic():
    assert convert_inline("*hello*") == "_hello_"


def test_convert_inline_strikethrough():
    assert convert_inline("~~gone~~") == "~gone~"


def test_convert_inline_no_change():
    assert convert_inline("plain text") == "plain text"


# --- markdown_to_slack ---

def test_heading_h1():
    assert markdown_to_slack("# Title") == "*Title*"


def test_heading_h2():
    assert markdown_to_slack("## Sub") == "*Sub*"


def test_heading_h6():
    assert markdown_to_slack("###### Deep") == "*Deep*"


def test_bullet_dash():
    assert markdown_to_slack("- item") == "• item"


def test_bullet_star():
    assert markdown_to_slack("* item") == "• item"


def test_ordered_list():
    assert markdown_to_slack("1. item") == "• item"


def test_task_list_unchecked():
    assert markdown_to_slack("- [ ] todo") == "• [ ] todo"


def test_task_list_checked():
    assert markdown_to_slack("- [x] done") == "• [x] done"


def test_blockquote():
    assert markdown_to_slack("> note") == "> note"


def test_code_fence_preserved():
    md = "```\ncode here\n```"
    result = markdown_to_slack(md)
    assert "```" in result
    assert "code here" in result


def test_inline_code_unchanged():
    assert markdown_to_slack("`snippet`") == "`snippet`"


def test_link_in_body():
    result = markdown_to_slack("[Docs](https://docs.example.com)")
    assert "<https://docs.example.com|Docs>" in result


def test_collapses_excess_blank_lines():
    md = "line1\n\n\n\nline2"
    result = markdown_to_slack(md)
    assert "\n\n\n" not in result


def test_multiline_document():
    md = "# Hello\n\nSome *italic* and **bold**.\n\n- a\n- b"
    result = markdown_to_slack(md)
    assert "*Hello*" in result
    assert "_italic_" in result
    assert "*bold*" in result
    assert "• a" in result
    assert "• b" in result


# --- _parse_dotenv ---

def test_parse_dotenv_basic():
    assert _parse_dotenv("KEY=value") == {"KEY": "value"}


def test_parse_dotenv_quoted_double():
    assert _parse_dotenv('KEY="value"') == {"KEY": "value"}


def test_parse_dotenv_quoted_single():
    assert _parse_dotenv("KEY='value'") == {"KEY": "value"}


def test_parse_dotenv_export_prefix():
    assert _parse_dotenv("export KEY=value") == {"KEY": "value"}


def test_parse_dotenv_ignores_comments():
    content = "# comment\nKEY=val"
    assert _parse_dotenv(content) == {"KEY": "val"}


def test_parse_dotenv_ignores_blank_lines():
    content = "\n\nKEY=val\n\n"
    assert _parse_dotenv(content) == {"KEY": "val"}


def test_parse_dotenv_multiple_keys():
    content = "A=1\nB=2"
    assert _parse_dotenv(content) == {"A": "1", "B": "2"}


def test_parse_dotenv_empty():
    assert _parse_dotenv("") == {}


# --- load_slack_token ---

def test_load_token_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-from-env")
    assert load_slack_token(tmp_path / "file.md", None) == "xoxb-from-env"


def test_load_token_from_dotenv(monkeypatch, tmp_path):
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    (tmp_path / ".env").write_text("SLACK_BOT_TOKEN=xoxb-dotenv\n")
    monkeypatch.chdir(tmp_path)
    result = load_slack_token(tmp_path / "file.md", None)
    assert result == "xoxb-dotenv"


def test_load_token_from_explicit_env_file(monkeypatch, tmp_path):
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    env_file = tmp_path / "custom.env"
    env_file.write_text("SLACK_BOT_TOKEN=xoxb-custom\n")
    result = load_slack_token(tmp_path / "file.md", str(env_file))
    assert result == "xoxb-custom"


def test_load_token_missing(monkeypatch, tmp_path):
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    monkeypatch.chdir(tmp_path)
    assert load_slack_token(tmp_path / "file.md", None) is None


# --- main ---

def test_main_missing_token_exits_1(monkeypatch, tmp_path, capsys):
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    monkeypatch.chdir(tmp_path)
    md = tmp_path / "msg.md"
    md.write_text("# Hello\n")
    monkeypatch.setattr(sys, "argv", ["prog", str(md), "#general"])
    assert main() == 1
    err = capsys.readouterr().err
    assert "SLACK_BOT_TOKEN" in err


def test_main_missing_file_exits_1(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    monkeypatch.setattr(sys, "argv", ["prog", str(tmp_path / "missing.md"), "#general"])
    assert main() == 1
    err = capsys.readouterr().err
    assert "not found" in err


def test_main_dry_run_prints_and_exits_0(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    md = tmp_path / "msg.md"
    md.write_text("# Hello\n")
    monkeypatch.setattr(sys, "argv", ["prog", str(md), "#general", "--dry-run"])
    assert main() == 0
    out = capsys.readouterr().out
    assert "*Hello*" in out


def test_main_empty_rendered_exits_1(monkeypatch, tmp_path, capsys):
    """A file whose content renders to empty (only blank lines) exits 1."""
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    md = tmp_path / "empty.md"
    md.write_text("\n\n\n")
    monkeypatch.setattr(sys, "argv", ["prog", str(md), "#general"])
    assert main() == 1
    err = capsys.readouterr().err
    assert "empty" in err.lower()


def test_main_api_error_exits_1(monkeypatch, tmp_path, capsys):
    """A RuntimeError from resolve_channel_id is caught, printed to stderr, exits 1."""
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    md = tmp_path / "msg.md"
    md.write_text("Hello\n")
    monkeypatch.setattr(sys, "argv", ["prog", str(md), "#general"])

    import publish_markdown_to_slack as _mod
    monkeypatch.setattr(_mod, "resolve_channel_id", lambda *_: (_ for _ in ()).throw(RuntimeError("channel_not_found")))
    assert main() == 1
    err = capsys.readouterr().err
    assert "channel_not_found" in err


def test_main_post_success_exits_0(monkeypatch, tmp_path, capsys):
    """A successful post prints channel and ts, exits 0."""
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    md = tmp_path / "msg.md"
    md.write_text("Hello world\n")
    monkeypatch.setattr(sys, "argv", ["prog", str(md), "CABCDEF123"])

    import publish_markdown_to_slack as _mod
    from publish_markdown_to_slack import SlackResult
    monkeypatch.setattr(_mod, "resolve_channel_id", lambda token, ch: "CABCDEF123")
    monkeypatch.setattr(_mod, "post_message", lambda token, ch, text: SlackResult(channel="CABCDEF123", ts="1234567890.000100"))
    assert main() == 0
    out = capsys.readouterr().out
    assert "CABCDEF123" in out
    assert "1234567890.000100" in out


# --- resolve_channel_id ---

def test_resolve_channel_id_already_an_id():
    """A bare channel ID matching CHANNEL_ID_RE is returned unchanged without an API call."""
    # CHANNEL_ID_RE = r"^[CGD][A-Z0-9]{8,}$"
    result = resolve_channel_id("xoxb-fake", "CABCDEF123")
    assert result == "CABCDEF123"


def test_resolve_channel_id_strips_hash_prefix_when_already_id():
    """A '#'-prefixed raw channel ID still gets resolved (hash stripped, lookup attempted)."""
    # '#CABCDEF123' -> normalized 'CABCDEF123' which matches CHANNEL_ID_RE -> returned directly
    result = resolve_channel_id("xoxb-fake", "#CABCDEF123")
    assert result == "CABCDEF123"


def test_resolve_channel_id_not_found_raises(monkeypatch):
    """A channel name that does not appear in the API response raises RuntimeError."""
    import publish_markdown_to_slack as _mod
    monkeypatch.setattr(_mod, "_iter_channels", lambda token: iter([{"name": "other-channel", "id": "COTHER0001"}]))
    with pytest.raises(RuntimeError, match="Could not resolve channel name"):
        resolve_channel_id("xoxb-fake", "#nonexistent")


def test_resolve_channel_id_found_by_name(monkeypatch):
    """A channel name matching an API result returns the correct ID."""
    import publish_markdown_to_slack as _mod
    monkeypatch.setattr(_mod, "_iter_channels", lambda token: iter([{"name": "general", "id": "CGENERAL001"}]))
    result = resolve_channel_id("xoxb-fake", "#general")
    assert result == "CGENERAL001"


# --- load_slack_token (additional cases) ---

def test_load_token_from_env_local_in_cwd(monkeypatch, tmp_path):
    """Token is found in .env.local in the cwd when no env var or .env exists."""
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    (tmp_path / ".env.local").write_text("SLACK_BOT_TOKEN=xoxb-local\n")
    monkeypatch.chdir(tmp_path)
    assert load_slack_token(tmp_path / "file.md", None) == "xoxb-local"


def test_load_token_from_dotenv_in_markdown_dir(monkeypatch, tmp_path):
    """Token is found in .env next to the markdown file when cwd differs."""
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    subdir = tmp_path / "docs"
    subdir.mkdir()
    (subdir / ".env").write_text("SLACK_BOT_TOKEN=xoxb-subdir\n")
    cwd_dir = tmp_path / "cwd"
    cwd_dir.mkdir()
    monkeypatch.chdir(cwd_dir)
    assert load_slack_token(subdir / "file.md", None) == "xoxb-subdir"


def test_load_token_explicit_env_file_missing(monkeypatch, tmp_path):
    """An explicit --env-file that does not exist returns None."""
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    result = load_slack_token(tmp_path / "file.md", str(tmp_path / "nonexistent.env"))
    assert result is None


def test_load_token_explicit_env_file_no_token(monkeypatch, tmp_path):
    """An explicit --env-file that exists but lacks SLACK_BOT_TOKEN returns None."""
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    env_file = tmp_path / "other.env"
    env_file.write_text("OTHER_VAR=foo\n")
    result = load_slack_token(tmp_path / "file.md", str(env_file))
    assert result is None


# --- convert_inline (additional cases) ---

def test_convert_inline_backtick_unchanged():
    """Inline code spans are not modified by convert_inline."""
    assert convert_inline("`some code`") == "`some code`"


def test_convert_inline_bold_and_italic_together():
    """Bold and italic in the same string are each converted independently."""
    result = convert_inline("**bold** and *italic*")
    assert "*bold*" in result
    assert "_italic_" in result


# --- markdown_to_slack (additional cases) ---

def test_bullet_plus():
    """'+' list marker is converted to a bullet."""
    assert markdown_to_slack("+ item") == "• item"


def test_task_list_uppercase_X():
    """'- [X] done' (uppercase X) is treated as checked."""
    assert markdown_to_slack("- [X] done") == "• [x] done"


def test_code_fence_with_language_tag():
    """A fenced code block with a language tag still outputs bare triple-backticks."""
    md = "```python\nprint('hi')\n```"
    result = markdown_to_slack(md)
    assert "```" in result
    assert "print('hi')" in result


def test_horizontal_rule_passthrough():
    """A line that is not a heading, list, or quote passes through convert_inline unchanged."""
    assert markdown_to_slack("---") == "---"


# --- resolve_channel_id (additional cases) ---

def test_resolve_channel_id_name_without_hash(monkeypatch):
    """A bare channel name (no '#' prefix) is looked up via _iter_channels."""
    import publish_markdown_to_slack as _mod
    monkeypatch.setattr(_mod, "_iter_channels", lambda token: iter([{"name": "general", "id": "CGENERAL001"}]))
    result = resolve_channel_id("xoxb-fake", "general")
    assert result == "CGENERAL001"


def test_resolve_channel_id_empty_channel_list_raises(monkeypatch):
    """An empty channel list raises RuntimeError with an informative message."""
    import publish_markdown_to_slack as _mod
    monkeypatch.setattr(_mod, "_iter_channels", lambda token: iter([]))
    with pytest.raises(RuntimeError, match="Could not resolve channel name"):
        resolve_channel_id("xoxb-fake", "emptychannel")


# --- _api_post error paths ---

def test_api_post_http_error_raises_runtime_error(monkeypatch):
    """An HTTP error from Slack raises RuntimeError with the status code."""
    import urllib.error
    import publish_markdown_to_slack as _mod

    def _raise(*args, **kwargs):
        raise urllib.error.HTTPError(url="https://slack.com/api/test", code=400, msg="Bad Request", hdrs=None, fp=None)

    monkeypatch.setattr(_mod.urllib.request, "urlopen", _raise)
    with pytest.raises(RuntimeError, match="Slack HTTP error 400"):
        _mod._api_post("xoxb-fake", "chat.postMessage", {"channel": "C1", "text": "hi"})


def test_api_post_url_error_raises_runtime_error(monkeypatch):
    """A URLError (network failure) raises RuntimeError with connection detail."""
    import urllib.error
    import publish_markdown_to_slack as _mod

    def _raise(*args, **kwargs):
        raise urllib.error.URLError(reason="Name or service not known")

    monkeypatch.setattr(_mod.urllib.request, "urlopen", _raise)
    with pytest.raises(RuntimeError, match="Slack connection error"):
        _mod._api_post("xoxb-fake", "chat.postMessage", {"channel": "C1", "text": "hi"})


def test_api_post_ok_false_raises_runtime_error(monkeypatch):
    """A 200 response with ok=false raises RuntimeError with the Slack error string."""
    import io
    import publish_markdown_to_slack as _mod

    class _FakeResp:
        def __enter__(self):
            return self
        def __exit__(self, *_):
            pass
        def read(self):
            return b'{"ok": false, "error": "not_authed"}'

    monkeypatch.setattr(_mod.urllib.request, "urlopen", lambda *a, **kw: _FakeResp())
    with pytest.raises(RuntimeError, match="not_authed"):
        _mod._api_post("xoxb-fake", "chat.postMessage", {"channel": "C1", "text": "hi"})


# --- _iter_channels pagination ---

def test_iter_channels_pagination(monkeypatch):
    """_iter_channels follows next_cursor and yields channels from both pages."""
    import publish_markdown_to_slack as _mod

    call_count = 0
    pages = [
        {"ok": True, "channels": [{"name": "alpha", "id": "C0000000001"}],
         "response_metadata": {"next_cursor": "cursor-abc"}},
        {"ok": True, "channels": [{"name": "beta", "id": "C0000000002"}],
         "response_metadata": {"next_cursor": ""}},
    ]

    def _fake_api_post(token, endpoint, payload):
        nonlocal call_count
        result = pages[call_count]
        call_count += 1
        return result

    monkeypatch.setattr(_mod, "_api_post", _fake_api_post)
    channels = list(_mod._iter_channels("xoxb-fake"))
    assert len(channels) == 2
    assert channels[0]["name"] == "alpha"
    assert channels[1]["name"] == "beta"
    assert call_count == 2


# --- load_slack_token (additional cases) ---

def test_load_token_export_prefix_in_dotenv(monkeypatch, tmp_path):
    """A dotenv line with 'export ' prefix is parsed and the token is returned."""
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    (tmp_path / ".env").write_text("export SLACK_BOT_TOKEN=xoxb-export\n")
    monkeypatch.chdir(tmp_path)
    assert load_slack_token(tmp_path / "file.md", None) == "xoxb-export"


# --- main (additional cases) ---

def test_main_with_env_file_arg(monkeypatch, tmp_path, capsys):
    """--env-file argument is forwarded to load_slack_token and used for the token."""
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    md = tmp_path / "msg.md"
    md.write_text("Hello\n")
    env_file = tmp_path / "custom.env"
    env_file.write_text("SLACK_BOT_TOKEN=xoxb-custom\n")

    import publish_markdown_to_slack as _mod
    from publish_markdown_to_slack import SlackResult
    monkeypatch.setattr(_mod, "resolve_channel_id", lambda token, ch: "CABCDEF123")
    monkeypatch.setattr(_mod, "post_message", lambda token, ch, text: SlackResult(channel="CABCDEF123", ts="111.222"))
    monkeypatch.setattr(sys, "argv", ["prog", str(md), "#general", "--env-file", str(env_file)])
    assert main() == 0


def test_main_post_message_runtime_error_exits_1(monkeypatch, tmp_path, capsys):
    """A RuntimeError from post_message is caught, printed to stderr, exits 1."""
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    md = tmp_path / "msg.md"
    md.write_text("Hello\n")
    monkeypatch.setattr(sys, "argv", ["prog", str(md), "CABCDEF123"])

    import publish_markdown_to_slack as _mod
    monkeypatch.setattr(_mod, "resolve_channel_id", lambda token, ch: "CABCDEF123")
    monkeypatch.setattr(_mod, "post_message", lambda *_: (_ for _ in ()).throw(RuntimeError("message_too_long")))
    assert main() == 1
    err = capsys.readouterr().err
    assert "message_too_long" in err
