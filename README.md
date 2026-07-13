# Fanaria-Bot
Fanaria Official Botのリポジトリ

Discord雑談サーバー [💫 𝔽𝕒𝕟𝕒𝕣𝕚𝕒](https://discord.gg/kftr8cMfED) の公式Botのソースコードです  
envやその他重要なファイルは含めてないはずです

プルリクエストは自由にしてください


---

|実行環境|バージョン|
|-------|-------|
|Python|3.11|
|discord.py|2.8.0a|
|Microsoft Windows|11 (Build 22631.6199)|

---

## 設計思想
- JSONファイルをデータベースとして使用しない

- 機能ごとにファイルやフォルダを可能な限り細分化する

- コマンドは同系統のコマンドをGroupコマンド（`discord.app_commands.Group`）としてまとめて登録する

- 基本的にIDや各種設定値は`bot/Configs/`内で管理する
