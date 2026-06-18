#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "VercelからOpenAI関連の環境変数を削除します。"
vercel env rm OPENAI_API_KEY production --yes >/dev/null 2>&1 || true
vercel env rm OPENAI_MODEL production --yes >/dev/null 2>&1 || true
echo "OpenAI関連の環境変数を削除しました。"
