d = {"1": 0, "2": 2, "3": 3}
# for item in set(d):
#     print(item)
    # k = item[0]
    # v = item[1]
    # print(k)
    # print(v)

for index, i in enumerate([1,2,3]):
    print(index)
    # print(i)


import datetime
res = datetime.datetime.utcnow()
import time
print( res)
print(time.asctime())
print(time.time())

from utils.time_util import get_timestamp

print(get_timestamp())


d = {"1":2, "a":"z"}
for i in set(d):
    print(i)

print(list(d.keys()))