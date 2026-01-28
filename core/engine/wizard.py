import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from rich.prompt import Prompt
from typer import Exit
from utils.loaders import load_yaml
from utils.config import get_tool_defaults
from utils.prompter import prompt_for_config
from .paths import get_tool_definition_path

console = Console()

def _save_config(p: str, content: str) -> bool:
    """Handles file saving with overwrite confirmation."""
    if os.path.exists(p):
        if Prompt.ask(f"[red]File '{p}' exists. Overwrite?[/red]", choices=["y", "n"], default="n") != "y":
            return False
    with open(p, "w") as f:
        f.write(content)
    return True

def run_config_flow(tool_name: str, default_filename: str):
    """Main interactive wizard for tool configuration."""
    def_path = get_tool_definition_path(tool_name)
    if not def_path:
        console.print(f"[red]Error: Tool '{tool_name}' definition not found.[/red]")
        return

    data = load_yaml(def_path)
    heading = data.get("heading", {})
    console.print(f"\n[bold]{heading.get('title', 'Configuration Wizard')}[/bold]")

    defaults = get_tool_defaults(tool_name)
    config = prompt_for_config(heading, global_defaults=defaults)
    if not config:
        return

    output = Prompt.ask("\nOutput file path", default=default_filename)
    
    # Add context & tool-specific logic (e.g. borgmatic encryption)
    config.update({"generation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "output_path": output})
    if tool_name.lower() == "borgmatic":
        p = config.get("encryption_passphrase")
        config["encryption_arg"] = f"--encryption='{p}'" if p else "--encryption=none"

    env = Environment(loader=FileSystemLoader(os.path.dirname(def_path)), autoescape=True)
    rendered = env.get_template(f"{tool_name.lower()}.yaml.j2").render(**config)

    if _save_config(output, rendered):
        after = heading.get("after", {})
        console.print(f"\n[green]{after.get('logs', {}).get('success', 'File saved.').format(output_path=output)}[/green]")
        for note in after.get("notes", []):
            console.print(f"\n[bold]Note:[/bold] {note.format(**config)}")
