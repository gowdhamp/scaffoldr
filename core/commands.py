"""Builds the per-tool Typer sub-app (generate/list subcommands)."""

from typer import Context, Option, Typer

from core.engine import list_config_fields, run_config_flow


def register_tool_commands(category_app: Typer, tool_name: str):
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
    def generate(
        values: str | None = Option(
            None, "--values", help="Path to a YAML/TOML file with pre-filled answers."
        ),
        set_fields: list[str] | None = Option(  # noqa: B008 — Typer needs the call as the default
            None, "--set", help="Override a single field as key=value (repeatable)."
        ),
        yes: bool = Option(
            False, "--yes", "-y", help="Overwrite the output file without confirmation."
        ),
    ):
        """Generate a configuration file, interactively or from --values/--set."""
        run_config_flow(
            tool_name,
            f"{tool_name}.yaml",
            values_file=values,
            set_overrides=set_fields,
            assume_yes=yes,
        )

    # Subcommand: list
    def list_fields():
        """List all configuration fields and global defaults."""
        list_config_fields(tool_name)

    tool_app.command(name="generate")(generate)
    tool_app.command(name="list")(list_fields)

    category_app.add_typer(tool_app, name=tool_name)
