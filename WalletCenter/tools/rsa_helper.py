import rsa
import base64


def generate_rsa_newkeys():
    """
    生成公私钥,为 SHA1withRSA 使用
    bash 生成方法:
    # openssl genrsa -out private_key.pem 1024
    # 然后通过这把私钥生成.pem格式的公钥：
    # openssl rsa -in private_key.pem -pubout -out public_key.pem
    :return: (pubkey, privkey)
    """
    (pubkey, privkey) = rsa.newkeys(1024)
    _privkey_key_pem = privkey.save_pkcs1('PEM')
    _pubkey_key_pem = pubkey.save_pkcs1('PEM')
    return _privkey_key_pem, _pubkey_key_pem


def get_signature_base64(privkey_key_pem, sign_data):
    """
    获取签文 base64编码, 根据 privkey_key_pem 进行签名 hash方式 SHA-1
    :param privkey_key_pem: 私钥
    :param sign_data: 签名数据 明文
    :return:
    """
    privatekey = rsa.PrivateKey.load_pkcs1(privkey_key_pem.encode("utf-8"))
    signature = rsa.sign(sign_data.encode('utf-8'), priv_key=privatekey, hash='SHA-1')
    signature_base64 = base64.b64encode(signature).decode('utf-8')
    return signature_base64


def verify_signature_data(pubkey_key_pem, signature_base64, signature_data):
    """
    校验签名, 数据是否合法
    :param pubkey_key_pem: 公钥
    :param signature_base64: 签名密文 base64编码
    :param signature_data: 签名数据 明文信息
    :return:
    """

    _pub = rsa.PublicKey.load_pkcs1(pubkey_key_pem.encode("utf-8"))
    signature = base64.b64decode(signature_base64)
    try:
        rsa.verify(signature_data.encode('utf-8'), signature, _pub)
        return True
    except:
        pass
    return False


if __name__ == "__main__":
    # from config import get_bank_config

    # privkey_key_pem = '-----BEGIN RSA PRIVATE KEY-----\nMIICYQIBAAKBgQCqgqOOSW+UFs6RutEO1QempHOtZx817AMVftXcB20BfGuP6trv\n6mxGA9ULSR6dL28oKCSIa0l0q/tkJAbz570Rf1QCgItHtU7onMqLa8eQfS6KHDuR\nqntG1oK3CsKfyd3ihi58FVEwaJL1lN0bwVhCtqlRVZ4U2aYlV0L2Tyts4QIDAQAB\nAoGAASRk4hQd2jkY4yMEOXw10+jwGW5CaEMPdjpmRlYKZeMmeU1ScB764LEv4SZ5\nPQZPUU6LiBpn4I8yXOZc4GUvpKSFAqKTTklCjvRvT4VYOlyu5GATQOd3gW3HFSQa\nZJSxjky+AQ98o/8qtVj0XBATRKoqLmQtxlFVQ1hCyYevG80CRQCt5Deg2xWF8not\n10Oca/UdP1DkPsOvHU5wyt7m8jz84wxNg/hqF/xy8SPEcN2eiEHeRMfg6iNWMuD1\nosT9FLpOreUyiwI9APsFteXZ5glbIYfBSe6cnldFxkv2LXNCgJ8uEVVwF7aGOxgl\nhQBEAIf8gQk+jszM23+aMeAtySm5bsBnwwJFAJmlg+2ShxMCrCgjA2+MCFmeX2g9\neQQavft1lby0H2VHbNB1IiMELKCXJwZkv71bIfA2D/JQj4aTkCgaeToxfWkVx+V/\nAj0A4cnoLKCLxtye02JsIuHjlzKexBLiHOuzj/q7ArO50Kb6nqSY9n00UR0x3+PS\nRKr7wNIsjK4CZLJzyUNLAkRUebhy35OrootDC4W/oaG/9yMuRTwcUjrwGpg8av7Y\n7qMT37HNY1gEtwAQaVp2Yy06l5TB3puprOblFKgbtiyfbFQahA==\n-----END RSA PRIVATE KEY-----\n'
    # pubkey_key_pem = '-----BEGIN RSA PUBLIC KEY-----\nMIGJAoGBAKqCo45Jb5QWzpG60Q7VB6akc61nHzXsAxV+1dwHbQF8a4/q2u/qbEYD\n1QtJHp0vbygoJIhrSXSr+2QkBvPnvRF/VAKAi0e1Tuicyotrx5B9LoocO5Gqe0bW\ngrcKwp/J3eKGLnwVUTBokvWU3RvBWEK2qVFVnhTZpiVXQvZPK2zhAgMBAAE=\n-----END RSA PUBLIC KEY-----\n'

    # print(generate_rsa_newkeys())

    # privkey_key_pem = get_bank_config()["privkey_key_pem"]
    # pubkey_key_pem = get_bank_config()["pubkey_key_pem"]
    #
    # sign_data = '{"a":"asd","b":"中文zxc阿斯123顿发生发的发发","c":12.00,"d":{"z":"qwe","f":10.00}}'
    # res = get_signature_base64(privkey_key_pem, sign_data)
    # print(res)
    #
    # signature_base64 = "TYzirjQl38XdylGgzCifZdVSwXKN198IrrqX6EICxMo42H4vG0FGlJHPlWRgwlfGf3Jnkj4fVxYKbImBH9uo+ccWQQkkEw7SwjReomHqMninRWr22qN29EvlPQFxGN1F3S+Spf4pekFhi4c10O63jOftsXUUeYpvZZZr6pB9SHw="
    # res2 = verify_signature_data(pubkey_key_pem, signature_base64, sign_data)
    # print(res2)
    pass
