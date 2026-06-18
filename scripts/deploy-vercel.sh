#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo ".env がありません。先に ./scripts/set-env.sh を実行してください。"
  exit 1
fi

cd "$ROOT_DIR"

set -a
# shellcheck disable=SC1091
source "$ENV_FILE"
set +a

required=(
  LINE_CHANNEL_SECRET
  LINE_CHANNEL_ACCESS_TOKEN
  OPENAI_API_KEY
)

for name in "${required[@]}"; do
  value="${!name:-}"
  if [[ -z "$value" || "$value" == ここに* ]]; then
    echo "$name が未設定です。./scripts/set-env.sh で入れ直してください。"
    exit 1
  fi
done

echo "Vercelへプロジェクトを公開します。"
echo "途中でログインやプロジェクト設定を聞かれたら、表示に従ってください。"
echo

vercel --yes

echo
echo "Vercelへ環境変数を登録します。"
echo "$LINE_CHANNEL_SECRET" | vercel env add LINE_CHANNEL_SECRET production --yes >/dev/null || true
echo "$LINE_CHANNEL_ACCESS_TOKEN" | vercel env add LINE_CHANNEL_ACCESS_TOKEN production --yes >/dev/null || true
echo "$OPENAI_API_KEY" | vercel env add OPENAI_API_KEY production --yes >/dev/null || true
echo "${OPENAI_MODEL:-gpt-4.1-mini}" | vercel env add OPENAI_MODEL production --yes >/dev/null || true

echo
echo "本番へ再デプロイします。"
vercel --prod --yes

echo
echo "完了です。表示された Production URL の末尾に /api/line-webhook を付けて、LINE DevelopersのWebhook URLに設定してください。"
