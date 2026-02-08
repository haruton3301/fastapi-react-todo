# システムアーキテクチャ

## 概要

タスク管理アプリケーション - モノレポ構成でFastAPI (バックエンド) + React (フロントエンド) を実装

## プロジェクト構成

```
fastapi-react-todo/
├── docs/                   # 設計ドキュメント
│   ├── architecture.md     # 本ドキュメント
│   ├── api-design.md       # APIエンドポイント設計
│   ├── database-schema.md  # DBスキーマ設計
│   └── setup.md            # 環境構築手順
│
├── api/                    # FastAPI バックエンド
│   ├── app/
│   │   ├── crud/          # CRUD操作（データアクセス層）
│   │   ├── models/        # SQLAlchemyモデル（DBテーブル定義）
│   │   ├── schemas/       # Pydanticスキーマ（リクエスト/レスポンス定義）
│   │   ├── routers/       # APIエンドポイント（ルーティング層）
│   │   ├── database.py    # DB接続設定
│   │   └── main.py        # FastAPIアプリケーションエントリポイント
│   ├── alembic/           # DBマイグレーション
│   ├── Dockerfile         # APIコンテナ定義
│   ├── docker-compose.yml # PostgreSQL + API開発環境
│   └── pyproject.toml     # Poetry依存関係管理
│
└── web/                   # React フロントエンド
    ├── src/
    │   ├── components/    # Reactコンポーネント
    │   ├── routes/        # TanStack Router (ページ定義)
    │   ├── api/           # Orval生成コード (OpenAPI→TypeScript)
    │   ├── hooks/         # カスタムhooks
    │   ├── lib/           # ユーティリティ関数
    │   └── main.tsx       # エントリポイント
    ├── package.json       # npm依存関係
    └── vite.config.ts     # Vite設定
```

## 技術スタック

### バックエンド (API)

| 技術 | バージョン | 用途 |
|------|-----------|------|
| FastAPI | 最新 | Webフレームワーク |
| SQLAlchemy | 2.x | ORM |
| Alembic | 最新 | DBマイグレーション |
| PostgreSQL | 16 | データベース |
| Poetry | 最新 | パッケージ管理 |
| Docker | 最新 | コンテナ化 |
| Pydantic | 2.x | バリデーション・スキーマ定義 |

### フロントエンド (Web)

| 技術 | バージョン | 用途 |
|------|-----------|------|
| React | 18.x | UIライブラリ |
| Vite | 最新 | ビルドツール |
| TypeScript | 5.x | 型安全性 |
| TanStack Query | v5 | データフェッチ・キャッシュ管理 |
| TanStack Router | v1 | ルーティング |
| DaisyUI | 最新 | UIコンポーネント (Tailwind CSS) |
| React Hook Form | v7 | フォーム管理 |
| Zod | 最新 | バリデーション |
| Orval | 最新 | OpenAPI→TypeScript/TanStack Query生成 |

## アーキテクチャ設計

### レイヤー構成

```
┌─────────────────────────────────────────┐
│          Frontend (React)                │
│  ┌─────────────────────────────────┐    │
│  │ Routes (TanStack Router)        │    │
│  └──────────┬──────────────────────┘    │
│             │                            │
│  ┌──────────▼──────────────────────┐    │
│  │ Components + React Hook Form    │    │
│  └──────────┬──────────────────────┘    │
│             │                            │
│  ┌──────────▼──────────────────────┐    │
│  │ TanStack Query Hooks (Orval生成)│    │
│  └──────────┬──────────────────────┘    │
│             │                            │
│  ┌──────────▼──────────────────────┐    │
│  │ API Client (Orval生成)          │    │
│  └──────────┬──────────────────────┘    │
└─────────────┼──────────────────────────┘
              │ HTTP (JSON)
              │
┌─────────────▼──────────────────────────┐
│         Backend (FastAPI)               │
│  ┌─────────────────────────────────┐   │
│  │ Routers (エンドポイント)         │   │
│  └──────────┬──────────────────────┘   │
│             │                           │
│  ┌──────────▼──────────────────────┐   │
│  │ Schemas (Pydantic)              │   │
│  └──────────┬──────────────────────┘   │
│             │                           │
│  ┌──────────▼──────────────────────┐   │
│  │ CRUD (ビジネスロジック)          │   │
│  └──────────┬──────────────────────┘   │
│             │                           │
│  ┌──────────▼──────────────────────┐   │
│  │ Models (SQLAlchemy)             │   │
│  └──────────┬──────────────────────┘   │
└─────────────┼──────────────────────────┘
              │
┌─────────────▼──────────────────────────┐
│      PostgreSQL Database                │
└─────────────────────────────────────────┘
```

### データフロー

#### 作成フロー例
1. ユーザーがフォーム入力 (React Hook Form + Zod)
2. TanStack Query mutation実行 (`useCreateTask()`)
3. FastAPI `POST /tasks` エンドポイント
4. Pydanticでバリデーション
5. CRUD層でDB操作 (SQLAlchemy)
6. レスポンス返却
7. TanStack Queryがキャッシュ更新 (Optimistic Update可能)

## OpenAPI連携

```
┌──────────────┐
│  FastAPI     │
│  (起動中)    │
└──────┬───────┘
       │ /openapi.json を提供
       │
┌──────▼───────┐
│    Orval     │
│  (codegen)   │
└──────┬───────┘
       │ 生成
       ├─ TypeScript型定義
       ├─ TanStack Query hooks (useListTasks等)
       ├─ Query Keys
       └─ APIクライアント関数
       │
┌──────▼───────┐
│  web/src/api/│
│  (自動生成)  │
└──────────────┘
```

## 開発フロー

1. **API開発**
   - モデル定義 → マイグレーション → CRUD実装 → ルーター実装
   - FastAPI起動で `/docs` でSwagger UI確認

2. **型生成**
   - `npm run generate:api` で Orval実行
   - OpenAPI → TypeScript/TanStack Query hooks生成

3. **フロントエンド開発**
   - 生成されたhooksを使用してコンポーネント実装
   - 型安全性が保証される

## セキュリティ・パフォーマンス

- **CORS**: 開発環境で `http://localhost:3000` を許可
- **バリデーション**: FastAPI (Pydantic) + フロントエンド (Zod) 二重チェック
- **タイムゾーン**: DBはUTCで保存、フロント側でローカルタイムゾーン変換
- **キャッシュ**: TanStack Queryで自動管理
- **エラーハンドリング**: FastAPI統一エラーフォーマット

## 環境変数

### API (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db
CORS_ORIGINS=http://localhost:3000
```

### Web (.env)
```
VITE_API_BASE_URL=http://localhost:8000
```
