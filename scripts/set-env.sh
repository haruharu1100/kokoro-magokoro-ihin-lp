#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"

echo "心まごころ遺品整理 LINE AI返信 .env 設定"
echo "入力した値は $ENV_FILE に保存されます。"
echo

read -r -p "LINE Channel secret: " LINE_CHANNEL_SECRET
read -r -p "LINE Channel access token: " LINE_CHANNEL_ACCESS_TOKEN
read -r -s -p "OpenAI API key: " OPENAI_API_KEY
echo

cat > "$ENV_FILE" <<EOF
LINE_CHANNEL_SECRET=$LINE_CHANNEL_SECRET
LINE_CHANNEL_ACCESS_TOKEN=$LINE_CHANNEL_ACCESS_TOKEN
OPENAI_API_KEY=$OPENAI_API_KEY
EOF

chmod 600 "$ENV_FILE"

echo
echo ".env を保存しました。"
echo "注意: このファイルはGitHubに上がらないよう .gitignore で除外されています。"
