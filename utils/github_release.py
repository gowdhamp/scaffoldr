"""Minimal GitHub Releases API client used by the self-upgrade command."""

import json
import urllib.error
import urllib.request
from typing import Any

from utils.version import GITHUB_REPO

API_BASE = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
USER_AGENT = "scaffoldr-upgrade"


class ReleaseLookupError(Exception):
    """Raised when release metadata or a matching asset cannot be found."""


def fetch_release(version: str | None) -> dict[str, Any]:
    """
    Fetches release metadata from GitHub for the latest or a specific version.

    Args:
        version: Semver tag without the 'v' prefix, or None for the latest release.

    Returns:
        Parsed JSON payload for the release.
    """
    url = (
        f"{API_BASE}/latest"
        if not version
        else f"{API_BASE}/tags/v{version.lstrip('v')}"
    )
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ReleaseLookupError(
                f"No release found for version '{version}'."
            ) from e
        raise ReleaseLookupError(f"GitHub API error: {e.code} {e.reason}") from e
    except urllib.error.URLError as e:
        raise ReleaseLookupError(f"Could not reach GitHub: {e.reason}") from e


def pick_asset(release: dict[str, Any], asset_name: str) -> dict[str, Any]:
    """Finds the release asset matching the current platform's binary name."""
    for asset in release.get("assets", []):
        if asset.get("name") == asset_name:
            return asset

    raise ReleaseLookupError(
        f"Release '{release.get('tag_name')}' has no asset named '{asset_name}'."
    )
