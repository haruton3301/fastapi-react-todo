# プロダクトバックログアイテム（PBI）

このリポジトリの構成を参考に、ゼロから同等のシステムを構築する場合のタスク一覧。

---

## API

- [ ] プロジェクト初期セットアップ（Poetry, FastAPI, ディレクトリ構成） — 1h
- [ ] Docker / Docker Compose 環境構築（API + PostgreSQL） — 2h
- [ ] DB接続・SQLAlchemy設定 — 1h
- [ ] Alembicセットアップ・初回マイグレーション作成 — 1h
- [ ] タスクCRUD API実装（エンドポイント + Pydanticスキーマ + バリデーション） — 3h
- [ ] CORSミドルウェア設定 — 0.5h

## Web 基盤

- [ ] Vite + React + TypeScript プロジェクト作成 — 0.5h
- [ ] TailwindCSS v4 + DaisyUI v5 導入 — 1h
- [ ] TanStack Router（ファイルベースルーティング）セットアップ — 1h
- [ ] TanStack Query セットアップ — 0.5h
- [ ] Orval設定（React Queryフック + Zodスキーマ生成） — 2h
- [ ] カスタムHTTPクライアント（fetch mutator）作成 — 0.5h
- [ ] Zodグローバルエラーメッセージ日本語化 — 0.5h

## Web 画面実装

- [ ] ルートレイアウト（ナビバー） — 0.5h
- [ ] タスク一覧画面（データ取得・テーブル表示・ソート切替） — 2h
- [ ] タスク作成画面（フォーム・バリデーション・API連携） — 2h
- [ ] タスク編集画面（データプリフィル・更新API連携） — 1.5h
- [ ] 削除確認モーダル — 1h

## 横断

- [ ] 環境変数管理（.env / VITE_API_BASE_URL） — 0.5h
- [ ] README作成 — 0.5h

---

**合計見積もり: 約22h**