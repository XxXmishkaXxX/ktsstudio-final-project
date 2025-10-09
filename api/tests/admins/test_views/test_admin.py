from aiohttp.test_utils import TestClient
from app.web.config import Config


class TestAdminViews:
    async def test_admin_login_success(
        self, client: TestClient, config: Config
    ):
        resp = await client.post(
            "/admin.login",
            json={
                "email": config.admin.email,
                "password": config.admin.password,
            },
        )

        assert resp.status == 200
        data = await resp.json()
        assert data["status"] == "ok"
        assert data["data"]["email"] == config.admin.email
        assert data["data"]["id"] == 1

    async def test_admin_login_invalid_password(
        self, client: TestClient, config: Config
    ):
        resp = await client.post(
            "/admin.login",
            json={"email": config.admin.email, "password": "wrong_password"},
        )

        assert resp.status == 403
        data = await resp.json()
        assert data["status"] == "forbidden"

    async def test_admin_login_unknown_email(self, client: TestClient):
        resp = await client.post(
            "/admin.login",
            json={"email": "unknown@example.com", "password": "any_password"},
        )

        assert resp.status == 403
        data = await resp.json()
        assert data["status"] == "forbidden"

    async def test_admin_current_view(self, client: TestClient, config: Config):
        login_resp = await client.post(
            "/admin.login",
            json={
                "email": config.admin.email,
                "password": config.admin.password,
            },
        )
        assert login_resp.status == 200

        resp = await client.get("/admin.current")
        assert resp.status == 200
        data = await resp.json()
        assert data["status"] == "ok"
        assert data["data"]["email"] == config.admin.email
        assert data["data"]["id"] == 1
