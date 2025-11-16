import os
from typer import Typer, Exit
from rich.console import Console
from rich.prompt import Prompt
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from utils.prompt_utils import prompt_for_config, load_prompts_from_yaml

console = Console()
app = Typer(help="Scaffold backup configurations for various tools.")

CONFIG_WIZARD_TITLE = "Scaffoldr - {tool_name} Configuration Wizard"


def _create_config_flow(tool_name: str, default_filename: str):
    """Generic function to handle the interactive configuration creation process."""
    try:
        prompt_file_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "definitions",
            "backup",
            tool_name.lower(),
            f"{tool_name.lower()}.yaml",
        )
        prompts = load_prompts_from_yaml(prompt_file_path)
        if not prompts:
            raise Exit(1)  # Exit if prompts failed to load

        heading = prompts.get("heading", {})
        console.print(
            f"\n[bold italic]{heading.get('title', CONFIG_WIZARD_TITLE.format(tool_name=tool_name.title()))}[/bold italic]"
        )

        config_data = prompt_for_config(heading)
        if not config_data:
            console.print("\n[yellow]Configuration cancelled.[/yellow]")
            return

        output_path = Prompt.ask("\nOutput file path", default=default_filename)

        if os.path.exists(output_path):
            if (
                not Prompt.ask(
                    f"[red]File '{output_path}' already exists. Overwrite?[/red]",
                    choices=["y", "n"],
                    default="n",
                )
                == "y"
            ):
                console.print("\n[yellow]Operation cancelled by user.[/yellow]")
                return

        # Add additional context for the template
        now = datetime.now()
        config_data["generation_timestamp"] = now.strftime("%Y-%m-%d %H:%M:%S")
        config_data["now"] = now
        config_data["output_path"] = output_path

        # Determine the correct encryption argument for borg init command
        if not config_data.get("encryption_passphrase"):
            config_data["encryption_arg"] = "--encryption=none"
        else:
            config_data["encryption_arg"] = (
                f"--encryption='{config_data['encryption_passphrase']}'"
            )

        template_dir = os.path.dirname(prompt_file_path)
        env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
        template = env.get_template(f"{tool_name.lower()}.yaml.j2")
        rendered_config = template.render(**config_data)

        with open(output_path, "w") as f:
            f.write(rendered_config)

        after_section = heading.get("after", {})
        success_message = after_section.get("logs", {}).get(
            "success", "Successfully created configuration file."
        )
        console.print(
            f"\n[green]{success_message.format(output_path=output_path)}[/green]"
        )

        for note in after_section.get("notes", []):
            console.print(f"\n[bold]Note:[/bold] {note.format(**config_data)}")

    except FileNotFoundError:
        console.print(
            f"[red]Error: Definition files for '{tool_name}' are missing.[/red]"
        )
    except Exception as e:
        error_message = (
            heading.get("after", {})
            .get("logs", {})
            .get("error", "An unexpected error occurred: {e}")
        )
        console.print(f"\n[red]{error_message.format(e=e)}[/red]")


@app.command(name="create-borgmatic")
def create_borgmatic_config():
    """Interactively creates a borgmatic.yaml file."""
    _create_config_flow("borgmatic", "borgmatic.yaml")


@app.command(name="create-autorestic")
def create_autorestic_config():
    """Interactively creates an autorestic.yml file."""
    _create_config_flow("autorestic", "autorestic.yml")


def register_cli(parent_app: Typer):
    """Register the backup command with the parent Typer app."""
    parent_app.add_typer(app, name="backup")
