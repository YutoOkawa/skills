#!/bin/bash
# ==============================================================================
# AI Agent 調査実行コアスクリプト
# 引数: <PAGE_ID> <TITLE> <PROMPT_CONTENT>
# ==============================================================================

if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <PAGE_ID> <TITLE> <PROMPT_CONTENT>"
    exit 1
fi

PAGE_ID="$1"
TITLE="$2"
PROMPT_CONTENT="$3"

# cron実行環境向けに anyenv / nodenv のパスを通す
export PATH="$HOME/.anyenv/envs/nodenv/shims:$HOME/.anyenv/bin:$PATH"

# ワークスペース（リポジトリルート）への移動
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT" || { echo "Error: Failed to change directory to project root"; exit 1; }

# プロジェクトルートに .env が存在する場合、環境変数をロード
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

export DISCORD_WEBHOOK_URL="${DISCORD_WEBHOOK_URL:-YOUR_DISCORD_WEBHOOK_URL_HERE}"

AGY_PATH="$HOME/.local/bin/agy"

# 必要なパーミッション設定の自動登録・更新
python3 "scripts/setup/setup_permissions.py"

INSTRUCTIONS=$(cat "rules/knowledge-reporter.md")

echo "[+] Starting research for: $TITLE (ID: $PAGE_ID)"

"$AGY_PATH" --print "$INSTRUCTIONS

【本日の調査テーマ】
$TITLE

【調査にあたっての追加指示・要件（文章本体より）】
$PROMPT_CONTENT

【対象NotionページID】
$PAGE_ID"

# agyの実行結果（終了ステータス）を確認
if [ $? -eq 0 ]; then
    # ページIDからハイフンを除去してNotion URLを構築
    clean_id=$(echo "$PAGE_ID" | tr -d '-')
    notion_url="https://www.notion.so/$clean_id"
    
    # ホスト環境からDiscordへ通知を送信
    echo "[+] Sending Discord notification..."
    python3 "skills/discord-messenger/scripts/send_message.py" "【調査完了通知】${TITLE}: ${notion_url}"
else
    echo "[!] Error: Research agent failed for $TITLE"
fi
echo "[+] Finished research for: $TITLE"
