from aiohttp_apispec import request_schema, response_schema
from aiohttp_session import new_session
from app.admin.schemes import AdminSchema
from db_core.accessors.admins import AdminAccessor
from app.web.app import View
from app.web.mixins import AdminRequiredMixin
from app.web.utils import error_json_response, json_response


class AdminLoginView(View):
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        email = self.data.get("email")
        password = self.data.get("password")

        admin_accessor: AdminAccessor = self.store.admins
        admin = await admin_accessor.get_by_email(email)

        if not admin or not await admin_accessor.verify_password(
            password, admin.password
        ):
            return error_json_response(
                http_status=403,
                status="forbidden",
                message="Invalid credentials",
                data={},
            )

        session = await new_session(request=self.request)
        session["role"] = "admin"
        session["email"] = admin.email
        session["id"] = admin.id

        return json_response(
            status="ok", data={"email": admin.email, "id": admin.id}
        )


class AdminCurrentView(AdminRequiredMixin, View):
    @response_schema(AdminSchema, 200)
    async def get(self):
        admin = self.request.admin
        return json_response(
            status="ok", data={"id": admin["id"], "email": admin["email"]}
        )
