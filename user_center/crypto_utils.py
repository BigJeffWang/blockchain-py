import os
import bcrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from errors.error_handler import InvalidUsageException
import hashlib
import base64


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


def get_bcrypt_pwd(password, salt):
    return str(bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8')), encoding='utf-8')


def encrypt_md5(input_str=''):
    md = hashlib.md5()  # 创建md5对象
    md.update(input_str.encode(encoding='utf-8'))  # 这里必须用encode()函数对字符串进行编码，不然会报 TypeError: Unicode-objects must be encoded before hashing
    return md.hexdigest()  # 加密


if __name__ == "__main__":
    salt = "$2a$12$sMjL4E/pmce4u8pHCMz2fu"
    psd = "yangyue"
    bcypt_password = get_bcrypt_pwd(psd, salt)
    print(bcypt_password)

    bcrypt_salt = get_bcrypt_salt().decode("utf-8")
    print(bcrypt_salt)
    passwd_salt = urandom(12)
    print(passwd_salt)
    res = sha512(str(bcypt_password), str(passwd_salt))
    print(res)




