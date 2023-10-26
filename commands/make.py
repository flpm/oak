# Performs the entire build process for the project.

from .reset import reset_library
from .add import bookshelf, audible
from .save import load_attributes, save_attributes
from .enrich import amazon
from .enrich import audible as enrich_audible
from .export import export_markdown


def make_catalogue(export_date: str, quiet: bool = True):
    print("=== Resetting library ===")
    reset_library()
    print("=== Importing books ===")
    bookshelf(export_date)
    print("=== Importing audiobooks ===")
    audible()
    print("=== Enriching books ===")
    amazon(quiet=quiet)
    print("=== Enriching audiobooks ===")
    enrich_audible()
    print("=== Loading attributes ===")
    load_attributes()
    print("=== Exporting ===")
    export_markdown()
