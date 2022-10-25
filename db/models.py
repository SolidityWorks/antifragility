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
    pts: fields.ManyToManyRelation["Pt"]


class Coin(Model):
    id: str = fields.CharField(7, pk=True)


class Ex(Model):
    id: int = fields.SmallIntField(pk=True)
    name: str = fields.CharField(31)
    type: ExType = fields.CharEnumField(ExType)
    pairs: fields.ReverseRelation["Pair"]


class Pair(Model):
    id = fields.SmallIntField(pk=True)
    ex: fields.ForeignKeyRelation[Ex] = fields.ForeignKeyField("models.Ex", related_name="pairs")
    coin: fields.ForeignKeyRelation[Coin] = fields.ForeignKeyField("models.Coin", related_name="pairs")
    cur: fields.ForeignKeyRelation[Cur] = fields.ForeignKeyField("models.Cur", related_name="pairs")
    sell: bool = fields.BooleanField()
    fee: float = fields.FloatField()
    total: int = fields.IntField()
    updated_at = fields.DatetimeField(auto_now=True)
    ad: fields.OneToOneRelation["Ad"]
    prices: fields.ReverseRelation["Price"]

    class Meta:
        unique_together = (("coin", "cur", "sell", "ex"),)

    def __str__(self):
        # noinspection PyUnresolvedReferences
        return f"{self.coin_id}/{self.cur_id} {'SELL' if self.sell else 'BUY'}"


class Price(Model):
    pair: fields.ForeignKeyRelation[Pair] = fields.ForeignKeyField("models.Pair", related_name="prices", pk=True)
    price: float = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)


class User(Model):
    uid: str = fields.CharField(63, unique=True)
    nickName: str = fields.CharField(63, unique=True, null=True)
    ex: fields.ForeignKeyRelation[Ex] = fields.ForeignKeyField("models.Ex", related_name="users")
    auth: {} = fields.JSONField(null=True)
    client: fields.ForeignKeyNullableRelation["Client"] = fields.ForeignKeyField("models.Client", related_name="users", null=True)
    is_active: bool = fields.BooleanField(default=True, null=True)
    updated_at = fields.DatetimeField(auto_now=True)


class Client(Model):
    gmail: str = fields.CharField(31, pk=True)
    tg_id: int = fields.IntField(null=True, unique=True)
    status: ClientStatus = fields.IntEnumField(ClientStatus, default=ClientStatus.wait)
    users: fields.ReverseRelation[User]

    def __str__(self):
        return f"User {self.gmail}({self.status}) tg:{self.tg_id}"


class Ad(Model):
    id: int = fields.BigIntField(pk=True)
    pair: fields.OneToOneRelation[Pair] = fields.OneToOneField("models.Pair", related_name="ads")
    maxFiat: float = fields.FloatField()
    minFiat: float = fields.FloatField()
    price: float = fields.FloatField()
    pts: fields.ManyToManyRelation["Pt"] = fields.ManyToManyField("models.Pt", "ad_pt", related_name="ads")
    user: fields.ForeignKeyRelation = fields.ForeignKeyField("models.User", "ads")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class Pt(Model):
    name: str = fields.CharField(31, pk=True)
    rank = fields.SmallIntField(default=0)
    curs: fields.ManyToManyRelation[Cur] = fields.ManyToManyField("models.Cur", related_name="pts")
    ads: fields.ManyToManyRelation[Ad]
    fiats: fields.ManyToManyRelation["Fiat"]


class Fiat(Model):
    id: int = fields.IntField(pk=True)
    pt: fields.ForeignKeyRelation[Pt] = fields.ForeignKeyField("models.Pt", related_name="fiats")
    detail: str = fields.CharField(127)
    pts_able: fields.ManyToManyRelation[Pt] = fields.ManyToManyField("models.Pt", "limit", related_name="founds_able")
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField("models.User", "fiats")
    amount: float = fields.FloatField(default=0, null=True)
    target: float = fields.FloatField(default=0, null=True)


class Asset(Model):
    # id: int = fields.IntField(pk=True)
    coin: fields.ForeignKeyRelation[Coin] = fields.ForeignKeyField("models.Coin", related_name="assets")
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField("models.User", "assets")
    free: float = fields.FloatField()
    freeze: float = fields.FloatField()
    lock: float = fields.FloatField()
    target: float = fields.FloatField(default=0, null=True)

    class Meta:
        unique_together = (("coin", "user"),)

class Limit(Model):
    fiat: fields.ForeignKeyRelation[Fiat] = fields.ForeignKeyField("models.Fiat", related_name="limits")
    pt: fields.ForeignKeyRelation[Pt] = fields.ForeignKeyField("models.Pt", related_name="limits")
    limit: int = fields.IntField()


class Order(Model):
    id: int = fields.BigIntField(pk=True)
    ad: fields.ForeignKeyRelation[Ad] = fields.ForeignKeyField("models.Pair", related_name="orders")
    limit: fields.ForeignKeyRelation[Limit] = fields.ForeignKeyField("models.Limit", related_name="orders")
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField("models.User", "orders")
    status: OrderStatus = fields.IntEnumField(OrderStatus)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
