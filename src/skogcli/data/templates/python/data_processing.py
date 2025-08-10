#!/usr/bin/env python3
"""
Data processing script for SkogCLI.
"""

import csv
import json
import sys
from pathlib import Path


def process_json(input_file, output_file=None):
    """Process JSON data."""
    with open(input_file, "r") as f:
        data = json.load(f)

    # Process the data here
    processed_data = data

    if output_file:
        with open(output_file, "w") as f:
            json.dump(processed_data, f, indent=2)
        print(f"Processed data written to {output_file}")
    else:
        print(json.dumps(processed_data, indent=2))


def process_csv(input_file, output_file=None):
    """Process CSV data."""
    rows = []
    with open(input_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Process the data here
    processed_rows = rows

    if output_file:
        with open(output_file, "w") as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(processed_rows)
        print(f"Processed data written to {output_file}")
    else:
        for row in processed_rows:
            print(row)


def main(args=None):
    """Main entry point for the script."""
    if args is None or len(args) < 1:
        print("Usage: script input_file [output_file]")
        return

    input_file = args[0]
    output_file = args[1] if len(args) > 1 else None

    if not Path(input_file).exists():
        print(f"Error: Input file {input_file} does not exist")
        return

    if input_file.endswith(".json"):
        process_json(input_file, output_file)
    elif input_file.endswith(".csv"):
        process_csv(input_file, output_file)
    else:
        print(f"Error: Unsupported file format for {input_file}")


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
