from sqlalchemy import Column, String, TEXT, Integer
from sqlalchemy.dialects.mysql import TINYINT
from models.base_model import BaseModel


class KeySaltModel(BaseModel):
    __tablename__ = "key_salt"
    source_type_1 = '1'  # pc
    source_type_2 = '2'  # wap
    source_type_3 = '3'  # iphone
    source_type_4 = '4'  # android

    user_id = Column(String(128), nullable=False, comment="用户id", server_default="")
    user_type = Column(TINYINT(1), nullable=False, comment="用户类型：0 invest, 1 admin", server_default="0")
    user_level = Column(Integer, nullable=False, comment="用户级别，user_type的子类", server_default="0")
    request_type = Column(TINYINT(1), nullable=False, comment="请求类型：0 注册, 1 登录后", server_default="1")
    bcrypt_salt = Column(String(128), nullable=False, comment="bcrypt算法密码加密参数", server_default="")
    server_public_key = Column(TEXT(1280), nullable=False, comment="服务器公钥PEM")
    server_private_key = Column(TEXT(1280), nullable=False, comment="服98`880务器私钥PEM")
    share_key = Column(String(256), nullable=False, comment="shareKey", server_default="")
    client_public_key = Column(TEXT(1280), nullable=False, comment="客户端公钥PEM")
    nonce = Column(String(128), nullable=False, comment="随机数", server_default="")
    source = Column(TINYINT(4), nullable=False, comment="用户来源", server_default=source_type_1)

    def __init__(self, *args, **kwargs):
        super(KeySaltModel, self).__init__(*args, **kwargs)

    @staticmethod
    def get_all_source_type():
        return [
            KeySaltModel.source_type_1,
            KeySaltModel.source_type_2,
            KeySaltModel.source_type_3,
            KeySaltModel.source_type_4,
        ]
