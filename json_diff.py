#!/usr/bin/env python3
"""
JSON Diff Tool — Highlights differences between two JSON inputs.

Usage:
    python json_diff.py                              # interactive mode
    python json_diff.py file1.json file2.json        # file mode
    python json_diff.py --json1 '{"a":1}' --json2 '{"a":2}'  # inline mode
"""

import argparse
import json
import sys
from typing import Any


# ANSI color codes
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def format_value(value: Any, indent: int = 0) -> str:
    """Format a JSON value for display."""
    return json.dumps(value, indent=2, sort_keys=True).replace(
        "\n", "\n" + " " * indent
    )


def diff_json(
    obj1: Any,
    obj2: Any,
    path: str = "$",
    results: list | None = None,
) -> list[dict]:
    """
    Recursively compare two JSON objects and collect differences.

    Each difference is a dict with keys:
        path  — JSON path (e.g. $.settings.theme)
        type  — "added", "removed", "changed", "type_changed"
        old   — previous value (if applicable)
        new   — new value (if applicable)
    """
    if results is None:
        results = []

    if type(obj1) != type(obj2):
        results.append(
            {
                "path": path,
                "type": "type_changed",
                "old": obj1,
                "new": obj2,
                "old_type": type(obj1).__name__,
                "new_type": type(obj2).__name__,
            }
        )
        return results

    if isinstance(obj1, dict):
        all_keys = sorted(set(list(obj1.keys()) + list(obj2.keys())))
        for key in all_keys:
            child_path = f"{path}.{key}"
            if key not in obj1:
                results.append({"path": child_path, "type": "added", "new": obj2[key]})
            elif key not in obj2:
                results.append(
                    {"path": child_path, "type": "removed", "old": obj1[key]}
                )
            else:
                diff_json(obj1[key], obj2[key], child_path, results)

    elif isinstance(obj1, list):
        max_len = max(len(obj1), len(obj2))
        for i in range(max_len):
            child_path = f"{path}[{i}]"
            if i >= len(obj1):
                results.append({"path": child_path, "type": "added", "new": obj2[i]})
            elif i >= len(obj2):
                results.append(
                    {"path": child_path, "type": "removed", "old": obj1[i]}
                )
            else:
                diff_json(obj1[i], obj2[i], child_path, results)

    else:
        if obj1 != obj2:
            results.append(
                {"path": path, "type": "changed", "old": obj1, "new": obj2}
            )

    return results


def print_diff(diffs: list[dict], use_color: bool = True) -> None:
    """Pretty-print the list of differences with color-coded output."""
    c = Colors if use_color else type("C", (), {k: "" for k in dir(Colors) if not k.startswith("_")})()

    if not diffs:
        print(f"\n{c.GREEN}{c.BOLD}✓ No differences found — the two JSONs are identical.{c.RESET}\n")
        return

    print(f"\n{c.BOLD}Found {len(diffs)} difference(s):{c.RESET}\n")
    print(f"{'─' * 60}")

    for diff in diffs:
        path = diff["path"]
        dtype = diff["type"]

        if dtype == "added":
            symbol = "+"
            color = c.GREEN
            label = "ADDED"
            print(f"\n{color}{c.BOLD}{symbol} [{label}]{c.RESET} {c.CYAN}{path}{c.RESET}")
            print(f"  {c.GREEN}Value: {format_value(diff['new'], indent=9)}{c.RESET}")

        elif dtype == "removed":
            symbol = "-"
            color = c.RED
            label = "REMOVED"
            print(f"\n{color}{c.BOLD}{symbol} [{label}]{c.RESET} {c.CYAN}{path}{c.RESET}")
            print(f"  {c.RED}Value: {format_value(diff['old'], indent=9)}{c.RESET}")

        elif dtype == "changed":
            symbol = "~"
            color = c.YELLOW
            label = "CHANGED"
            print(f"\n{color}{c.BOLD}{symbol} [{label}]{c.RESET} {c.CYAN}{path}{c.RESET}")
            print(f"  {c.RED}Old: {format_value(diff['old'], indent=7)}{c.RESET}")
            print(f"  {c.GREEN}New: {format_value(diff['new'], indent=7)}{c.RESET}")

        elif dtype == "type_changed":
            symbol = "!"
            color = c.YELLOW
            label = "TYPE CHANGED"
            print(
                f"\n{color}{c.BOLD}{symbol} [{label}]{c.RESET} {c.CYAN}{path}{c.RESET}"
                f" {c.DIM}({diff['old_type']} → {diff['new_type']}){c.RESET}"
            )
            print(f"  {c.RED}Old: {format_value(diff['old'], indent=7)}{c.RESET}")
            print(f"  {c.GREEN}New: {format_value(diff['new'], indent=7)}{c.RESET}")

    print(f"\n{'─' * 60}")
    added = sum(1 for d in diffs if d["type"] == "added")
    removed = sum(1 for d in diffs if d["type"] == "removed")
    changed = sum(1 for d in diffs if d["type"] in ("changed", "type_changed"))
    print(
        f"{c.BOLD}Summary:{c.RESET} "
        f"{c.GREEN}+{added} added{c.RESET}  "
        f"{c.RED}-{removed} removed{c.RESET}  "
        f"{c.YELLOW}~{changed} changed{c.RESET}\n"
    )


