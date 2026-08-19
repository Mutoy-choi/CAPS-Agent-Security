#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker가 필요합니다: https://docs.docker.com/get-docker/" >&2
  exit 1
fi

if [[ -f .env ]]; then
  echo ".env가 이미 존재합니다. 기존 설정으로 실행합니다."
  exec docker compose up --build
fi

read -r -p "Provider [openrouter/openai/deepseek] (default: openrouter): " provider
provider="${provider:-openrouter}"

case "$provider" in
  openrouter)
    upstream="https://openrouter.ai"
    default_model="openai/gpt-4o-mini"
    ;;
  openai)
    upstream="https://api.openai.com"
    default_model="gpt-4o-mini"
    ;;
  deepseek)
    upstream="https://api.deepseek.com"
    default_model="deepseek-chat"
    ;;
  *)
    echo "지원하지 않는 provider입니다: $provider" >&2
    exit 1
    ;;
esac

read -r -p "Model ID (default: $default_model): " model
model="${model:-$default_model}"

api_key="${CAPS_UPSTREAM_API_KEY:-}"
if [[ -z "$api_key" ]]; then
  read -r -s -p "Provider API key: " api_key
  echo
fi
if [[ -z "$api_key" ]]; then
  echo "API key가 필요합니다." >&2
  exit 1
fi

random_secret() {
  python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
}

cat > .env <<EOF
CAPS_PROVIDER=$provider
CAPS_UPSTREAM_BASE_URL=$upstream
CAPS_UPSTREAM_API_KEY=$api_key
CAPS_EVALUATION_API_KEY=$api_key
CAPS_APP_MODEL=$model
CAPS_APP_SECRET=$(random_secret)
CAPS_APP_ENCRYPTION_SECRET=$(random_secret)
CAPS_APP_ADMIN_TOKEN=$(random_secret)
CAPS_GATEWAY_CLIENT_TOKEN=$(random_secret)
CAPS_FINGERPRINT_SECRET=$(random_secret)
CAPS_APP_PUBLIC_NAME=CAPS Research Chat
CAPS_APP_RESEARCH_TERMS_VERSION=caps-research-v1
CAPS_APP_RESEARCH_RETENTION_DAYS=365
CAPS_APP_SECURE_COOKIE=false
CAPS_APP_ALLOW_INSECURE_DEV=false
CAPS_APP_PORT=8000
CAPS_ATTACK_PACK=
EOF

chmod 600 .env

echo "설정이 생성됐습니다. 관리자 토큰은 .env의 CAPS_APP_ADMIN_TOKEN에 저장되었습니다."
exec docker compose up --build
