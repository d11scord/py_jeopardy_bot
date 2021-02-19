from marshmallow import Schema, fields
from marshmallow.validate import Range


class UserSchema(Schema):
    user_id = fields.Int()
    firstname = fields.Str()
    lastname = fields.Str()
    score = fields.Int()
    # TODO: add games count


class UserListSchema(Schema):
    limit = fields.Int(missing=20, validate=Range(min=1, max=100))
    offset = fields.Int(missing=0, validate=Range(min=0))
