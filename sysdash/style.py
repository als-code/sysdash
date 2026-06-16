from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

BORDER_STYLE = "green"
PANEL_BOX = box.ROUNDED


def panel(content: str, title: str) -> Panel:
    return Panel(
        content,
        title=title,
        border_style=BORDER_STYLE,
        box=PANEL_BOX,
        padding=(1, 2),
    )


def print_panel(content: str, title: str) -> None:
    console.print(panel(content, title))


def status_table(rows: list[tuple[str, bool, str]]) -> Table:
    table = Table(show_header=True, header_style="bold", box=PANEL_BOX, border_style=BORDER_STYLE)
    table.add_column("Component", style="bold")
    table.add_column("Status", justify="center")
    table.add_column("Detail")

    for name, ok, detail in rows:
        status = "[green]OK[/green]" if ok else "[red]MISSING[/red]"
        table.add_row(name, status, detail)

    return table
