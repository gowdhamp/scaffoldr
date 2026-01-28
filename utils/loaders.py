import os
import tomllib
from typing import Dict, Any
from yaml import safe_load, YAMLError
from rich.console import Console

console = Console()

def load_yaml(file_path: str) -> Dict[str, Any]:
    """
    Loads a YAML file with error handling.
    
    Args:
        file_path: Absolute path to the YAML file.
        
    Returns:
        Dictionary of data or empty dict if error.
    """
    try:
        with open(file_path, "r") as f:
            return safe_load(f)
    except FileNotFoundError:
        console.print(f"[red]Error: File not found at: {file_path}[/red]")
    except YAMLError:
        console.print(f"[red]Error: Could not parse YAML file: {file_path}[/red]")
    except Exception as e:
        console.print(f"[red]Unexpected error loading YAML: {e}[/red]")
    return {}

def load_toml(file_path: str) -> Dict[str, Any]:
    """
    Loads a TOML file with error handling.
    
    Args:
        file_path: path to the TOML file.
        
    Returns:
        Dictionary of data or empty dict if error.
    """
    if not file_path or not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "rb") as f:
            return tomllib.load(f)
    except Exception:
        # Silently fail for config files to avoid breaking the tool
        return {}
