from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import jwt
from fastapi.testclient import TestClient

from app.auth import (
    ALGORITHM,
    REFRESH_TOKEN_EXPIRES,
    TokenType,
    create_password_reset_token,
    create_token,
)
from app.config import settings
from app.models.user import User
from tests.factories import UserFactory


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

    def test_login_sets_refresh_cookie(self, client: TestClient, test_user: User):
        res = client.post("/auth/login", data={
            "username": "test@example.com",
            "password": "testpassword",
        })
        assert res.status_code == 200
        assert "refresh_token" in res.cookies

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

    def test_refresh_token_rejected_as_bearer(
        self, client: TestClient, test_user: User
    ):
        """Refresh token を Bearer として使えないことを確認"""
        refresh = create_token(test_user.id, TokenType.REFRESH, REFRESH_TOKEN_EXPIRES)
        res = client.get("/auth/me", headers={"Authorization": f"Bearer {refresh}"})
        assert res.status_code == 401


class TestRefresh:
    def test_refresh_success(self, client: TestClient, test_user: User):
        refresh = create_token(test_user.id, TokenType.REFRESH, REFRESH_TOKEN_EXPIRES)
        res = client.post("/auth/refresh", cookies={"refresh_token": refresh})
        assert res.status_code == 200
        body = res.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        # 新しい refresh cookie がセットされること
        assert "refresh_token" in res.cookies

    def test_refresh_no_cookie(self, client: TestClient):
        res = client.post("/auth/refresh")
        assert res.status_code == 401

    def test_refresh_expired_token(self, client: TestClient, test_user: User):
        expired_payload = {
            "sub": str(test_user.id),
            "type": "refresh",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        }
        expired_token = jwt.encode(
            expired_payload, settings.secret_key, algorithm=ALGORITHM
        )
        res = client.post(
            "/auth/refresh", cookies={"refresh_token": expired_token}
        )
        assert res.status_code == 401

    def test_refresh_with_access_token_rejected(
        self, client: TestClient, test_user: User, auth_headers: dict
    ):
        """Access token を refresh に使えないことを確認"""
        access_token = auth_headers["Authorization"].split(" ")[1]
        res = client.post(
            "/auth/refresh", cookies={"refresh_token": access_token}
        )
        assert res.status_code == 401


class TestUpdateMe:
    def test_update(self, client: TestClient, test_user: User, auth_headers: dict):
        res = client.put("/auth/me", json={"username": "newname"}, headers=auth_headers)
        assert res.status_code == 200
        body = res.json()
        assert body["username"] == "newname"

    def test_duplicate_username_returns_409(
        self, client: TestClient, db, test_user: User, auth_headers: dict
    ):
        UserFactory(username="otheruser", email="other@example.com")
        res = client.put("/auth/me", json={"username": "otheruser"}, headers=auth_headers)
        assert res.status_code == 409

    def test_short_username_returns_422(
        self, client: TestClient, test_user: User, auth_headers: dict
    ):
        res = client.put("/auth/me", json={"username": "ab"}, headers=auth_headers)
        assert res.status_code == 422

    def test_unauthenticated_returns_401(self, client: TestClient):
        res = client.put("/auth/me", json={"username": "newname"})
        assert res.status_code == 401


class TestLogout:
    def test_logout(self, client: TestClient, test_user: User):
        # まずログインして cookie を取得
        login_res = client.post("/auth/login", data={
            "username": "test@example.com",
            "password": "testpassword",
        })
        assert "refresh_token" in login_res.cookies

        res = client.post("/auth/logout")
        assert res.status_code == 204
        # Cookie 削除の Set-Cookie ヘッダーが含まれること
        set_cookie = res.headers.get("set-cookie", "")
        assert "refresh_token" in set_cookie

    def test_logout_without_cookie(self, client: TestClient):
        """Cookie がなくても 204 を返す"""
        res = client.post("/auth/logout")
        assert res.status_code == 204


class TestPasswordReset:
    def test_request_returns_202(self, client: TestClient, test_user: User):
        with patch("app.routers.auth.send_password_reset_email", new_callable=AsyncMock):
            res = client.post("/auth/password-reset/request", json={"email": "test@example.com"})
        assert res.status_code == 202

    def test_request_unknown_email_returns_202(self, client: TestClient):
        with patch("app.routers.auth.send_password_reset_email", new_callable=AsyncMock):
            res = client.post("/auth/password-reset/request", json={"email": "unknown@example.com"})
        assert res.status_code == 202

    def test_confirm_success(self, client: TestClient, test_user: User, db):
        token = create_password_reset_token(test_user)
        res = client.post("/auth/password-reset/confirm", json={
            "token": token,
            "new_password": "newpassword123",
        })
        assert res.status_code == 200
        db.refresh(test_user)
        # 新しいパスワードでログインできること
        login_res = client.post("/auth/login", data={
            "username": "test@example.com",
            "password": "newpassword123",
        })
        assert login_res.status_code == 200

    def test_confirm_invalid_token_returns_400(self, client: TestClient):
        res = client.post("/auth/password-reset/confirm", json={
            "token": "invalid.token.here",
            "new_password": "newpassword123",
        })
        assert res.status_code == 400

    def test_confirm_already_used_token_returns_400(
        self, client: TestClient, test_user: User
    ):
        token = create_password_reset_token(test_user)
        # 1回目のリセット
        res = client.post("/auth/password-reset/confirm", json={
            "token": token,
            "new_password": "newpassword123",
        })
        assert res.status_code == 200
        # 同じトークンで2回目 → パスワードが変わったので pwd フィンガープリント不一致
        res2 = client.post("/auth/password-reset/confirm", json={
            "token": token,
            "new_password": "anotherpassword456",
        })
        assert res2.status_code == 400
