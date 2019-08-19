from sqlalchemy import Column, String, DateTime
from models.base_model import BaseModel
from sqlalchemy.dialects.mysql import TEXT, INTEGER, TINYINT


# banner录入表 banner_manage
class BannerManageModel(BaseModel):
    __tablename__ = "banner_manage"

    title = Column(String(255), nullable=False, server_default="", comment="标题")
    site = Column(String(255), nullable=False, server_default="", comment="地址")
    image = Column(String(255), server_default="", comment="图片")
    thumbnail = Column(String(255), server_default="", comment="图片缩略图")
    status = Column(TINYINT, nullable=False, server_default="0", comment="状态")  # 0：待上线 1：已上线 2：已下线 3：作废
    auto_online = Column(DateTime, nullable=False, server_default="1970-01-01 00:00:00", comment="自动上线时间")
    auto_offline = Column(DateTime, nullable=False, server_default="1970-01-01 00:00:00", comment="自动下线时间")
    remark = Column(String(255), nullable=False, server_default="", comment="备注")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
