#!/usr/bin/env bash
#
# bump_version.sh - Bump semantic version in pyproject.toml.
#
# Usage:
#   ./scripts/bump_version.sh 0.2.0
#
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <new_version>" >&2
    exit 1
fi

NEW_VERSION="$1"
if [[ ! "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version must match X.Y.Z semantic format" >&2
    exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYPROJECT="$ROOT_DIR/pyproject.toml"

python -c "
from pathlib import Path
import re
p = Path(r'$PYPROJECT')
text = p.read_text(encoding='utf-8')
updated, count = re.subn(r'^version\s*=\s*"[^"]+"', 'version = "$NEW_VERSION"', text, count=1, flags=re.MULTILINE)
assert count == 1, 'Could not locate version line in pyproject.toml'
p.write_text(updated, encoding='utf-8')
print('Updated pyproject.toml version to $NEW_VERSION')
"
