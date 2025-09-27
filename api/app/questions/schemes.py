from marshmallow import Schema, ValidationError, fields, validates_schema


class AnswerSchema(Schema):
    text = fields.Str(required=True)
    points = fields.Int(required=True)
    position = fields.Int(required=True, validate=lambda x: 1 <= x <= 5)


class QuestionSchema(Schema):
    id = fields.Int()
    text = fields.Str(required=True)
    answers = fields.List(fields.Nested(AnswerSchema), required=True)

    @validates_schema
    def validate_positions(self, data, **kwargs):
        positions = [answer["position"] for answer in data["answers"]]
        if len(positions) != len(set(positions)):
            raise ValidationError(
                "Все позиции ответов должны быть уникальны",
                field_name="answers",
            )


class QuestionsQuerySchema(Schema):
    page = fields.Int(load_default=1, validate=lambda x: x > 0)
    limit = fields.Int(load_default=10, validate=lambda x: x > 0)


class QuestionDeleteSchema(Schema):
    id = fields.Int(required=True)
