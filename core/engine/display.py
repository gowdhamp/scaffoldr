from rich.console import Console
from rich.table import Table
from utils.loaders import load_yaml
from utils.config import get_tool_defaults
from .paths import get_tool_definition_path

console = Console()

def list_config_fields(tool_name: str):
    """
    Displays a formatted table of all configuration fields for a given tool.
    Groups fields by section and shows global defaults from ~/.scaffoldr.
    """
    path = get_tool_definition_path(tool_name)
    if not path:
        console.print(f"[red]Error: Tool '{tool_name}' definition not found.[/red]")
        return

    data = load_yaml(path)
    tool_defaults = get_tool_defaults(tool_name)

    table = Table(title=f"Configuration Fields for {tool_name.title()}")
    table.add_column("Field", style="cyan")
    table.add_column("Global Default", style="green")
    table.add_column("Required", style="magenta")
    table.add_column("Description", style="white")

    for section in data.get("heading", {}).get("before", []):
        title = section.get("title", "Other")
        # Section header
        table.add_row(f"[bold yellow]{title}[/bold yellow]", end_section=True)
        
        for p in section.get("prompts", []):
            field = p.get("key", "N/A")
            val = str(tool_defaults.get(field, "None"))
            req = "Yes" if p.get("required") else "No"
            desc = p.get("description", "No description provided.")
            table.add_row(field, val, req, desc)

        # Visual spacer between sections
        table.add_row("", "", "", "", end_section=True)

    console.print(table)
