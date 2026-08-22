#!/usr/bin/env python3
"""
Main entry point for the Scaffoldr CLI application.

Scaffoldr is a fast and simple CLI tool for instantly generating configuration
files and boilerplates for your favorite DevOps and infrastructure tools.
"""

from rich.console import Console
from typer import Context, Exit, Option, Typer

from core import discovery
from core.upgrade import run_upgrade
from utils.version import APP_NAME, VERSION

# --- Globals ---
console = Console()

# --- App Definition ---
app = Typer(
    name=APP_NAME,
    help="[bold cyan]Scaffoldr[/bold cyan]: Your friendly configuration file generator.",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def _version_callback(value: bool):
    """Prints the version number and exits if the flag is set."""
    if value:
        console.print(f"[bold green]{APP_NAME}[/bold green] v[cyan]{VERSION}[/cyan]")
        raise Exit()


@app.callback(invoke_without_command=True)
def root_callback(
    ctx: Context,
    version: bool | None = Option(
        None,
        "--version",
        "-v",
        help="Show version information and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
):
    """
    Welcome to Scaffoldr! Use the subcommands below to start scaffolding.
    """
    # no_args_is_help=True takes care of showing the help screen.


@app.command(name="upgrade")
def upgrade_command(
    version: str | None = Option(
        None,
        "--version",
        "-v",
        help="Specific version to install (defaults to latest).",
    ),
    dry_run: bool = Option(
        False, "--dry-run", help="Show what would be installed without applying it."
    ),
):
    """Download and install the latest (or a specific) Scaffoldr release binary."""
    run_upgrade(version, dry_run)


def register_cli_commands():
    """Registers dynamic subcommands based on the tools discovery engine."""
    discovery.register_dynamic_commands(app)


if __name__ == "__main__":
    # TODO: Implement a system-wide log level setting via global flag.
    register_cli_commands()
    app()
