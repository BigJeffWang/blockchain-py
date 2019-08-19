from sqlalchemy import Column, String, Numeric, BigInteger, Boolean
from sqlalchemy.dialects.mysql import INTEGER, MEDIUMTEXT, TINYINT

from models.base_model import BaseModel


# app版本记录表
class AppUpgradeModel(BaseModel):
    __tablename__ = "app_upgrade"

    version_code = Column(INTEGER, unique=True, nullable=False, server_default="0", comment="版本代号")
    version_name = Column(String(64), nullable=False, server_default="", comment="版本名称")
    upgrade_describe = Column(String(255), nullable=False, server_default="", comment="升级描述")
    download_link = Column(String(255), nullable=False, server_default="", comment="下载地址")
    forced_update = Column(TINYINT, nullable=False, server_default="0", comment="是否强更")
    status = Column(TINYINT, nullable=False, server_default="0", comment="版本状态")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
