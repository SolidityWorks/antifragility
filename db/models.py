from enum import IntEnum, Enum
from tortoise import Model, fields


class ClientStatus(IntEnum):
    me = 7
    my = 5
    own = 3
    pause = 2
    wait = 1
    block = 0


class AdvStatus(IntEnum):
    defActive = 0
    active = 1
    two = 2
    old = 3
    four = 4
    notFound = 9


class OrderStatus(IntEnum):
    zero = 0
    one = 1
    two = 2
    three = 3
    done = 4
    fifth = 5
    canceled = 6
    paid_and_canceled = 7


class ExType(Enum):
    main = "main"
    dex = "dex"
    other = "other"
    futures = "futures"
    p2p = "p2p"


class Region(Enum):
    russia = "Russia"
    turkey = "Turkey"


class Cur(Model):
    id: str = fields.CharField(3, pk=True)
    pts: fields.ManyToManyRelation["Ptc"]
    ptcs: fields.ReverseRelation["Ptc"]


class Coin(Model):
    id: str = fields.CharField(7, pk=True)


class Ex(Model):
    id: int = fields.SmallIntField(pk=True)
    name: str = fields.CharField(31)
    type: ExType = fields.CharEnumField(ExType)
    pairs: fields.ReverseRelation["Pair"]


class Pair(Model):
    id = fields.SmallIntField(pk=True)
    coin: fields.ForeignKeyRelation[Coin] = fields.ForeignKeyField("models.Coin", related_name="pairs")
    cur: fields.ForeignKeyRelation[Cur] = fields.ForeignKeyField("models.Cur", related_name="pairs")
    sell: bool = fields.BooleanField()
    fee: float = fields.FloatField()
    total: int = fields.IntField()
    ex: fields.ForeignKeyRelation[Ex] = fields.ForeignKeyField("models.Ex", related_name="pairs")
    ads: fields.ReverseRelation["Ad"]
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        unique_together = (("coin", "cur", "sell", "ex"),)

    def __str__(self):
        # noinspection PyUnresolvedReferences
        return f"{self.coin_id}/{self.cur_id} {'SELL' if self.sell else 'BUY'}"


class User(Model):
    id: int = fields.IntField(pk=True)
    uid: str = fields.CharField(63, unique=True, null=True)
    nickName: str = fields.CharField(63)
    ex: fields.ForeignKeyRelation[Ex] = fields.ForeignKeyField("models.Ex", related_name="users")
    auth: {} = fields.JSONField(null=True)
    client: fields.ForeignKeyNullableRelation["Client"] = fields.ForeignKeyField("models.Client", related_name="users", null=True)
    is_active: bool = fields.BooleanField(default=True, null=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # @staticmethod
    # def defs(data: {}):
    #     return {
    #         'nickName': data['nickName'],
    #         'uid': data['userNo'],
    #         'ex_id': 1,
    #     }


class Client(Model):
    gmail: str = fields.CharField(31, pk=True)
    tg_id: int = fields.IntField(null=True, unique=True)
    status: ClientStatus = fields.IntEnumField(ClientStatus, default=ClientStatus.wait)
    users: fields.ReverseRelation[User]

    def __str__(self):
        return f"User {self.gmail}({self.status}) tg:{self.tg_id}"


class Ad(Model):
    id: int = fields.BigIntField(pk=True)
    pair: fields.ForeignKeyRelation[Pair] = fields.ForeignKeyField("models.Pair", related_name="ad")
    price: float = fields.FloatField()
    pts: fields.ManyToManyRelation["Pt"] = fields.ManyToManyField("models.Pt")  # only root pts
    maxFiat: float = fields.FloatField()
    minFiat: float = fields.FloatField()
    detail: str = fields.CharField(4095, null=True)
    autoMsg: str = fields.CharField(255, null=True)
    user: fields.ForeignKeyRelation = fields.ForeignKeyField("models.User", "ads")
    status: AdvStatus = fields.IntEnumField(AdvStatus)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True, index=True)

    orders: fields.ReverseRelation["Order"]


