#!/usr/bin/env bash
# Commit any change to the team's memory, locally only; never fails the Claude Code session.
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MEMORY=skills/sdet-team/memory
cd "$REPO" 2>/dev/null || exit 0
git add -- "$MEMORY" 2>/dev/null
git diff --cached --quiet -- "$MEMORY" && exit 0
git commit -q -m "memory: auto-commit $(date -Iseconds)" -- "$MEMORY" >/dev/null 2>&1
exit 0
