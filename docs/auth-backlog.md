# 認証系バックログ

## 実装済み

### API

| ID | アイテム | 詳細 | 見積 |
|----|---------|------|------|
| API_AUTH_01 | ユーザーモデル作成 | User テーブル（id, username, email, hashed_password, created_at, updated_at） | 1h |
| API_AUTH_02 | Task/Status に user_id 追加マイグレーション | Alembic で user_id FK カラム追加、ユーザースコープの前提 | 1h |
| API_AUTH_03 | ユーザー登録エンドポイント | `POST /auth/signup` — UserCreate スキーマ、Bcrypt ハッシュ化、重複時 409 | 1.5h |
| API_AUTH_04 | ログインエンドポイント | `POST /auth/login` — JWT 生成（HS256, access 30分/refresh 7日）、refresh token を HttpOnly Cookie に設定 | 3h |
| API_AUTH_05 | トークンリフレッシュエンドポイント | `POST /auth/refresh` — Cookie の refresh token から新規 access/refresh token 発行 | 1.5h |
| API_AUTH_06 | ログアウトエンドポイント | `POST /auth/logout` — refresh token Cookie 削除、204 返却 | 0.5h |
| API_AUTH_07 | 現在ユーザー取得エンドポイント | `GET /auth/me` — Bearer token 認証、UserResponse 返却 | 0.5h |
| API_AUTH_08 | 認証ガード作成 | `get_current_user` Depends — Bearer token からユーザー取得 | 1h |
| API_AUTH_09 | Task エンドポイントに認証適用 | 全 Task エンドポイントにガード追加 + CRUD を user_id でフィルタリング | 1.5h |
| API_AUTH_10 | Status エンドポイントに認証適用 | 全 Status エンドポイントにガード追加 + CRUD を user_id でフィルタリング | 1.5h |

### Web

| ID | アイテム | 詳細 | 見積 |
|----|---------|------|------|
| WEB_AUTH_01 | Orval コード生成 | OpenAPI → React Query hooks + Zod スキーマ自動生成 | 0.5h |
| WEB_AUTH_02 | Zustand 認証ストア | accessToken, user のインメモリ管理（localStorage 排除） | 0.5h |
| WEB_AUTH_03 | 新規登録ページ | Orval 生成 Zod スキーマ使用、409 重複エラー対応 | 2h |
| WEB_AUTH_04 | ログインページ | react-hook-form + Zod バリデーション、エラー表示 | 2h |
| WEB_AUTH_05 | 認証ユーティリティ（lib/auth.ts） | refreshAccessToken（シングルトン）+ logout 関数 | 1.5h |
| WEB_AUTH_06 | API クライアント 401 自動リトライ | 401 → refresh → リトライのループ処理、/auth/ パス除外 | 1.5h |
| WEB_AUTH_07 | ページリロード時の認証復帰 + Navbar 認証状態表示 | __root.tsx beforeLoad で refresh → getMe、pendingComponent でローディング表示、Navbar のログイン/未ログイン切替 + ユーザー名ドロップダウン + ログアウトボタン | 2.5h |
| WEB_AUTH_08 | 保護ルートガード | _protected.tsx — token なしで /login リダイレクト | 0.5h |
| WEB_AUTH_09 | 認証ルートガード | _auth.tsx — ログイン済みで / リダイレクト | 0.5h |
