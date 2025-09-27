from aiohttp_apispec import querystring_schema, request_schema, response_schema
from app.questions.schemes import (
    QuestionDeleteSchema,
    QuestionSchema,
    QuestionsQuerySchema,
)
from app.web.app import View
from app.web.mixins import AdminRequiredMixin
from app.web.utils import error_json_response, json_response


class QuestionsView(AdminRequiredMixin, View):
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema, 200)
    async def post(self):
        data = self.data
        question = await self.store.questions.create_question(data)
        return json_response(QuestionSchema().dump(question))

    @querystring_schema(QuestionsQuerySchema)
    @response_schema(QuestionSchema)
    async def get(self):
        page = int(self.request.query.get("page", 1))
        limit = int(self.request.query.get("limit", 10))

        offset = (page - 1) * limit

        questions = await self.store.questions.get_questions(
            limit=limit, offset=offset
        )

        total = await self.store.questions.count_questions()

        return json_response(
            {
                "page": page,
                "limit": limit,
                "total": total,
                "items": QuestionSchema(many=True).dump(questions),
            }
        )

    @request_schema(QuestionDeleteSchema)
    @response_schema(QuestionSchema, 200)
    async def delete(
        self,
    ):
        data = self.data
        question = await self.store.questions.delete_question(data)
        if question:
            return json_response(QuestionSchema().dump(question))
        return error_json_response(
            http_status=400,
            status="error",
            message=f"Нет вопроса с id - {data['id']}",
        )
