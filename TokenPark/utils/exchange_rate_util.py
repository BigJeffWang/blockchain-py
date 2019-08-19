import json
from common_settings import *
from tools.redis_tools import ExchangeRateRedisTools


# 返回币价
def get_exchange_rate(conin_id):
    # print(ExchangeRateRedisTools().get('btc_price'))
    if int(conin_id) == int(_COIN_ID_BTC):
        return json.loads(ExchangeRateRedisTools().get('btc_price').decode().replace("'", "\""))
    elif int(conin_id) == int(_COIN_ID_ETH):
        return json.loads(ExchangeRateRedisTools().get('eth_price').decode().replace("'", "\""))
    elif int(conin_id) == int(_COIN_ID_EOS):
        return json.loads(ExchangeRateRedisTools().get('eos_price').decode().replace("'", "\""))
    elif int(conin_id) == int(_COIN_ID_EXP):
        return {'price': 1}
    elif int(conin_id) == int(_COIN_ID_USDT):
        return {'price': 1}
    else:
        return json.loads(ExchangeRateRedisTools().get('btc_price').decode().replace("'", "\""))


if __name__ == "__main__":
    pass
    # get_exchange_rate(0)
