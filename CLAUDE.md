# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run in development mode
python main.py --help

# Run a specific tool action
python main.py backup borgmatic list
python main.py backup borgmatic generate

# Run tests
pytest

# Run a single test file
pytest tests/test_discovery.py

# Build distributable binary (CI uses PyInstaller)
pyinstaller --onefile --name scaffoldr-linux-x86_64 --add-data "definitions:definitions" main.py
```

## Architecture

Scaffoldr is a **data-driven CLI** built with Typer. The command hierarchy is not hardcoded — it is built at startup by scanning the `definitions/` directory.

### Startup flow

`main.py` → `core/discovery.py:register_dynamic_commands()` → scans `definitions/` → dynamically builds Typer sub-apps for each category and tool → registers `generate` and `list` subcommands.

### Definitions (data layer)

Every tool lives entirely in `definitions/<category>/<tool>/`:
- `<tool>.yaml` — wizard schema (prompts, validation, sections, post-generation notes)
- `<tool>.yaml.j2` — Jinja2 template rendered into the output config file

**Adding a new tool requires no Python changes** — only creating these two files. The discovery engine picks it up automatically.

### YAML definition schema

```yaml
heading:
  title: "Wizard title"
  before:           # list of sections shown to the user
    - title: "Section name"
      subtitle: "Optional description"
      prompts:
        - key: var_name          # passed to Jinja2 template as {{ var_name }}
          prompt: "Question?"
          description: "Shown in `list` command"
          required: true
          default: "fallback"
          choices: ["a", "b"]   # optional allowlist
          is_list: true          # splits comma-separated input into a Python list
          is_password: true      # masks input
          depends_on:            # conditional display
            key: other_key
            value: "expected"
  after:
    logs:
      success: "Message shown on success. Supports {output_path}."
    notes:
      - "Post-generation instruction. Supports {var_name} substitution."
```

Global defaults from `~/.scaffoldr` (TOML, keyed by tool name) override YAML `default` values.

### Core modules

- `core/discovery.py` — scans `definitions/`, builds Typer CLI tree
- `core/engine/wizard.py` — `run_config_flow()`: loads YAML, prompts user, renders Jinja2 template, saves file
- `core/engine/display.py` — `list_config_fields()`: renders a Rich table of all fields and their defaults
- `core/engine/paths.py` — `get_resource_path()`: resolves paths for both dev and PyInstaller (`sys._MEIPASS`) modes
- `utils/prompter.py` — interactive prompt loop with validation (regex, required, choices, dependency logic)
- `utils/config.py` — reads `~/.scaffoldr` TOML for global defaults
- `utils/loaders.py` — YAML and TOML loading helpers

### Coding standards

- All Python files stay **under 100 lines** — split into submodules if a file grows too large.
- All functions must have **type hints**.
- All CLI output must use the **`rich`** library (no bare `print()`).

### Release

Releases are triggered by pushing a `v*` tag. CI builds two native binaries (Linux x86_64 and ARM64) using PyInstaller and publishes them as GitHub Release assets. The `--add-data "definitions:definitions"` flag bundles the definitions directory into the binary.
