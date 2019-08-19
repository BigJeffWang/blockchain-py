from sqlalchemy import Column, String, Numeric, BigInteger, TEXT
from sqlalchemy.dialects.mysql import TINYINT
from models.base_model import BaseModel
from utils.util import get_decimal


class RecordPkModel(BaseModel):
    __tablename__ = "record_pk"
    order_no = Column(String(32), unique=True, nullable=False, server_default="", comment="请求订单号")
    coin_id = Column(String(128), nullable=False, server_default="", comment="货币id")
    address = Column(TEXT, comment="请求地址列表 list强转str")
    response = Column(TEXT, comment="返回的信息")
    category = Column(String(128), nullable=False, server_default="", comment="地址类型 普通子钱包地址 归集钱包地址")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
