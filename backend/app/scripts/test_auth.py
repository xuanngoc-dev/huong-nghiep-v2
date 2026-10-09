"""Smoke test đăng ký / đăng nhập."""

from __future__ import annotations

import time

from fastapi.testclient import TestClient

from app.main import app


def main() -> None:
    client = TestClient(app)
    email = f"user{int(time.time())}@example.com"

    reg = client.post(
        "/api/v1/auth/register",
        json={
            "ho_ten": "Nguyen Van A",
            "email": email,
            "so_dien_thoai": None,
            "mat_khau": "secret123",
        },
    )
    print("register", reg.status_code, reg.json())
    assert reg.status_code == 201, reg.text

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "mat_khau": "secret123"},
    )
    print("login", login.status_code, login.json().get("user", {}).get("email"))
    assert login.status_code == 200, login.text

    token = login.json()["access_token"]
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    print("me", me.status_code, me.json())
    assert me.status_code == 200, me.text
    print("ALL OK")


if __name__ == "__main__":
    main()
