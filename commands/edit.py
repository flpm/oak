"""Subcommand to easily add metadata to the books in the library."""

import typer
from rich import print

from collections import defaultdict

from .utils.file import read_catalogue, save_catalogue
from .utils.editing import edit_loop


def run_edit_loop():
    """Run the edit loop."""
    catalogue = defaultdict(dict, read_catalogue())
    print(f"Books in catalogue: {len(catalogue)} books.")
    print(f"Manage the book purchase dates.")
    catalogue = edit_loop(catalogue)
    if typer.confirm("Save catalogue?", False):
        print("[green]Saving catalogue...[/green]")
        save_catalogue(catalogue)
    else:
        print("[red]Exited without saving changes[/red]")
