import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LAUNCHER = REPO_ROOT / "bin" / "sysdash"
LOCAL_BIN = Path.home() / ".local" / "bin"
GLOBAL_COMMAND = LOCAL_BIN / "sysdash"


def ensure_launcher() -> Path:
    if not LAUNCHER.exists():
        raise FileNotFoundError(f"Launcher not found: {LAUNCHER}")
    LAUNCHER.chmod(0o755)
    return LAUNCHER


def path_has_local_bin() -> bool:
    return any(
        Path(entry).expanduser().resolve() == LOCAL_BIN.resolve()
        for entry in os.environ.get("PATH", "").split(":")
        if entry
    )


def install_cli_command() -> tuple[Path, bool]:
    """Symlink sysdash into ~/.local/bin. Returns (shim path, PATH already ok)."""
    launcher = ensure_launcher()
    LOCAL_BIN.mkdir(parents=True, exist_ok=True)

    if GLOBAL_COMMAND.is_symlink() or GLOBAL_COMMAND.exists():
        GLOBAL_COMMAND.unlink()

    GLOBAL_COMMAND.symlink_to(launcher.resolve())
    GLOBAL_COMMAND.chmod(0o755)
    return GLOBAL_COMMAND, path_has_local_bin()


def ensure_shell_path() -> bool:
    """Add ~/.local/bin to ~/.zshrc if missing. Returns True if PATH is configured."""
    if path_has_local_bin():
        return True

    zshrc = Path.home() / ".zshrc"
    line = 'export PATH="$HOME/.local/bin:$PATH"'
    marker = "# sysdash"

    if zshrc.exists():
        content = zshrc.read_text()
        if ".local/bin" in content:
            return False

    with zshrc.open("a") as handle:
        handle.write(f"\n{marker}\n{line}\n")

    os.environ["PATH"] = f"{LOCAL_BIN}{os.pathsep}{os.environ.get('PATH', '')}"
    return True
