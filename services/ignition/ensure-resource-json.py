#!/usr/bin/env python3
"""
Script to ensure resource.json files are created for all Ignition assets.
This script scans Ignition project directories and creates resource.json files
for leaf directories containing code assets (*.py, view.json, etc.) but NOT
for intermediate directories.
"""

import json
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Optional

# Define file patterns that indicate an asset directory (leaf node)
ASSET_FILE_PATTERNS = {
    ".py",  # Python scripts
    ".json",  # View definitions, configs
    ".bin",  # Binary data files
    ".sql",  # SQL queries
    ".html",  # HTML templates
    ".css",  # Stylesheets
    ".js",  # JavaScript files
}

# Special files to exclude from the files list in resource.json
EXCLUDE_FILES = {
    "resource.json",
    "project.json",
    ".DS_Store",
    "Thumbs.db",
}

# Directory patterns that should have resource.json files
IGNITION_ASSET_PATHS = [
    "ignition/script-python",
    "com.inductiveautomation.perspective/views",
    "com.inductiveautomation.perspective/page-config",
    "com.inductiveautomation.perspective/session-props",
    "com.inductiveautomation.vision/client-tags",
    "com.inductiveautomation.webdev/resources",
    "ignition/webdev",
    "ignition/global-props",
]


def is_asset_directory(path: Path) -> bool:
    """
    Determine if a directory is an asset directory (leaf node with code/config files).
    Returns True if the directory contains asset files and no subdirectories with assets.
    """
    if not path.is_dir():
        return False

    # Check if directory contains any asset files
    has_asset_files = False
    asset_files = []

    for item in path.iterdir():
        if item.is_file():
            # Check if this is an asset file
            if item.suffix in ASSET_FILE_PATTERNS or item.name in [
                "doGet.py",
                "doPost.py",
                "doPut.py",
                "doDelete.py",
            ]:
                has_asset_files = True
                if item.name not in EXCLUDE_FILES:
                    asset_files.append(item.name)

    if not has_asset_files:
        return False

    # Check if any subdirectories contain assets (making this NOT a leaf)
    for item in path.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            # Recursively check if subdirectory has assets
            if has_ignition_assets(item):
                return False  # This is not a leaf directory

    return True  # This is a leaf directory with assets


def has_ignition_assets(path: Path) -> bool:
    """
    Check if a directory or its subdirectories contain Ignition assets.
    """
    if not path.is_dir():
        return False

    # Check current directory for asset files
    for item in path.iterdir():
        if item.is_file() and (
            item.suffix in ASSET_FILE_PATTERNS
            or item.name in ["doGet.py", "doPost.py", "doPut.py", "doDelete.py"]
        ):
            return True

    # Check subdirectories
    for item in path.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            if has_ignition_assets(item):
                return True

    return False


def get_asset_files(path: Path) -> List[str]:
    """
    Get list of asset files in a directory (excluding resource.json itself).
    """
    asset_files = []
    for item in sorted(path.iterdir()):
        if item.is_file() and item.name not in EXCLUDE_FILES:
            # Include files with asset extensions or special handler names
            if item.suffix in ASSET_FILE_PATTERNS or item.name in [
                "doGet.py",
                "doPost.py",
                "doPut.py",
                "doDelete.py",
            ]:
                asset_files.append(item.name)
    return asset_files


def calculate_signature(files: List[str]) -> str:
    """
    Calculate a SHA256 signature for the modification.
    """
    content = "".join(sorted(files))
    return hashlib.sha256(content.encode()).hexdigest()


