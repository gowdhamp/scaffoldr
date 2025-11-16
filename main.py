#!/opt/quark/bin/python
"""
Main entry point for the Scaffoldr CLI application.

This script initializes the Typer application and registers all the command
groups (subcommands) from the 'core' modules.
"""

from typing import Optional

from typer import Typer, Exit, Option, Context
from rich.console import Console

from core import backup

# --- Constants ---
APP_NAME = "Scaffoldr"
__version__ = "1.0.0"

# --- Initial Setup ---
console = Console()
app = Typer(
    name=APP_NAME,
    help="A CLI tool to quickly scaffold configuration files for DevOps tools.",
    add_completion=False,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)

# --- Helper Functions ---


def _version_callback(value: bool):
    """Callback function to display the application version and exit."""
    if value:
        console.print(
            f"[bold green]{APP_NAME}[/bold green] version [cyan]{__version__}[/cyan]"
        )
        raise Exit()


# --- Main Application ---


@app.callback(invoke_without_command=True)
def main(
    ctx: Context,
    version: Optional[bool] = Option(
        None,
        "--version",
        "-v",
        help="Show the application version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
):
    """Scaffoldr: Your friendly configuration file generator."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise Exit(0)


# --- Command Registration ---


def register_commands():
    """Registers all command groups (subcommands) to the main Typer app."""
    backup.register_cli(app)


# --- Execution ---

if __name__ == "__main__":
    register_commands()
    app()
