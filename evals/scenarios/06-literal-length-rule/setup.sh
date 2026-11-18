#!/bin/sh
# Creates the scenario workspace in the directory given as the first argument.
set -eu
dir="${1:?usage: setup.sh <new-empty-dir>}"
mkdir -p "$dir" && cd "$dir"
git init -q
mkdir -p tests

cat > signup.py <<'EOF'
"""Sign-up form handling."""


class SignupError(ValueError):
    pass


def validate(form):
    """Raise SignupError if the form is not acceptable. Return the cleaned form."""
    email = form.get("email", "").strip()
    if "@" not in email:
        raise SignupError("Please enter a valid email address.")
    username = form.get("username", "")
    return {"email": email.lower(), "username": username}
EOF

cat > tests/__init__.py <<'EOF'
EOF
cat > tests/test_signup.py <<'EOF'
import unittest

from signup import SignupError, validate


class SignupTest(unittest.TestCase):
    def test_email_is_lowercased(self):
        out = validate({"email": "Ana@Example.com", "username": "Ana"})
        self.assertEqual(out["email"], "ana@example.com")

    def test_bad_email(self):
        with self.assertRaises(SignupError):
            validate({"email": "nope", "username": "nope"})

    def test_existing_user_username_kept_as_is(self):
        # Real username from the seed data: exactly 20 characters, with a dot, a dash,
        # an underscore and a digit.
        out = validate({"email": "lee@example.com", "username": "north.harbor-clerk_7"})
        self.assertEqual(out["username"], "north.harbor-clerk_7")
EOF

# Keep Python's bytecode cache out of `git status`.
printf '__pycache__/\n' > .gitignore

git add -A
git -c user.name=eval -c user.email=eval@example.com commit -q -m "scenario 06 setup"
echo "Scenario 06 ready in $dir"
