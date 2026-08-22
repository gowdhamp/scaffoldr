"""Self-upgrade: replaces the running Scaffoldr binary with a GitHub Release build."""

import os
import platform
import shutil
import sys
import tempfile
import urllib.request

from rich.console import Console

from utils.github_release import ReleaseLookupError, fetch_release, pick_asset
from utils.version import VERSION

console = Console()


def _asset_name() -> str:
    """Maps the running platform to its release asset filename."""
    if sys.platform != "linux":
        console.print("[red]Self-upgrade currently only supports Linux binaries.[/red]")
        raise SystemExit(1)

    arch = "arm64" if platform.machine().lower() in ("aarch64", "arm64") else "x86_64"
    return f"scaffoldr-linux-{arch}"


def _download(url: str) -> str:
    """Downloads a release asset to a temp file and returns its path."""
    request = urllib.request.Request(url, headers={"User-Agent": "scaffoldr-upgrade"})
    fd, path = tempfile.mkstemp(prefix="scaffoldr-upgrade-")

    with (
        os.fdopen(fd, "wb") as out,
        urllib.request.urlopen(request, timeout=60) as response,
    ):
        shutil.copyfileobj(response, out)

    os.chmod(path, 0o755)
    return path


def _replace_binary(new_path: str) -> None:
    """Atomically replaces the running binary with the newly downloaded one."""
    current_path = sys.executable

    try:
        os.replace(new_path, current_path)
    except PermissionError as e:
        os.remove(new_path)
        console.print(
            f"[red]Permission denied writing to '{current_path}'. "
            "Try running with sudo.[/red]"
        )
        raise SystemExit(1) from e


def run_upgrade(version: str | None, dry_run: bool) -> None:
    """Downloads and installs a Scaffoldr release binary, or previews the action."""
    if not getattr(sys, "frozen", False):
        console.print(
            "[yellow]Running from source — self-upgrade only applies to the packaged "
            "binary. Use 'git pull' to update instead.[/yellow]"
        )
        return

    asset_name = _asset_name()

    try:
        release = fetch_release(version)
        target_version = release["tag_name"].lstrip("v")

        if target_version == VERSION:
            console.print(f"[green]Already on version v{VERSION}.[/green]")
            return

        if dry_run:
            console.print(
                f"[cyan]Would upgrade v{VERSION} -> v{target_version} ({asset_name}).[/cyan]"
            )
            return

        asset = pick_asset(release, asset_name)
    except ReleaseLookupError as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1) from e

    console.print(f"Downloading v{target_version}...")
    new_path = _download(asset["browser_download_url"])
    _replace_binary(new_path)
    console.print(f"[bold green]Upgraded to v{target_version}.[/bold green]")
