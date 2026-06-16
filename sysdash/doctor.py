import subprocess
import sys

from rich import box
from rich.panel import Panel

from sysdash.components import COMPONENTS, is_installed, resolve_binary
from sysdash.gpu import has_gpu
from sysdash.style import BORDER_STYLE, console, status_table


def _pip_ok() -> bool:
    return (
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )


def _pip_version() -> str:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    return (result.stdout or result.stderr).strip().splitlines()[0][:80]


def _version_of(binary: str) -> str:
    cmd = resolve_binary(binary)
    flags = ("-V", "--version", "-v") if binary == "tmux" else ("--version", "-V", "-v")
    for flag in flags:
        try:
            result = subprocess.run(
                [cmd, flag],
                capture_output=True,
                text=True,
                timeout=5,
            )
            lines = (result.stdout or result.stderr).strip().splitlines()
            if lines:
                return lines[0][:80]
        except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
            continue
    return "found"


def check_system() -> tuple[list[tuple[str, bool, str]], bool]:
    rows: list[tuple[str, bool, str]] = []
    ok_all = True
    gpu = has_gpu()

    if _pip_ok():
        rows.append(("pip", True, _pip_version()))
    else:
        rows.append(("pip", False, "run ./install.sh"))
        ok_all = False

    for component in COMPONENTS:
        if component.binary == "nvtop" and not gpu:
            rows.append(("nvtop", True, "not required (no GPU)"))
            continue

        if is_installed(component.binary):
            rows.append((component.binary, True, _version_of(component.binary)))
        else:
            rows.append((component.binary, False, "not installed"))
            ok_all = False

    return rows, ok_all


def run_doctor() -> int:
    rows, ok_all = check_system()
    console.print(
        Panel(
            status_table(rows),
            title="Doctor",
            border_style=BORDER_STYLE,
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )

    if ok_all:
        console.print("\n[green]Ready.[/green] Run [bold]sysdash run[/bold].")
        return 0

    console.print("\n[yellow]Missing dependencies.[/yellow] Run [bold]./install.sh[/bold].")
    return 1