def load_json(source: str) -> Any:
    """Load JSON from a file path or a raw JSON string."""
    try:
        with open(source) as f:
            return json.load(f)
    except FileNotFoundError:
        pass
    except IsADirectoryError:
        pass

    try:
        return json.loads(source)
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse JSON — {e}", file=sys.stderr)
        sys.exit(1)


def read_json_interactively(label: str) -> Any:
    """Prompt the user to enter JSON interactively, supporting multi-line input."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}Enter {label} JSON{Colors.RESET}")
    print(f"{Colors.DIM}(paste your JSON, then press Enter on an empty line to finish){Colors.RESET}")

    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "" and lines:
            break
        lines.append(line)

    raw = "\n".join(lines).strip()
    if not raw:
        print("Error: No JSON provided.", file=sys.stderr)
        sys.exit(1)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON — {e}", file=sys.stderr)
        sys.exit(1)


def interactive_mode() -> None:
    """Run the tool interactively, prompting the user for JSON inputs."""
    print(f"\n{Colors.BOLD}{'═' * 50}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}  JSON Diff Tool — Interactive Mode{Colors.RESET}")
    print(f"{Colors.BOLD}{'═' * 50}{Colors.RESET}")

    obj1 = read_json_interactively("first")
    obj2 = read_json_interactively("second")

    diffs = diff_json(obj1, obj2)
    print_diff(diffs)

    # Ask if the user wants to compare again
    print(f"{Colors.DIM}Compare another pair? (y/n): {Colors.RESET}", end="")
    try:
        answer = input().strip().lower()
    except EOFError:
        answer = "n"

    if answer in ("y", "yes"):
        interactive_mode()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Highlight differences between two JSON inputs."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Two JSON file paths to compare.",
    )
    parser.add_argument("--json1", help="First JSON as a string.")
    parser.add_argument("--json2", help="Second JSON as a string.")
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable color output.",
    )
    parser.add_argument(
        "--output-json",
        action="store_true",
        help="Output diff as machine-readable JSON.",
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Run in interactive mode (prompt for JSON inputs).",
    )

    args = parser.parse_args()

    # Interactive mode: no args provided or --interactive flag
    if args.interactive or (not args.json1 and not args.json2 and len(args.files) == 0):
        interactive_mode()
        return

    # Determine sources
    if args.json1 and args.json2:
        source1, source2 = args.json1, args.json2
    elif len(args.files) == 2:
        source1, source2 = args.files
    else:
        parser.error(
            "Provide two JSON file paths as positional args, "
            "or use --json1 and --json2."
        )

    obj1 = load_json(source1)
    obj2 = load_json(source2)

    diffs = diff_json(obj1, obj2)

    if args.output_json:
        print(json.dumps(diffs, indent=2, default=str))
    else:
        print_diff(diffs, use_color=not args.no_color)


if __name__ == "__main__":
    main()
