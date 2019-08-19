from sqlalchemy import Column, String, DateTime
from models.base_model import BaseModel
from sqlalchemy.dialects.mysql import TEXT, INTEGER, TINYINT


# 公告录入表 announcement_manage
class AnnouncementManageModel(BaseModel):
    __tablename__ = "announcement_manage"

    title = Column(String(255), nullable=False, server_default="", comment="公告标题")
    site = Column(String(255), nullable=False, server_default="", comment="公告地址")
    status = Column(TINYINT, nullable=False, server_default="0", comment="状态")  # 0：待上线 1：已上线 2：已下线 3：作废
    auto_online = Column(DateTime, nullable=False, server_default="1970-01-01 00:00:00", comment="自动上线时间")
    auto_offline = Column(DateTime, nullable=False, server_default="1970-01-01 00:00:00", comment="自动下线时间")
    remark = Column(String(255), nullable=False, server_default="", comment="备注")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
