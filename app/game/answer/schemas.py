from marshmallow import Schema, fields
from marshmallow.validate import Range


class AnswerSchema(Schema):
    # id = fields.Int()
    question_id = fields.Int()
    title = fields.Str()
    is_right = fields.Bool()


class AnswerCreateSchema(Schema):
    question_id = fields.Int(required=True)
    title = fields.Str(required=True)
    is_right = fields.Bool(required=True, default=False)


class AnswerUpdateSchema(Schema):
    id = fields.Int(required=True)
    question_id = fields.Int(required=True)
    title = fields.Str(required=True)
    is_right = fields.Bool(required=True, default=False)


class AnswerDeleteSchema(Schema):
    id = fields.Int(required=True)


class AnswerListSchema(Schema):
    limit = fields.Int(missing=20, validate=Range(min=1, max=100))
    offset = fields.Int(missing=0, validate=Range(min=0))
    question_id = fields.Int()
    title = fields.Str()
