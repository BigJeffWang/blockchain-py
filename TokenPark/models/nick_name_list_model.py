from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import INTEGER

from models.base_model import BaseModel


# 昵称列表
class NickNameListModel(BaseModel):
    __tablename__ = "nick_name_list"

    uid = Column(String(20), unique=True, nullable=False, server_default="", comment="用户id")
    name = Column(String(200), nullable=False, server_default="", default="", comment="昵称")
    gender = Column(INTEGER, nullable=False, server_default="0", comment="用户id")
    birthday = Column(String(200), nullable=False, server_default="", default="", comment="昵称")
    location = Column(String(100), nullable=False, server_default="", default="", comment="昵称")
    description = Column(String(500), nullable=False, server_default="", default="", comment="昵称")
    register_time = Column(String(200), nullable=False, server_default="", default="", comment="昵称")
    verify_type = Column(INTEGER, nullable=False, server_default="0", comment="用户id")
    verify_info = Column(String(2500), nullable=False, server_default="", default="", comment="昵称")
    follows_num = Column(INTEGER, nullable=False, server_default="0", comment="用户id")
    fans_num = Column(INTEGER, nullable=False, server_default="0", comment="用户id")
    wb_num = Column(INTEGER, nullable=False, server_default="0", comment="用户id")
    level = Column(INTEGER, nullable=False, server_default="0", comment="用户id")
    tags = Column(String(500), nullable=False, server_default="", default="", comment="昵称")
    work_info = Column(String(500), nullable=False, server_default="", default="", comment="昵称")
    contact_info = Column(String(300), nullable=False, server_default="", default="", comment="昵称")
    education_info = Column(String(300), nullable=False, server_default="", default="", comment="昵称")
    head_img = Column(String(500), nullable=False, server_default="", default="", comment="昵称")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
