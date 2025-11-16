from rich.console import Console
from rich.prompt import Prompt
from typing import Dict, Any
from yaml import safe_load, YAMLError
from jinja2 import Environment

console = Console()
jinja_env = Environment()


def load_prompts_from_yaml(file_path: str) -> Dict[str, Any]:
    """Loads prompts from a YAML file with error handling.

    Args:
        file_path: The absolute path to the YAML file.

    Returns:
        A dictionary containing the loaded YAML data, or an empty dictionary if an error occurs.
    """
    try:
        with open(file_path, "r") as f:
            return safe_load(f)
    except FileNotFoundError:
        console.print(f"[red]Error: Prompt file not found at: {file_path}[/red]")
        return {}
    except YAMLError:
        console.print(f"[red]Error: Could not parse YAML file: {file_path}[/red]")
        return {}


def prompt_for_config(heading: Dict[str, Any]) -> Dict[str, Any]:
    """Prompts the user for configuration values based on a structured dictionary.

    This function iterates through sections and prompts defined in the input dictionary,
    collecting user input for each configuration key. It supports converting comma-separated
    input into lists if a prompt has `is_list: true`.

    Args:
        heading: A dictionary defining the prompt structure, including sections and prompts.

    Returns:
        A dictionary containing the user-provided configuration values.
    """
    config = {}
    if not heading:
        return config

    for section in heading.get("before", []):
        console.print(
            f"\n[italic underline blue]{section.get('title', 'Section')}[/italic underline blue]"
        )
        if "subtitle" in section:
            console.print(f"[dim]{section['subtitle']}[/dim]\n")

        for p in section.get("prompts", []):
            try:
                depends_on = p.get("depends_on")
                if depends_on:
                    dependency_key = depends_on.get("key")
                    dependency_value = depends_on.get("value")
                    if not (dependency_key and dependency_value):
                        # Invalid depends_on structure, skip prompt
                        continue
                    if config.get(dependency_key) != dependency_value:
                        # Condition not met, skip prompt
                        continue

                is_password = p.get("is_password", False)
                is_list = p.get("is_list", False)
                default = p.get("default")
                choices = p.get("choices")

                if default and isinstance(default, str) and "{{" in default:
                    try:
                        template = jinja_env.from_string(default)
                        default = template.render(config)
                    except Exception:
                        # If rendering fails, fall back to the raw string
                        pass

                value = Prompt.ask(
                    f"{p['prompt']}",
                    default=default,
                    password=is_password,
                    choices=choices,
                )

                if is_list:
                    # Split comma-separated string into a list, stripping whitespace
                    # and ignoring any empty strings that result from extra commas.
                    config[p["key"]] = (
                        [item.strip() for item in value.split(",") if item.strip()]
                        if value
                        else []
                    )
                else:
                    config[p["key"]] = value
            except KeyError:
                console.print(
                    "[yellow]Warning: Skipping a prompt due to a configuration error.[/yellow]"
                )
            except Exception:
                console.print(
                    "[red]An unexpected error occurred. Please check the configuration.[/red]"
                )

    return config
