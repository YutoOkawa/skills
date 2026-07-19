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

def get_page_content(page_id, token):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28"
    }
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode("utf-8"))
            results = data.get("results", [])
            lines = []
            for block in results:
                b_type = block.get("type")
                if not b_type:
                    continue
                block_data = block.get(b_type, {})
                rich_text = block_data.get("rich_text", [])
                if rich_text:
                    text = "".join([t.get("plain_text", "") for t in rich_text])
                    if b_type.startswith("heading_"):
                        try:
                            level = int(b_type.split("_")[1])
                            lines.append(f"{'#' * level} {text}")
                        except ValueError:
                            lines.append(text)
                    elif b_type == "bulleted_list_item":
                        lines.append(f"- {text}")
                    elif b_type == "numbered_list_item":
                        lines.append(f"1. {text}")
                    elif b_type == "quote":
                        lines.append(f"> {text}")
                    else:
                        lines.append(text)
                elif b_type == "code":
                    code_text = "".join([t.get("plain_text", "") for t in block_data.get("rich_text", [])])
                    lines.append(f"```{block_data.get('language', '')}\n{code_text}\n```")
            return "\n".join(lines)
    except Exception as e:
        print(f"[!] Error fetching page content for {page_id}: {e}", file=sys.stderr)
        return ""

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
                    # 本文を取得
                    content = get_page_content(page_id, token)
                    # タブ区切りで出力 (改行を含まないようにする)
                    title_clean = title.replace("\n", " ").replace("\r", " ")
                    content_clean = content.replace("\r", "").replace("\n", "\\n")
                    print(f"{page_id}\t{title_clean}\t{content_clean}")
    except Exception as e:
        print(f"[!] Error querying Notion API: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
