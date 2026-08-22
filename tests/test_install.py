import pytest

from core import install
from utils import tool_install


def _config(**overrides):
    config = {
        "repo": "someone/sometool",
        "tag_prefix": "v",
        "binary_name": "sometool",
        "archive": "raw",
        "assets": {
            "x86_64": "sometool-{version}-x86_64",
            "arm64": "sometool-{version}-arm64",
        },
    }
    config.update(overrides)
    return config


@pytest.fixture
def install_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(install, "INSTALL_DIR", str(tmp_path))
    monkeypatch.setattr(tool_install, "INSTALL_DIR", str(tmp_path))
    monkeypatch.setattr(install, "detect_arch", lambda: "x86_64")
    return tmp_path


def _fake_release(tag: str) -> dict:
    return {
        "tag_name": tag,
        "assets": [
            {
                "name": "sometool-9.9.9-x86_64",
                "browser_download_url": "https://example.test/asset",
            }
        ],
    }


def test_already_installed_skips(install_dir, monkeypatch, capsys):
    monkeypatch.setattr(install, "load_installer", lambda tool: _config())
    monkeypatch.setattr(
        install, "fetch_release", lambda repo, v, tp: _fake_release("v9.9.9")
    )
    monkeypatch.setattr(install, "installed_version", lambda tool: "9.9.9")
    monkeypatch.setattr(
        install, "_download", lambda url: pytest.fail("should not download")
    )

    install.run_install("sometool", None)

    assert "already at version 9.9.9" in capsys.readouterr().out


def test_installs_raw_binary(install_dir, monkeypatch, capsys):
    downloaded = install_dir / "downloaded"
    downloaded.write_bytes(b"raw-binary")

    monkeypatch.setattr(install, "load_installer", lambda tool: _config())
    monkeypatch.setattr(
        install, "fetch_release", lambda repo, v, tp: _fake_release("v9.9.9")
    )
    monkeypatch.setattr(install, "installed_version", lambda tool: None)
    monkeypatch.setattr(install, "_download", lambda url: str(downloaded))

    install.run_install("sometool", None)

    dest = install_dir / "sometool"
    assert dest.read_bytes() == b"raw-binary"
    assert (install_dir / ".sometool.scaffoldr-version").read_text() == "9.9.9"
    assert "Installed sometool 9.9.9" in capsys.readouterr().out


def test_no_asset_for_arch_exits(install_dir, monkeypatch):
    monkeypatch.setattr(install, "load_installer", lambda tool: _config(assets={}))

    with pytest.raises(SystemExit):
        install.run_install("sometool", None)


def test_missing_release_exits(install_dir, monkeypatch, capsys):
    def _raise(repo, version, tag_prefix):
        raise install.ReleaseLookupError(f"No release found for version '{version}'.")

    monkeypatch.setattr(install, "load_installer", lambda tool: _config())
    monkeypatch.setattr(install, "fetch_release", _raise)

    with pytest.raises(SystemExit) as exc_info:
        install.run_install("sometool", "9.9.9")

    assert exc_info.value.code == 1
    assert "No release found" in capsys.readouterr().out
