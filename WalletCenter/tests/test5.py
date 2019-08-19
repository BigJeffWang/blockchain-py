a = {"a": 1}
b = {"c": 1, "b": "2"}
if "a" not in a or "a" not in b:
    print(111)

if "s" in b:
    print(b["c"])