def create_resource_json(path: Path, files: List[str], actor: str = "admin") -> Dict:
    """
    Create the resource.json content structure.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    signature = calculate_signature(files)

    # Determine resource type based on path
    if "script-python" in str(path):
        # Script module format
        return {
            "scope": "A",
            "version": 1,
            "restricted": False,
            "overridable": True,
            "files": files,
            "attributes": {
                "hintScope": 2,
                "lastModificationSignature": signature,
                "lastModification": {"actor": actor, "timestamp": timestamp},
            },
        }
    elif "webdev" in str(path):
        # WebDev resource format
        return {
            "resource": {
                "version": 1,
                "type": "com.inductiveautomation.webdev.gateway.resource.PythonResource",
                "data": {"files": files},
            }
        }
    elif "perspective" in str(path):
        # Perspective resource format
        return {
            "scope": "A",
            "version": 1,
            "restricted": False,
            "overridable": True,
            "files": files,
            "attributes": {
                "lastModificationSignature": signature,
                "lastModification": {"actor": actor, "timestamp": timestamp},
            },
        }
    else:
        # Default format
        return {
            "scope": "A",
            "version": 1,
            "restricted": False,
            "overridable": True,
            "files": files,
            "attributes": {
                "lastModificationSignature": signature,
                "lastModification": {"actor": actor, "timestamp": timestamp},
            },
        }


def process_directory(
    path: Path,
    dry_run: bool = False,
    verbose: bool = True,
    remove_incorrect: bool = False,
) -> Dict[str, List[Path]]:
    """
    Process a directory tree and ensure resource.json files exist where needed.
    Returns a dict with 'created', 'updated', 'skipped', 'removed' lists of paths.
    """
    results = {"created": [], "updated": [], "skipped": [], "removed": [], "errors": []}

    # Walk through directory tree
    for root, dirs, files in os.walk(path):
        root_path = Path(root)

        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

        resource_json_path = root_path / "resource.json"

        # Check if this is an asset directory (leaf with code files)
        if is_asset_directory(root_path):
            asset_files = get_asset_files(root_path)

            if not asset_files:
                # If resource.json exists but no asset files, consider removing it
                if resource_json_path.exists() and remove_incorrect:
                    if verbose:
                        print(
                            f"  Removing incorrect {resource_json_path} - no asset files in directory"
                        )
                    if not dry_run:
                        resource_json_path.unlink()
                    results["removed"].append(root_path)
                else:
                    if verbose and resource_json_path.exists():
                        print(
                            f"  Warning: {resource_json_path} exists but no asset files found"
                        )
                    results["skipped"].append(root_path)
                continue

            if resource_json_path.exists():
                # Check if update is needed
                try:
                    with open(resource_json_path, "r") as f:
                        existing = json.load(f)

                    # Extract files list from existing structure
                    existing_files = []
                    if "files" in existing:
                        existing_files = existing["files"]
                    elif "resource" in existing and "data" in existing["resource"]:
                        existing_files = existing["resource"]["data"].get("files", [])

                    if set(existing_files) != set(asset_files):
                        if verbose:
                            print(f"  Updating {resource_json_path}")
                            print(f"    Old files: {existing_files}")
                            print(f"    New files: {asset_files}")

                        if not dry_run:
                            content = create_resource_json(root_path, asset_files)
                            with open(resource_json_path, "w") as f:
                                json.dump(content, f, indent=2)
                                f.write("\n")

                        results["updated"].append(root_path)
                    else:
                        if verbose:
                            print(
                                f"  Skipping {resource_json_path} - already up to date"
                            )
                        results["skipped"].append(root_path)

                except Exception as e:
                    print(f"  Error reading {resource_json_path}: {e}")
                    results["errors"].append((root_path, str(e)))
            else:
                # Create new resource.json
                if verbose:
                    print(f"  Creating {resource_json_path}")
                    print(f"    Files: {asset_files}")

                if not dry_run:
                    content = create_resource_json(root_path, asset_files)
                    with open(resource_json_path, "w") as f:
                        json.dump(content, f, indent=2)
                        f.write("\n")

                results["created"].append(root_path)
        else:
            # This is NOT an asset directory - check if it incorrectly has resource.json
            if resource_json_path.exists():
                # Check if this directory has subdirectories with assets
                has_asset_subdirs = any(
                    has_ignition_assets(subdir)
                    for subdir in root_path.iterdir()
                    if subdir.is_dir() and not subdir.name.startswith(".")
                )

                if has_asset_subdirs and remove_incorrect:
                    if verbose:
                        print(
                            f"  Removing incorrect {resource_json_path} - not a leaf directory"
                        )
                    if not dry_run:
                        resource_json_path.unlink()
                    results["removed"].append(root_path)
                elif has_asset_subdirs:
                    if verbose:
                        print(
                            f"  Warning: {resource_json_path} should not exist - not a leaf directory"
                        )
                    results["errors"].append(
                        (root_path, "resource.json in non-leaf directory")
                    )

    return results


def main():
    """
    Main function to process all Ignition projects.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Ensure resource.json files exist for Ignition assets"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")
    parser.add_argument(
        "--path",
        type=str,
        default="ignition-projects",
        help="Path to Ignition projects directory",
    )
    parser.add_argument(
        "--remove-incorrect",
        action="store_true",
        help="Remove resource.json files from non-leaf directories",
    )
    args = parser.parse_args()

    verbose = not args.quiet
    projects_path = Path(args.path)

    if not projects_path.exists():
        print(f"Error: Path {projects_path} does not exist")
        return 1

    if verbose:
        print(f"Processing Ignition projects in: {projects_path}")
        if args.dry_run:
            print("DRY RUN MODE - No changes will be made")
        if args.remove_incorrect:
            print("WILL REMOVE incorrect resource.json files from non-leaf directories")
        print("-" * 60)

    total_results = {
        "created": [],
        "updated": [],
        "skipped": [],
        "removed": [],
        "errors": [],
    }

    # Process each project
    for project_dir in sorted(projects_path.iterdir()):
        if project_dir.is_dir() and not project_dir.name.startswith("."):
            if verbose:
                print(f"\nProcessing project: {project_dir.name}")

            results = process_directory(
                project_dir,
                dry_run=args.dry_run,
                verbose=verbose,
                remove_incorrect=args.remove_incorrect,
            )

            # Aggregate results
            for key in total_results:
                total_results[key].extend(results[key])

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Created: {len(total_results['created'])} resource.json files")
    print(f"Updated: {len(total_results['updated'])} resource.json files")
    print(f"Removed: {len(total_results['removed'])} incorrect resource.json files")
    print(f"Skipped: {len(total_results['skipped'])} directories")
    print(f"Errors:  {len(total_results['errors'])} errors")

    if total_results["errors"]:
        print("\nErrors encountered:")
        for item in total_results["errors"]:
            if isinstance(item, tuple):
                path, error = item
                print(f"  {path}: {error}")
            else:
                print(f"  {item}")

    if args.dry_run:
        print("\nDRY RUN COMPLETE - No files were modified")

    return 0 if not total_results["errors"] else 1


if __name__ == "__main__":
    exit(main())
