#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo ".env がありません。"
  exit 1
fi

cd "$ROOT_DIR"

set -a
# shellcheck disable=SC1091
source "$ENV_FILE"
set +a

if [[ -z "${OPENAI_API_KEY:-}" || "${OPENAI_API_KEY:-}" == ここに* ]]; then
  echo "OPENAI_API_KEY が未設定です。"
  exit 1
fi

echo "Vercelの OPENAI_API_KEY を更新します。"
vercel env rm OPENAI_API_KEY production --yes >/dev/null 2>&1 || true
printf "%s" "$OPENAI_API_KEY" | vercel env add OPENAI_API_KEY production --yes >/dev/null
echo "OPENAI_API_KEY を更新しました。"
