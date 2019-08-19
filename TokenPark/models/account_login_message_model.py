from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import TINYINT
from models.base_model import BaseModel


class AccountLoginMessageModel(BaseModel):
    # 记录账户登陆信息
    __tablename__ = "account_login_message"

    source_type_1 = '1'  # pc
    source_type_2 = '2'  # wap
    source_type_3 = '3'  # iphone
    source_type_4 = '4'  # android

    user_id = Column(String(64), comment="用户ID", nullable=False, server_default="")
    source = Column(TINYINT(4), nullable=False, comment="注册渠道", server_default=source_type_1)
    login_ip = Column(String(128), nullable=False, server_default="", default="", comment="注册时的ip")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)







