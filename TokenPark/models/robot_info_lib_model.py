from sqlalchemy import Column, String, BigInteger
from sqlalchemy.dialects.mysql import INTEGER, TEXT

from models.base_model import BaseModel


# 昵称库
class RobotInfoLibModel(BaseModel):
    __tablename__ = "robot_info_lib"

    uid = Column(String(64), nullable=False, server_default="", comment="user id")
    name = Column(String(64), nullable=False, server_default="", comment="机器人名")
    gender = Column(INTEGER, nullable=False, server_default="0", comment="性别")
    birthday = Column(String(256), nullable=False, server_default="", comment="生日")
    location = Column(String(256), nullable=False, server_default="", comment="位置")
    description = Column(String(512), nullable=False, server_default="", comment="描述")
    register_time = Column(String(256), nullable=False, server_default="", comment="注册时间")
    verify_type = Column(INTEGER, nullable=False, server_default="0", comment="验证类型")
    verify_info = Column(TEXT, comment="验证信息")
    follows_num = Column(INTEGER, nullable=False, server_default="0", comment="订阅数")
    fans_num = Column(INTEGER, nullable=False, server_default="0", comment="粉丝数")
    wb_num = Column(INTEGER, nullable=False, server_default="0", comment="wb数")
    level = Column(INTEGER, nullable=False, server_default="0", comment="级别")
    tags = Column(TEXT, comment="标签")
    work_info = Column(String(512), nullable=False, server_default="", comment="工作信息")
    contact_info = Column(String(512), nullable=False, server_default="", comment="联系信息")
    education_info = Column(String(512), nullable=False, server_default="", comment="学历信息")
    head_img = Column(String(512), nullable=False, server_default="", comment="头像信息")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
