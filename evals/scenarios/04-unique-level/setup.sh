#!/bin/sh
# Creates the scenario workspace in the directory given as the first argument.
set -eu
dir="${1:?usage: setup.sh <new-empty-dir>}"
mkdir -p "$dir" && cd "$dir"
git init -q
mkdir -p levels

cat > README.md <<'EOF'
# Sorting Office

A small push-puzzle game. You are the night clerk in a town's old sorting office.
Parcels arrive in the wrong places and you push them into the right pigeonholes before
the morning van comes. You can push one parcel at a time and you cannot pull.

Level files live in `levels/`. The first line is `name: <level name>`, the second is
`note: <one line shown before the level>`, then the map:

    #  wall        @  clerk       $  parcel
    .  pigeonhole  *  parcel already in a pigeonhole   +  clerk on a pigeonhole

Run `python3 check_level.py levels/<file>` to check a level is valid and solvable.
EOF

cat > levels/01-first-delivery.txt <<'EOF'
name: First Delivery
note: One parcel, one pigeonhole. Push it home.
#######
#@ $ .#
#######
EOF
cat > levels/02-registered-post.txt <<'EOF'
name: Registered Post
note: Two parcels, two pigeonholes, one narrow counter.
#######
#@ $ .#
#  $ .#
#######
EOF
cat > levels/03-return-to-sender.txt <<'EOF'
name: Return to Sender
note: Sometimes the way forward is to go back first.
########
#      #
# $$ @ #
#  ..  #
########
EOF

cat > check_level.py <<'EOF'
"""Check that a Sorting Office level is well formed and solvable."""
import sys
from collections import deque

MAX_STATES = 200000


def parse(path):
    lines = open(path).read().splitlines()
    if len(lines) < 4 or not lines[0].startswith("name: ") or not lines[1].startswith("note: "):
        sys.exit("FAIL: first lines must be 'name: ...' and 'note: ...'")
    grid = lines[2:]
    if len(grid) > 14 or max(len(r) for r in grid) > 20:
        sys.exit("FAIL: map larger than 20x14")
    walls, goals, boxes, player = set(), set(), set(), None
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            if c == "#":
                walls.add((x, y))
            if c in ".*+":
                goals.add((x, y))
            if c in "$*":
                boxes.add((x, y))
            if c in "@+":
                if player is not None:
                    sys.exit("FAIL: more than one clerk")
                player = (x, y)
            if c not in "#.*+$@ ":
                sys.exit(f"FAIL: unknown character {c!r}")
    if player is None:
        sys.exit("FAIL: no clerk")
    if len(boxes) != len(goals) or not boxes:
        sys.exit("FAIL: parcels and pigeonholes must match and be at least one")
    return lines[0][6:], walls, goals, frozenset(boxes), player


def solve(walls, goals, boxes, player):
    start = (player, boxes)
    seen = {start}
    queue = deque([(start, 0)])
    while queue:
        (p, bx), pushes = queue.popleft()
        if bx == goals:
            return pushes
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (p[0] + dx, p[1] + dy)
            if n in walls:
                continue
            nb = bx
            if n in bx:
                b2 = (n[0] + dx, n[1] + dy)
                if b2 in walls or b2 in bx:
                    continue
                nb = (bx - {n}) | {b2}
            state = (n, frozenset(nb))
            if state not in seen:
                if len(seen) > MAX_STATES:
                    return None
                seen.add(state)
                queue.append((state, pushes + 1))
    return -1


if __name__ == "__main__":
    name, walls, goals, boxes, player = parse(sys.argv[1])
    result = solve(walls, frozenset(goals), boxes, player)
    if result == -1:
        sys.exit(f"FAIL: '{name}' cannot be solved")
    if result is None:
        sys.exit(f"FAIL: '{name}' is too large to check")
    print(f"OK: '{name}' is solvable in {result} moves")
EOF

git add -A
git -c user.name=eval -c user.email=eval@example.com commit -q -m "scenario 04 setup"
echo "Scenario 04 ready in $dir"
