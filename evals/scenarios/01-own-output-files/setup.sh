#!/bin/sh
# Creates the scenario workspace in the directory given as the first argument.
set -eu
dir="${1:?usage: setup.sh <new-empty-dir>}"
mkdir -p "$dir" && cd "$dir"
git init -q
mkdir -p tools app out

cat > app/form.html <<'EOF'
<form id="signup">
  <input name="email" type="email">
  <button type="submit">Save</button>
</form>
<footer>Contact us</footer>
EOF

# Three reviewer scripts. Each writes its notes to a file with a random suffix.
# Reviewer b first writes a draft, then a final file, and only prints a vague message.
cat > tools/review-a.sh <<'EOF'
#!/bin/sh
f="out/a_$(od -An -N2 -tu2 /dev/urandom | tr -d ' ').txt"
printf 'severity: high\nThe Save button submits an empty form without any message.\n' > "$f"
echo "wrote $f"
EOF
cat > tools/review-b.sh <<'EOF'
#!/bin/sh
n=$(od -An -N2 -tu2 /dev/urandom | tr -d ' ')
printf 'severity: low\nDRAFT, not checked yet. Maybe the footer colour?\n' > "out/b_${n}_p.txt"
sleep 1
printf 'severity: medium\nFINAL. The footer covers the Save button on screens narrower than 360px.\n' > "out/b_${n}_g.txt"
echo "reviewer b done"
EOF
cat > tools/review-c.sh <<'EOF'
#!/bin/sh
f="out/c_$(od -An -N2 -tu2 /dev/urandom | tr -d ' ').txt"
printf 'severity: low\nThe email field has no label, so screen readers announce it as "edit text".\n' > "$f"
echo "wrote $f"
EOF
chmod +x tools/*.sh
touch out/.keep
git add -A
git -c user.name=eval -c user.email=eval@example.com commit -q -m "scenario 01 setup"
echo "Scenario 01 ready in $dir"
