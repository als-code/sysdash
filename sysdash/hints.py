import shutil
import subprocess

from sysdash.components import COMPONENTS, gotop_download_url
from sysdash.paths import REPO_ROOT
from sysdash.pm import PackageManager, detect_package_manager, sudo_wrap


def apt_has_package(name: str) -> bool:
    return bool(shutil.which("apt-cache")) and subprocess.run(
        ["apt-cache", "show", name], capture_output=True
    ).returncode == 0


def _cmd(parts: list[str]) -> str:
    return " ".join(parts)


def pip_install_hint() -> str:
    return "./install.sh"


def install_hint(binary: str, pm: PackageManager | None = None) -> str:
    pm = pm or detect_package_manager()
    comp = next(c for c in COMPONENTS if c.binary == binary)

    if binary == "gotop":
        if pm and pm.name in ("nala", "apt") and apt_has_package(comp.apt_package):
            return _cmd([*pm.install_cmd, comp.apt_package])
        if shutil.which("snap"):
            return _cmd(sudo_wrap(["snap", "install", "gotop"]))
        if gotop_download_url():
            return "sysdash install"
        return "https://github.com/xxxserxxx/gotop/releases"

    if pm:
        return _cmd([*pm.install_cmd, comp.apt_package])

    return f"install {binary} manually, or run {REPO_ROOT / 'install.sh'}"
