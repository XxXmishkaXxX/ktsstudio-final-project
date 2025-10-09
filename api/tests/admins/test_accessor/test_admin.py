from app.store import Store
from app.web.config import Config
from passlib.hash import pbkdf2_sha256
from shared_models.admins import AdminModel


class TestAdminAccessor:
    async def test_admin_created_on_app_start(
        self, store: Store, config: Config
    ):
        """Проверяем, что при setup_app создаётся админ из конфига."""
        admin_accessor = store.admins
        admin = await admin_accessor.get_by_email(config.admin.email)
        assert admin is not None
        assert admin.email == config.admin.email

    async def test_create_and_get_admin(self, store: Store):
        """Проверяем создание и получение админа вручную."""
        email = "new_admin@example.com"
        password = "secret123"

        admin = await store.admins.create_admin(email, password)
        assert isinstance(admin, AdminModel)
        assert admin.email == email

        fetched = await store.admins.get_by_email(email)
        assert fetched.id == admin.id
        assert pbkdf2_sha256.verify(password, fetched.password)

    async def test_verify_password(self, store: Store):
        """Проверяем верификацию пароля."""
        password = "checkpass"
        admin = await store.admins.create_admin("verify@example.com", password)

        assert await store.admins.verify_password(password, admin.password)
        assert not await store.admins.verify_password("wrong", admin.password)
