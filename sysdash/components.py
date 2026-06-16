import json
import platform
import shutil
import tarfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from sysdash.constants import CORE_BINARIES, GPU_BINARY
from sysdash.gpu import has_gpu

INSTALL_DIR = Path.home() / ".local" / "bin"
GOTOP_REPO = "xxxserxxx/gotop"

ARCH_SUFFIX = {
    "x86_64": "linux_amd64",
    "aarch64": "linux_arm64",
    "armv7l": "linux_arm7",
}


@dataclass(frozen=True)
class Component:
    binary: str
    apt_package: str
    label: str


COMPONENTS = (
    Component("tmux", "tmux", "terminal multiplexer"),
    Component("gotop", "gotop", "process monitor"),
    Component("nvtop", "nvtop", "GPU monitor"),
)


def required_binaries() -> tuple[str, ...]:
    if has_gpu():
        return (*CORE_BINARIES, GPU_BINARY)
    return CORE_BINARIES


def resolve_binary(name: str) -> str:
    path = shutil.which(name)
    if path:
        return path
    local = INSTALL_DIR / name
    if local.exists():
        return str(local)
    return name


def is_installed(name: str) -> bool:
    if shutil.which(name):
        return True
    return name == "gotop" and (INSTALL_DIR / "gotop").exists()


def missing_components() -> list[Component]:
    needed = set(required_binaries())
    return [c for c in COMPONENTS if c.binary in needed and not is_installed(c.binary)]


def gotop_download_url() -> str | None:
    suffix = ARCH_SUFFIX.get(platform.machine())
    if suffix is None:
        return None

    try:
        with urllib.request.urlopen(
            f"https://api.github.com/repos/{GOTOP_REPO}/releases/latest",
            timeout=15,
        ) as response:
            release = json.loads(response.read().decode())
        for asset in release.get("assets", []):
            name = asset.get("name", "")
            if suffix in name and name.endswith(".tgz"):
                return asset["browser_download_url"]
    except (urllib.error.URLError, OSError, KeyError, json.JSONDecodeError):
        pass

    if suffix == "linux_amd64":
        return (
            "https://github.com/xxxserxxx/gotop/releases/download/"
            "v4.2.0/gotop_v4.2.0_linux_amd64.tgz"
        )
    return None


def extract_gotop_binary(archive: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as tar:
        member = next((m for m in tar.getmembers() if Path(m.name).name == "gotop"), None)
        if member is None:
            raise RuntimeError("gotop binary not found in archive")
        extracted = tar.extractfile(member)
        if extracted is None:
            raise RuntimeError("could not extract gotop binary")
        dest.write_bytes(extracted.read())
    dest.chmod(0o755)
