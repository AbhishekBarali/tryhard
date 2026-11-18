#!/bin/sh
# Creates the scenario workspace in the directory given as the first argument.
set -eu
dir="${1:?usage: setup.sh <new-empty-dir>}"
mkdir -p "$dir" && cd "$dir"
git init -q
mkdir -p data

cat > report.py <<'EOF'
"""Print the top customers by total spend from a CSV of orders."""
import argparse
import csv
from collections import defaultdict


def build(path):
    totals = defaultdict(float)
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            totals[row["customer"]] += float(row["amount"])
    return sorted(totals.items(), key=lambda kv: kv[1], reverse=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    rows = build(args.csv)
    for customer, total in rows:
        print(f"{customer:<12} {total:>10.2f}")


if __name__ == "__main__":
    main()
EOF

cat > README.md <<'EOF'
# report

    python3 report.py data/orders.csv [--top N]

Prints customers sorted by total spend. `--top` defaults to 5.
EOF

python3 - <<'EOF'
import csv, random
random.seed(3)
names = ["acme", "birch", "cobalt", "delta", "ember", "fjord", "garnet", "harbor", "indigo", "juniper",
         "kestrel", "linden", "maple", "nimbus", "onyx"]
with open("data/orders.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["customer", "amount"])
    for _ in range(200):
        w.writerow([random.choice(names), f"{random.uniform(5, 500):.2f}"])
EOF

git add -A
git -c user.name=eval -c user.email=eval@example.com commit -q -m "scenario 07 setup"
echo "Scenario 07 ready in $dir"
