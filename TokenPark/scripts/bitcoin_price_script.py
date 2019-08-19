import sys
import time
import logging
import json
import urllib
import urllib.parse
import urllib.request

import requests
from redis import StrictRedis

sys.path.append("..")
from config import get_redis_conf

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
# set console level and formatter
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)

# API 请求地址
HUOBI_URL = "https://api.huobi.pro"
BINANCE_URL = "https://api.binance.com"
OKEX_URL = "https://www.okex.com"


# REDIS
conf = get_redis_conf()
REDIS_HOST = conf["host"]
REDIS_PORT = conf["port"]
REDIS_DB = 12
REDIS_PASSWORD = conf["password"]

# ---------------- SYMBOL 和 PRICE LIST 需要同时进行配置 ----------------
# 可自定义配置 SYMBOL
HUOBI_SYMBOL = ["btcusdt", "ethusdt", "eosusdt"]
BINANCE_SYMBOL = ["BTCUSDT", "ETHUSDT", "EOSUSDT"]
OKEX_SYMBOL = ["btc_usdt", "eth_usdt", "eos_usdt"]

# 可自定义配置 PRICE LIST
PRICE_LIST = ["btc_price", "eth_price", "eos_price"]


# CONNECT REDIS
def connect_redis():
    r = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,
                    password=REDIS_PASSWORD)
    return r


def __get_ticker(symbol, url):
    """
    :param symbol:
    :param url
    :return:
    """
    params = {'symbol': symbol}

    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.3'
                       '6 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'
                       ),
    }
    postdata = urllib.parse.urlencode(params)
    try:
        response = requests.get(url, postdata, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return
    except Exception as e:
        raise ConnectionError("httpGet failed, detail is:%s" % e)


# 获取 HUOBI MERGE TICKER
def _huobi_get_ticker(symbol):
    url = HUOBI_URL + '/market/detail/merged'
    response = __get_ticker(symbol, url)
    return response["tick"]["close"], str(response['ts'])[:10]


# 获取 BINANCE MERGE TICKER
def _binance_get_ticker(symbol):
    url = BINANCE_URL + '/api/v3/ticker/price'
    response = __get_ticker(symbol, url)
    return float(response["price"]), str(int(time.time()))


# 获取 OKEX MERGE TICKER
def _okex_get_ticker(symbol):
    url = OKEX_URL + '/api/v1/ticker.do'
    response = __get_ticker(symbol, url)
    return round(float(response["ticker"]["last"]), 2), response['date']


# 获取信息
def _get_info(price_list: list, get_ticker_func, symbol_list: list,
              info_from: str) -> dict:
    price_dict = dict()
    for index, value in enumerate(price_list):
        price_item = dict()
        price_item['price'], price_item['timestamp'] = get_ticker_func(symbol_list[index])
        price_item['from'] = info_from
        price_dict[value] = price_item
    return price_dict


# 运行脚本
def run_srcipt():
    # HUOBI
    try:
        huobi_price_dict = _get_info(PRICE_LIST, _huobi_get_ticker,
                                     HUOBI_SYMBOL, 'huobi')
        pipe = connect_redis().pipeline()
        for key, value in huobi_price_dict.items():
            pipe.set(key, json.dumps(value))
        pipe.execute()
        return
    except ConnectionError as connect_error:
        logger.error("[HUOBI]" + str(connect_error))
    except Exception as error:
        logger.error("[HUOBI]" + str(error))

    # BINANCE
    try:
        binance_price_dict = _get_info(PRICE_LIST, _binance_get_ticker,
                                       BINANCE_SYMBOL, 'binance')
        pipe = connect_redis().pipeline()
        for key, value in binance_price_dict.items():
            pipe.set(key, json.dumps(value))
        pipe.execute()
        return
    except ConnectionError as connect_error:
        logger.error("[BINANCE]" + str(connect_error))
    except Exception as error:
        logger.error("[BINANCE]" + str(error))

    # OKEX
    try:
        okex_price_dict = _get_info(PRICE_LIST, _okex_get_ticker,
                                    OKEX_SYMBOL, 'okex')
        pipe = connect_redis().pipeline()
        for key, value in okex_price_dict.items():
            pipe.set(key, json.dumps(value))
        pipe.execute()
        return
    except ConnectionError as connect_error:
        logger.error("[OKEX]" + str(connect_error))
    except Exception as error:
        logger.error("[OKEX]" + str(error))


if __name__ == '__main__':
    run_srcipt()
    logger.info("Success!")
