# APIエンドポイント設計

## 概要

RESTful APIの設計に基づき、タスク管理のCRUD操作を提供します。
FastAPIの自動ドキュメント生成 (`/docs`) に準拠した設計です。

## ベースURL

- 開発環境: `http://localhost:8000`
- 本番環境: (デプロイ先に応じて設定)

## エンドポイント一覧

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/tasks` | タスク一覧取得 (ソート可能) |
| GET | `/tasks/{task_id}` | タスク詳細取得 |
| POST | `/tasks` | タスク作成 |
| PUT | `/tasks/{task_id}` | タスク更新 |
| DELETE | `/tasks/{task_id}` | タスク削除 |

---

## 詳細仕様

### 1. タスク一覧取得

タスクの一覧を取得します。締切日で昇順・降順のソートが可能です。

**エンドポイント**
```
GET /tasks
```

**クエリパラメータ**

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|-----|------|-----------|------|
| `order_by` | string | No | `due_date` | ソート対象フィールド (`due_date`のみサポート) |
| `order` | string | No | `desc` | ソート順 (`asc`: 昇順, `desc`: 降順) |

**リクエスト例**
```http
GET /tasks?order_by=due_date&order=asc
```

**レスポンス例**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "課題提出",
      "content": "FastAPIとReactのタスク管理アプリを完成させる",
      "due_date": "2026-02-15",
      "created_at": "2026-02-07T10:00:00Z",
      "updated_at": "2026-02-07T10:00:00Z"
    },
    {
      "id": 2,
      "title": "買い物",
      "content": "牛乳、卵、パンを買う",
      "due_date": "2026-02-20",
      "created_at": "2026-02-07T11:00:00Z",
      "updated_at": "2026-02-07T11:00:00Z"
    }
  ]
}
```

**ステータスコード**
- `200 OK`: 成功

---

### 2. タスク詳細取得

特定のタスクの詳細を取得します。

**エンドポイント**
```
GET /tasks/{task_id}
```

**パスパラメータ**

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `task_id` | integer | タスクID |

**リクエスト例**
```http
GET /tasks/1
```

**レスポンス例**
```json
{
  "id": 1,
  "title": "課題提出",
  "content": "FastAPIとReactのタスク管理アプリを完成させる",
  "due_date": "2026-02-15",
  "created_at": "2026-02-07T10:00:00Z",
  "updated_at": "2026-02-07T10:00:00Z"
}
```

**ステータスコード**
- `200 OK`: 成功
- `404 Not Found`: タスクが存在しない

**エラーレスポンス例**
```json
{
  "detail": "Task not found"
}
```

---

### 3. タスク作成

新しいタスクを作成します。

**エンドポイント**
```
POST /tasks
```

**リクエストボディ**

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `title` | string | Yes | タスクタイトル (最大255文字) |
| `content` | string | No | タスク内容 |
| `due_date` | string (date) | Yes | 締切日 (YYYY-MM-DD形式) |

**リクエスト例**
```json
{
  "title": "課題提出",
  "content": "FastAPIとReactのタスク管理アプリを完成させる",
  "due_date": "2026-02-15"
}
```

**レスポンス例**
```json
{
  "id": 1,
  "title": "課題提出",
  "content": "FastAPIとReactのタスク管理アプリを完成させる",
  "due_date": "2026-02-15",
  "created_at": "2026-02-07T10:00:00Z",
  "updated_at": "2026-02-07T10:00:00Z"
}
```

**ステータスコード**
- `201 Created`: 作成成功
- `422 Unprocessable Entity`: バリデーションエラー

**バリデーションエラー例**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

### 4. タスク更新

既存のタスクを更新します。

**エンドポイント**
```
PUT /tasks/{task_id}
```

**パスパラメータ**

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `task_id` | integer | タスクID |

**リクエストボディ**

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `title` | string | Yes | タスクタイトル (最大255文字) |
| `content` | string | No | タスク内容 |
| `due_date` | string (date) | Yes | 締切日 (YYYY-MM-DD形式) |

**リクエスト例**
```http
PUT /tasks/1
```

```json
{
  "title": "課題提出（修正版）",
  "content": "FastAPIとReactのタスク管理アプリを完成させる。テストも追加する。",
  "due_date": "2026-02-20"
}
```

**レスポンス例**
```json
{
  "id": 1,
  "title": "課題提出（修正版）",
  "content": "FastAPIとReactのタスク管理アプリを完成させる。テストも追加する。",
  "due_date": "2026-02-20",
  "created_at": "2026-02-07T10:00:00Z",
  "updated_at": "2026-02-07T12:00:00Z"
}
```

**ステータスコード**
- `200 OK`: 更新成功
- `404 Not Found`: タスクが存在しない
- `422 Unprocessable Entity`: バリデーションエラー

---

### 5. タスク削除

タスクを削除します。

**エンドポイント**
```
DELETE /tasks/{task_id}
```

**パスパラメータ**

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `task_id` | integer | タスクID |

**リクエスト例**
```http
DELETE /tasks/1
```

**レスポンス例**
```json
{
  "message": "Task deleted successfully"
}
```

**ステータスコード**
- `200 OK`: 削除成功
- `404 Not Found`: タスクが存在しない

---

## Pydanticスキーマ設計

### TaskBase (共通フィールド)
```python
class TaskBase(BaseModel):
    title: str = Field(..., max_length=255)
    content: str | None = None
    due_date: date
```

### TaskCreate (作成時)
```python
class TaskCreate(TaskBase):
    pass
```

### TaskUpdate (更新時)
```python
class TaskUpdate(TaskBase):
    pass
```

### TaskResponse (レスポンス)
```python
class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### TaskListResponse (一覧レスポンス)
```python
class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
```

---

## OpenAPI仕様

FastAPIが自動生成する `/openapi.json` をフロントエンド (Orval) で利用します。

**主要タグ**
- `tasks`: タスク関連エンドポイント

**セキュリティ**
- 今回は認証なし（将来的にJWT等を追加可能）

---

## エラーハンドリング

### 統一エラーフォーマット

```json
{
  "detail": "エラーメッセージ"
}
```

### 主要なHTTPステータスコード

| コード | 説明 |
|-------|------|
| 200 | 成功 (取得・更新・削除) |
| 201 | 作成成功 |
| 404 | リソースが見つからない |
| 422 | バリデーションエラー |
| 500 | サーバーエラー |

---

## CORS設定

開発環境では以下のオリジンを許可：

```python
origins = [
    "http://localhost:5173",  # Vite開発サーバー
]
```

本番環境では適切なドメインに変更します。

---

## 備考

- **日付フォーマット**: ISO 8601形式 (`YYYY-MM-DD`)
- **タイムゾーン**: DBはUTCで保存、フロントエンド側でローカルタイムゾーン変換
- **日時フォーマット**: ISO 8601形式 (`YYYY-MM-DDTHH:MM:SSZ`)
- **文字コード**: UTF-8
- **レスポンス形式**: JSON
