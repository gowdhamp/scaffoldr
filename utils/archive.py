"""Extracts a downloaded release asset into a raw, executable binary file."""

import bz2
import os
import shutil
import tarfile
import tempfile


def extract_binary(archive_path: str, archive_type: str, binary_name: str) -> str:
    """
    Extracts (or passes through) a downloaded asset and returns the path to the
    raw executable it contains.

    Args:
        archive_path: Path to the downloaded asset.
        archive_type: One of 'raw', 'bz2', 'tar.gz', 'tar.bz2'.
        binary_name: Filename of the executable inside a tar archive.

    Returns:
        Path to the extracted (or original) raw binary file.
    """
    if archive_type == "raw":
        return archive_path

    if archive_type == "bz2":
        out_path = archive_path + ".out"
        with bz2.open(archive_path, "rb") as src, open(out_path, "wb") as dst:
            shutil.copyfileobj(src, dst)
        return out_path

    if archive_type in ("tar.gz", "tar.bz2"):
        mode = "r:gz" if archive_type == "tar.gz" else "r:bz2"
        # Extract next to archive_path so the result stays on the same filesystem
        # as the final install target, keeping the caller's os.replace() atomic.
        extract_dir = tempfile.mkdtemp(
            prefix="scaffoldr-install-", dir=os.path.dirname(archive_path)
        )
        with tarfile.open(archive_path, mode) as tar:
            tar.extractall(extract_dir, filter="data")
        for root, _, files in os.walk(extract_dir):
            if binary_name in files:
                return os.path.join(root, binary_name)
        raise ValueError(f"Could not find '{binary_name}' inside {archive_path}.")

    raise ValueError(f"Unsupported archive type: '{archive_type}'.")


def cleanup_extraction(downloaded: str, binary_path: str, install_dir: str) -> None:
    """Removes the raw download and any extraction directory left behind in install_dir."""
    if binary_path != downloaded:
        extract_dir = os.path.dirname(binary_path)
        if extract_dir != install_dir:
            shutil.rmtree(extract_dir, ignore_errors=True)
    if os.path.exists(downloaded):
        os.remove(downloaded)
