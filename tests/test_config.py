"""Tests parsing of the configuration file."""

from __future__ import annotations

from commit import NewCommitType, NewGitmoji, parse_config


def test_parse() -> None:
    """Test parsing of the configuration file."""
    x = parse_config("tests/resources/.quick-commit-config.yaml")
    assert x.excluded_commit_types == ["chore", "revert"]
    assert x.new_commit_types == [
        NewCommitType("my-commit-type", "My custom commit type"),
        NewCommitType("my-other-commit-type", "My other custom commit type"),
    ]
    assert x.priority_commit_types == ["feat", "my-commit-type", "my-other-commit-type"]

    assert x.excluded_scopes == ["deps"]
    assert x.new_scopes == ["my-new-scope"]
    assert x.prohibit_no_scope

    assert x.message_pattern == r"^\w+\."

    assert x.excluded_gitmojis == ["art", "fire"]
    assert x.new_gitmojis == [
        NewGitmoji("🎨", "my-gitmoji", "My custom gitmoji."),
        NewGitmoji("🔥", "my-gitmoji-2", "My custom gitmoji number 2."),
    ]
    assert x.priority_gitmojis == ["sparkles", "my-gitmoji", "my-gitmoji-2"]

    assert x.enable_footer
    assert x.ai_template == "Made by $."


def test_parse_empty() -> None:
    """Test parsing an empty configuration file."""
    x = parse_config("tests/resources/.empty.yaml")
    assert x.excluded_commit_types == []
    assert x.new_commit_types == []
    assert x.priority_commit_types == []

    assert x.excluded_scopes == []
    assert x.new_scopes == []
    assert not x.prohibit_no_scope

    assert x.message_pattern is None

    assert x.excluded_gitmojis == []
    assert x.new_gitmojis == []
    assert x.priority_gitmojis == []

    assert not x.enable_footer


def test_parse_short_style() -> None:
    """Test parsing a configuration style that uses 'short' style for lists."""
    x = parse_config("tests/resources/.short-style.yaml")
    assert x.excluded_commit_types == ["chore"]
    assert x.new_commit_types == [
        NewCommitType("my-commit-type", "My custom commit type"),
    ]
    assert x.priority_commit_types == ["feat"]

    assert x.excluded_scopes == ["my-excluded-scope"]
    assert x.new_scopes == ["my-new-scope"]

    assert x.excluded_gitmojis == ["art"]
    assert x.new_gitmojis == [
        NewGitmoji("🎨", "my-gitmoji", "My custom gitmoji."),
    ]
    assert x.priority_gitmojis == ["sparkles"]
