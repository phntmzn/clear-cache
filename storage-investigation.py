Here’s a complete Python script named `macos_system_data.py` that automates the storage investigation. It checks disk usage, large Library directories, caches, Xcode, Python, Ollama, Docker, and Time Machine snapshots.

The script is **read-only by default**: it reports storage usage without deleting files. It also includes optional commands to clear selected caches after confirmation.



```python
# macos_system_data.py

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


HOME = Path.home()
LIBRARY = HOME / "Library"


def format_size(size):
    """Convert bytes to a readable size."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


def run_command(command, timeout=60):
    """Execute a system command without raising errors."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        if result.returncode == 0:
            return result.stdout.strip()

        return result.stderr.strip() or "Command failed."

    except FileNotFoundError:
        return f"Command not found: {command[0]}"

    except subprocess.TimeoutExpired:
        return "Command timed out."

    except OSError as error:
        return f"Error: {error}"


def section(title):
    """Print a section heading."""
    print(f"\n{'=' * 60}")
    print(title)
    print("=" * 60)


def check_disk_usage():
    """Show filesystem capacity and available space."""
    section("DISK USAGE")

    output = run_command(["df", "-h", "/"])
    print(output)


def directory_size(path):
    """Calculate directory size without following symbolic links."""
    path = Path(path)

    if not path.exists():
        return 0

    total = 0

    try:
        for root, dirs, files in os.walk(
            path,
            followlinks=False,
            onerror=lambda error: None,
        ):
            dirs[:] = [
                name for name in dirs
                if not (Path(root) / name).is_symlink()
            ]

            for filename in files:
                file_path = Path(root) / filename

                try:
                    if not file_path.is_symlink():
                        total += file_path.stat().st_size
                except OSError:
                    continue

    except OSError:
        pass

    return total


def inspect_directory(path):
    """Print the size of a directory."""
    path = Path(path)

    if not path.exists():
        print(f"{str(path):65} Not found")
        return

    size = directory_size(path)
    print(f"{format_size(size):>10}  {path}")


def inspect_largest_directories(path, limit=15):
    """List the largest immediate subdirectories."""
    path = Path(path)

    section(f"LARGEST DIRECTORIES: {path}")

    if not path.is_dir():
        print("Directory does not exist.")
        return

    results = []

    try:
        for item in path.iterdir():
            try:
                if item.is_symlink():
                    continue

                size = directory_size(item) if item.is_dir() else item.stat().st_size
                results.append((size, item))

            except OSError:
                continue

    except PermissionError:
        print("Permission denied.")
        return

    for size, item in sorted(results, reverse=True)[:limit]:
        print(f"{format_size(size):>10}  {item}")


def check_time_machine():
    """Inspect Time Machine local snapshots."""
    section("TIME MACHINE SNAPSHOTS")

    output = run_command(["tmutil", "listlocalsnapshots", "/"])
    print(output or "No snapshots reported.")


def check_apfs():
    """Inspect APFS container information."""
    section("APFS STORAGE")

    output = run_command(["diskutil", "apfs", "list"], timeout=90)
    print(output)


def check_developer_files():
    """Inspect common Xcode directories."""
    section("DEVELOPER STORAGE")

    paths = [
        LIBRARY / "Developer",
        LIBRARY / "Developer/Xcode/DerivedData",
        LIBRARY / "Developer/Xcode/Archives",
        LIBRARY / "Developer/CoreSimulator",
    ]

    for path in paths:
        inspect_directory(path)


def check_python_and_ai():
    """Inspect common Python and AI storage locations."""
    section("PYTHON AND AI STORAGE")

    paths = [
        HOME / ".cache",
        HOME / ".ollama",
        HOME / ".local/share",
        HOME / "Documents",
        HOME / "Downloads",
    ]

    for path in paths:
        inspect_directory(path)

    section("PYTHON PIP CACHE")

    print(
        run_command(
            [sys.executable, "-m", "pip", "cache", "info"]
        )
    )


def check_docker():
    """Inspect Docker storage if Docker is installed."""
    section("DOCKER STORAGE")

    docker = shutil.which("docker")

    if not docker:
        print("Docker CLI not installed. Skipping.")
        return

    print(run_command([docker, "system", "df"], timeout=90))


def run_diagnostics():
    """Run all read-only storage checks."""
    print("macOS SYSTEM DATA INVESTIGATION")
    print(f"User: {HOME}")
    print("Mode: READ-ONLY")
    print("No files will be deleted.")

    check_disk_usage()

    inspect_largest_directories(
        LIBRARY,
        limit=20,
    )

    inspect_largest_directories(
        LIBRARY / "Caches",
        limit=20,
    )

    inspect_largest_directories(
        LIBRARY / "Application Support",
        limit=20,
    )

    inspect_largest_directories(
        LIBRARY / "Containers",
        limit=20,
    )

    check_developer_files()
    check_python_and_ai()
    check_time_machine()
    check_apfs()
    check_docker()

    section("INVESTIGATION COMPLETE")
    print("Review the results before deleting any files.")


def clear_pip_cache():
    """Clear downloaded pip cache files after confirmation."""
    section("CLEAR PYTHON PIP CACHE")

    print(
        run_command(
            [sys.executable, "-m", "pip", "cache", "info"]
        )
    )

    confirmation = input(
        "\nRemove cached pip downloads? Type YES to continue: "
    )

    if confirmation != "YES":
        print("Cancelled.")
        return

    print(
        run_command(
            [sys.executable, "-m", "pip", "cache", "purge"]
        )
    )


def clear_user_caches():
    """Delete immediate contents of the user's Library/Caches."""
    cache_dir = LIBRARY / "Caches"

    section("CLEAR USER APPLICATION CACHES")

    if not cache_dir.is_dir():
        print("Cache directory not found.")
        return

    print(f"Target: {cache_dir}")
    print("Applications should be closed before cleanup.")
    print("Some applications may recreate these files.")

    confirmation = input(
        "Delete the immediate contents of this cache directory? "
        "Type YES to continue: "
    )

    if confirmation != "YES":
        print("Cancelled.")
        return

    deleted_size = 0
    failed = 0

    try:
        items = list(cache_dir.iterdir())
    except OSError as error:
        print(f"Cannot access cache directory: {error}")
        return

    for item in items:
        if item.is_symlink():
            print(f"Skipping symbolic link: {item.name}")
            continue

        size = directory_size(item) if item.is_dir() else 0

        if item.is_file():
            try:
                size = item.stat().st_size
            except OSError:
                size = 0

        try:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

            deleted_size += size
            print(f"Removed: {item.name} ({format_size(size)})")

        except OSError as error:
            failed += 1
            print(f"Could not remove {item.name}: {error}")

    section("CACHE CLEANUP SUMMARY")
    print(f"Estimated removed: {format_size(deleted_size)}")
    print(f"Failed items: {failed}")
    print("Restart affected applications if necessary.")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Inspect macOS System Data contributors "
            "and optionally clear selected caches."
        )
    )

    parser.add_argument(
        "--clear-pip",
        action="store_true",
        help="Clear the pip download cache after confirmation.",
    )

    parser.add_argument(
        "--clear-user-caches",
        action="store_true",
        help=(
            "Delete immediate contents of ~/Library/Caches "
            "after confirmation."
        ),
    )

    args = parser.parse_args()

    if sys.platform != "darwin":
        print("Warning: This script is designed for macOS.")

    if args.clear_pip and args.clear_user_caches:
        parser.error("Choose one cleanup option at a time.")

    if args.clear_pip:
        clear_pip_cache()
    elif args.clear_user_caches:
        clear_user_caches()
    else:
        run_diagnostics()


if __name__ == "__main__":
    main()
```

## How to use it

### 1. Run the storage investigation

Save the file as `macos_system_data.py`, then run:

```bash
python3 macos_system_data.py
```

It will inspect the main storage locations and display their sizes. **No files will be deleted in this mode.**

### 2. Clear the Python package cache

```bash
python3 macos_system_data.py --clear-pip
```

This asks for confirmation before clearing pip's download cache.

### 3. Clear user application caches

```bash
python3 macos_system_data.py --clear-user-caches
```

This asks for confirmation before deleting the immediate contents of `~/Library/Caches`. Close applications first. Some files may be in use, and some applications may recreate their caches.

**Note:** This option is more aggressive than inspecting the cache directories individually. If you want maximum control, run the default diagnostic mode first.

### What this script doesn't delete

It deliberately does not automatically remove:

- Ollama models.
- Xcode archives or simulator data.
- Time Machine snapshots.
- Docker images, containers, or volumes.
- Application container data.
- macOS system files.

Those locations can contain valuable data and should be reviewed individually.

**Recommended next step:** Run the diagnostic mode first and save its output. That will help identify which directories are actually responsible for your 92 GB of System Data before you decide what to remove.
