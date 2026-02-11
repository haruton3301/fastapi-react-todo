from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# SQLAlchemyエンジン作成
engine = create_engine(settings.database_url)

# セッションローカル
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラス
Base = declarative_base()


# 依存性注入用のDB取得関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
