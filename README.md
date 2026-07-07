# Skills Repository

このリポジトリは、Google Antigravity CLI (`agy`) 向けのカスタムスキルを管理するリポジトリです。

## インストール方法

リポジトリ内のスキルをローカルの agy 設定 (`~/.gemini/config/skills/`) にインストールするためのスクリプト `install.sh` を用意しています。

### 1. 全てのスキルを開発用（シンボリックリンク）としてインストールする
開発中にスキル内のコードを変更した際、即座に反映されるようにシンボリックリンクとしてインストールする推奨の方法です。

```bash
./install.sh
# または明示的に
./install.sh --symlink
```

### 2. 全てのスキルをコピーしてインストールする
ファイルを実体としてコピーしてインストールします。

```bash
./install.sh --copy
```

### 3. 特定のスキルのみをインストールする
特定のスキル（例: `discord-messenger`）のみを指定してインストールできます。

```bash
./install.sh -k discord-messenger
```

### 4. スキルをアンインストールする

```bash
# 全てのスキルをアンインストール
./install.sh --uninstall

# 特定のスキルのみをアンインストール
./install.sh --uninstall -k discord-messenger
```

### 5. ヘルプを表示する

```bash
./install.sh --help
```

---

## 開発ガイド

- 新しいスキルを追加する場合は、`skills/` ディレクトリの下に新しいディレクトリ（例: `skills/my-new-skill`）を作成し、その中に `SKILL.md` を配置してください。
- `SKILL.md` 内でスクリプトなどのファイルをリンク・参照する場合は、絶対パスではなく **相対パス**（例: `[my_script.py](scripts/my_script.py)`）で記述してください。
