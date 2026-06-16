import os
import platform
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from rich import box
from rich.panel import Panel

from sysdash.components import (
    COMPONENTS,
    INSTALL_DIR,
    extract_gotop_binary,
    gotop_download_url,
    is_installed,
    missing_components,
)
from sysdash.doctor import check_system
from sysdash.paths import REPO_ROOT, ensure_shell_path, install_cli_command
from sysdash.style import BORDER_STYLE, console, print_panel, status_table


@dataclass
class PackageManager:
    name: str
    install_cmd: list[str]


def _sudo(cmd: list[str], *, root: bool = True) -> list[str]:
    if not root or os.geteuid() == 0:
        return cmd
    return ["sudo", *cmd]


def detect_package_manager() -> PackageManager | None:
    if shutil.which("nala"):
        return PackageManager("nala", _sudo(["nala", "install", "-y"]))
    if shutil.which("apt"):
        return PackageManager("apt", _sudo(["apt", "install", "-y"]))
    if shutil.which("dnf"):
        return PackageManager("dnf", _sudo(["dnf", "install", "-y"]))
    if shutil.which("pacman"):
        return PackageManager("pacman", _sudo(["pacman", "-S", "--noconfirm"]))
    return None


def apt_has_package(name: str) -> bool:
    if not shutil.which("apt-cache"):
        return False
    return subprocess.run(["apt-cache", "show", name], capture_output=True).returncode == 0


def _audit_rows() -> list[tuple[str, bool, str]]:
    rows, _ = check_system()
    return rows


def _print_audit(title: str) -> None:
    console.print(
        Panel(
            status_table(_audit_rows()),
            title=title,
            border_style=BORDER_STYLE,
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )


def _run(cmd: list[str]) -> int:
    console.print(f"[dim]  $ {' '.join(cmd)}[/dim]")
    return subprocess.run(cmd).returncode


def _install_gotop_binary() -> bool:
    url = gotop_download_url()
    if not url:
        console.print(f"[yellow]  no gotop build for {platform.machine()}[/yellow]")
        return False

    dest = INSTALL_DIR / "gotop"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "gotop.tgz"
            urllib.request.urlretrieve(url, archive)
            extract_gotop_binary(archive, dest)
    except (OSError, RuntimeError, urllib.error.URLError) as err:
        console.print(f"[red]  download failed: {err}[/red]")
        return False

    console.print(f"[green]  installed {dest}[/green]")
    return dest.exists()


def _install_one(pm: PackageManager | None, binary: str) -> bool:
    comp = next(c for c in COMPONENTS if c.binary == binary)

    if is_installed(binary):
        console.print(f"[green]✓[/green] {binary}")
        return True

    console.print(f"\n[bold]→ {binary}[/bold]  [dim]{comp.label}[/dim]")

    if pm and apt_has_package(comp.apt_package):
        if _run([*pm.install_cmd, comp.apt_package]) == 0 and is_installed(binary):
            return True

    if binary == "gotop":
        if shutil.which("snap") and _run(_sudo(["snap", "install", "gotop"])) == 0:
            if is_installed(binary):
                return True
        if _install_gotop_binary() and is_installed(binary):
            return True

    if pm and pm.name not in ("nala", "apt"):
        if _run([*pm.install_cmd, comp.apt_package]) == 0 and is_installed(binary):
            return True

    console.print(f"[red]✗[/red] {binary}")
    return False


def _link_command() -> None:
    shim, in_path = install_cli_command()
    (REPO_ROOT / "bin" / "sysdash").chmod(0o755)
    if in_path:
        print_panel(f"[bold]sysdash[/bold] → {shim}", "Command")
    elif ensure_shell_path():
        print_panel(f"[bold]sysdash[/bold] → {shim}\n\nReload shell: [bold]source ~/.zshrc[/bold]", "Command")
    else:
        print_panel(f"{shim}\n\nexport PATH=\"$HOME/.local/bin:$PATH\"", "Command")


def install_packages() -> int:
    console.print()
    _print_audit("Status")

    missing = missing_components()
    pm = detect_package_manager()

    if not missing:
        _link_command()
        print_panel("Nothing to install.", "Install")
        return 0

    if pm is None:
        manual = ", ".join(c.binary for c in missing)
        print_panel(f"No package manager found.\nInstall manually: {manual}", "Install")
        return 1

    console.print(f"\n[bold]Missing:[/bold] {', '.join(c.binary for c in missing)}\n")

    failed = [b for b in (c.binary for c in missing) if not _install_one(pm, b)]

    console.print()
    _print_audit("Result")

    if failed:
        hint = ""
        if "gotop" in failed:
            hint = "\n\ngotop: try [bold]sudo snap install gotop[/bold]"
        print_panel("Failed:\n" + "\n".join(f"  • {b}" for b in failed) + hint, "Install")
        return 1

    rows, ok = check_system()
    if not ok:
        return 1

    _link_command()
    print_panel("System packages installed.", "Install")
    return 0
