"""Loads install metadata and tracks what scaffoldr has already installed."""

import os
import platform
import sys
from pathlib import Path
from typing import Any

from rich.console import Console

from core.engine.paths import get_resource_path
from utils.loaders import load_yaml

console = Console()
INSTALL_DIR = "/usr/local/bin"


def load_installer(tool_name: str) -> dict[str, Any]:
    """Loads a tool's install metadata, or exits if the tool isn't supported."""
    path = os.path.join(get_resource_path("installers"), f"{tool_name.lower()}.yaml")
    if not os.path.exists(path):
        console.print(
            f"[red]No install metadata for '{tool_name}'. "
            "See the 'installers/' directory for supported tools.[/red]"
        )
        raise SystemExit(1)
    return load_yaml(path)


def detect_arch() -> str:
    """Maps the running platform to an asset-name architecture key."""
    if sys.platform != "linux":
        console.print("[red]scaffoldr install currently only supports Linux.[/red]")
        raise SystemExit(1)
    return "arm64" if platform.machine().lower() in ("aarch64", "arm64") else "x86_64"


def marker_path(tool_name: str) -> Path:
    """Sidecar file scaffoldr uses to remember which version it installed."""
    return Path(INSTALL_DIR) / f".{tool_name}.scaffoldr-version"


def installed_version(tool_name: str) -> str | None:
    """Reads the version scaffoldr last installed for a tool, if any."""
    marker = marker_path(tool_name)
    return marker.read_text().strip() if marker.exists() else None
