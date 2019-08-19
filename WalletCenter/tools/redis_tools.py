import redis
from config import get_redis_conf, get_env
from tools.decorator_tools import FormateOutput


def get_redis_pool(host, port, db, password):
    return redis.ConnectionPool(host=host, port=port, db=db, password=password)


@FormateOutput(default_value=10005, return_type='return_error')
def get_redis():
    conf = get_redis_conf()
    connection_pool = get_redis_pool(conf["host"], conf["port"], conf["db"], conf["password"])
    return redis.Redis(connection_pool=connection_pool)


class RedisTools(object):
    def __init__(self):
        super().__init__()
        self.redis_conn = get_redis()

    @FormateOutput(default_value=10005, return_type='return_error')
    def get(self, name):
        return self.redis_conn.get(name)

    @FormateOutput(default_value=10005, return_type='return_error')
    def ttl(self, name):
        return self.redis_conn.ttl(name)

    @FormateOutput(default_value=10005, return_type='return_error')
    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        return self.redis_conn.set(name, value, ex=ex, px=px, nx=nx, xx=xx)

    @FormateOutput(default_value=10005, return_type='return_error')
    def exists(self, name):
        return self.redis_conn.exists(name)

    @FormateOutput(default_value=10005, return_type='return_error')
    def incr(self, name, amount=1):
        return self.redis_conn.incr(name, amount=amount)

    @FormateOutput(default_value=10005, return_type='return_error')
    def delete(self, *names):
        return self.redis_conn.delete(*names)


# 币价redis  db = 12 ======================================================================================================================
@FormateOutput(default_value=10005, return_type='return_error')
def get_exchange_rate_redis():
    conf = get_redis_conf()
    connection_pool = get_exchange_rate_redis_pool(conf["host"], conf["port"], conf["db"], conf["password"])
    return redis.Redis(connection_pool=connection_pool)


def get_exchange_rate_redis_pool(host, port, db, password):
    return redis.ConnectionPool(host=host, port=port, db=12, password=password)


class ExchangeRateRedisTools(object):
    def __init__(self):
        super().__init__()
        self.redis_conn = get_exchange_rate_redis()

    @FormateOutput(default_value=10005, return_type='return_error')
    def get(self, name):
        return self.redis_conn.get(name)

    @FormateOutput(default_value=10005, return_type='return_error')
    def ttl(self, name):
        return self.redis_conn.ttl(name)

    @FormateOutput(default_value=10005, return_type='return_error')
    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        return self.redis_conn.set(name, value, ex=ex, px=px, nx=nx, xx=xx)

    @FormateOutput(default_value=10005, return_type='return_error')
    def exists(self, name):
        return self.redis_conn.exists(name)

    @FormateOutput(default_value=10005, return_type='return_error')
    def incr(self, name, amount=1):
        return self.redis_conn.incr(name, amount=amount)

    @FormateOutput(default_value=10005, return_type='return_error')
    def delete(self, *names):
        return self.redis_conn.delete(*names)
