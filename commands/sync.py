"""Sync book catalogue output folder with another folder."""

from rich import print

from .utils.syncing import compare_folders, add_files, delete_files, update_files


def sync_folders(source_folder, destination_folder, item_type="books"):
    """Sync book catalogue output folder with another folder."""

    print(f"Syncing {item_type} from {source_folder} with {destination_folder}.")

    compare_result = compare_folders(
        source_folder, destination_folder, item_type=item_type
    )
    add_list = compare_result["add"]
    delete_list = compare_result["delete"]
    update_list = compare_result["update"]

    if add_list:
        print(f"  - [bold green]adding[/bold green] {len(add_list)} {item_type}.")
        add_files(add_list, destination_folder, item_type=item_type)

    if delete_list:
        print(f"  - [bold red]deleting[/bold red] {len(delete_list)} {item_type}.")
        delete_files(delete_list, destination_folder)

    if update_list:
        print(f"  - [bold blue]updating[/bold blue] {len(update_list)} {item_type}.")
        update_files(update_list, destination_folder, item_type=item_type)

    print("Sync complete.")
