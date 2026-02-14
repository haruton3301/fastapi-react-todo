from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from tests.utils import create_status_in_db, create_task_in_db

NONEXISTENT_ID = 9999

TASK_JSON = {
    "title": "テストタスク",
    "content": "テスト内容",
    "due_date": "2025-12-31",
}


class TestCreateTask:
    def test_create(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        status = create_status_in_db(db)
        res = client.post("/tasks", json={**TASK_JSON, "status_id": status.id}, headers=auth_headers)
        assert res.status_code == 201
        body = res.json()
        assert body["title"] == TASK_JSON["title"]
        assert body["content"] == TASK_JSON["content"]
        assert body["due_date"] == TASK_JSON["due_date"]
        assert "id" in body
        assert "status_id" in body
        assert "created_at" in body
        assert "updated_at" in body

    def test_title_empty_returns_422(self, client: TestClient, db: Session, auth_headers: dict):
        status = create_status_in_db(db)
        res = client.post("/tasks", json={**TASK_JSON, "title": "", "status_id": status.id}, headers=auth_headers)
        assert res.status_code == 422

    def test_missing_fields_returns_422(self, client: TestClient, auth_headers: dict):
        res = client.post("/tasks", json={}, headers=auth_headers)
        assert res.status_code == 422

    def test_unauthenticated_returns_401(self, client: TestClient, db: Session):
        status = create_status_in_db(db)
        res = client.post("/tasks", json={**TASK_JSON, "status_id": status.id})
        assert res.status_code == 401


class TestListTasks:
    def test_empty(self, client: TestClient, auth_headers: dict):
        res = client.get("/tasks", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["tasks"] == []

    def test_count(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        status = create_status_in_db(db)
        create_task_in_db(db, user_id=test_user.id, title="タスク1", status_id=status.id)
        create_task_in_db(db, user_id=test_user.id, title="タスク2", status_id=status.id)
        create_task_in_db(db, user_id=test_user.id, title="タスク3", status_id=status.id)

        tasks = client.get("/tasks", headers=auth_headers).json()["tasks"]
        assert len(tasks) == 3

    def test_order_desc(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        status = create_status_in_db(db)
        create_task_in_db(db, user_id=test_user.id, title="古い", due_date=date(2025, 1, 1), status_id=status.id)
        create_task_in_db(db, user_id=test_user.id, title="新しい", due_date=date(2025, 12, 31), status_id=status.id)

        tasks = client.get("/tasks", params={"order": "desc"}, headers=auth_headers).json()["tasks"]
        assert tasks[0]["title"] == "新しい"
        assert tasks[1]["title"] == "古い"

    def test_order_asc(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        status = create_status_in_db(db)
        create_task_in_db(db, user_id=test_user.id, title="古い", due_date=date(2025, 1, 1), status_id=status.id)
        create_task_in_db(db, user_id=test_user.id, title="新しい", due_date=date(2025, 12, 31), status_id=status.id)

        tasks = client.get("/tasks", params={"order": "asc"}, headers=auth_headers).json()["tasks"]
        assert tasks[0]["title"] == "古い"
        assert tasks[1]["title"] == "新しい"

    def test_search_by_title(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        status = create_status_in_db(db)
        create_task_in_db(db, user_id=test_user.id, title="買い物リスト", content="牛乳を買う", status_id=status.id)
        create_task_in_db(db, user_id=test_user.id, title="会議準備", content="資料を作成", status_id=status.id)

        tasks = client.get("/tasks", params={"q": "買い物"}, headers=auth_headers).json()["tasks"]
        assert len(tasks) == 1
        assert tasks[0]["title"] == "買い物リスト"

    def test_search_by_content(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        status = create_status_in_db(db)
        create_task_in_db(db, user_id=test_user.id, title="タスクA", content="牛乳を買う", status_id=status.id)
        create_task_in_db(db, user_id=test_user.id, title="タスクB", content="資料を作成", status_id=status.id)

        tasks = client.get("/tasks", params={"q": "牛乳"}, headers=auth_headers).json()["tasks"]
        assert len(tasks) == 1
        assert tasks[0]["title"] == "タスクA"

    def test_search_no_match(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        status = create_status_in_db(db)
        create_task_in_db(db, user_id=test_user.id, title="タスクA", content="内容A", status_id=status.id)

        tasks = client.get("/tasks", params={"q": "存在しない"}, headers=auth_headers).json()["tasks"]
        assert len(tasks) == 0

    def test_search_without_q_returns_all(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        status = create_status_in_db(db)
        create_task_in_db(db, user_id=test_user.id, title="タスク1", status_id=status.id)
        create_task_in_db(db, user_id=test_user.id, title="タスク2", status_id=status.id)

        tasks = client.get("/tasks", headers=auth_headers).json()["tasks"]
        assert len(tasks) == 2

    def test_unauthenticated_returns_401(self, client: TestClient):
        res = client.get("/tasks")
        assert res.status_code == 401


class TestGetTask:
    def test_get(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        task = create_task_in_db(db, user_id=test_user.id)
        res = client.get(f"/tasks/{task.id}", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["title"] == "テストタスク"

    def test_not_found(self, client: TestClient, auth_headers: dict):
        res = client.get(f"/tasks/{NONEXISTENT_ID}", headers=auth_headers)
        assert res.status_code == 404


class TestUpdateTask:
    def test_update(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        task = create_task_in_db(db, user_id=test_user.id)
        update_data = {
            "title": "更新タイトル",
            "content": "更新内容",
            "due_date": "2026-06-15",
            "status_id": task.status_id,
        }
        res = client.put(f"/tasks/{task.id}", json=update_data, headers=auth_headers)
        assert res.status_code == 200
        body = res.json()
        assert body["title"] == "更新タイトル"
        assert body["content"] == "更新内容"
        assert body["due_date"] == "2026-06-15"

    def test_not_found(self, client: TestClient, db: Session, auth_headers: dict):
        status = create_status_in_db(db)
        res = client.put(
            f"/tasks/{NONEXISTENT_ID}",
            json={**TASK_JSON, "status_id": status.id},
            headers=auth_headers,
        )
        assert res.status_code == 404

    def test_title_empty_returns_422(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        task = create_task_in_db(db, user_id=test_user.id)
        res = client.put(
            f"/tasks/{task.id}",
            json={**TASK_JSON, "title": "", "status_id": task.status_id},
            headers=auth_headers,
        )
        assert res.status_code == 422


class TestDeleteTask:
    def test_delete(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        task = create_task_in_db(db, user_id=test_user.id)
        res = client.delete(f"/tasks/{task.id}", headers=auth_headers)
        assert res.status_code == 204

        res = client.get(f"/tasks/{task.id}", headers=auth_headers)
        assert res.status_code == 404

    def test_not_found(self, client: TestClient, auth_headers: dict):
        res = client.delete(f"/tasks/{NONEXISTENT_ID}", headers=auth_headers)
        assert res.status_code == 404