class Pt(Model):
    name: str = fields.CharField(31, pk=True)
    rank = fields.SmallIntField(default=0)
    parent: fields.ForeignKeyNullableRelation["Pt"] = fields.ForeignKeyField("models.Pt", null=True, related_name="children")
    curs: fields.ManyToManyRelation[Cur] = fields.ManyToManyField("models.Cur", through="ptc")

    pairs: fields.ReverseRelation[Pair]
    curs: fields.ReverseRelation["Cur"]
    fiats: fields.ReverseRelation["Fiat"]
    orders: fields.ReverseRelation["Order"]
    children: fields.ReverseRelation["Pt"]


class Ptc(Model):
    pt: fields.ForeignKeyNullableRelation[Pt] = fields.ForeignKeyField("models.Pt")
    cur: fields.ForeignKeyRelation[Cur] = fields.ForeignKeyField("models.Cur")
    blocked: fields.BooleanField = fields.BooleanField(default=False)

    class Meta:
        unique_together = (("pt", "cur"),)


class Fiat(Model):
    id: int = fields.IntField(pk=True)
    ptc: fields.ForeignKeyRelation[Ptc] = fields.ForeignKeyField("models.Ptc")
    pts: fields.ManyToManyRelation[Ptc] = fields.ManyToManyField("models.Pt", through="ptc")
    region: fields.CharEnumField(Region) = fields.CharEnumField(Region, null=True)
    detail: str = fields.CharField(127)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField("models.User", "fiats")  # only user having client
    amount: float = fields.FloatField(default=0, null=True)
    target: float = fields.FloatField(default=0, null=True)

    orders: fields.ReverseRelation["Order"]


class Route(Model):
    ptc_from: fields.ForeignKeyRelation[Ptc] = fields.ForeignKeyField("models.Ptc", related_name="out_routes")
    ptc_to: fields.ForeignKeyRelation[Ptc] = fields.ForeignKeyField("models.Ptc", related_name="in_routes")


class Limit(Model):
    route: fields.ForeignKeyRelation[Route] = fields.ForeignKeyField("models.Route")
    limit: int = fields.IntField(default=-1, null=True)  # '$' if unit >= 0 else 'transactions count'
    unit: int = fields.IntField(default=30)  # positive: $/days, 0: $/transaction, negative: transactions count / days
    fee: float = fields.IntField(default=0, null=True)  # on multiply Limits for one Route - fees is quanting by minimum unit if units equal, else summing


class Asset(Model):
    id: int = fields.CharField(15, pk=True)
    coin: fields.ForeignKeyRelation[Coin] = fields.ForeignKeyField("models.Coin", related_name="assets")
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField("models.User", "assets")
    free: float = fields.FloatField()
    freeze: float = fields.FloatField()
    lock: float = fields.FloatField()
    target: float = fields.FloatField(default=0, null=True)

    class Meta:
        unique_together = (("coin", "user"),)


class Order(Model):
    id: int = fields.BigIntField(pk=True)
    ad: fields.ForeignKeyRelation[Ad] = fields.ForeignKeyField("models.Ad", related_name="orders")
    amount: float = fields.FloatField()
    fiat: fields.ForeignKeyRelation[Fiat] = fields.ForeignKeyField("models.Fiat", related_name="orders", null=True)
    pt: fields.ForeignKeyNullableRelation[Pt] = fields.ForeignKeyField("models.Pt", related_name="orders", null=True)
    taker: fields.ForeignKeyRelation[User] = fields.ForeignKeyField("models.User", "orders")
    status: OrderStatus = fields.IntEnumField(OrderStatus)
    created_at = fields.DatetimeField()
    updated_in_db_at = fields.DatetimeField(auto_now=True)
    notify_pay_at = fields.DatetimeField(null=True)
    confirm_pay_at = fields.DatetimeField(null=True)
