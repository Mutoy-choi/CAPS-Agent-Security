#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-skill}"
SCOPE="${CAPS_SCOPE:-user}"
REF="${CAPS_REF:-main}"
REPO_GIT="${CAPS_REPO:-https://github.com/Mutoy-choi/CAPS-Agent-Security.git}"
REPO_WEB="${CAPS_REPO_WEB:-https://github.com/Mutoy-choi/CAPS-Agent-Security}"
ORIGINAL_DIR="$PWD"
CAPS_HOME="${CAPS_HOME:-$HOME/.local/share/caps-unlock-lab}"
TMP_DIR=""
CHECKOUT=""

usage() {
  cat <<'EOF'
CAPS Unlock Lab universal installer

Usage:
  ./install.sh [skill|codex|chatgpt|claude|gemini|copilot|cursor|cline|windsurf|opencode|verify|mcp|chat|all]

Examples:
  ./install.sh codex
  CAPS_SCOPE=project ./install.sh copilot
  ./install.sh gemini
  ./install.sh verify

Environment:
  CAPS_SCOPE=user|project
  CAPS_REF=main
  CAPS_HOME=~/.local/share/caps-unlock-lab
  CAPS_REPO=https://github.com/Mutoy-choi/CAPS-Agent-Security.git
EOF
}

case "$MODE" in
  -h|--help|help) usage; exit 0 ;;
  skill|codex|chatgpt|claude|gemini|copilot|cursor|cline|windsurf|opencode|verify|mcp|chat|all) ;;
  *) usage >&2; exit 2 ;;
esac
if [[ "$SCOPE" != "user" && "$SCOPE" != "project" ]]; then
  echo "CAPS_SCOPE must be user or project" >&2
  exit 2
fi

cleanup() {
  [[ -n "$TMP_DIR" && -d "$TMP_DIR" ]] && rm -rf "$TMP_DIR"
}
trap cleanup EXIT

need() {
  command -v "$1" >/dev/null 2>&1 || { echo "$1 is required for mode '$MODE'" >&2; exit 1; }
}

checkout() {
  if [[ -n "$CHECKOUT" ]]; then return; fi
  need git
  TMP_DIR="$(mktemp -d)"
  CHECKOUT="$TMP_DIR/repo"
  git clone --quiet --depth 1 --branch "$REF" "$REPO_GIT" "$CHECKOUT"
}

copy_skill() {
  local root="$1" skill
  mkdir -p "$root"
  for skill in caps-agent-security caps-install; do
    rm -rf "$root/$skill"
    cp -R "$CHECKOUT/skills/$skill" "$root/$skill"
  done
  echo "  $root"
}

install_shared_skills() {
  checkout
  echo "Installing CAPS Agent Skills to:"
  if [[ "$SCOPE" == "project" ]]; then
    copy_skill "$ORIGINAL_DIR/.agents/skills"
    copy_skill "$ORIGINAL_DIR/.claude/skills"
    copy_skill "$ORIGINAL_DIR/.github/skills"
  else
    copy_skill "$HOME/.agents/skills"
    copy_skill "$HOME/.claude/skills"
    copy_skill "$HOME/.copilot/skills"
    copy_skill "$HOME/.config/opencode/skills"
  fi
}

install_codex() {
  checkout
  if [[ "$SCOPE" == "project" ]]; then
    echo "Installing Codex/OpenCode Skills to:"
    copy_skill "$ORIGINAL_DIR/.agents/skills"
  else
    echo "Installing Codex Skills to:"
    copy_skill "$HOME/.agents/skills"
  fi
  mkdir -p "$CAPS_HOME"
  rm -rf "$CAPS_HOME/openai-plugin"
  cp -R "$CHECKOUT/plugins/caps-unlock" "$CAPS_HOME/openai-plugin"
  echo "Local ChatGPT/Codex Plugin package: $CAPS_HOME/openai-plugin"
  echo "In Codex, use: $caps-agent-security or /skills"
}

install_claude() {
  need claude
  claude plugin marketplace add Mutoy-choi/CAPS-Agent-Security >/dev/null 2>&1 || \
    claude plugin marketplace update caps-labs >/dev/null 2>&1 || true
  claude plugin install caps-unlock@caps-labs --scope "$SCOPE"
  echo "Installed Claude Code Plugin: caps-unlock@caps-labs"
}

install_gemini() {
  need gemini
  gemini extensions install "$REPO_WEB" --auto-update || \
    gemini extensions update caps-unlock-lab
  echo "Installed Gemini CLI extension: caps-unlock-lab"
}

