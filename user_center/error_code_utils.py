# 1X 表示系统类错误，前端需要展示errorcode


def get_error_desc(error_code):
    if error_code in error_dic.keys():
        return error_dic[error_code]["desc"]
    else:
        return "error_code does not exists"


def get_error_msg(error_code):
    if error_code in error_dic.keys():
        return error_dic[error_code]["msg"]
    else:
        return "系统错误(" + str(error_code) + ")"


error_dic = {
    10000: {
        "desc": "unknow desc",
        "msg": "未知错误"
    },
    10001: {
        "desc": "System desc",
        "msg": "未知错误"
    },
    10002: {
        "desc": "Service unavailable",
        "msg": "服务暂停"
    },
    10003: {
        "desc": "Request Replay",
        "msg": "重复请求"
    },
    10004: {
        "desc": "Invalid request",
        "msg": "无效请求"
    },
    10005: {
        "desc": "Invalid request",
        "msg": "无效请求"
    },
    10006: {
        "desc": "Invalid request",
        "msg": "无效请求"
    },
    10007: {
        "desc": "request timeout",
        "msg": "请求超时"
    },
    10008: {
        "desc": "Invalid request",
        "msg": "无效请求"
    },
    10015: {
        "desc": "bad user type",
        "msg": "用户信息有误"
    },
    10016: {
        "desc": "bad user type",
        "msg": "用户信息有误"
    },
    10017: {
        "desc": "bad user type",
        "msg": "用户信息有误"
    },
    10018: {
        "desc": "no user info",
        "msg": "用户信息有误"
    },
    10019: {
        "desc": "wrong user type",
        "msg": "用户类型有误"
    },
    10020: {
        "desc": "wrong user name",
        "msg": "用户名有误"
    },
    10021: {
        "desc": "no user info",
        "msg": "用户信息有误"
    },
    10022: {
        "desc": "no user info",
        "msg": "解析参数出现错误,请重新尝试"
    },
    10030: {
        "desc": "Access Token Error",
        "msg": "登录凭证已过期,为了您的账户安全请重新登录"
    },
    10031: {
        "desc": "Access Token Error",
        "msg": "登录凭证已过期,为了您的账户安全请重新登录"
    },
    10032: {
        "desc": "Access Token Error",
        "msg": "登录凭证已过期,为了您的账户安全请重新登录"
    },
    10033: {
        "desc": "Access Token Error",
        "msg": "登录凭证已过期,为了您的账户安全请重新登录"
    },
    10034: {
        "desc": "Access Token Error",
        "msg": "登录凭证已过期,为了您的账户安全请重新登录"
    },
    10035: {
        "desc": "Access Token Error",
        "msg": "登录凭证已过期,为了您的账户安全请重新登录"
    },
    10036: {
        "desc": "Access Token Error",
        "msg": "登录凭证已过期,为了您的账户安全请重新登录"
    },
    10037: {
        "desc": "Access Token Error",
        "msg": "登录凭证已过期,为了您的账户安全请重新登录"
    },
    10038: {
        "desc": "no user info",
        "msg": "用户信息有误"
    },
    10039: {
        "desc": "bad user level",
        "msg": "用户权限有误"
    },
    10040: {
        "desc": "wrong user type",
        "msg": "用户类型有误"
    },
    10041: {
        "desc": "bad user source",
        "msg": "用户链接方式有误"
    },
    10042: {
        "desc": "System desc",  # 原因是usercenter与其他平台交互失败
        "msg": "未知错误"
    },
    10043: {
        "desc": "path too short",
        "msg": "无效的请求"
    },
    10044: {
        "desc": "Invalid request",
        "msg": "无效请求"
    },
    10045: {
        "desc": "no user info",
        "msg": "用户不存在或账号密码有误"
    },
    10046: {
        "desc": "Request Replay",
        "msg": "重复请求"
    },
    10047: {
        "desc": "nickname exists",
        "msg": "该昵称已存在"
    },
    10048: {
        "desc": "missing params",
        "msg": "缺少参数"
    },
    20000: {
        "desc": "time get fail",
        "msg": "时间获取失败"
    },
    20001: {
        "desc": "file size failed",
        "msg": "请上传小于20MB的图片"
    },
    20002: {
        "desc": "file format failed",
        "msg": "图片格式不正确"
    },
    20003: {
        "desc": "file empty failed",
        "msg": "未选择文件"
    },
    30000: {
        "desc": "bad platform",
        "msg": "无效的平台"
    },
    30050: {
        "desc": "bad picture vcode",
        "msg": "图形验证码获取失败，请稍后再试"
    },
    30051: {
        "desc": "send vcode failed",
        "msg": "发送验证码失败"
    },
    30052: {
        "desc": "bad picture vcode",
        "msg": "图形验证码有误"
    },
    30053: {
        "desc": "Send password frequently",
        "msg": "一分钟之内只允许发送一个验证码"
    },
    30054: {
        "desc": "send code exceeds limit.",
        "msg": "一日之内只允许发送不超过五个验证码"
    },
    30055: {
        "desc": "send code exceeds limit.",
        "msg": "验证码发送请求过频"
    },
    30056: {
        "desc": "send vcode failed",
        "msg": "发送验证码失败"
    },
    30057: {
        "desc": "get register token fail",
        "msg": "任务超时,请刷新页面"
    },
    30058: {
        "desc": "bad register token",
        "msg": "网络错误,请稍后重试"
    },
    30059: {
        "desc": "The mobile code verify failed",
        "msg": "验证码校验失败"
    },
    30060: {
        "desc": "bad picture vcode",
        "msg": "图形验证码有误"
    },
    30200: {
        "desc": "The mobile format is desc",
        "msg": "手机号码格式不正确"
    },
    30201: {
        "desc": "bad vcode",
        "msg": "验证码有误"
    },
    30202: {
        "desc": "user register fail",
        "msg": "该用户已存在"
    },
    30203: {
        "desc": "The user had registed",
        "msg": "该用户已注册"
    },
    30204: {
        "desc": "user login fail",
        "msg": "用户登录失败"
    },
    30205: {
        "desc": "access token refresh fail",
        "msg": "刷新失败"
    },
    30206: {
        "desc": "fail decode user",
        "msg": "用户信息解析失败"
    },
    30207: {
        "desc": "fail info user",
        "msg": "用户信息获取失败"
    },
    30208: {
        "desc": "change pwd fail",
        "msg": "重置密码失败"
    },
    30209: {
        "desc": "The user had registed",
        "msg": "该用户未注册"
    },
    30210: {
        "desc": "login password is desc",
        "msg": "用户名或密码错误"
    },
    30211: {
        "desc": "change pwd fail",
        "msg": "修改密码失败"
    },
    30212: {
        "desc": "old_pwd wrong",
        "msg": "旧密码有误"
    },
    30213: {
        "desc": "no user",
        "msg": "该用户不存在"
    },
    30214: {
        "desc": "fail info user",
        "msg": "用户信息更新失败"
    },
    30215: {
        "desc": "bad register by",
        "msg": "注册方式错误"
    },
    30216: {
        "desc": "bad user source",
        "msg": "用户设备有误"
    },
    30217: {
        "desc": "bad mobile_country_code",
        "msg": "手机号所在国区号有误"
    },
    30218: {
        "desc": "bad email",
        "msg": "邮箱有误"
    },
    30219: {
        "desc": "bad authentication",
        "msg": "认证失败"
    },
    30220: {
        "desc": "bad authentication params",
        "msg": "缺失认证数据"
    },
    30221: {
        "desc": "no authentication",
        "msg": "请先实名认证"
    },
    30222: {
        "desc": "diff authentication mobile",
        "msg": "手机号有误"
    },
    30223: {
        "desc": "bad register_by",
        "msg": "验证码发送方式有误"
    },
    30224: {
        "desc": "pwd equal resetpwd",
        "msg": "支付密码不能与登陆密码相同"
    },
    30225: {
        "desc": "set usermobiel fail",
        "msg": "手机号设置失败"
    },
    30226: {
        "desc": "login fail times reach limit",
        "msg": "登陆失败次数过频，请稍后尝试或重置密码"
    },
    30227: {
        "desc": "pay password is desc",
        "msg": "支付密码错误"
    },
    30228: {
        "desc": "pay fail times reach limit",
        "msg": "支付密码错误次数过频，请稍后尝试或重置密码"
    },
    30229: {
        "desc": "no paypwd",
        "msg": "您暂未设置支付密码，请先设置支付密码"
    },
    30230: {
        "desc": "not admin user",
        "msg": "非管理员权限不具有此功能的权限"
    },
    30231: {
        "desc": "bad change type",
        "msg": "错误的修改类型"
    },
    30232: {
        "desc": "bad user rights",
        "msg": "本用户不具有此权限"
    },
    30233: {
        "desc": "password none",
        "msg": "密码不能为空"
    },
    30234: {
        "desc": "reset pay password fail",
        "msg": "重置失败"
    },
    30235: {
        "desc": "set mobile fail",
        "msg": "手机号设置失败"
    },
    30236: {
        "desc": "set email fail",
        "msg": "email设置失败"
    },
    30237: {
        "desc": "mobile exists",
        "msg": "该账户已存在手机号"
    },
    30238: {
        "desc": "email exists",
        "msg": "该账户已存在邮箱"
    },
}
