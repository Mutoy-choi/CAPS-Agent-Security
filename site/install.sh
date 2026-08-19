#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-all}"
SCOPE="${CAPS_SCOPE:-user}"
REF="${CAPS_REF:-main}"
REPO="${CAPS_REPO:-https://github.com/Mutoy-choi/ChillMCP.git}"
ORIGINAL_DIR="$PWD"

usage() {
  cat <<'EOF'
CAPS installer

Usage:
  ./install.sh [all|plugin|skill]

Environment:
  CAPS_SCOPE=user|project   Installation scope (default: user)
  CAPS_REF=main             Git branch or tag
  CAPS_REPO=https://...     Repository URL
EOF
}

if [[ "$MODE" == "-h" || "$MODE" == "--help" ]]; then
  usage
  exit 0
fi
if [[ "$MODE" != "all" && "$MODE" != "plugin" && "$MODE" != "skill" ]]; then
  usage >&2
  exit 2
fi
if [[ "$SCOPE" != "user" && "$SCOPE" != "project" ]]; then
  echo "CAPS_SCOPE must be user or project" >&2
  exit 2
fi
if ! command -v git >/dev/null 2>&1; then
  echo "git is required" >&2
  exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

git clone --quiet --depth 1 --branch "$REF" "$REPO" "$TMP_DIR/repo"

install_skills() {
  local agents_root claude_root
  if [[ "$SCOPE" == "project" ]]; then
    agents_root="$ORIGINAL_DIR/.agents/skills"
    claude_root="$ORIGINAL_DIR/.claude/skills"
  else
    agents_root="$HOME/.agents/skills"
    claude_root="$HOME/.claude/skills"
  fi
  mkdir -p "$agents_root" "$claude_root"
  for skill in caps-agent-security caps-install; do
    rm -rf "$agents_root/$skill" "$claude_root/$skill"
    cp -R "$TMP_DIR/repo/.agents/skills/$skill" "$agents_root/$skill"
    cp -R "$TMP_DIR/repo/.agents/skills/$skill" "$claude_root/$skill"
  done
  echo "Installed Agent Skills to:"
  echo "  $agents_root"
  echo "  $claude_root"
}

install_plugin() {
  if ! command -v claude >/dev/null 2>&1; then
    if [[ "$MODE" == "plugin" ]]; then
      echo "Claude Code CLI is required for plugin installation" >&2
      exit 1
    fi
    echo "Claude Code CLI not found; skipped Plugin installation. Skills were still installed."
    return
  fi
  claude plugin marketplace add Mutoy-choi/ChillMCP >/dev/null 2>&1 || \
    claude plugin marketplace update caps-labs >/dev/null 2>&1 || true
  claude plugin install caps-security@caps-labs --scope "$SCOPE"
  echo "Installed Claude Code Plugin: caps-security@caps-labs"
}

case "$MODE" in
  skill)
    install_skills
    ;;
  plugin)
    install_plugin
    ;;
  all)
    install_skills
    install_plugin
    ;;
esac

echo "CAPS installation complete."
