import datetime
from utils.time_util import get_datetime_from_str


def format_utc(utc_time):
    utc_time_tuple = get_datetime_from_str(utc_time)
    bj_time = (utc_time_tuple - datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    return bj_time





res = format_utc("2018-12-14 10:56:26")
print(res)
