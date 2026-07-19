#!/bin/bash

# ==============================================================================
# AI Agent 定期実行スクリプト (cron想定)
# ==============================================================================

# cron実行環境向けに anyenv / nodenv のパスを通す
export PATH="$HOME/.anyenv/envs/nodenv/shims:$HOME/.anyenv/bin:$PATH"

# 3. ワークスペース（リポジトリルート）への移動
# agy コマンドはローカルの .agents フォルダを参照するため、リポジトリルートで実行する必要があります。
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT" || { echo "Error: Failed to change directory to project root"; exit 1; }

# プロジェクトルートに .env が存在する場合、環境変数をロード
if [ -f ".env" ]; then
    echo "[+] Loading environment variables from .env"
    export $(grep -v '^#' .env | xargs)
fi

# 1. 動作に必要な環境変数の定義
# ※ 環境変数 DISCORD_WEBHOOK_URL が設定されていない場合は、以下に直接記述してください。
export DISCORD_WEBHOOK_URL="${DISCORD_WEBHOOK_URL:-YOUR_DISCORD_WEBHOOK_URL_HERE}"

# 2. 実行に必要なコマンドのパス設定
# cron 実行時は PATH が限定されるため、絶対パスで指定します。
AGY_PATH="$HOME/.local/bin/agy"
# ※ リモートサーバーで動かす場合は、リモート先の agy パス（例: /usr/local/bin/agy や /usr/bin/agy）に書き換えてください。

# 3.5. 必要なパーミッション設定の自動登録・更新
python3 "scripts/setup/setup_permissions.py"

# 4. エージェントの実行
INSTRUCTIONS=$(cat "rules/knowledge-reporter.md")

# get_drafts.py を実行して下書き一覧を取得し、シリアルに処理
python3 "scripts/research/get_drafts.py" | while IFS=$'\t' read -r page_id title content; do
    if [ -n "$page_id" ] && [ -n "$title" ]; then
        echo "[+] Starting research for: $title (ID: $page_id)"

        # content (\\n で改行がエンコードされている) を Python でデコード
        decoded_content=$(python3 -c "import sys; print(sys.argv[1].replace('\\\\n', '\n'))" "$content" 2>/dev/null || echo "")

        # 調査内容の文章本体があれば指示に追加
        if [ -n "$decoded_content" ]; then
            prompt_content="【調査にあたっての追加指示・要件（文章本体より）】
$decoded_content"
        else
            prompt_content=""
        fi

        "$AGY_PATH" --print "$INSTRUCTIONS

【本日の調査テーマ】
$title

$prompt_content

【対象NotionページID】
$page_id"

        # agyの実行結果（終了ステータス）を確認
        if [ $? -eq 0 ]; then
            # ページIDからハイフンを除去してNotion URLを構築
            clean_id=$(echo "$page_id" | tr -d '-')
            notion_url="https://www.notion.so/$clean_id"
            
            # ホスト環境からDiscordへ通知を送信
            echo "[+] Sending Discord notification..."
            python3 "skills/discord-messenger/scripts/send_message.py" "【調査完了通知】${title}: ${notion_url}"
        else
            echo "[!] Error: Research agent failed for $title"
        fi
        echo "[+] Finished research for: $title"
    fi
done

echo "[+] Execution completed."
