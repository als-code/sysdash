from pathlib import Path
from unittest.mock import patch

from sysdash.components import gotop_download_url, missing_components, required_binaries
from sysdash.gpu import has_gpu
from sysdash.install import detect_package_manager


def test_required_binaries_without_gpu():
    with patch("sysdash.components.has_gpu", return_value=False):
        assert required_binaries() == ("tmux", "gotop")


def test_required_binaries_with_gpu():
    with patch("sysdash.components.has_gpu", return_value=True):
        assert required_binaries() == ("tmux", "gotop", "nvtop")


def test_has_gpu_nvidia_device():
    def fake_exists(self: Path) -> bool:
        return str(self) == "/dev/nvidia0"

    with patch.object(Path, "exists", fake_exists):
        assert has_gpu() is True


def test_has_gpu_false():
    with (
        patch.object(Path, "exists", return_value=False),
        patch("shutil.which", return_value=None),
        patch.object(Path, "is_dir", return_value=False),
        patch.object(Path, "glob", return_value=[]),
    ):
        assert has_gpu() is False


def test_gotop_url_amd64():
    url = gotop_download_url()
    assert url is None or "gotop" in url


def test_detect_package_manager_apt():
    with patch("shutil.which", side_effect=lambda name: "/usr/bin/apt" if name == "apt" else None):
        pm = detect_package_manager()
        assert pm is not None
        assert pm.name == "apt"
        assert "sudo" in pm.install_cmd


def test_missing_skips_nvtop_without_gpu(monkeypatch):
    monkeypatch.setattr("sysdash.components.has_gpu", lambda: False)
    monkeypatch.setattr("sysdash.components.is_installed", lambda name: name == "tmux")
    missing = [c.binary for c in missing_components()]
    assert "nvtop" not in missing
    assert "gotop" in missing
