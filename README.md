# Task Management App

タスク管理アプリケーション（モノレポ構成）

## 技術スタック

### API（`api/`）

| カテゴリ | 技術 |
|---------|------|
| 言語 | Python 3.12 |
| フレームワーク | FastAPI |
| ORM | SQLAlchemy 2.x |
| マイグレーション | Alembic |
| DB | PostgreSQL 16 |
| パッケージ管理 | Poetry 2.3.2 |
| 設定管理 | pydantic-settings |
| コンテナ | Docker / Docker Compose |

### Web（`web/`）

| カテゴリ | 技術 |
|---------|------|
| 言語 | TypeScript |
| フレームワーク | React |
| ビルドツール | Vite |
| ルーティング | TanStack Router |
| データ取得 | TanStack Query v5 |
| APIクライアント生成 | Orval（OpenAPI） |
| UIライブラリ | DaisyUI |
| フォーム | react-hook-form + Zod |

## 環境構築

### 前提条件

- Docker / Docker Compose がインストール済み

### API

```bash
cd api

# 環境変数ファイルを作成
cp .env.example .env

# コンテナ起動
docker compose up -d --build

# DBマイグレーション実行
docker compose exec api alembic upgrade head

# テスト実行
docker compose exec api pytest tests/ -v
```

API: http://localhost:8000

Swagger UI: http://localhost:8000/docs

### コンテナ操作

```bash
# ログ確認
docker compose logs -f api

# コンテナ停止
docker compose down

# DBデータも含めて削除
docker compose down -v
```

### Web

```bash
cd web

# パッケージインストール
pnpm install

# APIクライアント・Zodスキーマ生成（要API起動）
pnpm generate:api

# 開発サーバー起動（http://localhost:3000）
pnpm dev
```
