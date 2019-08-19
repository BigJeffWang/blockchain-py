from sqlalchemy import Column, Integer, String
from models.base_model import BaseModel


# 后台权限
class SmsMessageModel(BaseModel):

    __tablename__ = "sms_message"

    send_message = Column(String(1024), nullable=False, comment="发送的信息", server_default="")
    response_message = Column(String(1024), nullable=False, comment="回复的信息", server_default="")
    gateway = Column(String(16), nullable=False, comment="渠道", server_default="")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)