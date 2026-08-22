import sys

import pytest

from core import upgrade


@pytest.fixture
def frozen(monkeypatch, tmp_path):
    """Simulates running as a packaged (PyInstaller) binary."""
    binary = tmp_path / "scaffoldr"
    binary.write_bytes(b"old-binary")
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(binary))
    return binary


def _fake_release(tag: str) -> dict:
    return {
        "tag_name": tag,
        "assets": [
            {
                "name": "scaffoldr-linux-x86_64",
                "browser_download_url": "https://example.test/asset",
            }
        ],
    }


def test_not_frozen_skips_upgrade(monkeypatch, capsys):
    monkeypatch.setattr(sys, "frozen", False, raising=False)

    upgrade.run_upgrade(None, dry_run=False)

    assert "self-upgrade only applies" in capsys.readouterr().out


def test_already_on_target_version(frozen, monkeypatch, capsys):
    monkeypatch.setattr(
        upgrade, "fetch_release", lambda v: _fake_release(f"v{upgrade.VERSION}")
    )

    upgrade.run_upgrade(None, dry_run=False)

    assert f"Already on version v{upgrade.VERSION}" in capsys.readouterr().out
    assert frozen.read_bytes() == b"old-binary"


def test_dry_run_previews_without_downloading(frozen, monkeypatch, capsys):
    monkeypatch.setattr(upgrade, "fetch_release", lambda v: _fake_release("v9.9.9"))
    monkeypatch.setattr(
        upgrade, "_download", lambda url: pytest.fail("should not download")
    )

    upgrade.run_upgrade(None, dry_run=True)

    out = capsys.readouterr().out
    assert "Would upgrade" in out
    assert "9.9.9" in out
    assert frozen.read_bytes() == b"old-binary"


def test_upgrade_replaces_binary(frozen, monkeypatch, tmp_path, capsys):
    downloaded = tmp_path / "downloaded"
    downloaded.write_bytes(b"new-binary")
    monkeypatch.setattr(upgrade, "fetch_release", lambda v: _fake_release("v9.9.9"))
    monkeypatch.setattr(upgrade, "_download", lambda url: str(downloaded))

    upgrade.run_upgrade(None, dry_run=False)

    assert frozen.read_bytes() == b"new-binary"
    assert "Upgraded to v9.9.9" in capsys.readouterr().out


def test_missing_release_exits_nonzero(frozen, monkeypatch):
    def _raise(_version):
        raise upgrade.ReleaseLookupError("No release found for version '9.9.9'.")

    monkeypatch.setattr(upgrade, "fetch_release", _raise)

    with pytest.raises(SystemExit) as exc_info:
        upgrade.run_upgrade("9.9.9", dry_run=False)

    assert exc_info.value.code == 1
