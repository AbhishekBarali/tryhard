#!/bin/sh
# Creates the scenario workspace in the directory given as the first argument.
set -eu
dir="${1:?usage: setup.sh <new-empty-dir>}"
mkdir -p "$dir" && cd "$dir"
git init -q

cat > notes.py <<'EOF'
"""Quick notes kept in notes.json.

Usage:
  python3 notes.py add "call the plumber"
  python3 notes.py list
  python3 notes.py delete 2
"""
import json
import os
import sys

PATH = "notes.json"


def load():
    if not os.path.exists(PATH):
        return []
    with open(PATH) as f:
        return json.load(f)


def save(notes):
    with open(PATH, "w") as f:
        json.dump(notes, f, indent=2)


def show(number, note):
    print(f"{number}. {note}")


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "list"
    notes = load()
    if cmd == "add":
        text = " ".join(argv[2:]).strip()
        if not text:
            print("Usage: python3 notes.py add <text>")
            return 1
        notes.append(text)
        save(notes)
    elif cmd == "list":
        for number, note in enumerate(notes, 1):
            show(number, note)
    elif cmd == "delete":
        if len(argv) != 3 or not argv[2].isdigit() or not 1 <= int(argv[2]) <= len(notes):
            print("Usage: python3 notes.py delete <number from list>")
            return 1
        del notes[int(argv[2]) - 1]
        save(notes)
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
EOF

cat > README.md <<'EOF'
# notes

A tiny notes tool. Notes are kept in `notes.json` in the current folder.

- `python3 notes.py add <text>` adds a note.
- `python3 notes.py list` shows every note with its number.
- `python3 notes.py delete <number>` deletes the note with that number from `list`.
EOF

cat > notes.json <<'EOF'
[
  "Call the plumber about the kitchen tap",
  "Buy bread",
  "Plumber said Thursday after 3",
  "Renew the library card"
]
EOF

# Keep Python's bytecode cache out of `git status`.
printf '__pycache__/\n' > .gitignore
git add -A
git -c user.name=eval -c user.email=eval@example.com commit -q -m "scenario 10 setup"
echo "Scenario 10 ready in $dir"
