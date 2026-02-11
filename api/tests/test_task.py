from fastapi.testclient import TestClient

NONEXISTENT_ID = 9999

TASK_JSON = {
    "title": "テストタスク",
    "content": "テスト内容",
    "due_date": "2025-12-31",
}


def _create_task(client: TestClient, **overrides) -> dict:
    """ヘルパー: APIでタスクを作成してレスポンスを返す"""
    data = {**TASK_JSON, **overrides}
    res = client.post("/tasks", json=data)
    assert res.status_code == 201
    return res.json()


class TestCreateTask:
    def test_create(self, client: TestClient):
        body = _create_task(client)
        assert body["title"] == TASK_JSON["title"]
        assert body["content"] == TASK_JSON["content"]
        assert body["due_date"] == TASK_JSON["due_date"]
        assert "id" in body
        assert "created_at" in body
        assert "updated_at" in body

    def test_title_empty_returns_422(self, client: TestClient):
        res = client.post("/tasks", json={**TASK_JSON, "title": ""})
        assert res.status_code == 422

    def test_missing_fields_returns_422(self, client: TestClient):
        res = client.post("/tasks", json={})
        assert res.status_code == 422


class TestListTasks:
    def test_empty(self, client: TestClient):
        res = client.get("/tasks")
        assert res.status_code == 200
        assert res.json()["tasks"] == []

    def test_count(self, client: TestClient):
        _create_task(client, title="タスク1")
        _create_task(client, title="タスク2")
        _create_task(client, title="タスク3")

        tasks = client.get("/tasks").json()["tasks"]
        assert len(tasks) == 3

    def test_order_desc(self, client: TestClient):
        _create_task(client, title="古い", due_date="2025-01-01")
        _create_task(client, title="新しい", due_date="2025-12-31")

        tasks = client.get("/tasks", params={"order": "desc"}).json()["tasks"]
        assert tasks[0]["title"] == "新しい"
        assert tasks[1]["title"] == "古い"

    def test_order_asc(self, client: TestClient):
        _create_task(client, title="古い", due_date="2025-01-01")
        _create_task(client, title="新しい", due_date="2025-12-31")

        tasks = client.get("/tasks", params={"order": "asc"}).json()["tasks"]
        assert tasks[0]["title"] == "古い"
        assert tasks[1]["title"] == "新しい"


class TestGetTask:
    def test_get(self, client: TestClient):
        created = _create_task(client)
        res = client.get(f"/tasks/{created['id']}")
        assert res.status_code == 200
        assert res.json()["title"] == TASK_JSON["title"]

    def test_not_found(self, client: TestClient):
        res = client.get(f"/tasks/{NONEXISTENT_ID}")
        assert res.status_code == 404


class TestUpdateTask:
    def test_update(self, client: TestClient):
        created = _create_task(client)
        update_data = {
            "title": "更新タイトル",
            "content": "更新内容",
            "due_date": "2026-06-15",
        }
        res = client.put(f"/tasks/{created['id']}", json=update_data)
        assert res.status_code == 200
        body = res.json()
        assert body["title"] == "更新タイトル"
        assert body["content"] == "更新内容"
        assert body["due_date"] == "2026-06-15"

    def test_not_found(self, client: TestClient):
        res = client.put(f"/tasks/{NONEXISTENT_ID}", json=TASK_JSON)
        assert res.status_code == 404

    def test_title_empty_returns_422(self, client: TestClient):
        created = _create_task(client)
        res = client.put(
            f"/tasks/{created['id']}", json={**TASK_JSON, "title": ""}
        )
        assert res.status_code == 422


class TestDeleteTask:
    def test_delete(self, client: TestClient):
        created = _create_task(client)
        res = client.delete(f"/tasks/{created['id']}")
        assert res.status_code == 204

        res = client.get(f"/tasks/{created['id']}")
        assert res.status_code == 404

    def test_not_found(self, client: TestClient):
        res = client.delete(f"/tasks/{NONEXISTENT_ID}")
        assert res.status_code == 404
