from sqlalchemy import Column, String, Numeric
from models.base_model import BaseModel


# AES key nonce
class TokenSaltModel(BaseModel):
    __tablename__ = "token_salt"
    coin_id = Column(String(128), nullable=False, server_default="", comment="货币id")
    public_key_aes = Column(String(255), unique=True, nullable=False, server_default="", comment="公钥AES加密 key nonce 索引")
    key_aes = Column(String(255), nullable=False, server_default="", comment="AES key")
    nonce_aes = Column(String(255), nullable=False, server_default="", comment="AES nonce")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
