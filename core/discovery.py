import os

from typer import Typer

from core.commands import register_tool_commands
from core.engine import get_resource_path

# TODO: Add caching for discovered tools if configuration directory becomes very large.


def discover_tools() -> dict[str, list[str]]:
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


def register_dynamic_commands(app: Typer):
    """
    Dynamically builds the CLI command hierarchy based on tool definitions.
    """
    tool_mapping = discover_tools()

    for category, tools in sorted(tool_mapping.items()):
        # Each category gets its own Typer sub-app
        category_app = Typer(
            help=f"Scaffolding for {category} tools.", no_args_is_help=True
        )

        for tool in tools:
            register_tool_commands(category_app, tool)

        app.add_typer(category_app, name=category)
