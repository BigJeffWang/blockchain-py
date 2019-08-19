from tools.redis_tools import RedisTools
import time
import random

from utils.exchange_rate_util import get_exchange_rate
from utils.time_util import get_timestamp


def generate_phase(phase_prefix):
    phase_serial = 1
    redis_tool = RedisTools()
    today = time.strftime("%y%m%d", time.localtime())
    phase_date = today
    if redis_tool.exists("phase_date"):
        phase_date = redis_tool.get("phase_date")
        if int(today) != int(phase_date):
            redis_tool.set("phase_date", today)
            redis_tool.set("phase_serial", 1)
            phase_date = today
        else:
            if redis_tool.exists("phase_serial"):
                phase_serial = int(redis_tool.get("phase_serial")) + 1
                redis_tool.set("phase_serial", phase_serial)
            else:
                redis_tool.set("phase_serial", 1)
    else:
        redis_tool.set("phase_date", today)
        redis_tool.set("phase_serial", 1)

    return str(phase_prefix) + str(int(phase_date)) + str(phase_serial).zfill(4)


def dice_generate_phase():
    ram_num = random.randint(0, 1000)
    ram_num = str(ram_num).zfill(4)
    return str(round(get_timestamp() * 1000)) + ram_num


if __name__ == "__main__":
    pass
    # rate = dice_generate_phase()
    # print(rate)

