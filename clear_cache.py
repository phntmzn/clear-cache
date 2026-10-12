# clear_cache.py

import argparse
import shutil
from pathlib import Path


def get_cache_directories():
    """Return common user-level cache directories on macOS."""
    home = Path.home()

    return [
        home / "Library" / "Caches",
        home / "Library" / "Logs" / "DiagnosticReports",
    ]


def calculate_size(path):
    """Calculate the total size of a file or directory."""
    total = 0

    try:
        if path.is_file():
            return path.stat().st_size

        for item in path.rglob("*"):
            try:
                if item.is_file() and not item.is_symlink():
                    total += item.stat().st_size
            except (OSError, PermissionError):
                continue

    except (OSError, PermissionError):
        pass

    return total


def format_size(size):
    """Format bytes into a human-readable size."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{size:.2f} PB"


def clear_cache(dry_run=True):
    """Preview or delete contents of selected user cache directories."""
    total_freed = 0

    for cache_dir in get_cache_directories():
        print(f"\nDirectory: {cache_dir}")

        if not cache_dir.exists():
            print("  Directory does not exist. Skipping.")
            continue

        try:
            items = list(cache_dir.iterdir())
        except PermissionError:
            print("  Permission denied. Skipping.")
            continue

        for item in items:
            size = calculate_size(item)
            total_freed += size

            if dry_run:
                print(f"  [DRY RUN] {item.name} — {format_size(size)}")
                continue

            try:
                # Do not follow symbolic links.
                if item.is_symlink() or item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)

                print(f"  Deleted: {item.name} — {format_size(size)}")

            except (OSError, PermissionError) as error:
                print(f"  Could not delete {item.name}: {error}")

    print("\n" + "=" * 45)
    print(f"Estimated cache size: {format_size(total_freed)}")

    if dry_run:
        print("Dry run only. No files were deleted.")
        print("Run with --delete to remove the listed items.")
    else:
        print("Cache cleanup completed.")


def main():
    parser = argparse.ArgumentParser(
        description="Clear selected user caches on macOS."
    )

    parser.add_argument(
        "--delete",
        action="store_true",
        help="Actually delete cache contents. Without this flag, "
             "the script only previews them.",
    )

    args = parser.parse_args()

    if args.delete:
        confirmation = input(
            "Delete the contents of the selected cache directories? "
            "Enter YES to continue: "
        )

        if confirmation != "YES":
            print("Cancelled.")
            return

    clear_cache(dry_run=not args.delete)


if __name__ == "__main__":
    main()
