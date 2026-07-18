#!/usr/bin/env python3
import os
import json
from pathlib import Path

def setup():
    # 1. ユーザー設定ディレクトリのパス解決
    settings_dir = Path.home() / ".gemini" / "antigravity-cli"
    settings_path = settings_dir / "settings.json"

    # ディレクトリが存在しない場合は作成
    settings_dir.mkdir(parents=True, exist_ok=True)

    # 現在のプロジェクトルート（カレントディレクトリ）の絶対パスを取得
    project_root = os.getcwd()
    
    # 登録したい権限リスト
    required_permissions = [
        "mcp(notion-knowledge-base/*)",
        "command(python3)",
        f"read_file({project_root})"
    ]

    # 2. 既存の settings.json を読み込み、または新規作成
    settings_data = {}
    if settings_path.exists():
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings_data = json.load(f)
        except json.JSONDecodeError:
            print(f"[!] Warn: settings.json is corrupted. Creating a new one.")
            settings_data = {}

    # 初期構造の定義
    if "permissions" not in settings_data:
        settings_data["permissions"] = {}
    if "allow" not in settings_data["permissions"]:
        settings_data["permissions"]["allow"] = []

    # 3. 権限のマージ
    current_allow = settings_data["permissions"]["allow"]
    added_count = 0
    for perm in required_permissions:
        if perm not in current_allow:
            current_allow.append(perm)
            print(f"[+] Added permission: {perm}")
            added_count += 1
        else:
            print(f"[i] Already permitted: {perm}")

    # 4. 保存
    if added_count > 0:
        try:
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings_data, f, indent=2, ensure_ascii=False)
            print(f"[+] Successfully updated: {settings_path}")
        except Exception as e:
            print(f"[!] Error writing to settings.json: {e}")
    else:
        print("[i] settings.json is already up to date. No changes made.")

if __name__ == "__main__":
    setup()
