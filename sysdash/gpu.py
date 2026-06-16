import os
import shutil
import subprocess
from pathlib import Path


def has_gpu() -> bool:
    if os.environ.get("SYSDASH_FORCE_NO_GPU") == "1":
        return False

    if Path("/dev/nvidia0").exists():
        return True

    dri = Path("/dev/dri")
    if dri.is_dir() and any(dri.glob("card*")):
        return True

    for cmd, args in (("nvidia-smi", ["-L"]), ("rocm-smi", ["--showid"])):
        if not shutil.which(cmd):
            continue
        try:
            r = subprocess.run([cmd, *args], capture_output=True, text=True, timeout=5)
            if r.returncode == 0 and (r.stdout or "").strip():
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    return False
