import sys

import pytest

from utils import tool_install


def test_load_installer_reads_yaml(monkeypatch, tmp_path):
    installers_dir = tmp_path / "installers"
    installers_dir.mkdir()
    (installers_dir / "sometool.yaml").write_text(
        "repo: someone/sometool\narchive: raw\n"
    )
    monkeypatch.setattr(
        tool_install, "get_resource_path", lambda name: str(tmp_path / name)
    )

    config = tool_install.load_installer("sometool")

    assert config == {"repo": "someone/sometool", "archive": "raw"}


def test_load_installer_unknown_tool_exits(monkeypatch, tmp_path):
    monkeypatch.setattr(
        tool_install, "get_resource_path", lambda name: str(tmp_path / name)
    )

    with pytest.raises(SystemExit) as exc_info:
        tool_install.load_installer("unknown-tool")

    assert exc_info.value.code == 1


def test_detect_arch_maps_machine(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(tool_install.platform, "machine", lambda: "aarch64")
    assert tool_install.detect_arch() == "arm64"

    monkeypatch.setattr(tool_install.platform, "machine", lambda: "x86_64")
    assert tool_install.detect_arch() == "x86_64"


def test_detect_arch_rejects_non_linux(monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")

    with pytest.raises(SystemExit):
        tool_install.detect_arch()


def test_installed_version_roundtrip(monkeypatch, tmp_path):
    monkeypatch.setattr(tool_install, "INSTALL_DIR", str(tmp_path))

    assert tool_install.installed_version("restic") is None

    tool_install.marker_path("restic").write_text("1.2.3")

    assert tool_install.installed_version("restic") == "1.2.3"
