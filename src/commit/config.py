"""Responsible for parsing the configuration file."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import appdirs  # type: ignore[import-untyped]
import yaml


@dataclass
class NewCommitType:
    """Represents a new commit type."""

    name: str
    description: str


@dataclass
class NewGitmoji:
    """Represents a new gitmoji."""

    icon: str
    name: str
    description: str


@dataclass
class Config:
    """The configuration used for running quick-commit."""

    excluded_commit_types: list[str] = field(default_factory=list)
    new_commit_types: list[NewCommitType] = field(default_factory=list)
    priority_commit_types: list[str] = field(default_factory=list)

    excluded_scopes: list[str] = field(default_factory=list)
    new_scopes: list[str] = field(default_factory=list)
    prohibit_no_scope: bool = False

    message_pattern: str | None = None

    excluded_gitmojis: list[str] = field(default_factory=list)
    new_gitmojis: list[NewGitmoji] = field(default_factory=list)
    priority_gitmojis: list[str] = field(default_factory=list)

    enable_footer: bool = False

    ai_template: str = "Assisted-by: $"


def find_config() -> Config:
    """Find the configuration for your current working directory.

    Returns:
        Config: The configuration for your current working directory.
    """
    current = Path.cwd()
    while True:
        if (current / ".quick-commit-config.yaml").exists():
            return parse_config(current / ".quick-commit-config.yaml")
        if (current / ".quick-commit-config.yml").exists():
            return parse_config(current / ".quick-commit-config.yml")
        if current.parent == current:
            break
        current = current.parent

    # no local config found, finding global config instead.
    config_dir = Path(appdirs.user_config_dir("quick-commit", False))
    if not config_dir.exists():
        config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"
    if not config_file.exists():
        config_file = config_dir / "config.yml"
    if config_file.exists():
        return parse_config(config_file)
    return Config()


def parse_config(config: Path | str) -> Config:
    """Parse a configuration file.

    Args:
        config (Path | str): The path to the configuration file.

    Raises:
        ValueError: If the configuration file is invalid.

    Returns:
        Config: The parsed configuration.
    """
    if isinstance(config, str):
        config = Path(config)
    with config.open("r") as file:
        data = yaml.safe_load(file)

    c = Config()
    if data is None:
        return c

    if "types" in data:
        ######################################### types->exclude #########################################
        if "exclude" in data["types"]:
            value = data["types"]["exclude"]
            if isinstance(value, str):
                value = [value]
            elif not isinstance(value, list):
                msg = "Excluded commit types must be a a list of strings."
                raise ValueError(msg)
            c.excluded_commit_types = value
        ######################################### types->priority #########################################
        if "priority" in data["types"]:
            value = data["types"]["priority"]
            if isinstance(value, str):
                value = [value]
            elif not isinstance(value, list):
                msg = "Priority commit types must be a a list of strings."
                raise ValueError(msg)
            c.priority_commit_types = value
        ######################################### types->add #########################################
        if "add" in data["types"]:
            value = data["types"]["add"]
            if isinstance(value, dict):
                value = [value]
            elif not isinstance(value, list):
                msg = "Added commit types must be a a list of objects."
                raise ValueError(msg)
            for new in value:
                if "name" not in new or "description" not in new:
                    msg = "New commit types must have a name and a description."
                    raise ValueError(msg)
                name = str(new["name"])
                description = str(new["description"])
                if not name or not description:
                    msg = "The name and description of a commit type must not be empty."
                    raise ValueError(msg)
                c.new_commit_types.append(NewCommitType(name, description))
    if "scopes" in data:
        ######################################### scopes->exclude #########################################
        if "exclude" in data["scopes"]:
            value = data["scopes"]["exclude"]
            if isinstance(value, str):
                value = [value]
            elif not isinstance(value, list):
                msg = "Excluded scopes must be a a list of strings."
                raise ValueError(msg)
            c.excluded_scopes = value
        ######################################### scopes->add #########################################
        if "add" in data["scopes"]:
            value = data["scopes"]["add"]
            if isinstance(value, str):
                value = [value]
            elif not isinstance(value, list):
                msg = "Added scopes must be a a list of strings."
                raise ValueError(msg)
            c.new_scopes = value
        ######################################### scopes->prohibit_no_scope #########################################
        if "prohibit-no-scope" in data["scopes"]:
            if not isinstance(data["scopes"]["prohibit-no-scope"], bool):
                msg = "The prohibit-no-scope option must be a boolean."
                raise ValueError(msg)
            c.prohibit_no_scope = data["scopes"]["prohibit-no-scope"]
    ######################################### message->custom-pattern #########################################
    if "message" in data and "custom-pattern" in data["message"]:
        if not isinstance(data["message"]["custom-pattern"], str):
            msg = "The custom-pattern option must be a string."
            raise ValueError(msg)
        value = data["message"]["custom-pattern"]
        if not value:
            value = None
        c.message_pattern = value
    if "gitmojis" in data:
        ######################################### gitmojis->exclude #########################################
        if "exclude" in data["gitmojis"]:
            value = data["gitmojis"]["exclude"]
            if isinstance(value, str):
                value = [value]
            elif not isinstance(value, list):
                msg = "Excluded gitmojis must be a a list of strings."
                raise ValueError(msg)
            c.excluded_gitmojis = value
        ######################################### gitmojis->priority #########################################
        if "priority" in data["gitmojis"]:
            value = data["gitmojis"]["priority"]
            if isinstance(value, str):
                value = [value]
            elif not isinstance(value, list):
                msg = "Priority gitmojis must be a a list of strings."
                raise ValueError(msg)
            c.priority_gitmojis = value
        ######################################### gitmojis->add ################################
        if "add" in data["gitmojis"]:
            value = data["gitmojis"]["add"]
            if isinstance(value, dict):
                value = [value]
            elif not isinstance(value, list):
                msg = "Excluded gitmojis must be a a list of objects."
                raise ValueError(msg)
            for new in value:
                if "name" not in new or "description" not in new or "icon" not in new:
                    msg = "New gitmojis must have a name, a description and an icon."
                    raise ValueError(msg)
                name = str(new["name"])
                description = str(new["description"])
                icon = str(new["icon"])
                if not name or not description or not icon:
                    msg = "The name, description and icon of a gitmoji must not be empty."
                    raise ValueError(msg)
                if ":" in {icon[0], icon[-1]}:
                    msg = "The icon must be provided without leading/trailing ':' signs."
                    raise ValueError(msg)
                c.new_gitmojis.append(NewGitmoji(icon, name, description))
    if "always-enable-footer" in data:
        if not isinstance(data["always-enable-footer"], bool):
            msg = "The always-enable-footer option must be a boolean."
            raise ValueError(msg)
        c.enable_footer = data["always-enable-footer"]
    if "ai-template" in data:
        if not isinstance(data["ai-template"], str):
            msg = "The ai-template option must be a string."
            raise ValueError(msg)
        if "$" not in data["ai-template"]:
            msg = "The ai-template option must contain a '$' sign to indicate where the AI name(s) should be inserted."
            raise ValueError(msg)
        c.ai_template = data["ai-template"]

    return c
