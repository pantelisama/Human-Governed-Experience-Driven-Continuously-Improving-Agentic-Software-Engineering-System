#!/usr/bin/env bash
# Install the SDET E-Team agents and orchestrator skill into a project or into ~/.claude.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE=link
TARGET=""

usage() {
    cat >&2 <<EOF
usage: install.sh [--copy] (<project-dir> | --user)

  <project-dir>  install into <project-dir>/.claude/
  --user         install into \$HOME/.claude/ (available in every project)
  --copy         copy files instead of symlinking (symlink is the default, so a
                 git pull in this repo updates every install)
EOF
    exit 2
}

while [ $# -gt 0 ]; do
    case "$1" in
        --copy) MODE=copy ;;
        --user) TARGET="$HOME/.claude" ;;
        -h|--help) usage ;;
        -*) echo "install.sh: unknown option $1" >&2; usage ;;
        *)
            [ -d "$1" ] || { echo "install.sh: not a directory: $1" >&2; exit 1; }
            TARGET="$(cd "$1" && pwd)/.claude"
            ;;
    esac
    shift
done

[ -n "$TARGET" ] || usage

mkdir -p "$TARGET/agents" "$TARGET/skills"

for agent in "$SRC"/agents/*.md; do
    dest="$TARGET/agents/$(basename "$agent")"
    rm -rf "$dest"
    if [ "$MODE" = copy ]; then cp "$agent" "$dest"; else ln -s "$agent" "$dest"; fi
done

skill_dest="$TARGET/skills/sdet-team"
rm -rf "$skill_dest"
if [ "$MODE" = copy ]; then
    cp -r "$SRC/skills/sdet-team" "$skill_dest"
else
    ln -s "$SRC/skills/sdet-team" "$skill_dest"
fi

echo "Installed $(ls "$SRC"/agents/*.md | wc -l) agents and the sdet-team skill into $TARGET ($MODE)."
echo "Start a new Claude Code session there and run: /sdet-team <your task>"
