from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.mysql import TINYINT, CHAR, INTEGER, TEXT
from models.base_model import BaseModel
from utils.util import get_decimal, generate_order_no


class UserAccountModel(BaseModel):
    __tablename__ = "user_account"

    status_on = '1'  # 在用
    status_off = '0'  # 注销

    source_type_1 = '1'  # pc
    source_type_2 = '2'  # wap
    source_type_3 = '3'  # iphone
    source_type_4 = '4'  # android

    account_id = Column(String(64), unique=True, nullable=False, server_default="", comment="账户号")
    user_id = Column(String(64), comment="用户ID", nullable=False, server_default="")
    score = Column(INTEGER, nullable=False, server_default="0", comment="积分")
    id_card = Column(String(64), nullable=False, server_default="", comment="身份证号", default="")
    nick_name = Column(String(64), nullable=False, server_default="", default="", comment="昵称")
    source = Column(TINYINT(4), nullable=False, comment="注册渠道", server_default=source_type_1)
    avatar = Column(String(128), nullable=False, server_default="", default="", comment="头像地址")

    transaction_password = Column(String(128), nullable=False, server_default="", default="", comment="交易密码")
    transaction_passwd_salt = Column(String(128), nullable=False, comment="交易密码加密参数", server_default="", default="")
    transaction_bcrypt_salt = Column(String(128), nullable=False, comment="bcrypt算法交易密码加密参数", default="", server_default="")
    first_recharge_at = Column(DateTime, nullable=False, server_default="0000-00-00 00:00:00", comment="首次充值时间")

    # 下面这三个字段最后定为仅存在用户中心，故这里不能存，客户端若必须获取则需要发送userinfi请求到客户端获取
    user_mobile = Column(CHAR(64), nullable=False, comment="手机号", server_default="", default="")
    email = Column(String(128), nullable=False, server_default="", default="", comment="邮箱")
    mobile_country_code = Column(String(128), nullable=False, server_default="", default="", comment="手机号国家区号")
    user_name = Column(CHAR(64), default=None,  doc="用户名")
    register_ip = Column(String(128), nullable=False, server_default="", default="", comment="注册时的ip")

    # 邀请码相关的流程
    # inviter_code 自己生成的用来邀请别人的邀请码
    # invitee_code 别人邀请自己的邀请码
    inviter_code = Column(CHAR(8), nullable=False, default="", comment="邀请码")
    invitee_code = Column(CHAR(8), nullable=False, default="", comment="受邀请码")

    # 是否参与首次抽奖
    first_lottery = Column(TINYINT(1), nullable=False, default=0, comment="是否参与首次抽奖")

    # 用户头像
    profile_picture = Column(TEXT, nullable=False, default="", comment="用户头像")

    # 状态
    status = Column(TINYINT(1), nullable=False, server_default=str(status_on), comment="状态 0）注销 1）在用")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_id = generate_order_no(k=44)

