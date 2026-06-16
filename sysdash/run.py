import os
import shutil
import subprocess
import sys

from rich import box
from rich.panel import Panel

from sysdash.constants import SESSION_NAME, WINDOW_MONITOR
from sysdash.components import resolve_binary
from sysdash.doctor import check_system
from sysdash.gpu import has_gpu
from sysdash.style import BORDER_STYLE, console, print_panel


def _tmux(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["tmux", *args], capture_output=True, text=True)


def _gpu_pane_cmd() -> str:
    return f"{sys.executable} -m sysdash.gpu_pane"


def _configure_session() -> None:
    opts = {
        "pane-border-status": "top",
        "pane-border-format": " #{pane_title} ",
        "pane-border-style": "fg=colour8",
        "pane-active-border-style": "fg=green",
        "status-style": "fg=green,bg=black",
        "window-status-current-style": "fg=green,bg=colour8,bold",
    }
    for key, val in opts.items():
        _tmux("set-option", "-t", SESSION_NAME, key, val)
    _tmux("bind-key", "-T", "root", "C-c", "kill-session")


def create_session() -> None:
    target = f"{SESSION_NAME}:{WINDOW_MONITOR}"
    right_title = "nvtop" if has_gpu() else "gpu"

    _tmux("new-session", "-d", "-s", SESSION_NAME, "-n", WINDOW_MONITOR, resolve_binary("gotop"))
    _tmux("split-window", "-h", "-t", target, _gpu_pane_cmd())
    _tmux("select-pane", "-t", f"{target}.0", "-T", "gotop")
    _tmux("select-pane", "-t", f"{target}.1", "-T", right_title)
    _configure_session()


def run_dashboard(*, stop: bool = False) -> int:
    if not shutil.which("tmux"):
        print_panel("tmux is required.\nRun [bold]./install.sh[/bold]", "Run")
        return 1

    _, ok = check_system()
    if not ok:
        print_panel("Missing dependencies.\nRun [bold]./install.sh[/bold]", "Run")
        return 1

    if stop:
        if _tmux("has-session", "-t", SESSION_NAME).returncode == 0:
            _tmux("kill-session", "-t", SESSION_NAME)
            print_panel("Session stopped.", "Run")
        else:
            print_panel("No active session.", "Run")
        return 0

    if _tmux("has-session", "-t", SESSION_NAME).returncode == 0:
        _configure_session()
        console.print("[dim]Attaching…[/dim]\n")
        os.execvp("tmux", ["tmux", "attach-session", "-t", SESSION_NAME])

    create_session()
    right = "nvtop" if has_gpu() else "GPU status"
    console.print(
        Panel(
            f"[bold]gotop[/bold] (left) · [bold]{right}[/bold] (right)\n\n"
            "[cyan]Ctrl+C[/cyan]  close dashboard\n"
            "[cyan]Ctrl+b d[/cyan]  detach",
            title="sysdash",
            border_style=BORDER_STYLE,
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
    os.execvp("tmux", ["tmux", "attach-session", "-t", SESSION_NAME])
