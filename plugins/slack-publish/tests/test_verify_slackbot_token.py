import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from verify_slackbot_token import find_token, main


def test_find_token_from_env(monkeypatch):
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-from-env")
    assert find_token() == "xoxb-from-env"


def test_find_token_missing(monkeypatch, tmp_path):
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    monkeypatch.chdir(tmp_path)
    assert find_token() is None


def test_find_token_from_dotenv(monkeypatch, tmp_path):
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    (tmp_path / ".env").write_text("SLACK_BOT_TOKEN=xoxb-dotenv\n")
    monkeypatch.chdir(tmp_path)
    assert find_token() == "xoxb-dotenv"


def test_find_token_from_dotenv_local(monkeypatch, tmp_path):
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    (tmp_path / ".env.local").write_text("SLACK_BOT_TOKEN=xoxb-local\n")
    monkeypatch.chdir(tmp_path)
    assert find_token() == "xoxb-local"


def test_find_token_double_quoted(monkeypatch, tmp_path):
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    (tmp_path / ".env").write_text('SLACK_BOT_TOKEN="xoxb-quoted"\n')
    monkeypatch.chdir(tmp_path)
    assert find_token() == "xoxb-quoted"


def test_find_token_single_quoted(monkeypatch, tmp_path):
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    (tmp_path / ".env").write_text("SLACK_BOT_TOKEN='xoxb-single'\n")
    monkeypatch.chdir(tmp_path)
    assert find_token() == "xoxb-single"


def test_find_token_env_takes_precedence_over_dotenv(monkeypatch, tmp_path):
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-env")
    (tmp_path / ".env").write_text("SLACK_BOT_TOKEN=xoxb-file\n")
    monkeypatch.chdir(tmp_path)
    assert find_token() == "xoxb-env"


def test_find_token_dotenv_prefers_env_over_env_local(monkeypatch, tmp_path):
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    (tmp_path / ".env").write_text("SLACK_BOT_TOKEN=xoxb-dotenv\n")
    (tmp_path / ".env.local").write_text("SLACK_BOT_TOKEN=xoxb-local\n")
    monkeypatch.chdir(tmp_path)
    assert find_token() == "xoxb-dotenv"


def test_main_returns_0_when_token_set(monkeypatch, tmp_path):
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    assert main() == 0


def test_main_returns_1_when_token_missing(monkeypatch, tmp_path):
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    monkeypatch.chdir(tmp_path)
    assert main() == 1


def test_find_token_empty_value_in_dotenv_returns_none(monkeypatch, tmp_path):
    """An empty value after '=' in the dotenv file is treated as absent."""
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    (tmp_path / ".env").write_text("SLACK_BOT_TOKEN=\n")
    monkeypatch.chdir(tmp_path)
    assert find_token() is None


def test_find_token_unrelated_keys_ignored(monkeypatch, tmp_path):
    """Lines that do not start with SLACK_BOT_TOKEN= do not produce a token."""
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    (tmp_path / ".env").write_text("OTHER_KEY=xoxb-other\nFOO=bar\n")
    monkeypatch.chdir(tmp_path)
    assert find_token() is None


def test_find_token_mismatched_quotes_returned_as_is(monkeypatch, tmp_path):
    """A value with mismatched quote delimiters is returned verbatim (no stripping)."""
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    (tmp_path / ".env").write_text("SLACK_BOT_TOKEN=\"xoxb-bad'\n")
    monkeypatch.chdir(tmp_path)
    # Mismatched quotes: first char '"' != last char "'" so no stripping occurs.
    assert find_token() == "\"xoxb-bad'"


def test_find_token_dotenv_not_file(monkeypatch, tmp_path):
    """.env that is a directory (not a file) is skipped without error."""
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    (tmp_path / ".env").mkdir()
    monkeypatch.chdir(tmp_path)
    assert find_token() is None
