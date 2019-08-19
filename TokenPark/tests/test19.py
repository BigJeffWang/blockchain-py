a = "  adsf  "
a1 = ""
res = a.strip()
res2 = a1.strip()
print(res)
print(type(res2))

s = "024c57fad1fc88e6fe1debace16021e556ecb42c82027c7306667c819daf3c67"
print(int(s, 16))

a, b = [1, 19]
print(a)
print(b)

lottery_num = int(s, 16) % 10
print(lottery_num)
print(int(s, 16) / 10)

d = {"1": 123, "2": 234, "3": "a"}
dd = list(d.keys())
del d["1"]
print(d)
d.pop("2")
print(d)
print(dd)
ss = [1, 2, 3]
ss.remove(2)
print(ss)