# FastAPI Discord Bot System

## 概要
Discord Botと連携する仮想通貨システム。

## 構成
- `app/main.py`：FastAPIエントリポイント
- `app/server.py`：エンドポイントロジック
- `Dockerfile`：Docker構築設定
- `app/data`：データファイル保存場所

## 使用方法
1. Dockerイメージをビルド
   ```bash
   docker build -t discord-bot-system .
