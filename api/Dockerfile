# Python 3.12ベースイメージ
FROM python:3.12-slim

# 作業ディレクトリ設定
WORKDIR /app

# Poetryインストール
RUN pip install poetry==2.3.2

# Poetry設定（仮想環境をコンテナ内に作らない）
RUN poetry config virtualenvs.create false

# 依存関係ファイルをコピー
COPY pyproject.toml poetry.lock* ./

# 依存関係インストール（開発用: devツールも含む）
RUN poetry install --no-root
