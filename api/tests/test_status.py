from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.utils import create_status_in_db, create_task_in_db

NONEXISTENT_ID = 9999

STATUS_JSON = {
    "name": "テストステータス",
    "color": "#FF0000",
}


class TestCreateStatus:
    def test_create(self, client: TestClient):
        res = client.post("/statuses", json=STATUS_JSON)
        assert res.status_code == 201
        body = res.json()
        assert body["name"] == STATUS_JSON["name"]
        assert body["color"] == STATUS_JSON["color"]
        assert body["order"] == 1
        assert "id" in body
        assert "created_at" in body
        assert "updated_at" in body

    def test_auto_order(self, client: TestClient):
        r1 = client.post("/statuses", json={**STATUS_JSON, "name": "A"})
        r2 = client.post("/statuses", json={**STATUS_JSON, "name": "B"})
        r3 = client.post("/statuses", json={**STATUS_JSON, "name": "C"})
        assert r1.json()["order"] == 1
        assert r2.json()["order"] == 2
        assert r3.json()["order"] == 3

    def test_name_empty_returns_422(self, client: TestClient):
        res = client.post("/statuses", json={**STATUS_JSON, "name": ""})
        assert res.status_code == 422

    def test_missing_fields_returns_422(self, client: TestClient):
        res = client.post("/statuses", json={})
        assert res.status_code == 422


class TestListStatuses:
    def test_empty(self, client: TestClient):
        res = client.get("/statuses")
        assert res.status_code == 200
        assert res.json()["statuses"] == []

    def test_count(self, client: TestClient, db: Session):
        create_status_in_db(db, name="ステータス1", order=1)
        create_status_in_db(db, name="ステータス2", order=2)
        create_status_in_db(db, name="ステータス3", order=3)

        statuses = client.get("/statuses").json()["statuses"]
        assert len(statuses) == 3

    def test_order(self, client: TestClient, db: Session):
        create_status_in_db(db, name="先", order=1)
        create_status_in_db(db, name="後", order=2)

        statuses = client.get("/statuses").json()["statuses"]
        assert statuses[0]["name"] == "先"
        assert statuses[1]["name"] == "後"


class TestGetStatus:
    def test_get(self, client: TestClient, db: Session):
        status = create_status_in_db(db)
        res = client.get(f"/statuses/{status.id}")
        assert res.status_code == 200
        assert res.json()["name"] == "テストステータス"

    def test_not_found(self, client: TestClient):
        res = client.get(f"/statuses/{NONEXISTENT_ID}")
        assert res.status_code == 404


class TestUpdateStatus:
    def test_update(self, client: TestClient, db: Session):
        status = create_status_in_db(db)
        update_data = {
            "name": "更新ステータス",
            "color": "#00FF00",
        }
        res = client.put(f"/statuses/{status.id}", json=update_data)
        assert res.status_code == 200
        body = res.json()
        assert body["name"] == "更新ステータス"
        assert body["color"] == "#00FF00"

    def test_not_found(self, client: TestClient):
        res = client.put(f"/statuses/{NONEXISTENT_ID}", json=STATUS_JSON)
        assert res.status_code == 404

    def test_name_empty_returns_422(self, client: TestClient, db: Session):
        status = create_status_in_db(db)
        res = client.put(
            f"/statuses/{status.id}", json={**STATUS_JSON, "name": ""}
        )
        assert res.status_code == 422


class TestReorderStatuses:
    def test_reorder(self, client: TestClient, db: Session):
        s1 = create_status_in_db(db, name="A", order=1)
        s2 = create_status_in_db(db, name="B", order=2)
        s3 = create_status_in_db(db, name="C", order=3)

        res = client.put("/statuses/reorder", json={"order": [s3.id, s1.id, s2.id]})
        assert res.status_code == 200
        statuses = res.json()["statuses"]
        assert statuses[0]["name"] == "C"
        assert statuses[1]["name"] == "A"
        assert statuses[2]["name"] == "B"

    def test_missing_ids_returns_400(self, client: TestClient, db: Session):
        s1 = create_status_in_db(db, name="A", order=1)
        create_status_in_db(db, name="B", order=2)

        res = client.put("/statuses/reorder", json={"order": [s1.id]})
        assert res.status_code == 400

    def test_extra_ids_returns_400(self, client: TestClient, db: Session):
        s1 = create_status_in_db(db, name="A", order=1)

        res = client.put("/statuses/reorder", json={"order": [s1.id, NONEXISTENT_ID]})
        assert res.status_code == 400


class TestDeleteStatus:
    def test_delete(self, client: TestClient, db: Session):
        status = create_status_in_db(db)
        res = client.delete(f"/statuses/{status.id}")
        assert res.status_code == 204

        res = client.get(f"/statuses/{status.id}")
        assert res.status_code == 404

    def test_not_found(self, client: TestClient):
        res = client.delete(f"/statuses/{NONEXISTENT_ID}")
        assert res.status_code == 404

    def test_delete_with_tasks_returns_409(self, client: TestClient, db: Session):
        task = create_task_in_db(db)
        res = client.delete(f"/statuses/{task.status_id}")
        assert res.status_code == 409
