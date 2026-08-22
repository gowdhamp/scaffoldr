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

### 🤖 Non-Interactive Mode

For CI pipelines, scripts, or automated provisioning, `generate` also accepts answers from flags instead of prompts:

```sh
# Pass a values file (YAML or TOML)
scaffoldr backup borgmatic generate --values borgmatic-values.yaml

# Override individual keys inline (repeatable)
scaffoldr backup borgmatic generate --set backup_name=web --set source_directory=/srv/www

# Mix both — inline --set values take precedence over the values file
scaffoldr backup borgmatic generate --values base.yaml --set encryption_passphrase=secret

# Skip the overwrite confirmation
scaffoldr backup borgmatic generate --values base.yaml --yes
```

Once any `--values`/`--set` is provided, fields left unset simply take their default instead of prompting — only a *required* field with no override and no default still falls back to an interactive prompt. With no flags at all, `generate` behaves exactly as before.

### 📥 Installing the Tools Themselves

Beyond generating configs, scaffoldr can fetch the actual upstream tool binaries (borg, restic, autorestic) from their own GitHub releases — no `apt`/`go install` needed:

```sh
# Install the latest release to /usr/local/bin
scaffoldr install restic

# Install (or downgrade to) a specific version
scaffoldr install borg --version 1.4.5

# Re-running with the same version is a no-op
scaffoldr install restic
```

This downloads the release asset matching your architecture (Linux x86_64/arm64), extracts it if needed, and installs it with `chmod 755`. Requires write access to `/usr/local/bin` (use `sudo` if needed).

*Note: `borgmatic` is pure Python and has no GitHub binary release — install it with `pip install borgmatic` instead.*

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
