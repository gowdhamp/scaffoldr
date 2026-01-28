# Contributing to Scaffoldr

First off, thank you for considering contributing to Scaffoldr! It's people like you who make Scaffoldr such a great tool.

Scaffoldr is designed to be **highly extensible**. You can add support for new DevOps tools without touching a single line of Python code.

## 🚀 Adding a New Tool

To add a new tool (e.g., `nginx` or `docker`), you simply need to create a new folder structure in the `definitions/` directory.

### 1. Directory Structure

Scaffoldr follows a strict directory-based discovery pattern:
`definitions/<category>/<tool_name>/`

**Example for Nginx:**
```text
definitions/
└── webserver/
    └── nginx/
        ├── nginx.yaml        # The logic & prompts
        └── nginx.yaml.j2     # The Jinja2 template
```

### 2. The YAML Definition (`tool.yaml`)

This file defines the interactive wizard's layout, sections, and prompts.

**Key Schema Elements:**
- `heading`: Structure for the wizard.
  - `title`: Main title of the wizard.
  - `before`: List of sections (each with a `title`, `subtitle`, and `prompts`).
- `prompts`: Individual input fields.
  - `key`: The variable name passed to the template.
  - `prompt`: The text shown to the user.
  - `description`: Detailed tooltip shown in the `list` command.
  - `required`: (boolean) If true, the user cannot leave it empty.
  - `default`: The fallback value.
  - `choices`: (list) Limits input to specific values.
  - `is_list`: (boolean) If true, splits comma-separated input into a list.
  - `is_password`: (boolean) If true, masks the input.
  - `depends_on`: (object) Only show this prompt if another value matches criteria.

**Example Prompt with Dependency:**
```yaml
- key: backend_type
  prompt: "Backend Type"
  choices: ["s3", "local"]
- key: aws_secret
  prompt: "AWS Secret"
  depends_on:
    key: backend_type
    value: "s3"
```

### 3. The Jinja2 Template (`tool.yaml.j2`)

This is the boilerplate of your configuration file. All `key` values from your YAML prompts are available as variables here.

```jinja2
storage:
  type: {{ backend_type }}
  {% if backend_type == 's3' %}
  secret: {{ aws_secret }}
  {% endif %}
```

---

## 🛠️ Development Setup

If you wish to modify the core Scaffoldr engine:

1. **Clone the repo:**
   ```bash
   git clone https://github.com/gowdhamp/scaffoldr.git
   cd scaffoldr
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run in development mode:**
   ```bash
   python main.py --help
   ```

4. **Run Tests:**
   ```bash
   pytest
   ```

## 📜 Coding Standards

- **Stay Small**: We aim for all Python files to be **under 100 lines**. If a file grows too large, split it into a logical submodule.
- **Type Hints**: All functions should have type hints.
- **Rich Output**: Use the `rich` library for all CLI visual elements.

## 📝 Submitting Changes

1. Fork the repository.
2. Create a new branch: `git checkout -b feat/my-new-tool`.
3. Commit your changes: `git commit -m "feat: add support for nginx"`.
4. Push to the branch: `git push origin feat/my-new-tool`.
5. Submit a Pull Request.

Happy scaffolding!
