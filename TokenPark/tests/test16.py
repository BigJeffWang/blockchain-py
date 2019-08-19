a = 4294451820403939808
b = [-32, -39, 52, 124, 45, -11, -104, 59]
s = ""

aa = "2019-01-09T09:05:48.123"

import time
import datetime

datetime.timedelta(hours=0.5)
# 格式化字符串输出
# d3 = d2.strftime('%Y-%m-%d %H:%M:%S')
# 将字符串转化为时间类型
# res = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
# print(res)

dtime = datetime.datetime.strptime(aa, "%Y-%m-%dT%H:%M:%S.%f")
print(dtime.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3])

print(dtime.timetuple())
print(dtime.microsecond/1000000)
un_time = time.mktime(dtime.timetuple()) + dtime.microsecond/1000000
print(un_time)

times = datetime.datetime.fromtimestamp(un_time)
print(times.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3])


from utils.time_util import str_to_timestamp, timestamp_to_str
print(str_to_timestamp(aa))

ts = 1546995948.123
print(timestamp_to_str(ts))