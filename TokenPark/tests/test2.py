

def checksum_encode(addrstr):  # Takes a 20-byte binary address as input
    addr = bytes.fromhex(addrstr[2:])
    o = ''
    v = utils.big_endian_to_int(utils.sha3(addr.hex()))
    print(v)
    print(addr.hex())
    for i, c in enumerate(addr.hex()):
        if c in '0123456789':
            o += c
        else:
            o += c.upper() if (v & (2 ** (255 - 4 * i))) else c.lower()
    return '0x' + o


# def test(addrstr):
#     assert (addrstr == checksum_encode())


# test('0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed')
# test('0xfB6916095ca1df60bB79Ce92cE3Ea74c37c5d359')
# test('0xdbF03B407c01E7cD3CBea99509d93f8DDDC8C6FB')
# test('0xD1220A0cf47c7B9Be7A2E6BA89F429762e7b9aDb')

adress = "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed"
adress2 = "0x0f7771a3b2d4da6a867e24a837be463dfb589e3f"
res = checksum_encode(adress2)
print(res)
