from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


SIGNUP_JSON = {
    "username": "newuser",
    "email": "new@example.com",
    "password": "password123",
}


class TestSignup:
    def test_signup(self, client: TestClient):
        res = client.post("/auth/signup", json=SIGNUP_JSON)
        assert res.status_code == 201
        body = res.json()
        assert body["username"] == "newuser"
        assert body["email"] == "new@example.com"
        assert "id" in body
        assert "password" not in body
        assert "hashed_password" not in body

    def test_duplicate_username(self, client: TestClient, test_user: User):
        res = client.post("/auth/signup", json={
            "username": "testuser",
            "email": "other@example.com",
            "password": "password123",
        })
        assert res.status_code == 409

    def test_duplicate_email(self, client: TestClient, test_user: User):
        res = client.post("/auth/signup", json={
            "username": "otheruser",
            "email": "test@example.com",
            "password": "password123",
        })
        assert res.status_code == 409

    def test_short_username(self, client: TestClient):
        res = client.post("/auth/signup", json={**SIGNUP_JSON, "username": "ab"})
        assert res.status_code == 422

    def test_short_password(self, client: TestClient):
        res = client.post("/auth/signup", json={**SIGNUP_JSON, "password": "short"})
        assert res.status_code == 422


class TestLogin:
    def test_login(self, client: TestClient, test_user: User):
        res = client.post("/auth/login", data={
            "username": "test@example.com",
            "password": "testpassword",
        })
        assert res.status_code == 200
        body = res.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_wrong_password(self, client: TestClient, test_user: User):
        res = client.post("/auth/login", data={
            "username": "test@example.com",
            "password": "wrongpassword",
        })
        assert res.status_code == 401

    def test_nonexistent_user(self, client: TestClient):
        res = client.post("/auth/login", data={
            "username": "noone@example.com",
            "password": "password123",
        })
        assert res.status_code == 401


class TestMe:
    def test_me(self, client: TestClient, test_user: User, auth_headers: dict):
        res = client.get("/auth/me", headers=auth_headers)
        assert res.status_code == 200
        body = res.json()
        assert body["username"] == "testuser"
        assert body["email"] == "test@example.com"

    def test_unauthenticated(self, client: TestClient):
        res = client.get("/auth/me")
        assert res.status_code == 401
