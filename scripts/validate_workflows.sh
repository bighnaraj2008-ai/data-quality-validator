#!/usr/bin/env bash
#
# validate_workflows.sh - Validate GitHub Actions workflows locally.
#
# Uses actionlint when available, falling back to Python YAML syntax checks.
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> Validating GitHub Actions workflow files under .github/workflows/"

if command -v actionlint >/dev/null 2>&1; then
    actionlint .github/workflows/*.yml
    echo "==> actionlint validation passed"
else
    echo "actionlint not found; falling back to PyYAML syntax validation"
    python -c "
import glob, sys, yaml
files = sorted(glob.glob('.github/workflows/*.yml'))
assert files, 'No workflow YAML files found'
for wf in files:
    with open(wf, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    assert 'jobs' in data, f'{wf} missing jobs section'
    print(f'VALID: {wf}')
"
fi
