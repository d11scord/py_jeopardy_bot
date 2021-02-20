from marshmallow import Schema, fields
from marshmallow.validate import Range


class QuestionSchema(Schema):
    id = fields.Int()
    theme = fields.Str()
    title = fields.Str()


class QuestionCreateSchema(Schema):
    theme = fields.Str(required=True)
    title = fields.Str(required=True)


class QuestionDeleteSchema(Schema):
    id = fields.Int(required=True)


QuestionGetSchema = QuestionDeleteSchema


class QuestionListSchema(Schema):
    limit = fields.Int(missing=20, validate=Range(min=1, max=100))
    offset = fields.Int(missing=0, validate=Range(min=0))
    theme = fields.Str()
