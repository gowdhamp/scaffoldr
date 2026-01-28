import os
from typing import Dict, List
from typer import Typer, Context
from core.engine import run_config_flow, get_resource_path, list_config_fields

# TODO: Add caching for discovered tools if configuration directory becomes very large.

def discover_tools() -> Dict[str, List[str]]:
    """
    Scans the definitions directory and returns a mapping of categories to tools.
    
    Expected directory structure:
    definitions/<category>/<tool>/<tool>.yaml
    
    Returns:
        A dictionary where keys are category names and values are lists of tool names.
    """
    definitions_path = get_resource_path("definitions")
    mapping = {}

    if not definitions_path or not os.path.exists(definitions_path):
        return mapping

    # Traverse categories (e.g., backup, infra)
    for category in os.listdir(definitions_path):
        category_path = os.path.join(definitions_path, category)
        if not os.path.isdir(category_path):
            continue

        tools = []
        # Traverse individual tools (e.g., borgmatic, autorestic)
        for tool in os.listdir(category_path):
            tool_path = os.path.join(category_path, tool)
            definition_file = os.path.join(tool_path, f"{tool}.yaml")
            
            # A tool is valid if it contains its definition YAML
            if os.path.isdir(tool_path) and os.path.exists(definition_file):
                tools.append(tool)
        
        if tools:
            mapping[category] = sorted(tools)

    return mapping

def _register_tool_commands(category_app: Typer, tool_name: str):
    """
    Creates and registers a nested Typer app for a specific tool.
    Each tool app includes 'generate' and 'list' subcommands.
    """
    tool_app = Typer(help=f"Manage {tool_name} scaffolding.")

    # Default action: list fields if no subcommand is provided
    def tool_callback(ctx: Context):
        if ctx.invoked_subcommand is None:
            list_config_fields(tool_name)

    tool_app.callback(invoke_without_command=True)(tool_callback)

    # Subcommand: generate
    def generate():
        """Interactively generate a configuration file."""
        run_config_flow(tool_name, f"{tool_name}.yaml")
    
    # Subcommand: list
    def list_fields():
        """List all configuration fields and global defaults."""
        list_config_fields(tool_name)

    tool_app.command(name="generate")(generate)
    tool_app.command(name="list")(list_fields)

    category_app.add_typer(tool_app, name=tool_name)

def register_dynamic_commands(app: Typer):
    """
    Dynamically builds the CLI command hierarchy based on tool definitions.
    """
    tool_mapping = discover_tools()

    for category, tools in sorted(tool_mapping.items()):
        # Each category gets its own Typer sub-app
        category_app = Typer(
            help=f"Scaffolding for {category} tools.",
            no_args_is_help=True
        )

        for tool in tools:
            _register_tool_commands(category_app, tool)
        
        app.add_typer(category_app, name=category)
