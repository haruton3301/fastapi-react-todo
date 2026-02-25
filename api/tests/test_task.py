from fastapi.testclient import TestClient

from app.models.status import Status
from app.models.task import Task

NONEXISTENT_ID = 9999

TASK_JSON = {
    "title": "テストタスク",
    "content": "テスト内容",
    "due_date": "2025-12-31",
}


class TestCreateTask:
    def test_create(self, client: TestClient, test_status: Status, auth_headers: dict):
        res = client.post("/tasks", json={**TASK_JSON, "status_id": test_status.id}, headers=auth_headers)
        assert res.status_code == 201
        body = res.json()
        assert body["title"] == TASK_JSON["title"]
        assert body["content"] == TASK_JSON["content"]
        assert body["due_date"] == TASK_JSON["due_date"]
        assert "id" in body
        assert "status_id" in body
        assert "created_at" in body
        assert "updated_at" in body

    def test_title_empty_returns_422(self, client: TestClient, test_status: Status, auth_headers: dict):
        res = client.post("/tasks", json={**TASK_JSON, "title": "", "status_id": test_status.id}, headers=auth_headers)
        assert res.status_code == 422

    def test_missing_fields_returns_422(self, client: TestClient, auth_headers: dict):
        res = client.post("/tasks", json={}, headers=auth_headers)
        assert res.status_code == 422

    def test_invalid_status_returns_404(self, client: TestClient, auth_headers: dict):
        res = client.post("/tasks", json={**TASK_JSON, "status_id": NONEXISTENT_ID}, headers=auth_headers)
        assert res.status_code == 404

    def test_other_user_status_returns_404(self, client: TestClient, other_user_status: Status, auth_headers: dict):
        res = client.post("/tasks", json={**TASK_JSON, "status_id": other_user_status.id}, headers=auth_headers)
        assert res.status_code == 404

    def test_unauthenticated_returns_401(self, client: TestClient, test_status: Status):
        res = client.post("/tasks", json={**TASK_JSON, "status_id": test_status.id})
        assert res.status_code == 401


