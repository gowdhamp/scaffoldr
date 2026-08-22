"""Installs upstream backup tool binaries (borg, restic, autorestic, ...) from
their own GitHub releases — the install-side counterpart to core.upgrade."""

import os
import shutil
import tempfile
import urllib.request

from rich.console import Console

from utils.archive import cleanup_extraction, extract_binary
from utils.github_release import ReleaseLookupError, fetch_release, pick_asset
from utils.tool_install import (
    INSTALL_DIR,
    detect_arch,
    installed_version,
    load_installer,
    marker_path,
)

console = Console()
USER_AGENT = "scaffoldr-install"


def _download(url: str) -> str:
    """
    Downloads a release asset into a temp file inside INSTALL_DIR, so the later
    os.replace() lands on the same filesystem and stays atomic.
    """
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        fd, path = tempfile.mkstemp(prefix=".scaffoldr-install-", dir=INSTALL_DIR)
    except OSError as e:
        console.print(
            f"[red]Cannot write to '{INSTALL_DIR}': {e.strerror}. Try running with sudo.[/red]"
        )
        raise SystemExit(1) from e

    with (
        os.fdopen(fd, "wb") as out,
        urllib.request.urlopen(request, timeout=60) as response,
    ):
        shutil.copyfileobj(response, out)

    return path


def _install_binary(binary_path: str, tool_name: str, version: str) -> None:
    """Chmods and atomically installs the binary, recording the installed version."""
    dest = os.path.join(INSTALL_DIR, tool_name)
    os.chmod(binary_path, 0o755)
    os.replace(binary_path, dest)
    marker_path(tool_name).write_text(version)


def run_install(tool_name: str, version: str | None) -> None:
    """Downloads and installs an upstream tool binary, or confirms it's already current."""
    config = load_installer(tool_name)
    arch = detect_arch()
    tag_prefix = config.get("tag_prefix", "v")

    asset_template = config["assets"].get(arch)
    if not asset_template:
        console.print(f"[red]No '{arch}' build available for '{tool_name}'.[/red]")
        raise SystemExit(1)

    try:
        release = fetch_release(config["repo"], version, tag_prefix)
        target_version = release["tag_name"].removeprefix(tag_prefix)

        if installed_version(tool_name) == target_version:
            console.print(
                f"[green]{tool_name} is already at version {target_version}.[/green]"
            )
            return

        asset_name = asset_template.format(version=target_version)
        asset = pick_asset(release, asset_name)
    except ReleaseLookupError as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1) from e

    console.print(f"Downloading {tool_name} {target_version}...")
    downloaded = _download(asset["browser_download_url"])
    binary_path = extract_binary(downloaded, config["archive"], config["binary_name"])
    _install_binary(binary_path, tool_name, target_version)
    cleanup_extraction(downloaded, binary_path, INSTALL_DIR)
    console.print(
        f"[bold green]Installed {tool_name} {target_version} to {INSTALL_DIR}.[/bold green]"
    )
