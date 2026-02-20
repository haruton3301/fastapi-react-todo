from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.status import Status
from app.models.task import Task
from app.models.user import User
from tests.utils import create_status_in_db

NONEXISTENT_ID = 9999

STATUS_JSON = {
    "name": "テストステータス",
    "color": "#FF0000",
}


class TestCreateStatus:
    def test_create(self, client: TestClient, auth_headers: dict):
        res = client.post("/statuses", json=STATUS_JSON, headers=auth_headers)
        assert res.status_code == 201
        body = res.json()
        assert body["name"] == STATUS_JSON["name"]
        assert body["color"] == STATUS_JSON["color"]
        assert body["order"] == 1
        assert "id" in body
        assert "created_at" in body
        assert "updated_at" in body

    def test_auto_order(self, client: TestClient, auth_headers: dict):
        r1 = client.post("/statuses", json={**STATUS_JSON, "name": "A"}, headers=auth_headers)
        r2 = client.post("/statuses", json={**STATUS_JSON, "name": "B"}, headers=auth_headers)
        r3 = client.post("/statuses", json={**STATUS_JSON, "name": "C"}, headers=auth_headers)
        assert r1.json()["order"] == 1
        assert r2.json()["order"] == 2
        assert r3.json()["order"] == 3

    def test_name_empty_returns_422(self, client: TestClient, auth_headers: dict):
        res = client.post("/statuses", json={**STATUS_JSON, "name": ""}, headers=auth_headers)
        assert res.status_code == 422

    def test_missing_fields_returns_422(self, client: TestClient, auth_headers: dict):
        res = client.post("/statuses", json={}, headers=auth_headers)
        assert res.status_code == 422

    def test_unauthenticated_returns_401(self, client: TestClient):
        res = client.post("/statuses", json=STATUS_JSON)
        assert res.status_code == 401


class TestListStatuses:
    def test_empty(self, client: TestClient, auth_headers: dict):
        res = client.get("/statuses", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["statuses"] == []

    def test_count(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        create_status_in_db(db, user_id=test_user.id, name="ステータス1", order=1)
        create_status_in_db(db, user_id=test_user.id, name="ステータス2", order=2)
        create_status_in_db(db, user_id=test_user.id, name="ステータス3", order=3)

        statuses = client.get("/statuses", headers=auth_headers).json()["statuses"]
        assert len(statuses) == 3

    def test_order(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        create_status_in_db(db, user_id=test_user.id, name="先", order=1)
        create_status_in_db(db, user_id=test_user.id, name="後", order=2)

        statuses = client.get("/statuses", headers=auth_headers).json()["statuses"]
        assert statuses[0]["name"] == "先"
        assert statuses[1]["name"] == "後"


class TestGetStatus:
    def test_get(self, client: TestClient, test_status: Status, auth_headers: dict):
        res = client.get(f"/statuses/{test_status.id}", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["name"] == "テストステータス"

    def test_not_found(self, client: TestClient, auth_headers: dict):
        res = client.get(f"/statuses/{NONEXISTENT_ID}", headers=auth_headers)
        assert res.status_code == 404


class TestUpdateStatus:
    def test_update(self, client: TestClient, test_status: Status, auth_headers: dict):
        update_data = {
            "name": "更新ステータス",
            "color": "#00FF00",
        }
        res = client.put(f"/statuses/{test_status.id}", json=update_data, headers=auth_headers)
        assert res.status_code == 200
        body = res.json()
        assert body["name"] == "更新ステータス"
        assert body["color"] == "#00FF00"

    def test_not_found(self, client: TestClient, auth_headers: dict):
        res = client.put(f"/statuses/{NONEXISTENT_ID}", json=STATUS_JSON, headers=auth_headers)
        assert res.status_code == 404

    def test_name_empty_returns_422(self, client: TestClient, test_status: Status, auth_headers: dict):
        res = client.put(
            f"/statuses/{test_status.id}", json={**STATUS_JSON, "name": ""}, headers=auth_headers
        )
        assert res.status_code == 422


class TestReorderStatuses:
    def test_reorder(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        s1 = create_status_in_db(db, user_id=test_user.id, name="A", order=1)
        s2 = create_status_in_db(db, user_id=test_user.id, name="B", order=2)
        s3 = create_status_in_db(db, user_id=test_user.id, name="C", order=3)

        res = client.put("/statuses/reorder", json={"order": [s3.id, s1.id, s2.id]}, headers=auth_headers)
        assert res.status_code == 200
        statuses = res.json()["statuses"]
        assert statuses[0]["name"] == "C"
        assert statuses[1]["name"] == "A"
        assert statuses[2]["name"] == "B"

    def test_missing_ids_returns_400(self, client: TestClient, db: Session, test_user: User, auth_headers: dict):
        s1 = create_status_in_db(db, user_id=test_user.id, name="A", order=1)
        create_status_in_db(db, user_id=test_user.id, name="B", order=2)

        res = client.put("/statuses/reorder", json={"order": [s1.id]}, headers=auth_headers)
        assert res.status_code == 400

    def test_extra_ids_returns_400(self, client: TestClient, test_status: Status, auth_headers: dict):
        res = client.put("/statuses/reorder", json={"order": [test_status.id, NONEXISTENT_ID]}, headers=auth_headers)
        assert res.status_code == 400


class TestDeleteStatus:
    def test_delete(self, client: TestClient, test_status: Status, auth_headers: dict):
        res = client.delete(f"/statuses/{test_status.id}", headers=auth_headers)
        assert res.status_code == 204

        res = client.get(f"/statuses/{test_status.id}", headers=auth_headers)
        assert res.status_code == 404

    def test_not_found(self, client: TestClient, auth_headers: dict):
        res = client.delete(f"/statuses/{NONEXISTENT_ID}", headers=auth_headers)
        assert res.status_code == 404

    def test_delete_with_tasks_returns_409(self, client: TestClient, test_task: Task, auth_headers: dict):
        res = client.delete(f"/statuses/{test_task.status_id}", headers=auth_headers)
        assert res.status_code == 409
