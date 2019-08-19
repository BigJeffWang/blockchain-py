import json
import random

import redis_lock

from tools.redis_tools import RedisTools

"""
生成项目期号对应所有下注号码 game_serial:下注项目期号  total:可下注总数
return 
        redis已经存在=>4000 
        没有game_id对应项目下注号码=>3000
        奖池中号码不够下注所需号码数量=>3001
        game_id没有奖池号=>3002
"""


def create_all_bet_number(game_serial, total):
    redis_tool = RedisTools()
    if redis_tool.exists(game_serial):
        return 4000

    array_full = []
    while total > 0:
        array_full.append(total)
        total -= 1

    redis_tool.set(game_serial, json.dumps(array_full))
    return 2000


# 生成项目期号对应所有下注号码 game_serial:下注项目期号   amount:下注数量
def get_bet_number(game_serial, amount):
    redis_tool = RedisTools()

    if redis_tool.exists(game_serial):
        lock = redis_lock.Lock(redis_tool.redis_conn, 'bet_number', expire=1)
        if lock.acquire():
            array_full = json.loads(redis_tool.get(game_serial))

            length = len(array_full)
            if length <= 0:
                return 3000
            if length < amount:
                return 3001

            award_number_arr = random.sample(array_full, amount)

            # print(award_number_arr)
            # print(type(award_number_arr))

            array_full = list(set(array_full).difference(set(award_number_arr)))

            if len(array_full) <= 0:
                redis_tool.delete(game_serial)
            else:
                redis_tool.set(game_serial, json.dumps(array_full))

            lock.release()
            return award_number_arr

    return 3002


# 投注号码 归还 期号 添加号码list
def get_recover_number(game_serial, numbers):
    redis_tool = RedisTools()

    if redis_tool.exists(game_serial):
        lock = redis_lock.Lock(redis_tool.redis_conn, 'bet_number', expire=1)
        if lock.acquire():
            array_full = json.loads(redis_tool.get(game_serial))

            array_full.extend(numbers)
            redis_tool.set(game_serial, json.dumps(array_full))
            lock.release()

            return True

    return False


# import threading
# import time
#
# def test1_return_bet_number():
#     print("test1:", get_bet_number("test_create_all_bet_number", 3))
#
#
# def test2_return_bet_number():
#     print("test2:", get_bet_number("test_create_all_bet_number", 2))
#
#
if __name__ == "__main__":
    RedisTools().delete("0011812170002")
    # print("创建状态:", create_all_bet_number("test20", 8000))
    # print("返回下注号码:", get_bet_number("2", 20))

    # arr = [1, 2]
    # get_recover_number("test20", arr)

# s = 0
# while True:
#     if s % 2 == 0:
#         threading.Thread(target=test1_return_bet_number).start()
#     else:
#         threading.Thread(target=test2_return_bet_number).start()
#     s = s + 1
