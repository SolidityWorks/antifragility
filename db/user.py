from db.models import User, Client, ClientStatus, Ex


async def get_bc2c_users(pref: [] = None) -> [User]:
    return await User.filter(ex_id=1, client__status__gte=ClientStatus.own).prefetch_related(*(pref or []))  # .all()  # the same result


async def user_upd_bc(uid: int, gmail: str, nick: str, cook: str, tok: str) -> {}:  # bc: binance credentials
    client, cr = await Client.get_or_create(gmail=gmail)
    df = {'nickName': nick, 'auth': {"cook": cook, "tok": tok}, 'client': client}
    user, cr = await User.update_or_create(df, id=uid, ex_id=1)
    return user
