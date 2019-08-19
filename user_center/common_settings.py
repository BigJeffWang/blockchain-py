__all__ = [
    '_SHARE_KEY',
    '_NONCE',
    '_USER_TYPE_INVEST',
    '_USER_TYPE_ADMIN',
    '_ID_CARD_TYPE',
    '_REQUEST_TYPE_REGISTER',
    '_REQUEST_TYPE_LOGIN',
    '_VCODE_REGISTER',
    '_VCODE_LOGIN',
    '_VCODE_RESETPD',
    '_VCODE_RESET_PAY_PD',
    '_PICTURE_VCODE_BACKGROUND',
    '_PICTURE_VCODE_STRING',
    '_PICTURE_VCODE_LINE',
    '_PICTURE_VCODE_ARC',
    '_USER_ID_LEN',
    '_DECODE_TYPE_DEFAULT',
    '_DECODE_TYPE_INNER',
    '_INNER_SHARE_KEY',
    '_INNER_NONCE',
    '_USER_TYPE_BORROW',
    '_PASSWORD_CHECK_TYPE_SUCCESS',
    '_PASSWORD_CHECK_TYPE_REDIRECT',
    '_USER_TYPE_NONE',
    '_USER_TYPE_INNER',
    '_USER_TYPE_ADMIN_LEAVEL_PURCHASE',
    '_USER_TYPE_ADMIN_LEAVEL_RISK',
    '_USER_TYPE_ADMIN_LEAVEL_FINANCE',
    '_USER_TYPE_ADMIN_LEAVEL_MANAGE',
    '_PLATFORM_LEVEL_1',
    '_PLATFORM_LEVEL_2',
    '_PLATFORM_LEVEL_ALL',
    '_PLATFORM_LEVEL_NONE',
    '_PLATFORM_ALLOW_LEVEL',
    '_REGISTER_BY_MOBILE',
    '_REGISTER_BY_EMAIL',
    '_USE_SOURCE_TYPE_1',
    '_SOURCE_TYPE_1',
    '_SOURCE_TYPE_2',
    '_SOURCE_TYPE_3',
    '_SOURCE_TYPE_4',
    '_REGISTER_AUTHEN_MOBILE',
    '_REGISTER_AUTHEN_EMAIL',
    '_VCODE_SET_PAY_PD',
    '_REGISTER_SET_PAYPD_MOBILE',
    '_REGISTER_SET_PAYPD_EMAIL',
    '_LOGIN_FAIL_TIMES_LIMIT',
    '_LOGIN_FAIL_TIME_LIMIT',
    '_PAYPWD_FAIL_TIMES_LIMIT',
    '_PAYPWD_FAIL_TIME_LIMIT',
    '_RESET_PWD_MOBILE',
    '_RESET_PWD_EMAIL',
    '_ROOT_ADMIN_LEVEL',
    '_BASE_ADMIN_LEVEL',
    '_REQUEST_TYPE_LOGINING',
    '_LOGININ_BY_USER_NAME',
    '_REGISTER_RESET_PAYPD_MOBILE',
    '_REGISTER_RESET_PAYPD_EMAIL',
    '_REGISTER_SET_MOBILE',
    '_VCODE_SET_MOBILE',
    '_VCODE_SET_EMAIL',
    '_REGISTER_SET_EMAIL',
]

# 通用 --------------------------------------------------------------------------------------------

_SHARE_KEY = "ryLgF8uejTjBkIYbDHco1vQTjIi8PQcUBBFqG/0omY4TOkA9ggUZ9wFqEeDGEonH"
_NONCE = "caf6c4cb9be55a01da1b5fc6"

_INNER_SHARE_KEY = "/F+A1Oc+3uIAkg3dGzdwpElqE7v3AyNoSQzTFO5Gd1Vfi8Bmso1MY/aDP1x+NRFf"
_INNER_NONCE = "cd7c66da329a9b54e19d2b17"

# 用户 --------------------------------------------------------------------------------------------

_USER_TYPE_INVEST = 0  # 投资用户
_USER_TYPE_ADMIN = 1  # 管理用户
_USER_TYPE_BORROW = 2  # 借款用户
_USER_TYPE_NONE = 3  # 非任何一种用户，故而其加密使用通用的share_key和nonce
_USER_TYPE_INNER = 4  # 非任何一种用户,而是本项目与服务端其他项目的交互，故而其加密使用inner的share_key和nonce

# admin用户的子类,依据level划分
_USER_TYPE_ADMIN_LEAVEL_PURCHASE = 0b1  # 管理用户中的进件用户
_USER_TYPE_ADMIN_LEAVEL_RISK = 0b10  # 管理用户中的风控用户
_USER_TYPE_ADMIN_LEAVEL_FINANCE = 0b100  # 管理用户中的财务用户
_USER_TYPE_ADMIN_LEAVEL_MANAGE = 0b1000  # 管理用户中的后台管理用户