class TestListTasks:
    def test_empty(self, client: TestClient, auth_headers: dict):
        res = client.get("/tasks", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["tasks"] == []

    def test_count(self, client: TestClient, test_tasks: list[Task], auth_headers: dict):
        tasks = client.get("/tasks", headers=auth_headers).json()["tasks"]
        assert len(tasks) == 3

    def test_order_desc(self, client: TestClient, test_tasks: list[Task], auth_headers: dict):
        # test_tasks: タスク1(6/1), タスク2(9/15), タスク3(12/31)
        tasks = client.get("/tasks", params={"order": "desc"}, headers=auth_headers).json()["tasks"]
        assert tasks[0]["title"] == "タスク3"
        assert tasks[1]["title"] == "タスク2"

    def test_order_asc(self, client: TestClient, test_tasks: list[Task], auth_headers: dict):
        # test_tasks: タスク1(6/1), タスク2(9/15), タスク3(12/31)
        tasks = client.get("/tasks", params={"order": "asc"}, headers=auth_headers).json()["tasks"]
        assert tasks[0]["title"] == "タスク1"
        assert tasks[1]["title"] == "タスク2"

    def test_search_by_title(self, client: TestClient, test_tasks: list[Task], auth_headers: dict):
        tasks = client.get("/tasks", params={"q": "タスク1"}, headers=auth_headers).json()["tasks"]
        assert len(tasks) == 1
        assert tasks[0]["title"] == "タスク1"

    def test_search_by_content(self, client: TestClient, test_tasks: list[Task], auth_headers: dict):
        tasks = client.get("/tasks", params={"q": "内容1"}, headers=auth_headers).json()["tasks"]
        assert len(tasks) == 1
        assert tasks[0]["title"] == "タスク1"

    def test_search_no_match(self, client: TestClient, test_tasks: list[Task], auth_headers: dict):
        tasks = client.get("/tasks", params={"q": "存在しない"}, headers=auth_headers).json()["tasks"]
        assert len(tasks) == 0

    def test_search_without_q_returns_all(self, client: TestClient, test_tasks: list[Task], auth_headers: dict):
        tasks = client.get("/tasks", headers=auth_headers).json()["tasks"]
        assert len(tasks) == 3

    def test_due_date_from(self, client: TestClient, test_tasks: list[Task], auth_headers: dict):
        # タスク1(6/1), タスク2(9/15), タスク3(12/31) → 9/15以降
        tasks = client.get("/tasks", params={"due_date_from": "2025-09-15"}, headers=auth_headers).json()["tasks"]
        assert len(tasks) == 2
        titles = {t["title"] for t in tasks}
        assert titles == {"タスク2", "タスク3"}

    def test_due_date_to(self, client: TestClient, test_tasks: list[Task], auth_headers: dict):
        # タスク1(6/1), タスク2(9/15), タスク3(12/31) → 9/15以前
        tasks = client.get("/tasks", params={"due_date_to": "2025-09-15"}, headers=auth_headers).json()["tasks"]
        assert len(tasks) == 2
        titles = {t["title"] for t in tasks}
        assert titles == {"タスク1", "タスク2"}

    def test_due_date_range(self, client: TestClient, test_tasks: list[Task], auth_headers: dict):
        tasks = client.get("/tasks", params={"due_date_from": "2025-06-01", "due_date_to": "2025-09-15"}, headers=auth_headers).json()["tasks"]
        assert len(tasks) == 2

    def test_due_date_no_match(self, client: TestClient, test_tasks: list[Task], auth_headers: dict):
        tasks = client.get("/tasks", params={"due_date_from": "2030-01-01"}, headers=auth_headers).json()["tasks"]
        assert len(tasks) == 0

    def test_unauthenticated_returns_401(self, client: TestClient):
        res = client.get("/tasks")
        assert res.status_code == 401


class TestGetTask:
    def test_get(self, client: TestClient, test_task: Task, auth_headers: dict):
        res = client.get(f"/tasks/{test_task.id}", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["title"] == "テストタスク"

    def test_not_found(self, client: TestClient, auth_headers: dict):
        res = client.get(f"/tasks/{NONEXISTENT_ID}", headers=auth_headers)
        assert res.status_code == 404


class TestUpdateTask:
    def test_update(self, client: TestClient, test_task: Task, auth_headers: dict):
        update_data = {
            "title": "更新タイトル",
            "content": "更新内容",
            "due_date": "2026-06-15",
            "status_id": test_task.status_id,
        }
        res = client.put(f"/tasks/{test_task.id}", json=update_data, headers=auth_headers)
        assert res.status_code == 200
        body = res.json()
        assert body["title"] == "更新タイトル"
        assert body["content"] == "更新内容"
        assert body["due_date"] == "2026-06-15"

    def test_not_found(self, client: TestClient, test_status: Status, auth_headers: dict):
        res = client.put(
            f"/tasks/{NONEXISTENT_ID}",
            json={**TASK_JSON, "status_id": test_status.id},
            headers=auth_headers,
        )
        assert res.status_code == 404

    def test_invalid_status_returns_404(self, client: TestClient, test_task: Task, auth_headers: dict):
        res = client.put(
            f"/tasks/{test_task.id}",
            json={**TASK_JSON, "status_id": NONEXISTENT_ID},
            headers=auth_headers,
        )
        assert res.status_code == 404

    def test_other_user_status_returns_404(self, client: TestClient, test_task: Task, other_user_status: Status, auth_headers: dict):
        res = client.put(
            f"/tasks/{test_task.id}",
            json={**TASK_JSON, "status_id": other_user_status.id},
            headers=auth_headers,
        )
        assert res.status_code == 404

    def test_title_empty_returns_422(self, client: TestClient, test_task: Task, auth_headers: dict):
        res = client.put(
            f"/tasks/{test_task.id}",
            json={**TASK_JSON, "title": "", "status_id": test_task.status_id},
            headers=auth_headers,
        )
        assert res.status_code == 422


class TestDeleteTask:
    def test_delete(self, client: TestClient, test_task: Task, auth_headers: dict):
        res = client.delete(f"/tasks/{test_task.id}", headers=auth_headers)
        assert res.status_code == 204

        res = client.get(f"/tasks/{test_task.id}", headers=auth_headers)
        assert res.status_code == 404

    def test_not_found(self, client: TestClient, auth_headers: dict):
        res = client.delete(f"/tasks/{NONEXISTENT_ID}", headers=auth_headers)
        assert res.status_code == 404
