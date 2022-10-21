from enum import IntEnum, Enum

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


class ExType(Enum):
    main = "main"
    dex = "dex"
    other = "other"
    futures = "futures"
    p2p = "p2p"


class Cur(Model):
    id: str = fields.CharField(3, pk=True)


class Coin(Model):
    id: str = fields.CharField(7, pk=True)


class Ex(Model):
    id: int = fields.SmallIntField(pk=True)
    name: str = fields.CharField(31)
    type: ExType = fields.CharEnumField(ExType)


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
    auths: {} = fields.JSONField(null=True)  # todo: think about it - where move this attr in
    client: fields.ForeignKeyNullableRelation[Client] = fields.ForeignKeyField("models.Client", related_name="users")
    is_active: bool = fields.BooleanField(default=True)


class Ad(Model):
    id: int = fields.BigIntField(pk=True)
    pair: fields.ForeignKeyRelation[Pair] = fields.ForeignKeyField("models.Pair", related_name="ads")
    maxFiat: float = fields.FloatField()
    minFiat: float = fields.FloatField()
    pts: fields.ManyToManyRelation["Pt"] = fields.ManyToManyField("models.Pt", "ad_pt", related_name="ads")
    user: fields.ForeignKeyRelation = fields.ForeignKeyField("models.User", "ads")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class Pt(Model):
    name: str = fields.CharField(31, pk=True)
    rank = fields.SmallIntField()
    ads: fields.ManyToManyRelation[Ad]
    fiats: fields.ManyToManyRelation["Fiat"]


class Fiat(Model):
    id: int = fields.IntField(pk=True)
    pt: fields.ManyToManyRelation[Pt] = fields.ManyToManyField("models.Pt", "limit", related_name="fiats")
    cur: fields.ForeignKeyRelation[Cur] = fields.ForeignKeyField("models.Cur", related_name="pts")
    client: fields.ForeignKeyRelation[Client] = fields.ForeignKeyField("models.Client", "fiats")
    amount: float = fields.FloatField()
    target: float = fields.FloatField()


class Limit(Model):
    fiat: fields.ForeignKeyRelation[Fiat] = fields.ForeignKeyField("models.Fiat", related_name="limits")
    pt: fields.ForeignKeyRelation[Pt] = fields.ForeignKeyField("models.Pt", related_name="limits")
    limit: int = fields.IntField()


class Order(Model):
    id: int = fields.BigIntField(pk=True)
    ad: fields.ForeignKeyRelation[Ad] = fields.ForeignKeyField("models.Pair", related_name="orders")
    limit: fields.ForeignKeyRelation[Limit] = fields.ForeignKeyField("models.Limit", related_name="orders")
    user: fields.ForeignKeyRelation = fields.ForeignKeyField("models.User", "orders")
    status: OrderStatus = fields.IntEnumField(OrderStatus)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
