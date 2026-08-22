import re
from typing import Any

from jinja2 import Environment
from rich.console import Console
from rich.prompt import Prompt

from utils.overrides import apply_override, split_csv

console = Console()
jinja_env = Environment()


def _render_val(val: Any, context: dict[str, Any]) -> Any:
    """Renders a value if it contains Jinja2 templates."""
    if isinstance(val, str) and "{{" in val:
        try:
            return jinja_env.from_string(val).render(context)
        except Exception:  # noqa: BLE001 — template errors fall back to the raw value
            return val
    return val


def _get_input(
    p: dict[str, Any],
    ctx: dict[str, Any],
    defaults: dict[str, Any],
    overrides: dict[str, Any],
    automated: bool,
) -> Any:
    """Handles the interactive prompt loop for a single configuration key."""
    key = p["key"]
    required = p.get("required", False)

    if key in overrides:
        accepted, value = apply_override(p, overrides[key])
        if accepted:
            return value
        console.print(
            f"[yellow]Override for '{key}' is invalid; falling back to a prompt.[/yellow]"
        )

    # Global defaults (TOML) take precedence over definition defaults (YAML)
    default = _render_val(defaults.get(key, p.get("default")), ctx)

    if automated and not required:
        # Non-interactive run: accept the field's own default without prompting.
        return split_csv(default) if p.get("is_list") else default

    while True:
        value = Prompt.ask(
            p["prompt"],
            default=default,
            password=p.get("is_password", False),
            choices=p.get("choices"),
        )

        if required and not value:
            console.print("[red]This field is required.[/red]")
            continue

        regex = p.get("regex")
        if regex and value and not re.match(regex, str(value)):
            console.print(f"[red]Input must match: {regex}[/red]")
            continue
        break

    return split_csv(value) if p.get("is_list") else value


def prompt_for_config(
    heading: dict[str, Any],
    global_defaults: dict[str, Any] | None = None,
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Prompts for config values; missing fields prompt unless overrides make the run automated."""
    config = {}
    defaults = global_defaults or {}
    overrides = overrides or {}
    automated = bool(overrides)

    for section in heading.get("before", []):
        console.print(
            f"\n[italic underline blue]{section.get('title', 'Section')}[/italic underline blue]"
        )
        if "subtitle" in section:
            console.print(f"[dim]{section['subtitle']}[/dim]\n")

        for p in section.get("prompts", []):
            # Check dependency logic (skip if criteria not met)
            dep = p.get("depends_on")
            if dep:
                dep_val = dep.get("value")
                dep_vals = dep_val if isinstance(dep_val, list) else [dep_val]
                if config.get(dep.get("key")) not in dep_vals:
                    continue

            config[p["key"]] = _get_input(p, config, defaults, overrides, automated)

    return config
