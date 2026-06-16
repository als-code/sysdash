import subprocess
import sys

from sysdash.components import COMPONENTS, is_installed, resolve_binary
from sysdash.gpu import has_gpu
from sysdash.style import console, status_panel


def _pip_ok() -> bool:
    return subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True).returncode == 0


def _pip_version() -> str:
    r = subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True, text=True)
    return (r.stdout or r.stderr).strip().splitlines()[0][:80]


def _version_of(name: str) -> str:
    cmd = resolve_binary(name)
    flags = ("-V", "--version", "-v") if name == "tmux" else ("--version", "-V", "-v")
    for flag in flags:
        try:
            r = subprocess.run([cmd, flag], capture_output=True, text=True, timeout=5)
            lines = (r.stdout or r.stderr).strip().splitlines()
            if lines:
                return lines[0][:80]
        except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
            continue
    return "found"


def check_system() -> tuple[list[tuple[str, bool, str]], bool]:
    rows: list[tuple[str, bool, str]] = []
    ok = True
    gpu = has_gpu()

    if _pip_ok():
        rows.append(("pip", True, _pip_version()))
    else:
        rows.append(("pip", False, "run ./install.sh"))
        ok = False

    for c in COMPONENTS:
        if c.binary == "nvtop" and not gpu:
            rows.append(("nvtop", True, "not required (no GPU)"))
            continue
        if is_installed(c.binary):
            rows.append((c.binary, True, _version_of(c.binary)))
        else:
            rows.append((c.binary, False, "not installed"))
            ok = False

    return rows, ok


def run_doctor() -> int:
    rows, ok = check_system()
    status_panel(rows, "Doctor")

    if ok:
        console.print("\n[green]Ready.[/green] Run [bold]sysdash[/bold].")
        return 0

    console.print("\n[yellow]Missing dependencies.[/yellow] Run [bold]./install.sh[/bold].")
    return 1
