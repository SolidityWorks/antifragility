from asyncio import run
from aiohttp import ClientSession
import base64
import time
import datetime
import random
import requests
import jwt

host = 'garantex.io/'  # for tests: stage.garantex.biz


def tok():
    private_key = 'LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFcFFJQkFBS0NBUUVBdjk4MTBnbnJHT0lsU1RkbVJUSExBaDRxQ2ZIUytFalU1ckFjTHd0dDdKVE1GQWZaCnc5cEkyY1VTMGt4eU0vN3V0SG9DNXRZVEVrVFg4ZCtKbm83U1ZXS01yRWs1QWlIQTcyelhNZnRDVUNIdUZwM04Kck5FTi9IN2d3UzFSc3N4Z20wQ1VOS3NXL1FZRnZ6WEJVNk9vZUhRb1d5VVV4bXhyd3FSUFRUQUhMaWllMVNUOQppZHhTS1RRdmg5a0wxejJGNWg3ZlRXOHBhZDd3Q3owcUVsaWhqRERnblBIQi9hYnZVK3dSZlF1RGhaMWMrNHhvCjRxdkRabHNCcGFuOHExVml4aWNnWjFWdFVxYnc4eHppMDZUV3VjUFpRT2ZvdUIrWVVyeXROOE1lTkdHL2tDYnEKYXQrNXlDaHh0ay9vZ1UrQjk3Y0x1Sm5xa05qUkJwdEtYaGVlMlFJREFRQUJBb0lCQVFDcnd2bS9LVG5ZY0xuSQpMVnZVSFpzS0xrNmIwR3QzOEZzR21Daml4R3lIR1QwSHdXOWtNSWgreWpqcklad3FoOURRcDFqcHBFSTJYSUtqCjkrU09tSFFhRTdxeWtHb0VTb3NZeW1wcVIrODVKT2FxUUdIYWp0cmlhZ0p4YkV4eXJ4cmNZSmRML3N6NWZPYXcKSVVNTHlMb0wrcEFWNThBTlVRbTJtTGlVOUtXNDN2N3lxYjNtNnBNV0gzRks1bExwN0dsTWJXYUNnb09Rdm42ZgoxdnZUYkNiN2tHbUZqcStyaFZkd2IvMURWOXBSajgya3JuN25sM011eG10WUZMM2ppYmtVb2VRTzVxZitZU1Q4ClRrVmV6b3MwWXRLYlBJN2NWRFZ0WGNXdllncUhpaGxPSDZuanNzVmJGN2FkdHNScEFrNHBJZHFPc3pEVk94Y2sKbmYzN3Z1UXhBb0dCQU9oTGsySHlDazhFTSsweGNsV1dwa2VENmt2aUJ1by9BT2xSRHQyLzl5T3VXZm5LTmdvcwpsakNXaUlhT1ZtcDZkSVdMVWVRSjhId043SCtrWGUyM3dTRWoxTVVDUnJ4YlYyYXhyNzBNNDNxTWlJTmx3MWprCklYeUxuNnBvYS9sRWRTdElBa3Y5NzRhYXpmZE8xZXFyL2ZaMy9jRy9UV1cxb0ZmK01RdktHNWxMQW9HQkFOTnoKb0R0ZGptdkw2K1NIV0NXeUt2cWZlYUVOT0Z4b0NQdlRZS3daZytzUG1wZkR4aTluSWJ1RlBjZ3VsYkRJcG1TSgpIaHI2WSswUUdEMThrMHd5WmZjY3JnWHZqOGwzbC82NGhPNGxNempmSWhEd0pOQ0NZWTM1TVZsbEdTT0lzcE5OCnEvbklpT2JURithTE8rcFNEUzQrYllFZ1kza2tpN281czFrNUZGWHJBb0dCQU1TNUJDYWxnTjlyOHNIRDUwemUKV1JFbGdTMGtUTERpREZhSzQra2RvaUZnalNoQ2ZFTmZnUTNDM2ZuOTN1Y3JyelJOU1Z1eW95dWI2eFlwejdYNgpzUjdzcGtyMVk0d3VXclZJYzBqSituZVZQaUx3OGw5OFMzT2JGdXVNcFN3ak1vc2wzM1FWcUZ5NUN3YU9pQkRGCitUeGFYOWROdURFVGdLZ2tSOHJ4TFRCREFvR0FPS2MzSEJEQjh1SE5Ed3F3TkZGYk1KRC96b1d6UHhia3FVd0cKRDdZNllRVnFQeFZHQ1RkUmsyTnNuVERXREdxR0lsT1dqRlhmNWdrMDVXeDJMcWttSnFJNWdmK2dmN01hTnpZSwo3NTlwN09mandiUUZ1UlBsdlZzeHZLallwbXVlcE5iZnArbnh2QjU4dmRrNk1WclFpejVRcXBNWjg4QTE2NnhBCkFEekoxUWNDZ1lFQTFCdW1jbEptU1lDN3pTK0VtVHpRcHZVWStsbUNhSkJBUDBVbjFKU3pTWmhZTm9FRXh0VFAKb2VKeHFMTVJHT1pMbFE3K3E3eGh2b0N3aXZXRVFqUGdUdG9CYm9YZ0xoTlhYSjZNUVI3bDNQWU9Hc2I0M2gzWAplQWNXeXdTSnVXTk0wVjdKUnBZbzZPSEZJSjFzOUk5S1hVaUx0QUhDV1g1dHk2YlVMTDk1UHNZPQotLS0tLUVORCBSU0EgUFJJVkFURSBLRVktLS0tLQo='
    uid = '8e6d505b-588d-4d37-9f7e-5c7da4f7c611'

    key = base64.b64decode(private_key)
    iat = int(time.mktime(datetime.datetime.now().timetuple()))

    claims = {
        "exp": iat + 1*60*60,  # JWT Request TTL in seconds since epoch
        "jti": hex(random.getrandbits(12)).upper()
    }

    jwt_token = jwt.encode(claims, key, algorithm="RS256")

    print("JWT request token: %s\n" % jwt_token)

    ret = requests.post('https://dauth.' + host + '/api/v1/sessions/generate_jwt', json={'kid': uid, 'jwt_token': jwt_token})

    print("JWT response code: %d" % ret.status_code)
    print("JWY response text: %s\n" % ret.text)

    return ret.json().get('token')


async def get_pub(path: str, params: {} = None):
    async with ClientSession() as session:
        resp = await session.get('https://' + host + path, params=params)
        return await resp.json()


async def get_prv(path: str, params: {} = None):
    headers = {'Authorization': 'Bearer ' + tok()}
    async with ClientSession() as session:
        resp = await session.get('https://' + host + path, headers=headers, params=params)
        return await resp.json()


if __name__ == "__main__":
    res = run(get_prv('api/v2/members/me'))
    print(res)
