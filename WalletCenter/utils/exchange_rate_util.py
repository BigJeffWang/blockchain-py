import json

from tools.redis_tools import ExchangeRateRedisTools


# 返回币价
def get_exchange_rate():
    return json.loads(ExchangeRateRedisTools().get('btc_price'))
