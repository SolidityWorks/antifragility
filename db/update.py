from clients.binance_client import get_pts
from db.models import User, Client, ClientStatus, Ex, Fiat


async def upd_fiats():
    for user in await User.filter(ex=1):
        pts = await get_pts(user)
        for pt in pts:
            dtl = pt['fields'][3 if pt['identifier'] == 'Advcash' else 1]['fieldValue']
            client = await user.client
            f, cr = await Fiat.update_or_create(id=pt['id'], client=client, pt_id=pt['identifier'], detail=dtl)


# # # users:
async def user_upd_bc(uid: int, gmail: str, cook: str, tok: str, cur: str = None) -> {}:  # bc: binance credentials
    client, cr = await Client.update_or_create(gmail=gmail, status=ClientStatus.wait)
    return await User.update_or_create(id=uid, client=client, auth={"cook": cook, "tok": tok}, is_active=False, ex=await Ex.get(name="bc2c"))
