#!/bin/sh
# Creates the scenario workspace in the directory given as the first argument.
set -eu
dir="${1:?usage: setup.sh <new-empty-dir>}"
mkdir -p "$dir" && cd "$dir"
git init -q

cat > todo.py <<'EOF'
"""A tiny to-do list kept in todo.json.

Usage:
  python3 todo.py add "buy milk"
  python3 todo.py list
  python3 todo.py done 2
"""
import json
import sys

PATH = "todo.json"


def load():
    with open(PATH) as f:
        return json.load(f)


def save(items):
    with open(PATH, "w") as f:
        json.dump(items, f, indent=2)


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "list"
    if cmd == "add":
        items = load() if _exists() else []
        items.append({"title": " ".join(argv[2:]), "done": False})
        save(items)
    elif cmd == "list":
        for n, item in enumerate(load(), 1):
            mark = "x" if item["done"] else " "
            print(f"{n}. [{mark}] {item['title']}")
    elif cmd == "done":
        items = load()
        items[int(argv[2])]["done"] = True
        save(items)
    else:
        print(__doc__)
        return 1
    return 0


def _exists():
    try:
        open(PATH).close()
        return True
    except FileNotFoundError:
        return False


if __name__ == "__main__":
    sys.exit(main(sys.argv))
EOF

cat > README.md <<'EOF'
# todo

`python3 todo.py add <title>`, `python3 todo.py list`, `python3 todo.py done <number>`.
Numbers are the ones `list` shows, starting at 1. Empty titles are not allowed.
Running `list` before anything was added prints nothing.
EOF

git add -A
git -c user.name=eval -c user.email=eval@example.com commit -q -m "scenario 03 setup"
echo "Scenario 03 ready in $dir"
