from Crypto.Hash import keccak


class CheckEthAddress(object):

    @staticmethod
    def big_endian_to_int(value: bytes) -> int:
        return int.from_bytes(value, "big")

    @staticmethod
    def sha3_256_digest(x):
        return keccak.new(digest_bits=256, data=x).digest()

    @staticmethod
    def sha3_bytes(seed):
        return CheckEthAddress.sha3_256_digest(CheckEthAddress.to_string(seed))

    @staticmethod
    def to_string(value):
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            return bytes(value, 'utf-8')
        if isinstance(value, int):
            return bytes(str(value), 'utf-8')

    @staticmethod
    def checksum_encode(addr_str):
        if addr_str[:2] != "0x" or not isinstance(addr_str, str):
            raise Exception("checksum_encode address is not lawful address: " + str(addr_str))
        addr = bytes.fromhex(addr_str[2:])
        o = ''
        v = CheckEthAddress.big_endian_to_int(CheckEthAddress.sha3_bytes(addr.hex()))
        for i, c in enumerate(addr.hex()):
            if c in '0123456789':
                o += c
            else:
                o += c.upper() if (v & (2 ** (255 - 4 * i))) else c.lower()
        return '0x' + o

    @staticmethod
    def get_right_address(address):
        try:
            address = address.strip()
            if address[:2] == "0x" and len(address) == 42:
                right_address = CheckEthAddress.checksum_encode(address)
                if address.lower() == right_address.lower():
                    return right_address
            return ""
        except:
            return ""


if __name__ == "__main__":
    a = "0x7C0f4C22968C0CA715aCb001506Cd2502E2BCfaf"
    b = "0x0F9Df23deC74aD7afceDdC0af39b1FF00D868d2B"
    c = "0x7c0f4c22968c0ca715acb001506cd2502e2bcfaf"
    d = "  0x7c0f4c22968c0ca715acb001506cd2502e2bcfaf  "
    r_address = CheckEthAddress.get_right_address(d)
    print(r_address)
