#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-all}"
SCOPE="${CAPS_SCOPE:-user}"
REF="${CAPS_REF:-main}"
REPO="${CAPS_REPO:-https://github.com/Mutoy-choi/CAPS-Agent-Security.git}"
ORIGINAL_DIR="$PWD"

usage() {
  cat <<'EOF'
CAPS Unlock Lab installer

Usage:
  ./install.sh [all|plugin|skill|verify|chat]

Modes:
  all      Install Agent Skills and the Claude Code Plugin when available
  plugin   Install the Claude Code Plugin
  skill    Install cross-client Agent Skills
  verify   Clone CAPS and install CAPS Verify into a local virtual environment
  chat     Clone CAPS and prepare CAPS Research Chat

Environment:
  CAPS_SCOPE=user|project
  CAPS_REF=main
  CAPS_REPO=https://github.com/Mutoy-choi/CAPS-Agent-Security.git
EOF
}

if [[ "$MODE" == "-h" || "$MODE" == "--help" ]]; then
  usage
  exit 0
fi
case "$MODE" in
  all|plugin|skill|verify|chat) ;;
  *) usage >&2; exit 2 ;;
esac
if [[ "$SCOPE" != "user" && "$SCOPE" != "project" ]]; then
  echo "CAPS_SCOPE must be user or project" >&2
  exit 2
fi

install_plugin() {
  if ! command -v claude >/dev/null 2>&1; then
    echo "Claude Code CLI not found; Plugin installation skipped." >&2
    return
  fi
  claude plugin marketplace add Mutoy-choi/CAPS-Agent-Security >/dev/null 2>&1 || \
    claude plugin marketplace update caps-labs >/dev/null 2>&1 || true
  claude plugin install caps-security@caps-labs --scope "$SCOPE"
}

clone_temp() {
  if ! command -v git >/dev/null 2>&1; then
    echo "git is required" >&2
    exit 1
  fi
  git clone --quiet --depth 1 --branch "$REF" "$REPO" "$TMP_DIR/repo"
}

install_skills() {
  local agents_root claude_root
  clone_temp
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
  printf 'Installed Agent Skills:\n  %s\n  %s\n' "$agents_root" "$claude_root"
}

install_verify() {
  local destination venv python
  clone_temp
  if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required" >&2
    exit 1
  fi
  destination="${CAPS_HOME:-$HOME/.local/share/caps-unlock-lab}"
  rm -rf "$destination"
  mkdir -p "$(dirname "$destination")"
  cp -R "$TMP_DIR/repo" "$destination"
  rm -rf "$destination/.git"
  venv="$destination/.venv"
  python3 -m venv "$venv"
  python="$venv/bin/python"
  "$python" -m pip install --upgrade pip
  "$python" -m pip install -e "$destination/caps_verify[gateway]"
  printf 'CAPS Verify installed at %s\nCLI directory: %s\n' "$destination" "$venv/bin"
}

prepare_chat() {
  local destination
  clone_temp
  if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is required for CAPS Research Chat" >&2
    exit 1
  fi
  destination="${CAPS_HOME:-$HOME/.local/share/caps-unlock-lab}"
  rm -rf "$destination"
  mkdir -p "$(dirname "$destination")"
  cp -R "$TMP_DIR/repo" "$destination"
  rm -rf "$destination/.git"
  printf 'CAPS Research Chat prepared at %s/caps_app\nRun ./bootstrap.sh there.\n' "$destination"
}

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

case "$MODE" in
  skill) install_skills ;;
  plugin) install_plugin ;;
  verify) install_verify ;;
  chat) prepare_chat ;;
  all) install_skills; install_plugin ;;
esac

printf 'CAPS installation complete.\n'
