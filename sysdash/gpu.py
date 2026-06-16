"""GPU detection for optional nvtop."""

import shutil
import subprocess
from pathlib import Path


def has_gpu() -> bool:
    if Path("/dev/nvidia0").exists():
        return True

    dri = Path("/dev/dri")
    if dri.is_dir() and any(dri.glob("card*")):
        return True

    if shutil.which("nvidia-smi"):
        try:
            result = subprocess.run(
                ["nvidia-smi", "-L"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    if shutil.which("rocm-smi"):
        try:
            result = subprocess.run(
                ["rocm-smi", "--showid"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    return False
