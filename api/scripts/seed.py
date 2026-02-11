"""初期ステータスデータ投入スクリプト"""

from app.database import SessionLocal
from app.models.status import Status

SEED_STATUSES = [
    {"name": "未着手", "color": "#6B7280", "order": 1},
    {"name": "進行中", "color": "#3B82F6", "order": 2},
    {"name": "完了", "color": "#10B981", "order": 3},
]


def seed_statuses():
    db = SessionLocal()
    try:
        for data in SEED_STATUSES:
            exists = db.query(Status).filter(Status.name == data["name"]).first()
            if not exists:
                db.add(Status(**data))
        db.commit()
        print("Seed statuses created successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_statuses()
