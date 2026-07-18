#!/bin/bash

# ==============================================================================
# AI Agent 定期実行スクリプト (cron想定)
# ==============================================================================

# 1. 動作に必要な環境変数の定義
# ※ 環境変数 DISCORD_WEBHOOK_URL が設定されていない場合は、以下に直接記述してください。
export DISCORD_WEBHOOK_URL="${DISCORD_WEBHOOK_URL:-YOUR_DISCORD_WEBHOOK_URL_HERE}"

# 2. 実行に必要なコマンドのパス設定
# cron 実行時は PATH が限定されるため、絶対パスで指定します。
AGY_PATH="$HOME/.local/bin/agy"
# ※ リモートサーバーで動かす場合は、リモート先の agy パス（例: /usr/local/bin/agy や /usr/bin/agy）に書き換えてください。

# 3. ワークスペース（リポジトリルート）への移動
# agy コマンドはローカルの .agents フォルダを参照するため、リポジトリルートで実行する必要があります。
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT" || { echo "Error: Failed to change directory to project root"; exit 1; }

# 3.5. 必要なパーミッション設定の自動登録・更新
python3 "./setup_permissions.py"

# 4. 調査テーマの定義
RESEARCH_THEME="antigravity cli について調査してください。"

# 5. エージェントの実行
# - ルール指示書の内容をプロンプトとして直接流し込みます。
# - ※ settings.json にて notion-knowledge-base MCP および send_message.py コマンドが allow 登録されているため、無承認で自律実行されます。

INSTRUCTIONS=$(cat ".agents/rules/knowledge-reporter.md")
"$AGY_PATH" --print "$INSTRUCTIONS

【本日の調査テーマ】
$RESEARCH_THEME"

echo "[+] Execution completed."
