#!/usr/bin/env python3
"""
API client script for SkogCLI.
"""
import json
import sys
import requests
from urllib.parse import urljoin

BASE_URL = "https://api.example.com"  # Replace with your API base URL


def make_request(endpoint, method="GET", data=None, params=None):
    """Make an API request."""
    url = urljoin(BASE_URL, endpoint)
    headers = {
        "Content-Type": "application/json",
        # Add any authentication headers here
    }

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            print(f"Error: Unsupported method {method}")
            return None

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def main(args=None):
    """Main entry point for the script."""
    if args is None or len(args) < 1:
        print("Usage: script endpoint [method] [data]")
        return

    endpoint = args[0]
    method = args[1].upper() if len(args) > 1 else "GET"
    data = None

    if len(args) > 2 and (method == "POST" or method == "PUT"):
        try:
            data = json.loads(args[2])
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON data: {args[2]}")
            return

    result = make_request(endpoint, method, data)
    if result:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
