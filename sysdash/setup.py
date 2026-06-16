import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

from rich import box
from rich.panel import Panel

from sysdash import __version__
from sysdash.doctor import run_doctor
from sysdash.install import install_packages
from sysdash.paths import REPO_ROOT
from sysdash.style import BORDER, console, print_panel, step

VENV = REPO_ROOT / ".venv"
PY = VENV / "bin" / "python"
PIP = VENV / "bin" / "pip"


def _run(cmd: list[str], quiet: bool = False) -> int:
    if not quiet:
        console.print(f"[dim]  $ {' '.join(cmd)}[/dim]")
    return subprocess.run(cmd, capture_output=quiet, text=quiet).returncode


def _install_python_venv_pkg() -> bool:
    ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    for pkg in (f"python{ver}-venv", "python3-venv"):
        if shutil.which("nala") and _run(["sudo", "nala", "install", "-y", pkg]) == 0:
            return True
        if shutil.which("apt") and _run(["sudo", "apt", "install", "-y", pkg]) == 0:
            return True
    if shutil.which("dnf") and _run(["sudo", "dnf", "install", "-y", "python3-venv"]) == 0:
        return True
    if shutil.which("pacman") and _run(["sudo", "pacman", "-S", "--noconfirm", "python"]) == 0:
        return True
    return False


def ensure_venv() -> bool:
    step("Python", str(sys.version))

    if PY.exists() and PIP.exists():
        step("venv", "ok", ok=True)
        return True

    if VENV.exists():
        shutil.rmtree(VENV)

    step("venv", "creating…")
    if _run([sys.executable, "-m", "venv", str(VENV)]) == 0:
        step("venv", str(VENV), ok=True)
        return True

    if not _install_python_venv_pkg():
        step("venv", "need python3-venv", ok=False)
        return False

    if _run([sys.executable, "-m", "venv", str(VENV)]) != 0:
        step("venv", "failed", ok=False)
        return False

    step("venv", str(VENV), ok=True)
    return True


def ensure_pip() -> bool:
    if _run([str(PY), "-m", "pip", "--version"], quiet=True) == 0:
        step("pip", "ok", ok=True)
        return True

    if _run([str(PY), "-m", "ensurepip", "--upgrade"], quiet=True) == 0:
        step("pip", "ok", ok=True)
        return True

    try:
        with tempfile.NamedTemporaryFile(suffix=".py") as f:
            urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", f.name)
            if _run([str(PY), f.name]) != 0:
                step("pip", "failed", ok=False)
                return False
    except OSError as err:
        step("pip", str(err), ok=False)
        return False

    step("pip", "ok", ok=True)
    return True


def install_editable() -> bool:
    step("sysdash", f"v{__version__}")
    _run([str(PIP), "install", "--upgrade", "pip", "-q"], quiet=True)
    if _run([str(PIP), "install", "-e", str(REPO_ROOT), "-q"], quiet=True) != 0:
        step("sysdash", "failed", ok=False)
        return False
    step("sysdash", "ok", ok=True)
    return True


def run_full_setup() -> int:
    console.print()
    console.print(
        Panel(
            "gotop + nvtop in tmux",
            title="sysdash",
            border_style=BORDER,
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
    console.print()

    if not (ensure_venv() and ensure_pip() and install_editable()):
        return 1

    console.print()
    if install_packages() != 0:
        return 1

    console.print()
    code = run_doctor()
    if code == 0:
        print_panel("Run [bold]sysdash[/bold]. [bold]Ctrl+C[/bold] to exit.", "Done")
    return code


if __name__ == "__main__":
    raise SystemExit(run_full_setup())
