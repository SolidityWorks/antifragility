from binance.spot import Spot

# mixartemev
client = Spot(key='p6ZW9WXQkUeHJlyOmZN3n63eX7ReVfVsSdYe4SQxkFNK12PsnHXmLc4538hcuM0G', secret='gBbvwj2gcDvLnkbFNnjf8vFEcAvwAY05KeHcu7UFvlVEOyfUgnmfo1kbZtttSXkK')
# alena
# client = Spot(key='dtyLk0I4S4zlWMN6sqO1aFtHKfjDcjstTbG2fuSpfZVEvr2NJLnUnSt0UFyCyHGv', secret='EE3tnb8I2IZGYtWUt72wXZ3NrIaKqUkaGFgMoHxRtkTas2y8EuKK0sQg1jcbGwTI')

# spot assets
a = client.user_asset()
print(a)

# funding assets
f = client.funding_wallet()
print(f)

# transfer
# t = client.user_universal_transfer(type='FUNDING_MAIN', asset='BUSD', amount=11)
# print(t)

n = client.ticker_price('USDTRUB')

r = client.enable_fast_withdraw()
r = client.withdraw(coin='SHIB', amount=100000, walletType=1, address='0x2469f1a2aa61dba2107d9905d94f1efa9f60eadc', network='BSC', withdrawOrderId=357058112)
print(r)
