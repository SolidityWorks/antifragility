from enum import IntEnum  # , Enum

from tortoise import Model, fields


class ClientStatus(IntEnum):
    me = 7
    my = 5
    own = 3
    pause = 2
    wait = 1
    block = 0


class OrderStatus(IntEnum):
    canceled = 0
    created = 1
    wait = 2
    done = 3


class Cur(Model):
    id: str = fields.CharField(3, pk=True)


class Coin(Model):
    id: str = fields.CharField(7, pk=True)


class Ex(Model):
    id: int = fields.SmallIntField(pk=True)
    name: str = fields.CharField(31)


class Pair(Model):
    id = fields.SmallIntField(pk=True)
    ex: fields.ForeignKeyRelation[Ex] = fields.ForeignKeyField("models.Ex", related_name="pairs")
    coin: fields.ForeignKeyRelation[Coin] = fields.ForeignKeyField("models.Coin", related_name="pairs")
    cur: fields.ForeignKeyRelation[Cur] = fields.ForeignKeyField("models.Cur", related_name="pairs")
    sell: bool = fields.BooleanField()
    price: float = fields.FloatField()
    fee: float = fields.FloatField()


class Client(Model):
    id: int = fields.SmallIntField(pk=True)
    tg_id: int = fields.IntField()
    status: ClientStatus = fields.IntEnumField(ClientStatus)

    def __str__(self):
        return f"User #{self.id}({self.status}) tg:{self.tg_id}"


class User(Model):
    id: int = fields.IntField(pk=True)
    ex: fields.ForeignKeyRelation[Ex] = fields.ForeignKeyField("models.Ex", related_name="users")
    auths: {} = fields.JSONField()
    client: fields.ForeignKeyNullableRelation[Client] = fields.ForeignKeyField("models.Client", related_name="users")
    is_active: bool = fields.BooleanField()


class Ad(Model):
    id: int = fields.BigIntField(pk=True)
    pair: fields.ForeignKeyRelation[Pair] = fields.ForeignKeyField("models.Pair", related_name="ads")
    maxFiat: float = fields.FloatField()
    minFiat: float = fields.FloatField()
    pts: fields.ManyToManyRelation["Pt"] = fields.ManyToManyField("models.Pt", "ad_pt", related_name="ads")
    user: fields.ForeignKeyRelation = fields.ForeignKeyField("models.User", "ads")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class PtGroup(Model):
    id: int = fields.SmallIntField(pk=True)
    name: str = fields.CharField(31)
    cur: fields.ForeignKeyRelation[Cur] = fields.ForeignKeyField("models.Cur", related_name="pt_groups")


class Pt(Model):
    id: str = fields.CharField(31, pk=True)
    group: fields.ForeignKeyRelation[PtGroup] = fields.ForeignKeyField("models.PtGroup", related_name="pts")
    rank = fields.SmallIntField()
    ads: fields.ManyToManyRelation[Ad]


class Fiat(Model):
    id: int = fields.IntField(pk=True)
    client: fields.ForeignKeyRelation[Client] = fields.ForeignKeyField("models.Client", "fiats")
    pt: fields.ForeignKeyRelation[Pt] = fields.ForeignKeyField("models.Pt", "fiats")
    amount: float = fields.FloatField()
    target: float = fields.FloatField()


class Order(Model):
    id: int = fields.BigIntField(pk=True)
    ad: fields.ForeignKeyRelation[Ad] = fields.ForeignKeyField("models.Pair", related_name="orders")
    pt: fields.ForeignKeyRelation[Pt] = fields.ForeignKeyField("models.Pt", related_name="orders")
    user: fields.ForeignKeyRelation = fields.ForeignKeyField("models.User", "orders")
    status: OrderStatus = fields.IntEnumField(OrderStatus)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
