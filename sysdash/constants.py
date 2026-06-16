SESSION_NAME = "sysdash"
WINDOW_MONITOR = "monitor"

CORE_BINARIES = ("tmux", "gotop")
GPU_BINARY = "nvtop"

PACKAGE_NAMES = {
    "apt": ("tmux", "gotop", "nvtop"),
    "nala": ("tmux", "gotop", "nvtop"),
    "dnf": ("tmux", "gotop", "nvtop"),
    "pacman": ("tmux", "gotop", "nvtop"),
}
