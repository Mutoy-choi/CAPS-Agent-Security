#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-skill}"
SCOPE="${CAPS_SCOPE:-user}"
REF="${CAPS_REF:-main}"
REPO_GIT="${CAPS_REPO:-https://github.com/Mutoy-choi/CAPS-Agent-Security.git}"
REPO_WEB="${CAPS_REPO_WEB:-https://github.com/Mutoy-choi/CAPS-Agent-Security}"
CAPS_HOME="${CAPS_HOME:-$HOME/.local/share/caps-unlock-lab}"
PROJECT_DIR="$PWD"
TMP_DIR=""
CHECKOUT=""

usage() {
  cat <<'EOF'
CAPS Unlock Lab universal installer

Usage:
  ./install.sh [skill|codex|chatgpt|claude|gemini|copilot|cursor|cline|windsurf|opencode|verify|mcp|chat|all]

Scope:
  CAPS_SCOPE=user      install user Skills or native extensions (default)
  CAPS_SCOPE=project   copy repository-scoped Skills/agents where supported
EOF
}

case "$MODE" in
  -h|--help|help) usage; exit 0 ;;
  skill|codex|chatgpt|claude|gemini|copilot|cursor|cline|windsurf|opencode|verify|mcp|chat|all) ;;
  *) usage >&2; exit 2 ;;
esac
[[ "$SCOPE" == "user" || "$SCOPE" == "project" ]] || { echo "CAPS_SCOPE must be user or project" >&2; exit 2; }

cleanup() { [[ -z "$TMP_DIR" || ! -d "$TMP_DIR" ]] || rm -rf "$TMP_DIR"; }
trap cleanup EXIT
need() { command -v "$1" >/dev/null 2>&1 || { echo "$1 is required for mode '$MODE'" >&2; exit 1; }; }

checkout() {
  [[ -n "$CHECKOUT" ]] && return
  need git
  TMP_DIR="$(mktemp -d)"
  CHECKOUT="$TMP_DIR/repo"
  git clone --quiet --depth 1 --branch "$REF" "$REPO_GIT" "$CHECKOUT"
}

copy_skills() {
  local destination="$1" skill
  checkout
  mkdir -p "$destination"
  for skill in caps-agent-security caps-install; do
    rm -rf "$destination/$skill"
    cp -R "$CHECKOUT/skills/$skill" "$destination/$skill"
  done
  printf '  %s\n' "$destination"
}

install_shared_skills() {
  echo "Installing shared Agent Skills:"
  if [[ "$SCOPE" == "project" ]]; then
    copy_skills "$PROJECT_DIR/.agents/skills"
    copy_skills "$PROJECT_DIR/.claude/skills"
    copy_skills "$PROJECT_DIR/.github/skills"
  else
    copy_skills "$HOME/.agents/skills"
    copy_skills "$HOME/.claude/skills"
    copy_skills "$HOME/.copilot/skills"
    copy_skills "$HOME/.config/opencode/skills"
  fi
}

install_codex() {
  if [[ "$SCOPE" == "project" ]]; then copy_skills "$PROJECT_DIR/.agents/skills"; else copy_skills "$HOME/.agents/skills"; fi
  checkout
  mkdir -p "$CAPS_HOME"
  rm -rf "$CAPS_HOME/openai-plugin"
  cp -R "$CHECKOUT/plugins/caps-unlock" "$CAPS_HOME/openai-plugin"
  printf 'Local ChatGPT/Codex Plugin package: %s\n' "$CAPS_HOME/openai-plugin"
  printf 'In Codex, use: $%s or /skills\n' 'caps-agent-security'
}

install_claude() {
  need claude
  claude plugin marketplace add Mutoy-choi/CAPS-Agent-Security >/dev/null 2>&1 || \
    claude plugin marketplace update caps-labs >/dev/null 2>&1 || true
  claude plugin install caps-unlock@caps-labs --scope "$SCOPE"
}

