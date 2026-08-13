# quick-commit

[![PyPI](https://img.shields.io/pypi/v/quick-commit?logo=pypi&style=flat-square)](https://pypi.org/project/quick-commit/)
![OS](https://img.shields.io/badge/os-linux%20%7C%20macos%20%7C%20windows-blue?style=flat-square)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![CI](https://img.shields.io/github/actions/workflow/status/DRovara/quick-commit/ci.yml?branch=main&style=flat-square&logo=github&label=ci)](https://github.com/DRovara/quick-commit/actions/workflows/ci.yml)
[![CD](https://img.shields.io/github/actions/workflow/status/DRovara/quick-commit/cd.yml?style=flat-square&logo=github&label=cd)](https://github.com/DRovara/quick-commit/actions/workflows/cd.yml)
<a href="https://gitmoji.dev">
<img
    src="https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg?style=flat-square"
    alt="Gitmoji"
  />
</a>

`quick-commit` is a CLI-based git commit automation tool that helps you follow the _Conventional Commits_ specification.

The main features include:

- automatic generation of commit messages based on the _Conventional Commits_ specification with gitmoji support.
- filter functions to find your desired commit types, scopes, and gitmojis.
- sorting methods to give you your most commonly/recently used gitmojis and scopes right away.
- commit message validation to ensure your commit messages are formatted correctly.
- a simple and easy-to-use interface.
- a customisable configuration file to suit your needs.

`quick-commit` is designed to help you write better commit messages and make your git history more readable and understandable with the least amount of effort.

## Installation

To install `quick-commit`, you can use the following command:

```bash
pipx install quick-commit
```

This installs the `quick-commit` python application (requires Python 3.10 or later) and makes it available as a command-line tool.

## Usage

To use `quick-commit`, you can run the following command:

```bash
quick-commit
```

This will open the `quick-commit` CLI interface where you can customise your commit message.
Starting `quick-commit` with the `-a` flag additionally stages all modified files for the commit.

If you wish to include a footer in your commit message, use the flag `--footer` (or enable it by default in the configuration file).

To mark breaking changes in your commit message, use the flag `--breaking`.

The `--ai [ai agent]` option allows you to specify AI agents that were used to generate the code of the commit. The AI agents are listed in the footer of the commit message.

Finally, the `-r [message]` option allows you to repeat a previous commit with the same structure (type, scope, and gitmoji) but with a different message. This is useful for making multiple commits of the same type.

## Configuration

`quick-commit` uses a configuration file to store your preferences. A configuration file can be stored locally
for your project at `.quick-commit-config.yaml` or globally in your user-config directory (`/home/username/.config/quick-commit/config.yaml` for Linux, or `C:\Users\username\AppData\Roaming\quick-commit\config.yaml` for Windows).

An example configuration file that shows off all supported settings is as follows:

```yaml
types:
  exclude:
    - chore
    - revert
  add:
    - name: my-commit-type
      description: My custom commit type
    - name: my-other-commit-type
      description: My other custom commit type
  priority:
    - feat
    - my-commit-type
    - my-other-commit-type

scopes:
  exclude:
    - deps
    - '#\d+'
  add:
    - my-new-scope
  prohibit-no-scope: true

message:
  custom-pattern: '^\w+\.'

gitmojis:
  exclude:
    - art
    - fire
  add:
    - icon: 🎨
      name: my-gitmoji
      description: My custom gitmoji.
    - icon: 🔥
      name: my-gitmoji-2
      description: My custom gitmoji number 2.
  priority:
    - sparkles
    - my-gitmoji
    - my-gitmoji-2

always-enable-footer: true
ai-template: Hey we used the AI agent(s) $
```
