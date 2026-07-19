#!/usr/bin/env python3
import json
import sys
import urllib.request
from pathlib import Path

def get_notion_token():
    # mcp_config.json からトークンを取得
    mcp_config_path = Path.home() / ".gemini" / "antigravity-cli" / "mcp_config.json"
    if mcp_config_path.exists():
        try:
            with open(mcp_config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("mcpServers", {}).get("notion-knowledge-base", {}).get("env", {}).get("NOTION_TOKEN")
        except Exception as e:
            print(f"[!] Error reading mcp_config.json: {e}", file=sys.stderr)
    return None

def main():
    token = get_notion_token()
    if not token:
        print("[!] Error: Notion token not found in mcp_config.json", file=sys.stderr)
        sys.exit(1)

    database_id = "2c92e9fd-d1f7-80f0-8fab-d96e41360446"
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # プロパティ「選択」の値が「下書き」のものをフィルタ
    data = {
        "filter": {
            "property": "選択",
            "select": {
                "equals": "下書き"
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
            results = response_data.get("results", [])
            for page in results:
                page_id = page.get("id")
                # タイトルを取得
                title_prop = page.get("properties", {}).get("名前", {}).get("title", [])
                title = title_prop[0].get("plain_text", "") if title_prop else ""
                if page_id and title:
                    # タブ区切りで出力 (改行を含まないようにする)
                    title_clean = title.replace("\n", " ").replace("\r", " ")
                    print(f"{page_id}\t{title_clean}")
    except Exception as e:
        print(f"[!] Error querying Notion API: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
