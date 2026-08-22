"""Minimal GitHub Releases API client shared by self-upgrade and tool installation."""

import json
import urllib.error
import urllib.request
from typing import Any

USER_AGENT = "scaffoldr-release-client"


class ReleaseLookupError(Exception):
    """Raised when release metadata or a matching asset cannot be found."""


def fetch_release(
    repo: str, version: str | None, tag_prefix: str = "v"
) -> dict[str, Any]:
    """
    Fetches release metadata from GitHub for the latest or a specific version.

    Args:
        repo: GitHub repo as 'owner/name'.
        version: Version string (with or without `tag_prefix`), or None for latest.
        tag_prefix: Prefix release tags use (e.g. 'v' for 'v1.2.3', '' for borg's '1.2.3').

    Returns:
        Parsed JSON payload for the release.
    """
    base = f"https://api.github.com/repos/{repo}/releases"
    if version:
        tag = tag_prefix + version.removeprefix(tag_prefix)
        url = f"{base}/tags/{tag}"
    else:
        url = f"{base}/latest"
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
    """Finds the release asset matching the given filename."""
    for asset in release.get("assets", []):
        if asset.get("name") == asset_name:
            return asset

    raise ReleaseLookupError(
        f"Release '{release.get('tag_name')}' has no asset named '{asset_name}'."
    )
