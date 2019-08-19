from sqlalchemy import Column, String, TEXT, Boolean
from models.base_model import BaseModel
from utils.util import get_decimal


class RecordSignModel(BaseModel):
    __tablename__ = "record_sign"
    order_no = Column(String(32), unique=True, nullable=False, server_default="", comment="请求订单号")
    coin_id = Column(String(128), nullable=False, server_default="", comment="货币id")
    parameter = Column(String(512), nullable=False, server_default="", comment="交易相关参数")
    sign = Column(TEXT, comment="交易所需签名")
    response = Column(TEXT, comment="返回的信息")
    do_result = Column(Boolean, nullable=False, default=0, server_default="0", comment="交易处理结果 0-失败, 1-成功")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
