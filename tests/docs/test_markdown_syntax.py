"""
Automated Markdown Syntax & Link Integrity Test
Verifies that all documentation files adhere to GitHub Flavored Markdown standards,
have valid titles, and contain no broken relative links or corrupted characters.
"""

import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

EXCLUDED_DIRS = {".git", ".github", "venv", ".venv", "__pycache__", ".pytest_cache", "build", "dist"}
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")
CORRUPT_PATTERN = re.compile(r"Ã|Â|â€™|Ã¢")


def get_all_markdown_files():
    files = []
    for root, dirs, filenames in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for f in filenames:
            if f.endswith(".md"):
                files.append(Path(root) / f)
    return files


def test_markdown_files_exist():
    md_files = get_all_markdown_files()
    assert len(md_files) >= 15, f"Expected at least 15 markdown files, found {len(md_files)}"


def test_markdown_files_have_h1():
    for f in get_all_markdown_files():
        content = f.read_text(encoding="utf-8", errors="replace")
        first_line = content.strip().splitlines()[0] if content.strip() else ""
        assert first_line.startswith("#"), f"{f} must start with an H1 header, found '{first_line}'"


def test_no_corrupted_characters():
    for f in get_all_markdown_files():
        content = f.read_text(encoding="utf-8", errors="replace")
        match = CORRUPT_PATTERN.search(content)
        assert match is None, f"Found corrupted character sequence in {f}: {match.group(0)}"


def test_internal_links_resolve():
    for f in get_all_markdown_files():
        content = f.read_text(encoding="utf-8", errors="replace")
        for match in LINK_PATTERN.finditer(content):
            _, target = match.groups()
            target = target.strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part = target.split("#")[0]
            if not path_part:
                continue
            rel_path = (f.parent / path_part).resolve()
            root_path = (REPO_ROOT / path_part).resolve()
            assert rel_path.exists() or root_path.exists(), f"Broken link '{target}' in {f}"
