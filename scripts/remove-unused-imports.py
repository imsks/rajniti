#!/usr/bin/env python3
"""
Script to automatically remove unused imports from Python files.
This script uses autoflake to remove unused imports and variables.
"""

import subprocess
import sys


def remove_unused_imports():
    """Remove unused imports from Python files."""
    try:
        # Use autoflake to remove unused imports
        result = subprocess.run(
            [
                "autoflake",
                "--remove-all-unused-imports",
                "--remove-unused-variables",
                "--in-place",
                "--recursive",
                "app/",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Unused imports removed successfully")
            return True
        else:
            print(f"❌ Error removing unused imports: {result.stderr}")
            return False

    except FileNotFoundError:
        print("❌ autoflake not found. Installing...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "autoflake"], check=True
            )
            print("✅ autoflake installed successfully")
            return remove_unused_imports()  # Try again
        except subprocess.CalledProcessError:
            print("❌ Failed to install autoflake")
            return False


if __name__ == "__main__":
    success = remove_unused_imports()
    sys.exit(0 if success else 1)
