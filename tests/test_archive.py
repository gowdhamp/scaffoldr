import bz2
import os
import tarfile

import pytest

from utils.archive import cleanup_extraction, extract_binary


def test_extract_binary_raw_passes_through(tmp_path):
    raw = tmp_path / "tool"
    raw.write_bytes(b"binary-content")

    assert extract_binary(str(raw), "raw", "tool") == str(raw)


def test_extract_binary_bz2(tmp_path):
    archive = tmp_path / "tool.bz2"
    archive.write_bytes(bz2.compress(b"binary-content"))

    out_path = extract_binary(str(archive), "bz2", "tool")

    assert out_path == str(archive) + ".out"
    with open(out_path, "rb") as f:
        assert f.read() == b"binary-content"


@pytest.mark.parametrize(
    "archive_type,tar_mode", [("tar.gz", "w:gz"), ("tar.bz2", "w:bz2")]
)
def test_extract_binary_tar(tmp_path, archive_type, tar_mode):
    payload_dir = tmp_path / "payload"
    payload_dir.mkdir()
    binary = payload_dir / "tool"
    binary.write_bytes(b"binary-content")

    archive = tmp_path / f"tool.{archive_type.split('.')[1]}"
    with tarfile.open(archive, tar_mode) as tar:
        tar.add(binary, arcname="tool")

    out_path = extract_binary(str(archive), archive_type, "tool")

    assert os.path.basename(out_path) == "tool"
    with open(out_path, "rb") as f:
        assert f.read() == b"binary-content"
    # Extraction happens next to the archive (same filesystem as the caller's install target)
    assert os.path.dirname(out_path).startswith(str(tmp_path))


def test_extract_binary_tar_missing_binary_raises(tmp_path):
    other = tmp_path / "other-file"
    other.write_bytes(b"not-the-binary")

    archive = tmp_path / "tool.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(other, arcname="other-file")

    with pytest.raises(ValueError, match="Could not find"):
        extract_binary(str(archive), "tar.gz", "tool")


def test_extract_binary_unsupported_type_raises(tmp_path):
    with pytest.raises(ValueError, match="Unsupported archive type"):
        extract_binary(str(tmp_path / "x"), "zip", "tool")


def test_cleanup_extraction_raw_noop(tmp_path):
    downloaded = tmp_path / "tool"
    downloaded.write_bytes(b"x")

    # For "raw", binary_path == downloaded and the file has already been moved
    # out by the caller's os.replace(), so nothing should be touched here.
    cleanup_extraction(str(downloaded), str(downloaded), str(tmp_path))


def test_cleanup_extraction_bz2_removes_raw_download(tmp_path):
    downloaded = tmp_path / "tool.bz2"
    downloaded.write_bytes(b"x")
    binary_path = str(downloaded) + ".out"  # already moved out by the caller

    cleanup_extraction(str(downloaded), binary_path, str(tmp_path))

    assert not downloaded.exists()


def test_cleanup_extraction_tar_removes_archive_and_extract_dir(tmp_path):
    downloaded = tmp_path / "tool.tar.gz"
    downloaded.write_bytes(b"x")
    extract_dir = tmp_path / "extracted"
    extract_dir.mkdir()
    (extract_dir / "leftover-sibling-file").write_bytes(b"y")

    cleanup_extraction(str(downloaded), str(extract_dir / "tool"), str(tmp_path))

    assert not downloaded.exists()
    assert not extract_dir.exists()
