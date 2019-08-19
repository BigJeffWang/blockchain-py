from sqlalchemy import Column, String, DateTime
from models.base_model import BaseModel
from sqlalchemy.dialects.mysql import TINYINT, INTEGER


class TokenTypeModel(BaseModel):
    __tablename__ = "token_type"

    token_name = Column(String(64), unique=True, nullable=False, server_default="", comment="名称")
    token_eng_name = Column(String(255), nullable=False, server_default="", comment="英文简称")
    legal_tender = Column(String(64), nullable=False, server_default="", comment="法币汇率")
    usdt_tender = Column(INTEGER, nullable=False, server_default="0", comment="USDT汇率")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
