# Scaffoldr

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Release](https://github.com/gowdhamp/scaffoldr/actions/workflows/release.yml/badge.svg)
![GitHub Release](https://img.shields.io/github/v/release/gowdhamp/scaffoldr)
![GitHub Downloads](https://img.shields.io/github/downloads/gowdhamp/scaffoldr/total)

**Scaffoldr is a fast and simple CLI tool for instantly generating configuration files and boilerplates for your favorite DevOps and infrastructure tools.**

Stop searching for documentation and examples. With Scaffoldr, you can interactively generate validated and ready-to-use configuration files for tools like Borgmatic, Autorestic, and more, directly from your terminal.

## Core Features

- **🚀 Interactive Wizards**: Guide you through complex configurations with simple, descriptive prompts.
- **🛠️ Hierarchical CLI**: Intuitive command structure: `scaffoldr <category> <tool> <action>`.
- **📊 Field Discovery**: Use the `list` action to see all available configuration fields, their descriptions, and global defaults.
- **⚙️ Global Configuration**: Set persistent defaults in `~/.scaffoldr` (TOML) to speed up your scaffolding process.
- **✅ Smart Validation**: Ensures required fields are filled and values match expected patterns (regex).
- **📦 Zero Dependencies**: Distributed as a single, portable binary for Linux (x86_64 & ARM64).

## Getting Started

### One-Line Install (Linux)

```sh
curl -sSL https://raw.githubusercontent.com/gowdhamp/scaffoldr/main/scripts/install.sh | bash
```

### Manual Installation

1.  Download the latest binary from the [GitHub Releases](https://github.com/gowdhamp/scaffoldr/releases).
2.  Place it in your `PATH` (e.g., `/usr/local/bin`).
3.  Make it executable: `chmod +x /usr/local/bin/scaffoldr`.

## Usage

Scaffoldr uses a simple nested command structure. Running any command or category without arguments will display the help menu automatically.

### Commands

Every tool supports two main actions:
- `generate`: Start the interactive configuration wizard.
- `list`: Show a table of all configuration fields and their current defaults.

*Note: Running just the tool name (e.g., `scaffoldr backup borgmatic`) defaults to the `list` action.*

### 💾 Global Defaults

You can set global defaults in `~/.scaffoldr` to avoid re-typing common values:

```toml
[borgmatic]
remote_path = "/usr/bin/borg"
repository_path = "ssh://backup-server/./repo"

[autorestic]
backend_type = "s3"
```

## Examples

### 1. Explore Configuration Fields
See what fields are required for a tool and what your current defaults are:
```sh
scaffoldr backup borgmatic list
```

### 2. Generate a Configuration
Launch the interactive wizard to create a file:
```sh
scaffoldr backup borgmatic generate
```

### 3. Quick Scaffolding with Autorestic
```sh
scaffoldr backup autorestic generate
```

## Contributing

Scaffoldr is designed to be highly extensible. To add a new tool or category, simply add a YAML definition and a Jinja2 template to the `definitions/` directory. No code changes required!

## License

Distributed under the MIT License. See `LICENSE` for more information.
