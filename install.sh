#!/usr/bin/env bash
# Tryhard installer.
#
# Adds the optional always-on Tryhard block to the Codex user
# instructions file (${CODEX_HOME:-~/.codex}/AGENTS.md) between marker lines,
# after saving a backup, and prints the Codex commands that install the plugin.
# Running it again updates the block in place. It changes nothing else.
#
#   ./install.sh            add or update the block, then print the next steps
#   ./install.sh --remove   take the block out again (backup first)
#   ./install.sh --help     show this help

set -euo pipefail

START_MARKER='<!-- tryhard:start -->'
END_MARKER='<!-- tryhard:end -->'
REPO='AbhishekBarali/tryhard'

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

# CDPATH= keeps cd from printing the folder when CDPATH is exported.
script_dir="$(CDPATH='' cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
snippet="$script_dir/agents-md/AGENTS.snippet.md"
if [ -n "${CODEX_HOME:-}" ]; then
  codex_dir="$CODEX_HOME"
elif [ -n "${HOME:-}" ]; then
  codex_dir="$HOME/.codex"
else
  echo "Neither CODEX_HOME nor HOME is set, so the Codex folder can't be found." >&2
  exit 1
fi
agents="$codex_dir/AGENTS.md"
status=0
CR="$(printf '\r')"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

backup() {
  local target
  target="$agents.bak-tryhard-$(date +%Y%m%d-%H%M%S)"
  if [ -e "$target" ]; then
    target="$target-$$"
  fi
  cp -p "$agents" "$target"
  echo "Saved a backup of $agents to $target"
}

# Marker lines also match with a Windows line ending, in case an editor
# converted the file to CRLF after the block was added.
has_line() { [ -f "$agents" ] && grep -qxF -e "$1" -e "$1$CR" "$agents"; }
has_start() { has_line "$START_MARKER"; }
has_end() { has_line "$END_MARKER"; }

# Print the current file with the marked block replaced by the file in $1
# (or removed when $1 is empty). Lines outside the block are kept as they are,
# except that removing the block also drops the one blank line the installer
# put before it, so install then remove gives back the original file. The one
# difference: if the original had no final newline, the installer added one,
# and it stays after removal.
rewrite() {
  awk -v start="$START_MARKER" -v end="$END_MARKER" -v block="${1:-}" '
    function flush() { if (held) { print last; held = 0 } }
    { line = $0; sub(/\r$/, "", line) }
    line == start {
      if (block == "" && held && bare == "") { held = 0 } else { flush() }
      if (block != "" && !written) { while ((getline text < block) > 0) print text }
      written = 1
      skipping = 1
      next
    }
    skipping && line == end { skipping = 0; next }
    skipping { next }
    { flush(); last = $0; bare = line; held = 1 }
    END { flush() }
  ' "$agents"
}

# Write $1 over AGENTS.md only if it differs, backing up the old file first.
apply() {
  local new="$1" what="$2"
  if [ -f "$agents" ] && cmp -s "$new" "$agents"; then
    echo "$agents already has the current Tryhard block. Nothing changed."
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
    echo "$agents has the Tryhard start marker but no end marker, so the block can't be" >&2
    echo "updated safely. Fix or remove the lines starting with '<!-- tryhard:' and run this again." >&2
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
    tr -d '\r' <"$snippet" | grep -vxF -e "$START_MARKER" -e "$END_MARKER" || true
    echo "$END_MARKER"
  } >"$block"

  if has_start; then
    rewrite "$block" >"$new"
    apply "$new" "Updated the Tryhard block in"
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
    apply "$new" "Added the Tryhard block to"
  fi

  local size
  size=$(wc -c <"$agents" | tr -d ' ')
  if [ "$size" -gt 32768 ]; then
    echo "Note: $agents is now $size bytes. Codex reads at most 32 KiB of AGENTS.md text by default" >&2
    echo "(project_doc_max_bytes), so the end of the file may be cut off." >&2
  fi
  if [ -s "$codex_dir/AGENTS.override.md" ]; then
    echo "Note: $codex_dir/AGENTS.override.md exists and is not empty. Codex reads it instead of" >&2
    echo "AGENTS.md, so the Tryhard block won't load until you move it there or empty that file." >&2
  fi
}

remove_block() {
  if ! has_start; then
    echo "$agents has no Tryhard block. Nothing changed."
    return
  fi
  check_markers
  local new="$work/AGENTS.md"
  rewrite "" >"$new"
  # The block was all there was (the installer created the file), so take the
  # file away again instead of leaving it empty. A symlinked file is emptied
  # instead, so the link stays.
  if [ ! -s "$new" ] && [ ! -L "$agents" ]; then
    backup
    rm -f "$agents"
    echo "Removed $agents, which held only the Tryhard block"
    return
  fi
  apply "$new" "Removed the Tryhard block from"
}

print_steps() {
  cat <<EOF

Next steps for Codex:

  1. Add the marketplace and install the plugin:

       codex plugin marketplace add $REPO
       codex plugin add tryhard@tryhard

     From a local copy you can use the folder instead of the GitHub name:

       codex plugin marketplace add "$script_dir"

  2. Start Codex, type /hooks and trust the Tryhard Stop hook. Codex skips
     plugin hooks until you trust them. The approval covers every file in the plugin,
     so Codex asks again after each plugin update.

  3. Optional: use the higher-effort profile.

       cp "$script_dir/profiles/tryhard.config.toml" "$codex_dir/tryhard.config.toml"
       codex --profile tryhard

To turn the Stop hook off, start Codex with TRYHARD_HOOK=off. To run only some of
its checks, set TRYHARD_CHECKS to a list such as handback,own-work,readability.
EOF
}

print_remove_steps() {
  cat <<EOF

To remove the plugin as well:

  codex plugin remove tryhard@tryhard
  codex plugin marketplace remove tryhard
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
