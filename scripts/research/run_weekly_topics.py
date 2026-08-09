#!/usr/bin/env python3
"""
週次の自動調査スケジュール実行スクリプト
cron 等から呼び出すことを想定。
各テーマについてNotionデータベースに新規ページを作成し、exec_research.sh を呼び出してAgentに調査を依頼します。
"""
import json
import sys
import os
import urllib.request
import subprocess
from pathlib import Path
from datetime import datetime

def get_notion_token():
    mcp_config_path = Path.home() / ".gemini" / "antigravity-cli" / "mcp_config.json"
    if mcp_config_path.exists():
        try:
            with open(mcp_config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("mcpServers", {}).get("notion-knowledge-base", {}).get("env", {}).get("NOTION_TOKEN")
        except Exception as e:
            print(f"[!] Error reading mcp_config.json: {e}", file=sys.stderr)
    return None

def create_notion_page(token, database_id, title):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "名前": {  # ※データベースのタイトルプロパティ名が「名前」である前提です
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        }
    }
    
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode("utf-8"), 
        headers=headers, 
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as res:
            response_data = json.loads(res.read().decode("utf-8"))
            return response_data.get("id")
    except Exception as e:
        print(f"[!] Error creating Notion page: {e}", file=sys.stderr)
        return None

def main():
    token = get_notion_token()
    if not token:
        print("[!] Error: Notion token not found in mcp_config.json", file=sys.stderr)
        sys.exit(1)

    project_root = Path(__file__).resolve().parent.parent.parent
    env_path = project_root / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip().strip("'").strip('"')

    today_str = datetime.now().strftime("%Y-%m-%d")

    # =========================================================================
    # 定期実行する調査テーマの設定
    # 各データベースIDは、プロジェクトルートの .env ファイルから読み込みます。
    # =========================================================================

    TOPICS = [
        {
            "database_id": os.environ.get("NOTION_DB_AI_NEWS"),
            "title_template": f"【週次】生成AI・LLM関連の最新ニュース ({today_str})",
            "prompt": "ここ1週間で発表された、主要AI企業（OpenAI, Google, Anthropic, Metaなど）の新しいモデルや機能アップデート、および話題になっているAIツールのニュースを調査してください。それぞれの技術的なブレイクスルーや、一般ユーザー/開発者にとってのメリットを構造化してまとめてください。"
        },
        {
            "database_id": os.environ.get("NOTION_DB_GITHUB_TRENDS"),
            "title_template": f"【週次】GitHubにおけるAI/ML分野トレンド ({today_str})",
            "prompt": "現在GitHub等で急激にスターを集めている、あるいは開発者の間で話題になっているAI・機械学習関連のオープンソースプロジェクトを3〜5つピックアップしてください。それぞれの概要、解決する課題、主なユースケース、および既存の代替手段との比較をレポートにまとめてください。"
        },
        {
            "database_id": os.environ.get("NOTION_DB_AI_REGULATION"),
            "title_template": f"【月次】日本および世界のAI規制・法整備の最新動向 ({today_str})",
            "prompt": "直近1ヶ月における、日本（政府のガイドライン動向など）、EU（AI Actの進捗など）、および米国のAIに関する法整備や規制についてのニュースを調査してください。特に、AIを利用する企業がコンプライアンス上注意すべきポイントや、今後のスケジュールについて要約してください。"
        },
        {
            "database_id": os.environ.get("NOTION_DB_SECURITY"),
            "title_template": f"【週次】セキュリティ脆弱性(CVE)とインシデント事例 ({today_str})",
            "prompt": "ここ数週間で報告された影響度（CVSSスコア）の高いセキュリティ脆弱性（CVE）や、話題になった大規模なサイバー攻撃の事例を調査してください。それらがどのようなシステムやソフトウェアに影響を及ぼすか、また企業や開発者が取るべき推奨対策（パッチの適用など）を整理してまとめてください。"
        }
    ]

    exec_script = project_root / "scripts" / "research" / "exec_research.sh"

    if not exec_script.exists():
        print(f"[!] Error: Exec script not found at {exec_script}", file=sys.stderr)
        sys.exit(1)

    for topic in TOPICS:
        db_id = topic["database_id"]
        title = topic["title_template"]
        prompt = topic["prompt"]

        if not db_id:
            print(f"[!] Warning: database_id is not set for '{title}'. Check your .env file. Skipping.", file=sys.stderr)
            continue

        print(f"[*] Processing topic: {title}")
        
        # 1. Notionに空ページを作成
        page_id = create_notion_page(token, db_id, title)
        if not page_id:
            print(f"[!] Failed to create page for '{title}'. Skipping.", file=sys.stderr)
            continue
            
        print(f"[+] Created empty Notion page: {page_id}")

        # 2. Agent 実行スクリプトの呼び出し
        try:
            # プロンプトを引数として渡す
            subprocess.run(
                [str(exec_script), page_id, title, prompt],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"[!] Agent execution failed for '{title}': {e}", file=sys.stderr)

    print("[+] All scheduled topics processed.")

if __name__ == "__main__":
    main()
