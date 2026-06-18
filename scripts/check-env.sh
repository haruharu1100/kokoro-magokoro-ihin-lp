#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo ".env がありません。./scripts/set-env.sh を実行してください。"
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

missing=0

check_var() {
  local name="$1"
  local value="${!name:-}"
  if [[ -z "$value" || "$value" == ここに* ]]; then
    echo "NG: $name が未設定です"
    missing=1
  else
    echo "OK: $name は設定済みです"
  fi
}

check_var "LINE_CHANNEL_SECRET"
check_var "LINE_CHANNEL_ACCESS_TOKEN"
check_var "OPENAI_API_KEY"

if [[ $missing -ne 0 ]]; then
  echo
  echo "不足があります。./scripts/set-env.sh で入れ直してください。"
  exit 1
fi

echo
echo ".env の必須項目はそろっています。"
