#!/bin/sh
# Creates the scenario workspace in the directory given as the first argument.
set -eu
dir="${1:?usage: setup.sh <new-empty-dir>}"
mkdir -p "$dir" && cd "$dir"
git init -q

cat > README.md <<'EOF'
# games

Small games that run straight from a file in the browser.
EOF

git add -A
git -c user.name=eval -c user.email=eval@example.com commit -q -m "scenario 09 setup"
echo "Scenario 09 ready in $dir"
