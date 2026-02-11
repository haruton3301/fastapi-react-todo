from fastapi.testclient import TestClient

NONEXISTENT_ID = 9999

STATUS_JSON = {
    "name": "テストステータス",
    "color": "#FF0000",
}


def _create_status(client: TestClient, **overrides) -> dict:
    """ヘルパー: APIでステータスを作成してレスポンスを返す"""
    data = {**STATUS_JSON, **overrides}
    res = client.post("/statuses", json=data)
    assert res.status_code == 201
    return res.json()


class TestCreateStatus:
    def test_create(self, client: TestClient):
        body = _create_status(client)
        assert body["name"] == STATUS_JSON["name"]
        assert body["color"] == STATUS_JSON["color"]
        assert body["order"] == 1
        assert "id" in body
        assert "created_at" in body
        assert "updated_at" in body

    def test_auto_order(self, client: TestClient):
        s1 = _create_status(client, name="A")
        s2 = _create_status(client, name="B")
        s3 = _create_status(client, name="C")
        assert s1["order"] == 1
        assert s2["order"] == 2
        assert s3["order"] == 3

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

    def test_count(self, client: TestClient):
        _create_status(client, name="ステータス1")
        _create_status(client, name="ステータス2")
        _create_status(client, name="ステータス3")

        statuses = client.get("/statuses").json()["statuses"]
        assert len(statuses) == 3

    def test_order(self, client: TestClient):
        _create_status(client, name="先")
        _create_status(client, name="後")

        statuses = client.get("/statuses").json()["statuses"]
        assert statuses[0]["name"] == "先"
        assert statuses[1]["name"] == "後"


class TestGetStatus:
    def test_get(self, client: TestClient):
        created = _create_status(client)
        res = client.get(f"/statuses/{created['id']}")
        assert res.status_code == 200
        assert res.json()["name"] == STATUS_JSON["name"]

    def test_not_found(self, client: TestClient):
        res = client.get(f"/statuses/{NONEXISTENT_ID}")
        assert res.status_code == 404


class TestUpdateStatus:
    def test_update(self, client: TestClient):
        created = _create_status(client)
        update_data = {
            "name": "更新ステータス",
            "color": "#00FF00",
        }
        res = client.put(f"/statuses/{created['id']}", json=update_data)
        assert res.status_code == 200
        body = res.json()
        assert body["name"] == "更新ステータス"
        assert body["color"] == "#00FF00"

    def test_not_found(self, client: TestClient):
        res = client.put(f"/statuses/{NONEXISTENT_ID}", json=STATUS_JSON)
        assert res.status_code == 404

    def test_name_empty_returns_422(self, client: TestClient):
        created = _create_status(client)
        res = client.put(
            f"/statuses/{created['id']}", json={**STATUS_JSON, "name": ""}
        )
        assert res.status_code == 422


class TestReorderStatuses:
    def test_reorder(self, client: TestClient):
        s1 = _create_status(client, name="A")
        s2 = _create_status(client, name="B")
        s3 = _create_status(client, name="C")

        res = client.put("/statuses/reorder", json={"order": [s3["id"], s1["id"], s2["id"]]})
        assert res.status_code == 200
        statuses = res.json()["statuses"]
        assert statuses[0]["name"] == "C"
        assert statuses[1]["name"] == "A"
        assert statuses[2]["name"] == "B"

    def test_missing_ids_returns_400(self, client: TestClient):
        s1 = _create_status(client, name="A")
        _create_status(client, name="B")

        res = client.put("/statuses/reorder", json={"order": [s1["id"]]})
        assert res.status_code == 400

    def test_extra_ids_returns_400(self, client: TestClient):
        s1 = _create_status(client, name="A")

        res = client.put("/statuses/reorder", json={"order": [s1["id"], NONEXISTENT_ID]})
        assert res.status_code == 400


class TestDeleteStatus:
    def test_delete(self, client: TestClient):
        created = _create_status(client)
        res = client.delete(f"/statuses/{created['id']}")
        assert res.status_code == 204

        res = client.get(f"/statuses/{created['id']}")
        assert res.status_code == 404

    def test_not_found(self, client: TestClient):
        res = client.delete(f"/statuses/{NONEXISTENT_ID}")
        assert res.status_code == 404

    def test_delete_with_tasks_returns_409(self, client: TestClient):
        status = _create_status(client)
        client.post("/tasks", json={
            "title": "タスク",
            "content": "内容",
            "due_date": "2025-12-31",
            "status_id": status["id"],
        })
        res = client.delete(f"/statuses/{status['id']}")
        assert res.status_code == 409
