from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import TINYINT, CHAR
from models.base_model import BaseModel


class BorrowUserModel(BaseModel):
    __tablename__ = "borrow_users"
    status_on = '1'

    #基础信息
    user_id = Column(String(64), nullable=False, unique=True, doc="用户ID", server_default="")
    user_mobile = Column(CHAR(12), nullable=False, unique=True, doc="手机号", server_default="")
    status = Column(TINYINT(1), nullable=False, server_default=status_on, doc="用户状态 1=可使用 删除状态必须写入delete这个字段")
    real_name = Column(String(64), nullable=False, unique=True, server_default="", doc="真实姓名")
    id_card = Column(String(64), nullable=False, unique=True, server_default="", doc="身份证号")

    # 密码
    # 登录密码
    password = Column(String(128), nullable=False, server_default="", doc="登录密码")
    passwd_salt = Column(String(128), nullable=False, doc="密码加密参数", server_default="")
    bcrypt_salt = Column(String(128), nullable=False, doc="bcrypt算法密码加密参数", server_default="")

    # 扩展参数
    option1 = Column(String(128), nullable=False, server_default="", doc="扩展字段")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = self.uuid()

    def get_all_status(self):
        return [self.status_on]



