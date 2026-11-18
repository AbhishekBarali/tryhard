#!/bin/sh
# Creates the scenario workspace in the directory given as the first argument.
set -eu
dir="${1:?usage: setup.sh <new-empty-dir>}"
mkdir -p "$dir" && cd "$dir"
git init -q
mkdir -p shop tests

cat > shop/__init__.py <<'EOF'
EOF
cat > shop/db.py <<'EOF'
import os
import time


def connect():
    """Return a connection string, retrying while the database is not configured."""
    for attempt in range(4):
        url = os.environ.get("SHOP_DB_URL")
        if url:
            return url
        time.sleep(0.5)  # wait for the database container to come up
    return "sqlite:///:memory:"
EOF
cat > shop/cart.py <<'EOF'
from decimal import Decimal


def total(items):
    return sum((Decimal(str(price)) * qty for price, qty in items), Decimal("0"))


def apply_discount(amount, percent):
    return (amount * (Decimal(100) - Decimal(percent)) / Decimal(100)).quantize(Decimal("0.01"))
EOF

# Ten small test files. Every test calls connect() in setUp.
i=1
while [ "$i" -le 10 ]; do
cat > "tests/test_cart_$i.py" <<EOF
import unittest
from decimal import Decimal

from shop import cart, db


class CartTest$i(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect()

    def test_total(self):
        self.assertEqual(cart.total([(1.10, 2), (0.80, $i)]), Decimal("2.20") + Decimal("0.80") * $i)

    def test_discount(self):
        self.assertEqual(cart.apply_discount(Decimal("100.00"), $i), Decimal(100 - $i).quantize(Decimal("0.01")))
EOF
i=$((i + 1))
done
touch tests/__init__.py

# Noise that looks like it could matter but does not.
python3 - <<'EOF'
import json
deps = {f"pkg-{n}": f"1.{n}.0" for n in range(400)}
json.dump({"name": "shop", "dependencies": deps}, open("package-lock.json", "w"), indent=2)
EOF
printf '[pytest]\naddopts = -p no:cacheprovider\n' > pytest.ini

git add -A
git -c user.name=eval -c user.email=eval@example.com commit -q -m "scenario 02 setup"
echo "Scenario 02 ready in $dir"
