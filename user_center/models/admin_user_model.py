from sqlalchemy import Column, Integer, String
from models.base_model import BaseModel


# 管理员表
class AdminUserModel(BaseModel):
    __tablename__ = "admin_users"
    user_id = Column(String(64), nullable=False, unique=True, doc="用户ID", server_default="")
    name = Column(String(64), unique=True, nullable=False, doc="管理员用户名", server_default="")
    password = Column(String(128), nullable=False, server_default="", doc="密码")
    platform = Column(String(64), nullable=False, server_default="", doc="平台")
    level = Column(Integer, nullable=False, server_default="0", doc="权限")

    passwd_salt = Column(String(128), nullable=False, doc="密码加密参数", server_default="")
    bcrypt_salt = Column(String(128), nullable=False, doc="bcrypt算法密码加密参数", server_default="")

    def __init__(self, *args, **kwargs):
        super(AdminUserModel, self).__init__(*args, **kwargs)
        self.user_id = self.uuid()
