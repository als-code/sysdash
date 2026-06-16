import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LAUNCHER = REPO_ROOT / "bin" / "sysdash"
LOCAL_BIN = Path.home() / ".local" / "bin"
GLOBAL_COMMAND = LOCAL_BIN / "sysdash"


def ensure_launcher() -> Path:
    if not LAUNCHER.is_file():
        raise FileNotFoundError(LAUNCHER)
    LAUNCHER.chmod(0o755)
    return LAUNCHER


def path_has_local_bin() -> bool:
    return any(
        Path(p).expanduser().resolve() == LOCAL_BIN.resolve()
        for p in os.environ.get("PATH", "").split(":")
        if p
    )


def install_cli_command() -> tuple[Path, bool]:
    launcher = ensure_launcher()
    LOCAL_BIN.mkdir(parents=True, exist_ok=True)
    if GLOBAL_COMMAND.exists() or GLOBAL_COMMAND.is_symlink():
        GLOBAL_COMMAND.unlink()
    GLOBAL_COMMAND.symlink_to(launcher.resolve())
    return GLOBAL_COMMAND, path_has_local_bin()


def ensure_shell_path() -> bool:
    if path_has_local_bin():
        return True

    zshrc = Path.home() / ".zshrc"
    if zshrc.exists() and ".local/bin" in zshrc.read_text():
        return False

    with zshrc.open("a") as f:
        f.write('\n# sysdash\nexport PATH="$HOME/.local/bin:$PATH"\n')

    os.environ["PATH"] = f"{LOCAL_BIN}{os.pathsep}{os.environ.get('PATH', '')}"
    return True
