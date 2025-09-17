#!/usr/bin/env python3
"""
Simple Ignition Linter Integration for Cursor AI
Direct integration with empirical ignition linter for production-validated code quality.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Path to the empirical linter
EMPIRICAL_LINTER_PATH = (
    Path(__file__).parent.parent.parent
    / "empirical-ignition-perspective-component-schema"
)
PERSPECTIVE_LINTER = EMPIRICAL_LINTER_PATH / "tools" / "ignition-perspective-linter.py"
SCRIPT_LINTER = EMPIRICAL_LINTER_PATH / "tools" / "ignition-script-linter.py"


def check_linter_availability():
    """Check if the empirical linter is available."""
    if not EMPIRICAL_LINTER_PATH.exists():
        print(f"❌ Empirical linter not found at: {EMPIRICAL_LINTER_PATH}")
        print(
            "   Please ensure the empirical-ignition-perspective-component-schema repository is cloned"
        )
        print("   at the expected location relative to this project.")
        return False

    if not PERSPECTIVE_LINTER.exists():
        print(f"❌ Perspective linter not found at: {PERSPECTIVE_LINTER}")
        return False

    if not SCRIPT_LINTER.exists():
        print(f"❌ Script linter not found at: {SCRIPT_LINTER}")
        return False

    print("✅ Empirical linter is available")
    print(f"   Path: {EMPIRICAL_LINTER_PATH}")
    return True


def lint_perspective(target_path, component_type=None, verbose=False):
    """Lint Perspective components."""
    if not check_linter_availability():
        return False

    cmd = ["python3", str(PERSPECTIVE_LINTER), "--target", target_path]

    if component_type:
        cmd.extend(["--component-type", component_type])

    if verbose:
        cmd.append("--verbose")

    print(f"🔍 Linting Perspective components in {target_path}")
    print(f"Command: {' '.join(cmd)}")
    print("")

    try:
        result = subprocess.run(cmd, cwd=EMPIRICAL_LINTER_PATH)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running linter: {e}")
        return False


def lint_scripts(target_path, verbose=False):
    """Lint Python/Jython scripts."""
    if not check_linter_availability():
        return False

    cmd = ["python3", str(SCRIPT_LINTER), "--target", target_path]

    if verbose:
        cmd.append("--verbose")

    print(f"🔍 Linting scripts in {target_path}")
    print(f"Command: {' '.join(cmd)}")
    print("")

    try:
        result = subprocess.run(cmd, cwd=EMPIRICAL_LINTER_PATH)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running linter: {e}")
        return False


def _lint_perspective_components(project_path, component_type, verbose):
    """Lint Perspective components in a project."""
    perspective_path = project_path / "com.inductiveautomation.perspective" / "views"
    if perspective_path.exists():
        return lint_perspective(str(perspective_path), component_type, verbose)
    else:
        print(f"ℹ️  No Perspective views found at {perspective_path}")
        return True


def _lint_project_scripts(project_path, verbose):
    """Lint Python scripts in a project."""
    script_path = project_path / "ignition" / "script-python"
    if script_path.exists():
        return lint_scripts(str(script_path), verbose)
    else:
        print(f"ℹ️  No Python scripts found at {script_path}")
        return True


def _print_project_results(success):
    """Print final project linting results."""
    print("=" * 60)
    if success:
        print("🎉 All linting checks passed!")
    else:
        print("⚠️  Some linting checks failed. See details above.")


def lint_project(project_path, lint_type="all", component_type=None, verbose=False):
    """Lint an entire Ignition project."""
    project_path = Path(project_path).resolve()

    if not project_path.exists():
        print(f"❌ Project path does not exist: {project_path}")
        return False

    print(f"🚀 Linting Ignition project: {project_path.name}")
    print("=" * 60)

    success = True

    # Lint Perspective components
    if lint_type in ["perspective", "all"]:
        if not _lint_perspective_components(project_path, component_type, verbose):
            success = False

    # Lint Python scripts
    if lint_type in ["scripts", "all"]:
        if not _lint_project_scripts(project_path, verbose):
            success = False

    _print_project_results(success)
    return success


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Lint Ignition projects using the empirical ignition linter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check if linter is available
  python scripts/lint-ignition.py --check-linter

  # Lint entire project
  python scripts/lint-ignition.py --project ignition-projects/DemoAIProject

  # Lint only Perspective components
  python scripts/lint-ignition.py --project ignition-projects/Global --type perspective

  # Lint specific component type with verbose output
  python scripts/lint-ignition.py --project ignition-projects/DemoAIProject --type perspective --component ia.display.button --verbose
        """,
    )

    parser.add_argument("--project", "-p", help="Path to Ignition project directory")

    parser.add_argument(
        "--type",
        "-t",
        choices=["perspective", "scripts", "all"],
        default="all",
        help="Type of linting to perform (default: all)",
    )

    parser.add_argument(
        "--component",
        "-c",
        help="Filter to specific component type (e.g., 'ia.display.button')",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--check-linter",
        action="store_true",
        help="Check if empirical linter is available and exit",
    )

    args = parser.parse_args()

    # Check linter availability
    if args.check_linter:
        success = check_linter_availability()
        sys.exit(0 if success else 1)

    # Require project path
    if not args.project:
        print("❌ Project path is required. Use --project or --check-linter")
        parser.print_help()
        sys.exit(1)

    # Run linting
    success = lint_project(args.project, args.type, args.component, args.verbose)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
