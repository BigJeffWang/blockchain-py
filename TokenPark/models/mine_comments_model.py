from sqlalchemy import Column, String, DateTime
from models.base_model import BaseModel
from sqlalchemy.dialects.mysql import TEXT, INTEGER, TINYINT


# 用户互动记录表 mine_comments
class MineCommentsModel(BaseModel):
    __tablename__ = "mine_comments"

    user_id = Column(String(64), comment="用户ID", nullable=False, server_default="")
    user_name = Column(String(64), server_default="", nullable=False, comment="用户名")
    submit_time = Column(DateTime, nullable=False, server_default="1970-01-01 00:00:00", comment="提交时间")
    submit_content = Column(String(255), nullable=False, server_default="", comment="提交内容")
    submit_image = Column(String(255), server_default="", comment="提交图片")
    submit_thumbnail = Column(String(255), server_default="", comment="提交图片缩略图")
    praise_number = Column(INTEGER, comment="点赞数", nullable=False, server_default="0")
    praise_users = Column(TEXT, comment="点赞的用户id")  # 规则: 用户id, 逗号分隔
    status = Column(TINYINT, nullable=False, server_default="1", comment="状态")  # 0：隐藏  1：显示

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
