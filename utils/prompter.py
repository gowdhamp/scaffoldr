import re
from typing import Dict, Any, List, Optional
from jinja2 import Environment
from rich.console import Console
from rich.prompt import Prompt

console = Console()
jinja_env = Environment()

def _render_val(val: Any, context: Dict[str, Any]) -> Any:
    """Renders a value if it contains Jinja2 templates."""
    if isinstance(val, str) and "{{" in val:
        try:
            return jinja_env.from_string(val).render(context)
        except Exception:
            return val
    return val

def _get_input(p: Dict[str, Any], ctx: Dict[str, Any], defaults: Dict[str, Any]) -> Any:
    """Handles the interactive prompt loop for a single configuration key."""
    key = p['key']
    is_password = p.get("is_password", False)
    is_list = p.get("is_list", False)
    required = p.get("required", False)
    regex = p.get("regex")
    
    # Global defaults (TOML) take precedence over definition defaults (YAML)
    default = defaults.get(key, p.get("default"))
    default = _render_val(default, ctx)

    while True:
        value = Prompt.ask(p['prompt'], default=default, password=is_password, choices=p.get("choices"))

        if required and not value:
            console.print("[red]This field is required.[/red]")
            continue
            
        if regex and value and not re.match(regex, str(value)):
            console.print(f"[red]Input must match: {regex}[/red]")
            continue
        break
    
    if is_list and isinstance(value, str):
        return [i.strip() for i in value.split(",") if i.strip()]
    return value

def prompt_for_config(heading: Dict[str, Any], global_defaults: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Interactively prompts for configuration values based on a tool's definition.
    """
    config = {}
    defaults = global_defaults or {}

    for section in heading.get("before", []):
        console.print(f"\n[italic underline blue]{section.get('title', 'Section')}[/italic underline blue]")
        if "subtitle" in section:
            console.print(f"[dim]{section['subtitle']}[/dim]\n")

        for p in section.get("prompts", []):
            # Check dependency logic (skip if criteria not met)
            dep = p.get("depends_on")
            if dep and config.get(dep.get("key")) != dep.get("value"):
                continue

            config[p['key']] = _get_input(p, config, defaults)

    return config
