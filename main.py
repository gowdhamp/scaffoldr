#!/usr/bin/env python3
"""
Main entry point for the Scaffoldr CLI application.

Scaffoldr is a fast and simple CLI tool for instantly generating configuration
files and boilerplates for your favorite DevOps and infrastructure tools.
"""

from typing import Optional
from typer import Typer, Exit, Option, Context
from rich.console import Console
from core import discovery

# --- Meta-data ---
APP_NAME = "Scaffoldr"
VERSION = "1.1.1"

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
    version: Optional[bool] = Option(
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
    pass


def register_cli_commands():
    """Registers dynamic subcommands based on the tools discovery engine."""
    discovery.register_dynamic_commands(app)


if __name__ == "__main__":
    # TODO: Implement a system-wide log level setting via global flag.
    register_cli_commands()
    app()
