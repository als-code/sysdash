import os
import shutil
from dataclasses import dataclass


@dataclass(frozen=True)
class PackageManager:
    name: str
    install_cmd: list[str]


def sudo_wrap(cmd: list[str]) -> list[str]:
    return cmd if os.geteuid() == 0 else ["sudo", *cmd]


def detect_package_manager() -> PackageManager | None:
    if shutil.which("nala"):
        return PackageManager("nala", sudo_wrap(["nala", "install", "-y"]))
    if shutil.which("apt"):
        return PackageManager("apt", sudo_wrap(["apt", "install", "-y"]))
    if shutil.which("dnf"):
        return PackageManager("dnf", sudo_wrap(["dnf", "install", "-y"]))
    if shutil.which("pacman"):
        return PackageManager("pacman", sudo_wrap(["pacman", "-S", "--noconfirm"]))
    return None
