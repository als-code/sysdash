import os
import shutil
import time

from sysdash.components import resolve_binary
from sysdash.gpu import has_gpu
from sysdash.style import console, print_panel


def main() -> None:
    if has_gpu() and shutil.which("nvtop"):
        os.execvp(resolve_binary("nvtop"), ["nvtop"])

    text = "No GPU or drivers detected.\n\nnvtop will run here when they are available."
    try:
        while True:
            console.clear()
            print_panel(text, "GPU monitor")
            time.sleep(60)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
