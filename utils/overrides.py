"""Builds and validates a merged overrides dict from --values files and --set flags."""

import os
import re
from typing import Any

from rich.console import Console

from .loaders import load_toml, load_yaml

console = Console()


def split_csv(value: Any) -> Any:
    """Splits a comma-separated string into a stripped list; passes other types through."""
    if isinstance(value, str):
        return [i.strip() for i in value.split(",") if i.strip()]
    return value


def apply_override(p: dict[str, Any], value: Any) -> tuple[bool, Any]:
    """Validates and normalizes an override value against a prompt's rules."""
    if p.get("is_list"):
        value = split_csv(value)

    if p.get("required") and not value:
        return False, value
    if p.get("regex") and value and not re.match(p["regex"], str(value)):
        return False, value
    choices = p.get("choices")
    if choices and value not in choices:
        return False, value

    return True, value


def _load_values_file(path: str) -> dict[str, Any]:
    """Loads a values file, dispatching on its extension (YAML or TOML)."""
    ext = os.path.splitext(path)[1].lower()

    if ext in (".yaml", ".yml"):
        return load_yaml(path) or {}
    if ext == ".toml":
        return load_toml(path)

    console.print(
        f"[red]Unsupported values file extension: '{ext}'. Use .yaml or .toml.[/red]"
    )
    return {}


def build_overrides(values_path: str | None, set_flags: list[str]) -> dict[str, Any]:
    """
    Merges a --values file with repeated --set key=value flags.

    Inline --set flags take precedence over the values file.

    Args:
        values_path: Path to a YAML/TOML file of pre-filled answers, or None.
        set_flags: Repeated "key=value" strings from --set.

    Returns:
        Merged dict of field overrides.
    """
    overrides: dict[str, Any] = {}

    if values_path:
        if not os.path.exists(values_path):
            console.print(f"[red]Values file not found: '{values_path}'[/red]")
        else:
            overrides.update(_load_values_file(values_path))

    for item in set_flags:
        if "=" not in item:
            console.print(
                f"[red]Ignoring malformed --set value (expected key=value): '{item}'[/red]"
            )
            continue
        key, _, value = item.partition("=")
        overrides[key.strip()] = value.strip()

    return overrides