install_copilot() {
  checkout
  if [[ "$SCOPE" == "project" ]]; then
    echo "Installing GitHub Copilot project files:"
    copy_skill "$ORIGINAL_DIR/.github/skills"
    mkdir -p "$ORIGINAL_DIR/.github/agents"
    cp "$CHECKOUT/.github/agents/caps-unlock.md" "$ORIGINAL_DIR/.github/agents/caps-unlock.md"
    if [[ ! -e "$ORIGINAL_DIR/.github/copilot-instructions.md" ]]; then
      cp "$CHECKOUT/.github/copilot-instructions.md" "$ORIGINAL_DIR/.github/copilot-instructions.md"
    else
      echo "  Existing .github/copilot-instructions.md kept unchanged"
    fi
  else
    echo "Installing GitHub Copilot user Skills to:"
    copy_skill "$HOME/.copilot/skills"
    echo "Use CAPS_SCOPE=project to install the custom agent profile."
  fi
}

install_cursor() {
  checkout
  mkdir -p "$ORIGINAL_DIR/.cursor/rules"
  cp "$CHECKOUT/.cursor/rules/caps-unlock.mdc" "$ORIGINAL_DIR/.cursor/rules/caps-unlock.mdc"
  cp "$CHECKOUT/.cursor/mcp.json.example" "$ORIGINAL_DIR/.cursor/mcp.caps.example.json"
  echo "Installed Cursor adapter in $ORIGINAL_DIR/.cursor"
  echo "The MCP example is not enabled automatically."
}

install_cline() {
  checkout
  mkdir -p "$ORIGINAL_DIR/.clinerules/workflows"
  cp "$CHECKOUT/.clinerules/caps-unlock.md" "$ORIGINAL_DIR/.clinerules/caps-unlock.md"
  cp "$CHECKOUT/.clinerules/workflows/caps-unlock-audit.md" "$ORIGINAL_DIR/.clinerules/workflows/caps-unlock-audit.md"
  echo "Installed Cline adapter in $ORIGINAL_DIR/.clinerules"
}

install_windsurf() {
  checkout
  mkdir -p "$ORIGINAL_DIR/.windsurf/rules" "$ORIGINAL_DIR/.windsurf/workflows"
  cp "$CHECKOUT/.windsurf/rules/caps-unlock.md" "$ORIGINAL_DIR/.windsurf/rules/caps-unlock.md"
  cp "$CHECKOUT/.windsurf/workflows/caps-unlock-audit.md" "$ORIGINAL_DIR/.windsurf/workflows/caps-unlock-audit.md"
  echo "Installed Windsurf adapter in $ORIGINAL_DIR/.windsurf"
}

install_opencode() {
  checkout
  if [[ "$SCOPE" == "project" ]]; then
    echo "Installing OpenCode project Skills to:"
    copy_skill "$ORIGINAL_DIR/.agents/skills"
  else
    echo "Installing OpenCode user Skills to:"
    copy_skill "$HOME/.config/opencode/skills"
  fi
}

install_verify() {
  local destination venv python
  checkout
  need python3
  destination="$CAPS_HOME"
  rm -rf "$destination"
  mkdir -p "$(dirname "$destination")"
  cp -R "$CHECKOUT" "$destination"
  rm -rf "$destination/.git"
  venv="$destination/.venv"
  python3 -m venv "$venv"
  python="$venv/bin/python"
  "$python" -m pip install --upgrade pip
  "$python" -m pip install -e "$destination/caps_verify[gateway,mcp]"
  echo "CAPS Verify installed at $destination"
  echo "CLI directory: $venv/bin"
}

prepare_chat() {
  local destination="$CAPS_HOME"
  checkout
  need docker
  rm -rf "$destination"
  mkdir -p "$(dirname "$destination")"
  cp -R "$CHECKOUT" "$destination"
  rm -rf "$destination/.git"
  echo "CAPS Research Chat prepared at $destination/caps_app"
  echo "Run ./bootstrap.sh from that directory when ready to enter provider secrets."
}

case "$MODE" in
  skill) install_shared_skills ;;
  codex|chatgpt) install_codex ;;
  claude) install_claude ;;
  gemini) install_gemini ;;
  copilot) install_copilot ;;
  cursor) install_cursor ;;
  cline) install_cline ;;
  windsurf) install_windsurf ;;
  opencode) install_opencode ;;
  verify|mcp) install_verify ;;
  chat) prepare_chat ;;
  all)
    install_shared_skills
    command -v claude >/dev/null 2>&1 && install_claude || echo "Claude Code CLI not found; skipped native Plugin."
    command -v gemini >/dev/null 2>&1 && install_gemini || echo "Gemini CLI not found; skipped native extension."
    ;;
esac

echo "CAPS installation complete. Restart the host if the Skill does not appear immediately."
