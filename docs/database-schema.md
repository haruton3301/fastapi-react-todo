# データベーススキーマ設計

## 概要

PostgreSQLを使用したタスク管理用のデータベーススキーマ設計。
SQLAlchemyのORMで実装します。

## データベース情報

- **DBMS**: PostgreSQL 16
- **データベース名**: `todo_db`
- **文字コード**: UTF-8
- **タイムゾーン**: UTC (Universal Time Coordinated)

---

## テーブル設計

### tasks テーブル

タスク情報を管理するメインテーブル。

#### スキーマ定義

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---------|---------|------|-----------|------|------|
| `id` | INTEGER | NOT NULL | AUTO INCREMENT | PRIMARY KEY | タスクID (連番) |
| `title` | VARCHAR(255) | NOT NULL | - | - | タスクタイトル |
| `content` | TEXT | NULL | NULL | - | タスク内容 |
| `due_date` | DATE | NOT NULL | - | - | 締切日 |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | CURRENT_TIMESTAMP | - | 作成日時 (UTC) |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | CURRENT_TIMESTAMP | - | 更新日時 (UTC) |

#### インデックス

| インデックス名 | 対象カラム | 種類 | 目的 |
|--------------|-----------|------|------|
| `pk_tasks` | `id` | PRIMARY KEY | 主キー |
| `idx_tasks_due_date` | `due_date` | BTREE | 締切日でのソート高速化 |

#### SQL定義

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    due_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_tasks_due_date ON tasks(due_date);
```

---

## SQLAlchemyモデル定義

`api/app/models/task.py`

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    due_date = Column(Date, nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
```

---

## ER図

```
┌─────────────────────────────────┐
│           tasks                 │
├─────────────────────────────────┤
│ id (PK)          INTEGER        │
│ title            VARCHAR(255)   │
│ content          TEXT           │
│ due_date         DATE           │
│ created_at       TIMESTAMPTZ    │
│ updated_at       TIMESTAMPTZ    │
└─────────────────────────────────┘
```

※ 現在は単一テーブルのみ。将来的に拡張可能な設計。

---

## マイグレーション戦略

### Alembicを使用

1. **初期マイグレーション**
   ```bash
   alembic revision --autogenerate -m "Create tasks table"
   ```

2. **マイグレーション適用**
   ```bash
   alembic upgrade head
   ```

3. **ロールバック**
   ```bash
   alembic downgrade -1
   ```

### マイグレーションファイル構成

```
api/alembic/
├── versions/
│   └── xxxx_create_tasks_table.py
├── env.py
└── alembic.ini
```

---

## データ制約

### 必須項目
- `title`: 空文字不可
- `due_date`: 必須

### 任意項目
- `content`: 未入力可 (NULL許可)

### バリデーション
- `title`: 最大255文字 (Pydanticでも二重チェック)
- `due_date`: 日付形式 (`YYYY-MM-DD`)

---

## タイムゾーン処理

### DB保存ルール
- すべての日時は **UTC** で保存
- `TIMESTAMP WITH TIME ZONE` 型を使用

### フロントエンド表示
- ユーザーのローカルタイムゾーンで表示
- JavaScriptの `Intl.DateTimeFormat` 等を使用

### 例
- DB保存: `2026-02-07 10:00:00+00:00` (UTC)
- 日本表示: `2026-02-07 19:00:00` (JST = UTC+9)

---

## 将来の拡張案

### ユーザー機能追加時

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

ALTER TABLE tasks ADD COLUMN user_id INTEGER REFERENCES users(id);
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
```

### カテゴリ機能追加時

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7) -- HEXカラーコード
);

ALTER TABLE tasks ADD COLUMN category_id INTEGER REFERENCES categories(id);
CREATE INDEX idx_tasks_category_id ON tasks(category_id);
```

### タグ機能追加時

```sql
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE task_tags (
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);
```

---

## パフォーマンス考慮事項

### インデックス戦略
- `due_date` にインデックスを付与（ソートクエリ高速化）
- 将来的に `user_id` を追加する場合もインデックス必須

### クエリ最適化
- N+1問題を避けるため、必要に応じて `joinedload` 使用
- 大量データ対策として、ページネーション実装も検討可能

---

## サンプルデータ

```sql
INSERT INTO tasks (title, content, due_date) VALUES
('課題提出', 'FastAPIとReactのタスク管理アプリを完成させる', '2026-02-15'),
('買い物', '牛乳、卵、パンを買う', '2026-02-10'),
('運動', 'ジムに行く', '2026-02-08');
```

---

## バックアップ戦略

### 開発環境
- Docker volumeでデータ永続化
- 必要に応じて `pg_dump` でバックアップ

### 本番環境（将来的に）
- 定期的な自動バックアップ設定
- Point-in-Time Recovery (PITR) 設定
