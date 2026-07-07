---
name: discord-messenger
description: DiscordのWebhookを利用して、特定のチャンネルにメッセージを送信します。
---
# Discord Messenger

このスキルは、設定されたDiscord Webhook URLを使用して、Discordチャンネルへメッセージを投稿します。

## 必要条件
- Discord Webhook URLが環境変数 `DISCORD_WEBHOOK_URL` に設定されていること。

## 構成ファイル
- 送信スクリプト: [send_message.py](scripts/send_message.py)

## 使い方
送信したいメッセージを引数としてスクリプトを実行します。

```bash
python3 scripts/send_message.py "送信するメッセージ内容"
```

または、標準入力を介してメッセージをパイプで渡すことも可能です。

```bash
echo "送信するメッセージ内容" | python3 scripts/send_message.py
```
