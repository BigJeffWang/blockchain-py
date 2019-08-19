import datetime
import time
import decimal


def get_timestamp(time_array=None, microsecond_digits=3):
    if not time_array:
        time_tuple = time.time()
    else:
        time_tuple = time.mktime(time_array.timetuple()) + time_array.microsecond / 1000000
    utc_time = decimal.Decimal(("%." + str(microsecond_digits) + "f") % time_tuple)
    return utc_time


def str_to_timestamp(time_str, format_style="%Y-%m-%dT%H:%M:%S.%f"):
    """
    字符串转时间
    :param time_str:
    :param format_style:
    :return:
    """
    time_array = datetime.datetime.strptime(time_str, format_style)
    time_stamp = time.mktime(time_array.timetuple()) + time_array.microsecond / 1000000
    return time_stamp


def timestamp_to_str(timestamp, format_style="%Y-%m-%dT%H:%M:%S.%f", microsecond_digits=3):
    """

    :param timestamp:
    :param format_style:
    :param microsecond_digits: 毫秒保留位数
    :return:
    """
    times = datetime.datetime.fromtimestamp(timestamp)
    if "." not in format_style:
        return times.strftime(format_style)
    return times.strftime(format_style)[:-microsecond_digits]


def get_datetime_now():
    return datetime.datetime.now()


def get_utc_now():
    return datetime.datetime.utcnow()


def get_month_begin():
    # 获取这个月第一天
    d_today = datetime.datetime.today()
    day = datetime.datetime(d_today.year, d_today.month, 1)
    return day


def get_month_now():
    # 获取今天在哪个月
    d_today = datetime.datetime.today()
    return d_today.month


def get_year_now():
    # 获取今天在哪年
    d_today = datetime.datetime.today()
    return d_today.year


def get_day_now():
    # 获取今天在哪天
    d_today = datetime.datetime.today()
    return d_today.day


def get_zero_oclock(today=None):
    if today is None:
        today = datetime.datetime.today()
    # 获取当天零点
    zero = datetime.datetime(today.year, today.month, today.day, 0, 0, 0)
    return zero


def days_diff(day1, day2, minus=True):
    '''
    :param day1:
    :param day2:
    :param minus:是否可以是负数,如果是负数回传0
    :return:
    '''
    if isinstance(day1, datetime.datetime):
        day1 = datetime.date(day1.year, day1.month, day1.day)
    if isinstance(day2, datetime.datetime):
        day2 = datetime.date(day2.year, day2.month, day2.day)
    # 获取两个日期之间的天数差
    a = (day2 - day1).days
    if minus is False:
        if a < 0:
            a = 0
    return a


def n_day_ago(n):
    # 获取几天前
    today = datetime.date.today()
    oneday = datetime.timedelta(days=n)
    day = today - oneday
    return day


def months_diff(day1, day2):
    # 获取两个日期直间的月份差
    if day1 > day2:
        n = (day1.year - day2.year) * 12 - day2.month + day1.month
    else:
        n = (day2.year - day1.year) * 12 - day1.month + day2.month
    return n


def monthdelta(date, delta):
    # 日期月份加减
    y = date.year + (date.month + delta - 1) // 12
    m = (date.month + delta) % 12
    if not m:
        m = 12
    d = min(date.day, [31,
                       29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return date.replace(day=d, month=m, year=y)
