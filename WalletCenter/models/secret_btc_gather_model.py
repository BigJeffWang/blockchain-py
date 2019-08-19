from sqlalchemy import Column, String, Numeric, BigInteger
from models.base_model import BaseModel


class SecretBtcGatherModel(BaseModel):
    __tablename__ = "secret_btc_gather"
    sub_index = Column(BigInteger, nullable=False, comment="归集账户 子钱包索引")
    change_index = Column(String(255), nullable=False, server_default="", comment="归集账户 change index")
    sub_private_key_aes = Column(String(255), unique=True, nullable=False, server_default="", comment="归集账户 子私钥AES加密")
    sub_public_key_aes = Column(String(255), unique=True, nullable=False, server_default="", comment="归集账户 子公钥AES加密")
    sub_public_address = Column(String(255), unique=True, nullable=False, server_default="", comment="归集账户 子地址")
    acct_public_key_aes = Column(String(255), nullable=False, server_default="", comment="归集账户 主公钥AES加密防止以后有多个助记词生成主秘钥同时使用")
    coin_id = Column(String(128), nullable=False, server_default="", comment="归集账户 货币id")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
