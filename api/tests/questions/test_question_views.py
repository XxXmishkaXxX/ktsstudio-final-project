from aiohttp.test_utils import TestClient


class TestQuestionsAPI:
    async def test_post_question_unauthorized(self, client: TestClient):
        payload = {
            "text": "Попытка без авторизации?",
            "answers": [
                {"text": "A", "points": 10, "position": 1},
                {"text": "B", "points": 5, "position": 2},
                {"text": "C", "points": 3, "position": 3},
                {"text": "D", "points": 2, "position": 4},
                {"text": "E", "points": 1, "position": 5},
            ],
        }

        resp = await client.post("/questions", json=payload)
        assert resp.status == 401

        data = await resp.json()
        assert "error" in data or "message" in data

    async def test_post_question_valid(self, auth_cli: TestClient):
        payload = {
            "text": "Назовите языки программирования?",
            "answers": [
                {"text": "Python", "points": 10, "position": 1},
                {"text": "Java", "points": 5, "position": 2},
                {"text": "C++", "points": 3, "position": 3},
                {"text": "Go", "points": 2, "position": 4},
                {"text": "Rust", "points": 1, "position": 5},
            ],
        }

        resp = await auth_cli.post("/questions", json=payload)
        assert resp.status == 200

        data = await resp.json()
        assert data["data"]["text"] == payload["text"]
        assert len(data["data"]["answers"]) == 5
        positions = [a["position"] for a in data["data"]["answers"]]
        assert len(positions) == len(set(positions))

    async def test_post_question_invalid_count(self, auth_cli: TestClient):
        payload = {
            "text": "Вопрос с 3 ответами?",
            "answers": [
                {"text": "Ответ 1", "points": 10, "position": 1},
                {"text": "Ответ 2", "points": 5, "position": 2},
                {"text": "Ответ 3", "points": 3, "position": 3},
            ],
        }

        resp = await auth_cli.post("/questions", json=payload)
        assert resp.status == 400

    async def test_post_question_invalid_positions(self, auth_cli: TestClient):
        payload = {
            "text": "Вопрос с повторяющимися позициями?",
            "answers": [
                {"text": "Ответ 1", "points": 10, "position": 1},
                {"text": "Ответ 2", "points": 5, "position": 1},  # дубликат
                {"text": "Ответ 3", "points": 3, "position": 3},
                {"text": "Ответ 4", "points": 2, "position": 4},
                {"text": "Ответ 5", "points": 1, "position": 5},
            ],
        }

        resp = await auth_cli.post("/questions", json=payload)
        assert resp.status == 400

    async def test_get_questions_pagination(self, auth_cli: TestClient, store):
        for i in range(3):
            await store.questions.create_question(
                {
                    "text": f"Вопрос {i + 1}?",
                    "answers": [
                        {
                            "text": f"Ответ {j + 1}",
                            "points": j + 1,
                            "position": j + 1,
                        }
                        for j in range(5)
                    ],
                }
            )

        resp = await auth_cli.get("/questions?page=1&limit=2")
        assert resp.status == 200

        data = await resp.json()
        assert data["data"]["page"] == 1
        assert data["data"]["limit"] == 2
        assert "items" in data["data"]
        for item in data["data"]["items"]:
            assert len(item["answers"]) == 5
            positions = [a["position"] for a in item["answers"]]
            assert len(positions) == len(set(positions))

    async def test_delete_question_success(self, auth_cli: TestClient, store):
        question = await store.questions.create_question(
            {
                "text": "Удаляемый вопрос?",
                "answers": [
                    {
                        "text": f"Ответ {i + 1}",
                        "points": i + 1,
                        "position": i + 1,
                    }
                    for i in range(5)
                ],
            }
        )

        resp = await auth_cli.delete("/questions", json={"id": question.id})
        assert resp.status == 200
        data = await resp.json()
        assert data["data"]["id"] == question.id

    async def test_delete_question_not_found(self, auth_cli: TestClient):
        resp = await auth_cli.delete("/questions", json={"id": 99999})
        assert resp.status == 400
        data = await resp.json()
        assert "Нет вопроса с id" in data["message"]
