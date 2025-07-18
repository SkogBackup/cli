#!/usr/bin/env python3
"""
Line counting script for files and directories.
"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional


def count_lines_in_file(file_path: Path) -> Tuple[int, int, int]:
    """
    Count the number of lines, blank lines, and comment lines in a file.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (total lines, blank lines, comment lines)
    """
    if not file_path.exists():
        print(f"Error: File {file_path} does not exist")
        return (0, 0, 0)

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if line.strip() == "")

        # Count comment lines based on file extension
        comment_lines = 0
        ext = file_path.suffix.lower()

        # Define comment markers for different file types
        comment_markers = {
            ".py": "#",
            ".js": "//",
            ".java": "//",
            ".c": "//",
            ".cpp": "//",
            ".h": "//",
            ".sh": "#",
            ".rb": "#",
            ".pl": "#",
            ".php": "//",
            ".html": "<!--",
            ".xml": "<!--",
            ".css": "/*",
        }

        if ext in comment_markers:
            marker = comment_markers[ext]
            comment_lines = sum(1 for line in lines if line.strip().startswith(marker))

        return (total_lines, blank_lines, comment_lines)

    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return (0, 0, 0)


def count_lines_in_directory(
    dir_path: Path, extensions: Optional[List[str]] = None
) -> Dict[str, Tuple[int, int, int]]:
    """
    Count lines in all files in a directory (recursively).

    Args:
        dir_path: Path to the directory
        extensions: List of file extensions to include (e.g., ['.py', '.js'])
                   If None, count all files

    Returns:
        Dictionary mapping file paths to line counts
    """
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"Error: Directory {dir_path} does not exist or is not a directory")
        return {}

    results = {}

    try:
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = Path(root) / file

                # Skip if we're filtering by extension and this file doesn't match
                if extensions and not any(
                    file.lower().endswith(ext) for ext in extensions
                ):
                    continue

                # Skip binary files and very large files
                if file_path.stat().st_size > 1024 * 1024:  # Skip files > 1MB
                    continue

                try:
                    # Try to read the first few bytes to check if it's binary
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        f.read(1024)

                    # If we got here, it's probably a text file
                    line_counts = count_lines_in_file(file_path)
                    if line_counts[0] > 0:  # Only include files with lines
                        results[str(file_path)] = line_counts

                except UnicodeDecodeError:
                    # Probably a binary file
                    continue
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

    except Exception as e:
        print(f"Error scanning directory {dir_path}: {str(e)}")

    return results


def print_summary(results: Dict[str, Tuple[int, int, int]]) -> None:
    """Print a summary of the line counting results."""
    if not results:
        print("No files found or processed.")
        return

    # Calculate totals
    total_files = len(results)
    total_lines = sum(counts[0] for counts in results.values())
    total_blank = sum(counts[1] for counts in results.values())
    total_comments = sum(counts[2] for counts in results.values())
    total_code = total_lines - total_blank - total_comments

    # Print summary
    print(f"\nSummary:")
    print(f"  Total files: {total_files}")
    print(f"  Total lines: {total_lines}")
    print(f"  Code lines: {total_code}")
    print(f"  Blank lines: {total_blank}")
    print(f"  Comment lines: {total_comments}")

    if total_lines > 0:
        print(f"\nPercentages:")
        print(f"  Code: {total_code / total_lines * 100:.1f}%")
        print(f"  Comments: {total_comments / total_lines * 100:.1f}%")
        print(f"  Blank: {total_blank / total_lines * 100:.1f}%")


def main(args=None):
    """Main entry point for the script."""
    if args is None or len(args) == 0:
        print("Usage: count_lines [file_or_directory] [extension1,extension2,...]")
        print("Examples:")
        print("  count_lines myfile.py")
        print("  count_lines src/")
        print("  count_lines src/ .py,.js,.html")
        return

    path = Path(args[0])

    # Parse extensions if provided
    extensions = None
    if len(args) > 1 and args[1]:
        extensions = [
            ext if ext.startswith(".") else f".{ext}" for ext in args[1].split(",")
        ]
        print(f"Filtering by extensions: {', '.join(extensions)}")

    if path.is_file():
        # Count lines in a single file
        total, blank, comments = count_lines_in_file(path)
        code = total - blank - comments

        print(f"File: {path}")
        print(f"  Total lines: {total}")
        print(f"  Code lines: {code}")
        print(f"  Blank lines: {blank}")
        print(f"  Comment lines: {comments}")

    elif path.is_dir():
        # Count lines in a directory
        print(f"Scanning directory: {path}")
        results = count_lines_in_directory(path, extensions)

        # Print detailed results for each file
        for file_path, (total, blank, comments) in sorted(results.items()):
            code = total - blank - comments
            rel_path = Path(file_path).relative_to(path)
            print(
                f"{rel_path}: {total} lines ({code} code, {blank} blank, {comments} comments)"
            )

        # Print summary
        print_summary(results)

    else:
        print(f"Error: {path} does not exist")


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
