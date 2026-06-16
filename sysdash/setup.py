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
from sysdash.style import BORDER_STYLE, console, print_panel

ROOT = Path(__file__).resolve().parent.parent
VENV = ROOT / ".venv"
PY = VENV / "bin" / "python"
PIP = VENV / "bin" / "pip"


def _panel(title: str, text: str, ok: bool | None = None) -> None:
    mark = {True: "[green]✓[/green] ", False: "[red]✗[/red] ", None: "→ "}[ok]
    console.print(
        Panel(
            f"{mark}{text}",
            title=title,
            border_style=BORDER_STYLE,
            box=box.ROUNDED,
            padding=(0, 2),
        )
    )


def _run(cmd: list[str], quiet: bool = False) -> int:
    if not quiet:
        console.print(f"[dim]  $ {' '.join(cmd)}[/dim]")
    return subprocess.run(cmd, capture_output=quiet, text=quiet).returncode


def _install_venv_deb() -> bool:
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
    _panel("Python", f"{sys.version}")

    if PY.exists() and PIP.exists():
        _panel("venv", "ok", ok=True)
        return True

    if VENV.exists():
        shutil.rmtree(VENV)

    _panel("venv", "creating…")
    if _run([sys.executable, "-m", "venv", str(VENV)]) == 0:
        _panel("venv", str(VENV), ok=True)
        return True

    if not _install_venv_deb():
        _panel("venv", "install python3-venv first", ok=False)
        return False

    if _run([sys.executable, "-m", "venv", str(VENV)]) != 0:
        _panel("venv", "creation failed", ok=False)
        return False

    _panel("venv", str(VENV), ok=True)
    return True


def ensure_pip() -> bool:
    if _run([str(PY), "-m", "pip", "--version"], quiet=True) == 0:
        _panel("pip", "ok", ok=True)
        return True

    if _run([str(PY), "-m", "ensurepip", "--upgrade"], quiet=True) == 0:
        _panel("pip", "ok", ok=True)
        return True

    try:
        with tempfile.NamedTemporaryFile(suffix=".py") as f:
            urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", f.name)
            if _run([str(PY), f.name]) != 0:
                _panel("pip", "bootstrap failed", ok=False)
                return False
    except OSError as err:
        _panel("pip", str(err), ok=False)
        return False

    _panel("pip", "ok", ok=True)
    return True


def install_editable() -> bool:
    _panel("sysdash", f"v{__version__}")
    _run([str(PIP), "install", "--upgrade", "pip", "-q"], quiet=True)
    if _run([str(PIP), "install", "-e", f"{ROOT}[dev]", "-q"], quiet=True) != 0:
        _panel("sysdash", "pip install failed", ok=False)
        return False
    _panel("sysdash", "installed", ok=True)
    return True


def run_tests() -> bool:
    _panel("tests", "running pytest…")
    code = _run([str(PY), "-m", "pytest", "-q", str(ROOT / "tests")], quiet=True)
    _panel("tests", "passed" if code == 0 else "failed", ok=code == 0)
    return code == 0


def run_full_setup() -> int:
    console.print()
    console.print(
        Panel(
            "[bold]sysdash[/bold]  gotop + nvtop in tmux",
            title="Setup",
            border_style=BORDER_STYLE,
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
    if not run_tests():
        return 1

    console.print()
    code = run_doctor()
    if code == 0:
        print_panel("Run [bold cyan]sysdash run[/bold cyan]. Exit with [bold]Ctrl+C[/bold].", "Done")
    return code


if __name__ == "__main__":
    raise SystemExit(run_full_setup())
