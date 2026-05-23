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
    markdown_to_slack,
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
