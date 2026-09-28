#!/usr/bin/env bash
# Remind Claude, on every prompt, to record a user correction in the team's memory.
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
printf '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"%s"}}\n' \
  "If this message corrects you or rejects your work, record the correction generalised, not verbatim, in ${REPO}/skills/sdet-team/memory/corrections.md, as the Learning section of the sdet-team skill describes."
