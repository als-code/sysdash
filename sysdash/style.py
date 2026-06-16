from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
BORDER = "green"
BOX = box.ROUNDED


def print_panel(body: str, title: str) -> None:
    console.print(
        Panel(body, title=title, border_style=BORDER, box=BOX, padding=(1, 2))
    )


def step(title: str, text: str, ok: bool | None = None) -> None:
    mark = {True: "[green]✓[/green] ", False: "[red]✗[/red] ", None: "→ "}[ok]
    console.print(
        Panel(
            f"{mark}{text}",
            title=title,
            border_style=BORDER,
            box=BOX,
            padding=(0, 2),
        )
    )


def status_table(rows: list[tuple[str, bool, str]]) -> Table:
    table = Table(show_header=True, header_style="bold", box=BOX, border_style=BORDER)
    table.add_column("Component", style="bold")
    table.add_column("Status", justify="center")
    table.add_column("Detail")
    for name, ok, detail in rows:
        label = "[green]OK[/green]" if ok else "[red]MISSING[/red]"
        table.add_row(name, label, detail)
    return table


def status_panel(rows: list[tuple[str, bool, str]], title: str) -> None:
    console.print(
        Panel(status_table(rows), title=title, border_style=BORDER, box=BOX, padding=(1, 2))
    )
