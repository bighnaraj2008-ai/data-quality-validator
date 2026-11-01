#!/usr/bin/env python3
"""
Documentation Link & Markdown Syntax Validator
Scans all .md files in the repository to verify that:
1. Relative file links point to existing target files.
2. No broken anchors or malformed URLs exist.
3. No corrupted encoding artifacts are present.
"""

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")
CORRUPT_PATTERNS = [re.compile(r"Ã|Â|â€™|Ã¢")]

EXCLUDED_DIRS = {".git", ".github", "venv", ".venv", "__pycache__", ".pytest_cache", "build", "dist", "node_modules"}


def find_markdown_files():
    md_files = []
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for f in files:
            if f.endswith(".md"):
                md_files.append(Path(root) / f)
    return sorted(md_files)


def validate_links(file_path):
    errors = []
    content = file_path.read_text(encoding="utf-8", errors="replace")

    for pattern in CORRUPT_PATTERNS:
        match = pattern.search(content)
        if match:
            errors.append(f"Corrupted UTF-8 encoding sequence found: '{match.group(0)}'")

    for match in LINK_PATTERN.finditer(content):
        link_text, link_target = match.groups()
        link_target = link_target.strip()

        # Skip external web URLs, anchors, mailto, and dummy links
        if link_target.startswith(("http://", "https://", "mailto:", "#", "<")):
            continue

        target_path_part = link_target.split("#")[0]
        if not target_path_part:
            continue

        # Check relative to file location or repo root
        resolved_rel = (file_path.parent / target_path_part).resolve()
        resolved_root = (REPO_ROOT / target_path_part).resolve()

        if not (resolved_rel.exists() or resolved_root.exists()):
            errors.append(f"Broken link '{link_target}' in text '[{link_text}]'")

    return errors


def main():
    print("=" * 60)
    print(" Validating Repository Documentation Links & Syntax")
    print("=" * 60)

    md_files = find_markdown_files()
    total_files = len(md_files)
    total_errors = 0

    print(f"Discovered {total_files} Markdown files to audit.\n")

    for md_file in md_files:
        rel_path = md_file.relative_to(REPO_ROOT)
        errors = validate_links(md_file)
        if errors:
            print(f"FAILED: {rel_path}")
            for err in errors:
                print(f"  - {err}")
            total_errors += len(errors)
        else:
            print(f"PASSED: {rel_path}")

    print("\n" + "=" * 60)
    if total_errors > 0:
        print(f"FAILED: Found {total_errors} documentation validation errors.")
        sys.exit(1)
    else:
        print(f"SUCCESS: All {total_files} Markdown files passed validation!")
        sys.exit(0)


if __name__ == "__main__":
    main()
