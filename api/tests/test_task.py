from fastapi.testclient import TestClient

NONEXISTENT_ID = 9999

STATUS_JSON = {
    "name": "テストステータス",
    "color": "#6B7280",
}

TASK_JSON = {
    "title": "テストタスク",
    "content": "テスト内容",
    "due_date": "2025-12-31",
}


def _create_status(client: TestClient, **overrides) -> dict:
    """ヘルパー: APIでステータスを作成してレスポンスを返す"""
    data = {**STATUS_JSON, **overrides}
    res = client.post("/statuses", json=data)
    assert res.status_code == 201
    return res.json()


def _create_task(client: TestClient, **overrides) -> dict:
    """ヘルパー: APIでタスクを作成してレスポンスを返す"""
    if "status_id" not in overrides:
        status = _create_status(client)
        overrides["status_id"] = status["id"]
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
        assert "status_id" in body
        assert "created_at" in body
        assert "updated_at" in body

    def test_title_empty_returns_422(self, client: TestClient):
        status = _create_status(client)
        res = client.post("/tasks", json={**TASK_JSON, "title": "", "status_id": status["id"]})
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
        status = _create_status(client)
        sid = status["id"]
        _create_task(client, title="タスク1", status_id=sid)
        _create_task(client, title="タスク2", status_id=sid)
        _create_task(client, title="タスク3", status_id=sid)

        tasks = client.get("/tasks").json()["tasks"]
        assert len(tasks) == 3

    def test_order_desc(self, client: TestClient):
        status = _create_status(client)
        sid = status["id"]
        _create_task(client, title="古い", due_date="2025-01-01", status_id=sid)
        _create_task(client, title="新しい", due_date="2025-12-31", status_id=sid)

        tasks = client.get("/tasks", params={"order": "desc"}).json()["tasks"]
        assert tasks[0]["title"] == "新しい"
        assert tasks[1]["title"] == "古い"

    def test_order_asc(self, client: TestClient):
        status = _create_status(client)
        sid = status["id"]
        _create_task(client, title="古い", due_date="2025-01-01", status_id=sid)
        _create_task(client, title="新しい", due_date="2025-12-31", status_id=sid)

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
            "status_id": created["status_id"],
        }
        res = client.put(f"/tasks/{created['id']}", json=update_data)
        assert res.status_code == 200
        body = res.json()
        assert body["title"] == "更新タイトル"
        assert body["content"] == "更新内容"
        assert body["due_date"] == "2026-06-15"

    def test_not_found(self, client: TestClient):
        status = _create_status(client)
        res = client.put(
            f"/tasks/{NONEXISTENT_ID}",
            json={**TASK_JSON, "status_id": status["id"]},
        )
        assert res.status_code == 404

    def test_title_empty_returns_422(self, client: TestClient):
        created = _create_task(client)
        res = client.put(
            f"/tasks/{created['id']}",
            json={**TASK_JSON, "title": "", "status_id": created["status_id"]},
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
