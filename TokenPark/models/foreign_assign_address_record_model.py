from sqlalchemy import Column, String
from models.base_model import BaseModel


class ForeignAssignAddressRecordModel(BaseModel):
    __tablename__ = "foreign_assign_address_record"
    req_no = Column(String(32), unique=True, nullable=False, server_default="", comment="请求记录单号")
    account_id = Column(String(64), nullable=False, server_default="", comment="账户id")
    coin_id = Column(String(128), nullable=False, server_default="", comment="货币id")
    sub_public_address = Column(String(255), server_default="", comment="子地址")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
