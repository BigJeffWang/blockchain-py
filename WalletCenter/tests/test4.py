import ctypes


def int_overflow(val):
    maxint = 2147483647
    if not -maxint - 1 <= val <= maxint:
        val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
    return val


def unsigned_right_shitf(n, i):
    # 数字小于0，则转为32位无符号uint
    if n < 0:
        n = ctypes.c_uint32(n).value
    # 正常位移位数是为正数，但是为了兼容js之类的，负数就右移变成左移好了
    if i < 0:
        return -int_overflow(n << abs(i))
    # print(n)
    return int_overflow(n >> i)


def encode_hex(bytes_list):
    digits_lower = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
    l_list = len(bytes_list)
    out_sub = l_list << 1
    out = []
    for i in range(l_list):
        out.append(digits_lower[unsigned_right_shitf(0xF0 & bytes_list[i], 4)])
        out.append(digits_lower[0x0F & bytes_list[i]])
    return "".join(out)[:out_sub]


def char_idx(c):
    ord_c = ord(c)
    ord_a = ord('a')
    ord_z = ord('z')
    ord_1 = ord('1')
    ord_5 = ord('5')
    if ord_a <= ord_c <= ord_z:
        return (ord_c - ord_a) + 6
    elif ord_5 >= ord_c >= ord_1:
        return (ord_c - ord_1) + 1
    else:
        return 0


def to_binary_string(i):
    if i == 0:
        return 32
    n = 1
    if unsigned_right_shitf(i, 16) == 0:
        n += 16
        i = i << 16
    if unsigned_right_shitf(i, 24) == 0:
        n += 8
        i = i << 8
    if unsigned_right_shitf(i, 28) == 0:
        n += 4
        i = i << 4
    if unsigned_right_shitf(i, 30) == 0:
        n += 2
        i = i << 2

    n -= unsigned_right_shitf(i, 31)
    return n


def str_to_bits(n):
    bits_len = 64
    bits = ""
    for i in range(12 + 1):
        c = char_idx(n[i]) if i < len(n) else 0
        bit_len = 5 if i < 12 else 4
        _b = bin(c)[2:]
        for j in range(bit_len - len(_b)):
            bits += "0"
        bits += _b
    return bits[:bits_len]


def get_bytes_list(bits_big_int):
    bytes_list = []
    for i in range(8):
        offset = 64 - (8 - 1 - i + 1) * 8
        bytes_num = (bits_big_int >> offset & 0xFF)
        if bytes_num >= 128:
            bytes_num -= 256
            # bytes_num = int(str(bytes_num).replace("-", ""))
        bytes_list.append(bytes_num)
    return bytes_list


def get_str_to_hex(arg):
    bits = str_to_bits(arg)
    bits_big_int = int(bits, 2)
    bytes_list = get_bytes_list(bits_big_int)
    encode_hex_data = encode_hex(bytes_list)

    return encode_hex_data


def get_quantity_to_hex(arg):
    quantity_bytes = []
    pattern = arg.split(" ")
    amount_precision = pattern[0]
    symbol = pattern[1]
    symbol_len = len(symbol)
    symbol_bytes = [ord(i) for i in symbol]
    if "." not in amount_precision:
        amount = int(amount_precision)
        precision = 0
    else:
        amount = int(amount_precision.replace(".", ""))
        amount_precision = str(float(amount_precision))
        precision = len(amount_precision) - amount_precision.rindex(".") - 1

    quantity_bytes.append(amount)
    quantity_bytes.append(precision)
    quantity_bytes += symbol_bytes
    for j in range(7-symbol_len):
        quantity_bytes.append(0x0)
    print(quantity_bytes)
    encode_hex_data = encode_hex(quantity_bytes)
    return encode_hex_data


def json_to_bin(arg):
    _from = arg.get("from")
    _to = arg.get("to")
    _quantity = arg.get("quantity")
    _memo = arg.get("memo")
    bin_data = get_str_to_hex(_from) + get_str_to_hex(_to) + get_quantity_to_hex(_quantity)
    print(get_quantity_to_hex(_quantity))
    print(encode_hex([1231]))
    return bin_data


json_arg = {
    "from": "bigjeffwangy",
    "to": "eosluckypark",
    # "quantity": "0.1000 EOS",
    "quantity": "00.1231 EOS",
    "memo": "1000001"
}

print(json_to_bin(json_arg))
