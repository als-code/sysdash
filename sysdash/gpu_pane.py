import os
import shutil
import sys
import time

from rich.console import Console

from sysdash.components import resolve_binary
from sysdash.gpu import has_gpu
from sysdash.style import print_panel


def main() -> None:
    if has_gpu() and shutil.which("nvtop"):
        os.execvp(resolve_binary("nvtop"), ["nvtop"])

    console = Console()
    message = (
        "No GPU or graphics drivers were detected.\n\n"
        "This pane would run nvtop when a supported GPU and drivers are present."
    )
    try:
        while True:
            console.clear()
            print_panel(message, "GPU monitor")
            time.sleep(60)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
