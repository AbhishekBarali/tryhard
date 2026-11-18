#!/usr/bin/env bash
# Follow Through installer.
#
# Adds the optional always-on Follow Through block to the Codex user
# instructions file (${CODEX_HOME:-~/.codex}/AGENTS.md) between marker lines,
# after saving a backup, and prints the Codex commands that install the plugin.
# Running it again updates the block in place. It changes nothing else.
#
#   ./install.sh            add or update the block, then print the next steps
#   ./install.sh --remove   take the block out again (backup first)
#   ./install.sh --help     show this help

set -euo pipefail

START_MARKER='<!-- follow-through:start -->'
END_MARKER='<!-- follow-through:end -->'
REPO='AbhishekBarali/follow-through'

usage() {
  sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'
}

mode=install
case "${1:-}" in
  "" | --install) ;;
  --remove | --uninstall) mode=remove ;;
  -h | --help)
    usage
    exit 0
    ;;
  *)
    echo "Unknown option: $1" >&2
    usage >&2
    exit 2
    ;;
esac

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
snippet="$script_dir/agents-md/AGENTS.snippet.md"
codex_dir="${CODEX_HOME:-$HOME/.codex}"
agents="$codex_dir/AGENTS.md"
status=0

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

backup() {
  local target
  target="$agents.bak-follow-through-$(date +%Y%m%d-%H%M%S)"
  if [ -e "$target" ]; then
    target="$target-$$"
  fi
  cp -p "$agents" "$target"
  echo "Saved a backup of $agents to $target"
}

has_start() { [ -f "$agents" ] && grep -qxF "$START_MARKER" "$agents"; }
has_end() { [ -f "$agents" ] && grep -qxF "$END_MARKER" "$agents"; }

# Print the current file with the marked block replaced by the file in $1
# (or removed when $1 is empty). Lines outside the block are kept as they are.
rewrite() {
  awk -v start="$START_MARKER" -v end="$END_MARKER" -v block="${1:-}" '
    $0 == start {
      if (block != "" && !written) { while ((getline line < block) > 0) print line }
      written = 1
      skipping = 1
      next
    }
    skipping && $0 == end { skipping = 0; next }
    !skipping { print }
  ' "$agents"
}

# Write $1 over AGENTS.md only if it differs, backing up the old file first.
apply() {
  local new="$1" what="$2"
  if [ -f "$agents" ] && cmp -s "$new" "$agents"; then
    echo "$agents already has the current Follow Through block. Nothing changed."
    return
  fi
  if [ -f "$agents" ]; then
    backup
  fi
  cat "$new" >"$agents"
  echo "$what $agents"
}

check_markers() {
  if has_start && ! has_end; then
    echo "$agents has the Follow Through start marker but no end marker, so the block can't be" >&2
    echo "updated safely. Fix or remove the lines starting with '<!-- follow-through:' and run this again." >&2
    exit 1
  fi
}

install_block() {
  if [ ! -f "$snippet" ]; then
    echo "The always-on block was not added: $snippet is missing." >&2
    echo "Run this script from a full copy of the repository (git clone https://github.com/$REPO)." >&2
    status=1
    return
  fi
  check_markers
  mkdir -p "$codex_dir"

  local block="$work/block.md" new="$work/AGENTS.md"
  {
    echo "$START_MARKER"
    grep -vxF -e "$START_MARKER" -e "$END_MARKER" "$snippet" || true
    echo "$END_MARKER"
  } >"$block"

  if has_start; then
    rewrite "$block" >"$new"
    apply "$new" "Updated the Follow Through block in"
  else
    if [ -s "$agents" ]; then
      cat "$agents" >"$new"
      # Keep one blank line between the existing text and the block.
      if [ -n "$(tail -c 1 "$agents")" ]; then
        echo >>"$new"
      fi
      echo >>"$new"
    else
      : >"$new"
    fi
    cat "$block" >>"$new"
    apply "$new" "Added the Follow Through block to"
  fi

  local size
  size=$(wc -c <"$agents" | tr -d ' ')
  if [ "$size" -gt 32768 ]; then
    echo "Note: $agents is now $size bytes. Codex reads at most 32 KiB of AGENTS.md text by default" >&2
    echo "(project_doc_max_bytes), so the end of the file may be cut off." >&2
  fi
  if [ -s "$codex_dir/AGENTS.override.md" ]; then
    echo "Note: $codex_dir/AGENTS.override.md exists and is not empty. Codex reads it instead of" >&2
    echo "AGENTS.md, so the Follow Through block won't load until you move it there or empty that file." >&2
  fi
}

remove_block() {
  if ! has_start; then
    echo "$agents has no Follow Through block. Nothing changed."
    return
  fi
  check_markers
  local new="$work/AGENTS.md"
  rewrite "" >"$new"
  apply "$new" "Removed the Follow Through block from"
}

print_steps() {
  cat <<EOF

Next steps for Codex:

  1. Add the marketplace and install the plugin:

       codex plugin marketplace add $REPO
       codex plugin add follow-through@follow-through

     From a local copy you can use the folder instead of the GitHub name:

       codex plugin marketplace add "$script_dir"

  2. Start Codex, type /hooks and trust the Follow Through Stop hook. Codex skips
     plugin hooks until you trust them, and asks again when an update changes the hook.

  3. Optional: use the higher-effort profile.

       cp "$script_dir/profiles/follow-through.config.toml" "$codex_dir/follow-through.config.toml"
       codex --profile follow-through

To turn the Stop hook off, start Codex with FOLLOW_THROUGH_HOOK=off. To run only some of
its checks, set FOLLOW_THROUGH_CHECKS to a list such as handback,own-work,readability.
EOF
}

print_remove_steps() {
  cat <<EOF

To remove the plugin as well:

  codex plugin remove follow-through@follow-through
  codex plugin marketplace remove follow-through
EOF
}

if [ "$mode" = remove ]; then
  remove_block
  print_remove_steps
else
  install_block
  print_steps
fi
exit "$status"
