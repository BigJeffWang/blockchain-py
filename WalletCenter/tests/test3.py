
from utils.crypto_utils import encode_str_hex

salt1 = "leadnode"
salt2 = "cymwy"


key = encode_str_hex(salt1)
nonce = encode_str_hex(salt2)

print(key, nonce)


print("""
key: 717765727479
nonce: 617364313233
""")