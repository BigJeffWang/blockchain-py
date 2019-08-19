import binascii
import os
import bcrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from errors.error_handler import InvalidUsageException
import hashlib
import base64
from functools import partial


def sha512(data, salt=""):
    return hashlib.sha512((str(data) + str(salt)).encode("utf-8")).hexdigest()


def sha256(data, salt=""):
    return hashlib.sha256((data + salt).encode("utf-8")).digest()


def sha256_hex(data):
    return hashlib.sha256((data).encode("utf-8")).hexdigest()


# constant-time algorithms
def slow_is_equal(a, b):
    if len(a) != len(b):
        return False
    if isinstance(a, str):
        a = a.encode()
    if isinstance(b, str):
        b = b.encode()
    result = 0
    for x, y in zip(a, b):
        result |= x ^ y
    return result == 0


def urandom(size=64):
    return os.urandom(size).hex()


def get_ecc_shared_key(peer_public_key, private_key):
    loaded_public_key = serialization.load_pem_public_key(peer_public_key, backend=default_backend())
    shared_key = private_key.exchange(ec.ECDH(), loaded_public_key)
    shared_key_bytes = base64.b64encode(shared_key)
    shared_key_str = shared_key_bytes.decode()
    return shared_key_str


def get_ecc_public_key_pem_from_private(private_key):
    """
    通过ECC私钥,获取ECC公钥,返回PEM格式的字符串
    :param private_key:
    :return:
    """
    public_bytes = private_key.public_key().public_bytes(encoding=serialization.Encoding.PEM,
                                                         format=serialization.PublicFormat.SubjectPublicKeyInfo)
    return bytes.decode(public_bytes)


def generate_ecc_private_key():
    """
    获取ECC私钥
    :return: ECC私钥
    """
    return ec.generate_private_key(
        ec.SECP384R1(), default_backend())


def get_ecc_private_key_pem_from_private(private_key):
    """
    通过ECC私钥,返回PEM格式的字符串
    :param private_key:
    :return:
    """
    public_bytes = private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                             format=serialization.PrivateFormat.TraditionalOpenSSL,
                                             encryption_algorithm=serialization.BestAvailableEncryption(b'ecc_password'))
    return bytes.decode(public_bytes)


def generate_encryption_key(entype="AES_GCM", bit_length=128):
    if entype == "AES_GCM":
        key = AESGCM.generate_key(bit_length=bit_length)
        return key
    else:
        raise InvalidUsageException(10007)


def AES(data, key, nonce, entype="AES_GCM", associated_data=None):
    if isinstance(data, str):
        data = data.encode("utf-8")
    if entype == "AES_GCM":

        aesgcm = AESGCM(key)
        if nonce is None:
            nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, data, associated_data)
        return ct
    else:
        raise InvalidUsageException(10005)


def deAES(data, key, nonce, entype="AES_GCM", associated_data=None):
    if entype == "AES_GCM":
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, data, associated_data)
    else:
        raise InvalidUsageException(10006)


def get_bcrypt_salt():
    return bcrypt.gensalt(prefix=b"2a")


def encode_str_hex(data):
    if isinstance(data, str):
        return str(binascii.hexlify(bytes(data, encoding="utf-8")), encoding='utf-8')
    elif isinstance(data, bytes):
        return str(binascii.hexlify(data), encoding='utf-8')
    else:
        raise Exception("Wrong type, neither string nor bytes")


def decode_str_hex(data, conversion="str"):
    if conversion == "str":
        return str(binascii.unhexlify(data), encoding='utf-8')
    elif conversion == "bytes":
        return binascii.unhexlify(data)
    else:
        raise Exception("Wrong type, neither string nor bytes")


def encode_salt(data, type="encode"):
    ret_dict = {}
    for k, v in data.items():
        if type == "encode":
            ret_dict[k] = encode_str_hex(v)
        else:
            ret_dict[k] = decode_str_hex(v)
    return ret_dict


decode_salt = partial(encode_salt, type="decode")


def encode_str_sha256_digest(data):
    return hashlib.sha256((data + "").encode("utf-8")).digest()


def super_deAES(data, key, nonce, rule="_key"):
    rule_index = len(rule)
    encrypt_key = encode_str_sha256_digest(decode_str_hex(key))
    encrypt_nonce = bytes(decode_str_hex(nonce), encoding="utf-8")
    if isinstance(data, dict):
        ret_data = {}
        for k, v in data.items():
            if k[-rule_index:] == rule:
                ret_data[k] = str(deAES(decode_str_hex(v, "bytes"), encrypt_key, encrypt_nonce), encoding='utf-8')
            else:
                ret_data[k] = v
    else:
        ret_data = str(deAES(decode_str_hex(data, "bytes"), encrypt_key, encrypt_nonce), encoding='utf-8')
    return ret_data


def super_AES(data, key, nonce, rule="_key"):
    rule_index = len(rule)
    encrypt_key = encode_str_sha256_digest(decode_str_hex(key))
    encrypt_nonce = bytes(decode_str_hex(nonce), encoding="utf-8")
    if isinstance(data, (dict)):
        ret_data = {}
        for k, v in data.items():
            if k[-rule_index:] == rule:
                ret_data[k] = encode_str_hex(AES(v, encrypt_key, encrypt_nonce))
            else:
                ret_data[k] = v
    else:
        ret_data = encode_str_hex(AES(data, encrypt_key, encrypt_nonce))
    return ret_data


if __name__ == "__main__":
    pass
    # d = {"private_key": "11CAA2F2F8DB42E3F843C022E8C529FB647CA5F4F933E6266480C54412918374"}
    # key = "58696e6469736869313233"
    # nonce = "776f62757a686964616f"
    # res = super_AES(d, key, nonce)
    # print(res)

    d_de = {"private_key": "9cd82f32992b2f7306722513513eb647e025be6f64817958e04908030ae0a99b49562dc275425ca4a65f1770eabd71ba02abdfd078e52a918696f7ff44177cc7cc909cc155efeb8c89bbd32dd7031cda"}
    # eth
    # key = "58696e6469736869313233"
    # nonce = "776f62757a686964616f"

    # gather eth
    key = "717765727479"
    nonce = "617364313233"
    res_de = super_deAES(d_de, key, nonce)
    print(res_de)
