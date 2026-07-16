---
name: notion-knowledge-archiver
description: AI Agent が調査してまとめた内容を、notion-knowledge-base MCP サーバーのツールを使用して Notion に新しいページとして保存します。
---
# Notion Knowledge Archiver

このスキルは、AI Agent が特定のトピックについて調査した内容を整理し、`notion-knowledge-base` MCP サーバーを介して Notion に美しく構造化されたページとして記録するための指示書です。

## 前提条件
- `notion-knowledge-base` MCP サーバーが有効であり、Notion側で対象の親ページまたはデータベースに対してインテグレーションの権限（接続）が付与されていること。

## 実行ワークフロー

エージェントは、調査結果を Notion に記録する際、以下の手順を順に実行します。

### Step 1: 記録先（親ページ）の特定
記録先となる親ページの ID が指定されていない場合、まずは `notion-knowledge-base` の `API-post-search` ツール等を使用して、親となるページを検索・特定します。
※ 親ページ ID が既知の場合は、このステップをスキップして構いません。

### Step 2: ページの作成
特定した親ページ（またはデータベース）の下に、`notion-knowledge-base/API-post-page` ツールを用いて新しい子ページを作成します。
- **タイトル**: 調査テーマを示す簡潔で明確なタイトル（例: `[調査] 〇〇についての技術調査`）
- **アイコン**: 内容に関連する絵文字（Emoji）を設定します。

### Step 3: コンテンツの追記
作成したページに対して、調査結果を構造化して書き込みます。
- `notion-knowledge-base/API-update-page-markdown` を利用して、Markdown 形式で一括で書き込むか、
- `notion-knowledge-base/API-patch-block-children` を利用して、Notion のブロック構造（ヘッダー、箇流書き、コードブロック等）に変換して追加します。

### Step 4: 完了報告
書き込み完了後、作成したページの Notion の URL をユーザーに提示します。
URL フォーマット: `https://www.notion.so/{page_id}` (ハイフンを除去した32文字のID)

## Notion ページ構成の推奨テンプレート
書き込む内容は以下のセクションで構成してください：
1. **概要 (Summary)**: 調査内容の要約（3〜5行）。
2. **詳細内容 (Detailed Findings)**: 項目ごとの詳細な解説（見出し、箇条書き、テーブル、コードブロックなどを活用）。
3. **結論・推奨事項 (Conclusion & Recommendations)**: 調査から得られた結論。
4. **参照ソース (References)**: 調査の参照元URLやドキュメントリンク。
