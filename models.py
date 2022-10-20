from tortoise import Model, fields


class Ex(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(31)


class User(Model):
    id = fields.IntField(pk=True)
    ex: fields.ForeignKeyRelation[Ex] = fields.ForeignKeyField(
        "models.Ex", related_name="users"
    )
    auths = fields.JSONField()
    status = fields.SmallIntField(default=1)


class Partners(Model):
    id: int = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="events"
    )
    tg_id: int = fields.IntField()
    status: int = fields.SmallIntField(default=1)

    def __str__(self):
        return f"User #{self.id}({self.status}) tg:{self.tg_id}"
