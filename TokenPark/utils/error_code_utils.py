# TODO  错误码解释 1000X 系统级错误代码  2000X 服务级错误代码  3000X 资金类错误代码


def get_error_desc(error_code):
    if error_code in error_dic.keys():
        return error_dic[error_code]["desc"]
    else:
        return "error_code does not exists"


def get_error_msg(error_code):
    if error_code in error_dic.keys():
        return error_dic[error_code]["msg"]
    else:
        return "error_code does not exists"


error_dic = {
    10000: {
        "desc": "Other desc",
        "msg": "其他错误"
    },
    10001: {
        "desc": "System desc",
        "msg": "系统错误"
    },
    10002: {
        "desc": "Service unavailable",
        "msg": "服务暂停"
    },
    10003: {
        "desc": "Param desc, see doc for more info",
        "msg": "参数错误，请参考API文档"
    },
    10004: {
        "desc": "Job expired",
        "msg": "任务超时"
    },
    10005: {
        "desc": "Encrypt desc",
        "msg": "加密错误"
    },
    10006: {
        "desc": "Decrypt desc",
        "msg": "解密错误"
    },
    10007: {
        "desc": "Generate encryption key desc",
        "msg": "生成key错误"
    },
    10008: {
        "desc": "Repetition Request",
        "msg": "重复请求"
    },
    10009: {
        "desc": "Login frequency exceeds limit.",
        "msg": "登录次数超限"
    },
    10010: {
        "desc": "Send password frequently",
        "msg": "一分钟之内只允许发送一个验证码"
    },
    10011: {
        "desc": "send code exceeds limit.",
        "msg": "一日之内只允许发送不超过五个验证码"
    },
    10012: {
        "desc": "get code failed",
        "msg": "获取验证码失败"
    },
    10013: {
        "desc": "send vcode failed",
        "msg": "发送验证码失败"
    },
    10014: {
        "desc": "file size failed",
        "msg": "请上传小于20MB的图片"
    },
    10015: {
        "desc": "file format failed",
        "msg": "图片格式不正确"
    },
    10016: {
        "desc": "file empty failed",
        "msg": "未选择文件"
    },
    10017: {
        "desc": "wrong user type",
        "msg": "用户类型有误"
    },
    10018: {
        "desc": "Invalid request",
        "msg": "无效的请求"
    },
    10019: {
        "desc": "System desc",  # 原因是usercenter与其他平台交互失败
        "msg": "未知错误"
    },
    10020: {
        "desc": "error",
        "msg": "归集手续费配置过低"
    },
    10021: {
        "desc": "request header have not TimeZone",
        "msg": "请求头没有时区TimeZone字段"
    },
    10022: {
        "desc": "Mysql connect failed",
        "msg": "网络不畅"
    },
    10023: {
        "desc": "redis connect failed",
        "msg": "网络不畅"
    },
    10024: {
        "desc": "mongodb connect failed",
        "msg": "网络不畅"
    },
    10025: {
        "desc": "wallet error",
        "msg": "wallet error"
    },
    20001: {
        "desc": "User does not exists",
        "msg": "用户不存在"
    },
    20002: {
        "desc": "Project does not exists",
        "msg": "项目不存在或者状态不对"
    },
    20003: {
        "desc": "Param is desc, please try again",
        "msg": "参数错误,请重新尝试"
    },
    20004: {
        "desc": "Account does not exists",
        "msg": "账户不存在或者账户状态不对"
    },
    20005: {
        "desc": "Project has been audited",
        "msg": "项目已通过审核，不能被删除"
    },
    20006: {
        "desc": "Create project failure",
        "msg": "创建项目失败"
    },
    20007: {
        "desc": "The user has not opened the account or did not bind the card",
        "msg": "用户未开户或未绑卡"
    },
    20008: {
        "desc": "The accumulative amount of individual borrowing should not exceed 200 thousand",
        "msg": "个人借款累计金额应不大于20万"
    },
    20009: {
        "desc": "The accumulative amount of the enterprise loan should not be more than 1 million",
        "msg": "企业借款累计金额应不大于100万"
    },
    20010: {
        "desc": "Incorrect project status type",
        "msg": "项目状态类型不正确"
    },
    20011: {

        "desc": "The user had open the account or did not register",
        "msg": "用户已经开户或者还没有注册"
    },
    20012: {
        "desc": "The mobile format is desc",
        "msg": "手机号码格式不正确"
    },
    20014: {
        "desc": "Refresh Token Error",
        "msg": "登录凭证已过期,为了您的账户安全请重新登录"
    },
    20015: {
        "desc": "login password is desc",
        "msg": "登录密码错误"
    },
    20016: {
        "desc": "The mobile code verify failed",
        "msg": "验证码校验失败"
    },
    20017: {
        "desc": "The mobile code is expire",
        "msg": "验证码已经过期"
    },
    20018: {
        "desc": "The user had registed",
        "msg": "该用户已注册"
    },
    20019: {
        "desc": "Access Token Error",
        "msg": "AccessToken已经过期"
    },
    20020: {
        "desc": "The old password verify failed",
        "msg": "原密码错误，请重新输入"
    },
    20021: {
        "desc": "Decrypt Data Error",
        "msg": "登录凭证已过期,为了您的账户安全请重新登录"
    },
    20022: {
        "desc": "Refresh Token Error",
        "msg": "登录凭证已过期,为了您的账户安全请重新登录"
    },
    20023: {
        "desc": "Request Signature Error",
        "msg": "Signature 校验失败,请重新生成"
    },
    20024: {
        "desc": "Request Timestamp Error",
        "msg": "请求发送时间过长"
    },
    20025: {
        "desc": "Request Replay",
        "msg": "重复请求"
    },
    20026: {
        "desc": "Company Replay",
        "msg": "企业已存在"
    },
    20027: {
        "desc": "Car number failed",
        "msg": "购车数量与车辆列表数量不符"
    },
    20028: {
        "desc": "Car amount failed",
        "msg": "车辆采购总金额与合同金额不符"
    },
    30001: {
        "desc": "User balance is insufficient",
        "msg": "用户余额不足"
    },
    30002: {
        "desc": "The amount of investment is less than the minimum amount of investment",
        "msg": "投资金额小于最小投资金额"
    },
    30003: {
        "desc": "The amount of investment is greater than the amount of the project available",
        "msg": "投资金额大于项目可用金额"
    },
    30004: {
        "desc": "The withdrawal amount shall not exceed the available balance.",
        "msg": "提现金额不能大于可用余额"
    },
    30005: {
        "desc": "Users do not assess the risk.",
        "msg": "用户未进行风险测评"
    },
    34000: {
        "desc": "repayment start",
        "msg": "还款相关报错的起始"
    },
    34001: {
        "desc": "bad loan order id",
        "msg": "订单编号有误"
    },
    34002: {
        "desc": "bad loan car list",
        "msg": "所选车辆有误"
    },
    34003: {
        "desc": "bad loan car list",
        "msg": "所选车辆有误"
    },
    34004: {
        "desc": "bad loan car list",
        "msg": "所选车辆有误"
    },
    34005: {
        "desc": "no loan order rate",
        "msg": "还款利率异常"
    },
    34006: {
        "desc": "bad repayment process",
        "msg": "还款确认失败"
    },
    34007: {
        "desc": "bad repayment process car id",
        "msg": "存在状态异常车辆，请重新勾选"
    },
    34999: {
        "desc": "repayment end",
        "msg": "还款相关报错的结束"
    },
    35000: {
        "desc": "account start",
        "msg": "账户相关报错的起始"
    },
    35001: {
        "desc": "no account",
        "msg": "账户不存在"
    },
    35002: {
        "desc": "account invest fail",
        "msg": "账户投资失败"
    },
    35003: {
        "desc": "subaccount invest fail",
        "msg": "账户投资失败"
    },
    35004: {
        "desc": "bad invest duplicat",
        "msg": "复投类型有误"
    },
    35005: {
        "desc": "no subaccount",
        "msg": "账户不存在"
    },
    35006: {
        "desc": "account frozon to invest fail",
        "msg": "账户冻结资产转入已投资产失败"
    },
    35007: {
        "desc": "subaccount frozon to invest fail",
        "msg": "账户冻结资产转入已投资产失败"
    },
    35008: {
        "desc": "account frozon to balance fail",
        "msg": "账户冻结资产转入余额失败"
    },
    35009: {
        "desc": "subaccount frozon to balance fail",
        "msg": "账户冻结资产转入余额失败"
    },
    35010: {
        "desc": "subaccount close fail",
        "msg": "子账户注销失败"
    },
    35011: {
        "desc": "repayment account change fail",
        "msg": "汇款账户信息变更失败"
    },
    35012: {
        "desc": "repayment subaccount change fail",
        "msg": "汇款账户信息变更失败"
    },
    35013: {
        "desc": "project not end",
        "msg": "未到达项目结束时间"
    },
    35014: {
        "desc": "account settlement fail",
        "msg": "账户结息失败"
    },
    35015: {
        "desc": "subaccount settlement fail",
        "msg": "账户结息失败"
    },
    35016: {
        "desc": "subaccount reinvest fail",
        "msg": "账户复投失败"
    },
    35017: {
        "desc": "bad token coin id",
        "msg": "错误的币种"
    },
    35018: {
        "desc": "bad recharge amount",
        "msg": "充值金额不能为负"
    },
    35019: {
        "desc": "bad recharge record id",
        "msg": "充值申请有误"
    },
    35020: {
        "desc": "recharge fail",
        "msg": "充值失败"
    },
    35021: {
        "desc": "can not bet",
        "msg": "下注失败"
    },
    35022: {
        "desc": "can not increase",
        "msg": "加币失败"
    },
    35023: {
        "desc": "no pay password",
        "msg": "请先设置交易密码"
    },
    35024: {
        "desc": "bad pay password",
        "msg": "交易密码错误"
    },
    35025: {
        "desc": "bad withdraw amount",
        "msg": "提现金额有误"
    },
    35026: {
        "desc": "bad withdraw fee",
        "msg": "提现手续费有误"
    },
    35027: {
        "desc": "no token account",
        "msg": "余额不足"
    },
    35028: {
        "desc": "apply withdraw fail",
        "msg": "提现金额有误"
    },
    35029: {
        "desc": "account apply withdraw fail",
        "msg": "提现执行异常"
    },
    35030: {
        "desc": "bad account change record id",
        "msg": "无效的账户变换id"
    },
    35031: {
        "desc": "bad account change type",
        "msg": "错误的账户变更类型"
    },
    35032: {
        "desc": "bad change type",
        "msg": "错误的变化类型"
    },
    35033: {
        "desc": "bad withdraw amount",
        "msg": "实际提现数值与记录中不一致"
    },
    35034: {
        "desc": "bad sms email key",
        "msg": "错误的验证码发送场景"
    },
    30035: {
        "desc": "send sms email fail",
        "msg": "发送失败，请再次尝试"
    },
    30036: {
        "desc": "bad sms email vcode",
        "msg": "验证码错误"
    },
    30037: {
        "desc": "get private key fail",
        "msg": "获取私钥失败"
    },
    30038: {
        "desc": "nick name used",
        "msg": "该昵称已被占用"
    },
    30039: {
        "desc": "nick name used",
        "msg": "该昵称已被占用"
    },
    30040: {
        "desc": "account lottery",
        "msg": "用户已拥有首次注册红包"
    },
    30041: {
        "desc": "Registration abnormal channels",
        "msg": "注册渠道异常"
    },
    35999: {
        "desc": "account end",
        "msg": "账户相关报错的结束"
    },
    40001: {
        "desc": "template name not found",
        "msg": "夺宝标题未找到"
    },
    40002: {
        "desc": "content is empty",
        "msg": "提交内容不能为空"
    },
    40003: {
        "desc": "not found comment",
        "msg": "没有找到评论"
    },
    40004: {
        "desc": "price out of range",
        "msg": "币价波动范围超过设定值"
    },
    40005: {
        "desc": "no such instance",
        "msg": "未找到此实例"
    },
    40006: {
        "desc": "no such winners",
        "msg": "未找到中奖人"
    },
    40007: {
        "desc": "the user has already praise",
        "msg": "该用户已经点过赞"
    },
    40008: {
        "desc": "need is not digit",
        "msg": "总需数不为数字"
    },
    40009: {
        "desc": "Incorrect total need setting",
        "msg": "总需数设置有误"
    },
    40010: {
        "desc": "game serial repeat",
        "msg": "期号重复"
    },
    40011: {
        "desc": "offline early than online",
        "msg": "下线时间早于上线时间"
    },
    40012: {
        "desc": "announce was online",
        "msg": "公告已经上线或作废"
    },
    40013: {
        "desc": "banner was online",
        "msg": "banner已经上线或作废"
    },
    40014: {
        "desc": "block chain info error",
        "msg": "发布信息上链失败"
    },
    40015: {
        "desc": "create all bet number fail",
        "msg": "创建奖号失败"
    },
    40016: {
        "desc": "participate_in id not found",
        "msg": "未找到用户参与号码"
    },
    40017: {
        "desc": "bet in not enough",
        "msg": "本次投入数量不足"
    },
    40018: {
        "desc": "instance is none",
        "msg": "目前没有可下注的项目, 请稍后再试"
    },
    40019: {
        "desc": "initiate_merge fail",
        "msg": "合买发起失败, 请重新投注后再发起"
    },
    40020: {
        "desc": "version not found",
        "msg": "未发现最新版本"
    },
    40021: {
        "desc": "dice not found",
        "msg": "未找到猜拳游戏信息"
    },
    40022: {
        "desc": "coin dice info not found",
        "msg": "未找到此币种的猜拳游戏配置信息"
    },
    40023: {
        "desc": "winning control",
        "msg": "当前参与用户过多"
    },
    40024: {
        "desc": "eos block",
        "msg": "eos区块获取失败"
    },
    40025: {
        "desc": "bet out of range",
        "msg": "超出可投额度"
    },
    40026: {
        "desc": "bet error",
        "msg": "投注失败"
    },

    50000: {
        "desc": "enter full information",
        "msg": "请配置完整信息"
    },

    50001: {
        "desc": "no such template",
        "msg": "未找到此模版"
    },

    50002: {
        "desc": "no such template",
        "msg": "配置参数错误"
    },

    50003: {
        "desc": "no such template",
        "msg": "此模版名称已存在"
    },

    60000: {
        "desc": "No such item",
        "msg": "当前项目不是可投状态"
    },

    60001: {
        "desc": "No such item",
        "msg": "当前期数不存在"
    },
    60002: {
        "desc": "No such item",
        "msg": "项目待揭晓，不可再投"
    },
    60003: {
        "desc": "No such item",
        "msg": "项目已完结，不可再投"
    },
    60004: {
        "desc": "No such item",
        "msg": "投注数量大于剩余可下注数量"
    },

    60005: {
        "desc": "No such item",
        "msg": "账户余额不足"
    },

    60006: {
        "desc": "No such item",
        "msg": "下注扣款失败"
    },

    60007: {
        "desc": "No such item",
        "msg": "下注失败，奖号已被抢空"
    },

    60008: {
        "desc": "No such item",
        "msg": "下注失败，项目不支持此币种"
    },

    60009: {
        "desc": "No such item",
        "msg": "提交扣款申请失败"
    },

    60010: {
        "desc": "No such item",
        "msg": "提交扣款申请失败!"
    },

    60011: {
        "desc": "No such item",
        "msg": "获取期号异常!!!"
    },

    60012: {
        "desc": "No such item",
        "msg": "获取期号异常"
    },

    60013: {
        "desc": "No such item",
        "msg": "扣款异常"
    },

    60014: {
        "desc": "No such item",
        "msg": "删除失败"
    },
    60015: {
        "desc": "experience out of range",
        "msg": "单次最多支付10个USDT体验金"
    },
    60016: {
        "desc": "instance experience out of range",
        "msg": "本期体验金使用额度已用完"
    },
    60017: {
        "desc": "user experience out of range",
        "msg": "您今日体验金使用额度已用完"
    },

    60018: {
        "desc": "user experience out of range",
        "msg": "当前项目不支持此币种"
    },
    60019: {
        "desc": "user experience out of range",
        "msg": "机器人数量小于平局下注数量"
    },
    60020: {
        "desc": "user experience out of range",
        "msg": "时间配置错误"
    },

    60021: {
        "desc": "No such item",
        "msg": "机器人和下注数量规则不匹配 太多"
    },

    60022: {
        "desc": "No such item",
        "msg": "机器人和下注数量规则不匹配 太少"
    },

    70000: {
        "desc": "No such item",
        "msg": "闲置机器人不够"
    },

    70001: {
        "desc": "No such item",
        "msg": "机器人配置错误"
    },

    70003: {
        "desc": "No such item",
        "msg": "机器人任务添加失败,请重试"
    },

    70002: {
        "desc": "No such item",
        "msg": "机器人投注失败"
    },

    70004: {
        "desc": "No such item",
        "msg": "机器人时间设定不正确"
    },

    70005: {
        "desc": "No such item",
        "msg": "机器人已被占用请重新筛选"
    },

    70006: {
        "desc": "No such item",
        "msg": "机器人重置失败"
    },

    80000: {
        "desc": "No such item",
        "msg": "项目未募满 开奖失败"
    },

    80001: {
        "desc": "No such item",
        "msg": "未获得开奖区块Hash值"
    },

    80002: {
        "desc": "No such item",
        "msg": "无人参与"
    },

    80003: {
        "desc": "No such item",
        "msg": "无人中奖"
    },

    80004: {
        "desc": "No such item",
        "msg": "奖金领取失败"
    },

    80005: {
        "desc": "No such item",
        "msg": "项目更改已开奖失败"
    },

    90000: {
        "desc": "Send transaction broadcast failed",
        "msg": "发送交易广播失败"
    },
    90001: {
        "desc": "The parameter address that parses the secret key is not a list or a string",
        "msg": "解析秘钥所传参数地址不是列表或字符串"
    },
    90002: {
        "desc": "This coin type does not exist",
        "msg": "该币种类型不存在"
    },
    90003: {
        "desc": "The address does not exist",
        "msg": "该地址不存在"
    },
    90004: {
        "desc": "this coin_id has no available address",
        "msg": "该币种没有可用的地址"
    },
    90005: {
        "desc": "To apply for withdrawal, conditions for error",
        "msg": "提现申请,条件有误"
    },
    90006: {
        "desc": "Transaction from_address and to_address duplicate",
        "msg": "交易 发送地址和收款地址 重复"
    },
    90007: {
        "desc": "The transaction fee is 0 !",
        "msg": "手续费为零"
    },
    90008: {
        "desc": "Aggregate amount less than handling fee",
        "msg": "归集金额小于手续费"
    },
    90009: {
        "desc": "Insufficient balance of transaction address",
        "msg": "交易地址余额不足"
    },
    90010: {
        "desc": "This type is not found in the transaction type",
        "msg": "交易类型中没有这种类型"
    },
    90011: {
        "desc": "The ETH address is incorrect. It should be a 42-bit string starting with 0x",
        "msg": "以太坊地址错误,应为0x开头的42位字符串"
    },
    90012: {
        "desc": "EOS fees cannot be zero",
        "msg": "EOS手续费不能为零"
    },
    90013: {
        "desc": "EOS has no corresponding account",
        "msg": "EOS没有对应账户"
    }
}
