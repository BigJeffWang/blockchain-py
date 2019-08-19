from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import TINYINT, CHAR
from models.base_model import BaseModel


class InvestUserModel(BaseModel):
    __tablename__ = "invest_users"
    status_on = '1'  # 可使用
    status_pending = '2'  # 注册成功，有待生成账户

    authentication_status_off = '1'  # 未实名认证
    authentication_status_on = '2'  # 已实名认证

    #基础信息
    user_id = Column(String(64), nullable=False, unique=True, doc="用户ID", server_default="", default="")
    user_mobile = Column(CHAR(64), default=None,  unique=True, doc="手机号")
    user_name = Column(CHAR(64), default=None,  unique=True, doc="用户名")  # 用户名不可改，昵称可改，真实姓名必须是真实姓名
    status = Column(TINYINT(1), nullable=False, server_default=status_pending, comment="用户状态 1=可使用 2)注册成功，有待生成账户", default="")
    real_name = Column(String(64), default=None, unique=True, comment="真实姓名")
    id_card = Column(String(64), default=None, unique=True, comment="身份证号")

    # 密码
    # 登录密码
    password = Column(String(128), nullable=False, server_default="", comment="登录密码", default="")
    passwd_salt = Column(String(128), nullable=False, comment="密码加密参数", server_default="", default="")
    bcrypt_salt = Column(String(128), nullable=False, comment="bcrypt算法密码加密参数", default="", server_default="")

    email = Column(String(128), default=None, unique=True, comment="邮箱")
    transaction_password = Column(String(128), nullable=False, server_default="", default="", comment="交易密码")
    transaction_passwd_salt = Column(String(128), nullable=False, comment="交易密码加密参数", server_default="", default="")
    transaction_bcrypt_salt = Column(String(128), nullable=False, comment="bcrypt算法交易密码加密参数", default="", server_default="")
    mobile_country_code = Column(String(128), nullable=False, server_default="", default="", comment="手机号国家区号")
    register_ip = Column(String(128), nullable=False, server_default="", default="", comment="注册时的ip")
    authentication_status = Column(TINYINT(1), nullable=False, server_default=authentication_status_off, default=authentication_status_off, comment="实名认证状态")
    nick_name = Column(String(64), nullable=False, server_default="", default="", comment="昵称")
    avatar = Column(String(128), nullable=False, server_default="", default="", comment="头像地址")

    # 扩展参数
    option1 = Column(String(128), nullable=False, server_default="", comment="扩展字段", default="")

    def __init__(self, *args, **kwargs):
        super(InvestUserModel, self).__init__(*args, **kwargs)
        self.user_id = self.uuid()

    def get_all_status(self):
        return [self.status_on, self.status_pending]