# 平台的划分
# 进件平台需要的权限列表
_PLATFORM_LEVEL_1 = [_USER_TYPE_ADMIN_LEAVEL_PURCHASE]
# 我方后台需要的权限列表
_PLATFORM_LEVEL_2 = [_USER_TYPE_ADMIN_LEAVEL_MANAGE,  _USER_TYPE_ADMIN_LEAVEL_FINANCE, _USER_TYPE_ADMIN_LEAVEL_RISK]
# 全部权限列表
_PLATFORM_LEVEL_ALL = [_USER_TYPE_ADMIN_LEAVEL_MANAGE,  _USER_TYPE_ADMIN_LEAVEL_FINANCE, _USER_TYPE_ADMIN_LEAVEL_RISK,
                       _USER_TYPE_ADMIN_LEAVEL_PURCHASE]

_ROOT_ADMIN_LEVEL = 9999  # admin的最高权限
_BASE_ADMIN_LEVEL = 0  # admin最低权限

# 最低权限列表
_PLATFORM_LEVEL_NONE = []
# 可以存在的平台权限
_PLATFORM_ALLOW_LEVEL = [_PLATFORM_LEVEL_1, _PLATFORM_LEVEL_2, _PLATFORM_LEVEL_ALL]


_ID_CARD_TYPE = 1  # 身份证

_REQUEST_TYPE_REGISTER = 0  # 注册状态
_REQUEST_TYPE_LOGIN = 1  # 登录状态
_REQUEST_TYPE_LOGINING = 2  # 注册后用户登陆

_VCODE_REGISTER = 0  # 注册验证码
_VCODE_LOGIN = 1  # 登录验证码
_VCODE_RESETPD = 2  # 重置密码验证码
_VCODE_SET_PAY_PD = 3  # 设置支付密码验证码
_VCODE_RESET_PAY_PD = 4  # 重置支付密码验证码
_VCODE_SET_MOBILE = 5  # 设置手机号
_VCODE_SET_EMAIL = 6  # 设置email


_USER_ID_LEN = 32  # 数据库中userid的长度

_DECODE_TYPE_DEFAULT = 0
_DECODE_TYPE_INNER = 1

_PASSWORD_CHECK_TYPE_SUCCESS = 0  # 校验password正常是继续走之后的程序
_PASSWORD_CHECK_TYPE_REDIRECT = 1  # 校验password正常则跳转

_PICTURE_VCODE_BACKGROUND = [
    (249, 249, 249)
]
_PICTURE_VCODE_STRING = [
    (255, 181, 60),
    (122, 152, 247),
    (47, 170, 255),
    (250, 155, 153),
    (255, 196, 99),
    (123, 230, 255),
    (122, 152, 247),
    (184, 233, 134),
    (245, 166, 35),
]
_PICTURE_VCODE_LINE = [
    (255, 181, 60),
    (122, 152, 247),
    (47, 170, 255),
    (250, 165, 153),
    (255, 196, 99),
    (123, 230, 255),
    (122, 152, 247),
    (139, 233, 134),
]
_PICTURE_VCODE_ARC = [
    (255, 181, 60),
    (122, 152, 247),
    (47, 170, 255),
    (250, 155, 153),
    (255, 196, 99),
    (123, 230, 255),
    (122, 152, 247),
    (184, 233, 134),
]

_USE_SOURCE_TYPE_1 = '1'  # 客户端来源使用方法的类别

_SOURCE_TYPE_1 = '1'  # pc
_SOURCE_TYPE_2 = '2'  # wap
_SOURCE_TYPE_3 = '3'  # iphone
_SOURCE_TYPE_4 = '4'  # android

_LOGIN_FAIL_TIMES_LIMIT = 5  # 短时间内登陆失败最大次数
_LOGIN_FAIL_TIME_LIMIT = 600  # 短时间内登陆失败超过次数后限制此时间内不能登陆
_PAYPWD_FAIL_TIMES_LIMIT = 5  # 短时间内登陆失败最大次数
_PAYPWD_FAIL_TIME_LIMIT = 600  # 短时间内登陆失败超过次数后限制此时间内不能登陆

# 以下连贯各项值不能冲突！！！！！
_REGISTER_BY_MOBILE = '1'  # 采用手机号注册
_REGISTER_BY_EMAIL = '2'  # 采用email注册
_REGISTER_AUTHEN_MOBILE = '3'  # 注册且实名制后采用mobile实名认证
_REGISTER_AUTHEN_EMAIL = '4'  # 注册且实名制后采用email实名认证
_REGISTER_SET_PAYPD_MOBILE = '5'  # 注册后采用mobile设置密码
_REGISTER_SET_PAYPD_EMAIL = '6'  # 注册后采用email设置密码
_RESET_PWD_MOBILE = '7'  # 手机号找回密码
_RESET_PWD_EMAIL = '8'  # email找回密码
_LOGININ_BY_USER_NAME = '9'  # 以用户名登陆
_REGISTER_RESET_PAYPD_MOBILE = '10'  # 注册后采用mobile设置密码
_REGISTER_RESET_PAYPD_EMAIL = '11'  # 注册后采用email设置密码
_REGISTER_SET_MOBILE = '12'  # 设置手机号
_REGISTER_SET_EMAIL = '13'  # 设置email








