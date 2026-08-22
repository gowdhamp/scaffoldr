import os
from typing import Any

from .loaders import load_toml


def get_global_config() -> dict[str, Any]:
    """
    Loads global configuration from ~/.scaffoldr (TOML format).

    Returns:
        Dictionary containing the parsed TOML data.
    """
    config_path = os.path.expanduser("~/.scaffoldr")
    return load_toml(config_path)


def get_tool_defaults(tool_name: str) -> dict[str, Any]:
    """
    Retrieves the configuration section for a specific tool from the global config.

    Args:
        tool_name: Name of the tool (e.g., 'borgmatic').

    Returns:
        A dictionary of default values for the tool, or an empty dict.
    """
    config = get_global_config()
    return config.get(tool_name.lower(), {})
