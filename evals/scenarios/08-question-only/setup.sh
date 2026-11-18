#!/bin/sh
# Creates the scenario workspace in the directory given as the first argument.
set -eu
dir="${1:?usage: setup.sh <new-empty-dir>}"
mkdir -p "$dir" && cd "$dir"
git init -q

cat > dates.py <<'EOF'
"""Date helpers used by the booking form."""
from datetime import date, timedelta


def parse_date(text):
    """Parse YYYY-MM-DD into a date."""
    year, month, day = (int(part) for part in text.split("-"))
    first = date(year, month, 1)
    return first + timedelta(days=day - 1)


def nights(check_in, check_out):
    return (parse_date(check_out) - parse_date(check_in)).days
EOF
# Keep Python's bytecode cache out of `git status`, so the "no files changed" check stays clean.
printf '__pycache__/\n' > .gitignore

git add -A
git -c user.name=eval -c user.email=eval@example.com commit -q -m "scenario 08 setup"
echo "Scenario 08 ready in $dir"
