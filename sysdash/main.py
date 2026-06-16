import typer

from sysdash import __version__
from sysdash.doctor import run_doctor
from sysdash.install import install_packages
from sysdash.run import run_dashboard

app = typer.Typer(name="sysdash", no_args_is_help=True)


@app.command()
def install() -> None:
    """Install tmux, gotop, and nvtop (when a GPU is present)."""
    raise typer.Exit(install_packages())


@app.command()
def doctor() -> None:
    """Check dependencies."""
    raise typer.Exit(run_doctor())


@app.command()
def run(stop: bool = typer.Option(False, "--stop", help="Kill the tmux session.")) -> None:
    """Open gotop and nvtop side by side."""
    raise typer.Exit(run_dashboard(stop=stop))


@app.command()
def version() -> None:
    typer.echo(f"sysdash {__version__}")


if __name__ == "__main__":
    app()
