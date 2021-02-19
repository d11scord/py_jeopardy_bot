from marshmallow import Schema, fields
from marshmallow.validate import Range


class GameSessionSchema(Schema):
    id = fields.Int()
    chat_id = fields.Int()
    questions = fields.List(fields.Int)
    last_question_id = fields.Int()
    is_finished = fields.Boolean()


class GameSessionCreateSchema(Schema):
    chat_id = fields.Int(required=True)
    questions = fields.List(fields.Int)


class GameSessionListSchema(Schema):
    limit = fields.Int(missing=20, validate=Range(min=1, max=100))
    offset = fields.Int(missing=0, validate=Range(min=0))
    chat_id = fields.Int()
