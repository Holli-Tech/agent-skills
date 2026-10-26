#!/usr/bin/env bash
# Extract every filename example from the docs and validate it.
# Mirrors the CI step — kept here so it can be run locally before pushing.
set -u
cd "$(dirname "$0")"
ROOT=..
extracted=$(mktemp)
grep -rhoE '[A-Za-z0-9-]+(_[A-Za-z0-9-]+)+\.[0-9]+\.[a-z]{2,4}' \
    "$ROOT/SKILL.md" "$ROOT/README.md" "$ROOT/references/"*.md \
    | sort -u > "$extracted"
total=$(wc -l < "$extracted")
echo "Found $total candidate filename examples in the docs"
if [ "$total" -eq 0 ]; then
    echo "::error::no filename examples found — the extraction pattern is stale"
    exit 1
fi
failed=0
while read -r name; do
    if ! python3 validate_name.py "$name" >/dev/null 2>&1; then
        echo "INVALID: $name"
        python3 validate_name.py "$name" 2>&1 | sed 's/^/    /'
        failed=$((failed + 1))
    fi
done < "$extracted"
echo "$((total - failed))/$total examples validate"
[ "$failed" -eq 0 ]