install_gemini() {
  need gemini
  gemini extensions install "$REPO_WEB" --auto-update || gemini extensions update caps-unlock-lab
}

install_copilot() {
  checkout
  if [[ "$SCOPE" == "project" ]]; then
    copy_skills "$PROJECT_DIR/.github/skills"
    mkdir -p "$PROJECT_DIR/.github/agents"
    cp "$CHECKOUT/.github/agents/caps-unlock.md" "$PROJECT_DIR/.github/agents/caps-unlock.md"
    if [[ -e "$PROJECT_DIR/.github/copilot-instructions.md" ]]; then
      echo "Existing .github/copilot-instructions.md kept unchanged."
    else
      cp "$CHECKOUT/.github/copilot-instructions.md" "$PROJECT_DIR/.github/copilot-instructions.md"
    fi
  else
    copy_skills "$HOME/.copilot/skills"
    echo "Use CAPS_SCOPE=project to add the custom-agent profile."
  fi
}

install_cursor() {
  checkout
  mkdir -p "$PROJECT_DIR/.cursor/rules"
  cp "$CHECKOUT/.cursor/rules/caps-unlock.mdc" "$PROJECT_DIR/.cursor/rules/caps-unlock.mdc"
  cp "$CHECKOUT/.cursor/mcp.json.example" "$PROJECT_DIR/.cursor/mcp.caps.example.json"
  echo "Cursor rule installed; the MCP example remains disabled."
}

install_cline() {
  checkout
  mkdir -p "$PROJECT_DIR/.clinerules/workflows"
  cp "$CHECKOUT/.clinerules/caps-unlock.md" "$PROJECT_DIR/.clinerules/caps-unlock.md"
  cp "$CHECKOUT/.clinerules/workflows/caps-unlock-audit.md" "$PROJECT_DIR/.clinerules/workflows/caps-unlock-audit.md"
}

install_windsurf() {
  checkout
  mkdir -p "$PROJECT_DIR/.windsurf/rules" "$PROJECT_DIR/.windsurf/workflows"
  cp "$CHECKOUT/.windsurf/rules/caps-unlock.md" "$PROJECT_DIR/.windsurf/rules/caps-unlock.md"
  cp "$CHECKOUT/.windsurf/workflows/caps-unlock-audit.md" "$PROJECT_DIR/.windsurf/workflows/caps-unlock-audit.md"
}

install_opencode() {
  if [[ "$SCOPE" == "project" ]]; then copy_skills "$PROJECT_DIR/.agents/skills"; else copy_skills "$HOME/.config/opencode/skills"; fi
}

install_verify() {
  local venv python
  checkout
  need python3
  rm -rf "$CAPS_HOME"
  mkdir -p "$(dirname "$CAPS_HOME")"
  cp -R "$CHECKOUT" "$CAPS_HOME"
  rm -rf "$CAPS_HOME/.git"
  venv="$CAPS_HOME/.venv"
  python3 -m venv "$venv"
  python="$venv/bin/python"
  "$python" -m pip install --upgrade pip
  "$python" -m pip install -e "$CAPS_HOME/caps_verify[gateway,mcp]"
  printf 'CAPS Verify installed at %s\nCLI directory: %s\n' "$CAPS_HOME" "$venv/bin"
}

prepare_chat() {
  checkout
  need docker
  rm -rf "$CAPS_HOME"
  mkdir -p "$(dirname "$CAPS_HOME")"
  cp -R "$CHECKOUT" "$CAPS_HOME"
  rm -rf "$CAPS_HOME/.git"
  printf 'Research Chat prepared at %s/caps_app\nRun ./bootstrap.sh there.\n' "$CAPS_HOME"
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
    if command -v claude >/dev/null 2>&1; then install_claude; else echo "Claude Code CLI not found; skipped native Plugin."; fi
    if command -v gemini >/dev/null 2>&1; then install_gemini; else echo "Gemini CLI not found; skipped native extension."; fi
    ;;
esac

echo "CAPS installation complete. Restart the host if the Skill does not appear immediately."
