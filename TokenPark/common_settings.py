_DOC = """

"""
__all__ = [
    '_SERVER_IP',
    '_SERVER_ENTRY_IP',
    '_ZERO_S',
    '_ONE_S',
    '_TWO_S',
    '_THREE_S',
    '_FOUR_S',
    '_FIVE_S',
    '_SIX_S',
    '_SEVEN_S',
    '_EIGHT_S',
    '_NINE_S',
    '_TEN_S',
    '_ZERO',
    '_ONE',
    '_TWO',
    '_TWO_S',
    '_THREE',
    '_FOUR',
    '_FIVE',
    '_SIX',
    '_SEVEN',
    '_EIGHT',
    '_NINE',
    '_TEN',
    '_SIXTY',
    '_SIXTY_S',
    '_HUNDRED',
    '_THOUSAND',
    '_YEAR',
    '_MONTH',
    '_WEEK',
    '_DAY',
    '_HOUR',
    '_PROCESSING',
    '_SUCCESSFUL',
    '_FAILURE',
    '_Min_INVEST_AMOUNT',
    '_USER_TYPE_INVEST',
    '_USER_TYPE_BORROWING',
    '_USER_TYPE_ADMIN',
    '_RESPONSE_HEADER',
    '_SHARE_KEY',
    '_NONCE',
    '_INNER_SHARE_KEY',
    '_INNER_NONCE',
    '_NEW_USER_SCORE',
    '_GATHER',
    '_ACCOUNT',
    '_BTC',
    '_ETH',
    '_USDT',
    '_EOS',
    '_COIN_ID_BTC',
    '_COIN_ID_ETH',
    '_COIN_ID_EOS',
    '_COIN_ID_USDT',
    '_COIN_ID_EXP',
    '_EOS_RECHARGE_ADDRESS',
    '_REQUEST_KEY_LIST',
    '_RESPONSE_KEY_LIST'
]

# 通用 --------------------------------------------------------------------------------------------

_SERVER_IP = "https://api.rongmofang.com"
_SERVER_ENTRY_IP = "http://39.105.32.28:19000"  # 服务的入口,由Nginx接收并作反向代理
_ZERO = 0
_ZERO_S = "0"
_ONE = 1
_ONE_S = "1"
_TWO = 2
_TWO_S = "2"
_THREE = 3
_THREE_S = "3"
_FOUR = 4
_FOUR_S = "4"
_FIVE = 5
_FIVE_S = "5"
_SIX = 6
_SIX_S = "6"
_SEVEN = 7
_SEVEN_S = "7"
_EIGHT = 8
_EIGHT_S = "8"
_NINE = 9
_NINE_S = "9"
_TEN = 10
_TEN_S = "10"
_SIXTY = 60
_SIXTY_S = "60"
_HUNDRED = 100
_THOUSAND = 1000
_YEAR = 365  # 1年365天
_MONTH = 12
_WEEK = 7
_DAY = 24  # 1天24小时
_HOUR = 60
_PROCESSING = 0  # 处理中
_SUCCESSFUL = 1  # 成功
_FAILURE = 2  # 失败
_Min_INVEST_AMOUNT = 100  # 可投资最小金额

# 用户 -----------------------------------------------------------------------------------------------------------------
_USER_TYPE_INVEST = 0
_USER_TYPE_BORROWING = 1
_USER_TYPE_ADMIN = 2
_NEW_USER_SCORE = 10000  # 新用户积分

# 其他 -----------------------------------------------------------------------------------------------------------------
_RESPONSE_HEADER = ["date", "Error_Msg", "Error_Code", "Error_Desc"]

_SHARE_KEY = "YKVD42i3sY17MIfV8BERh0oM7Ti2AcDkLH+4gG/RVHaUKsD5EhOXs5ugTGKNXS3j"
_NONCE = "540929e21c04a3a4bef16fe3"

# 与用户中心交互的加密
_INNER_SHARE_KEY = "/F+A1Oc+3uIAkg3dGzdwpElqE7v3AyNoSQzTFO5Gd1Vfi8Bmso1MY/aDP1x+NRFf"
_INNER_NONCE = "cd7c66da329a9b54e19d2b17"

# 区块链相关 -----------------------------------------------------------------------------------------------------------------
_GATHER = "gather"
_ACCOUNT = "account"
_BTC = "BTC"
_ETH = "ETH"
_USDT = "USDT"
_EOS = "EOS"

_COIN_ID_BTC = "0"
_COIN_ID_ETH = "60"
_COIN_ID_EOS = "194"
_COIN_ID_USDT = "100000000"
_COIN_ID_EXP = "236"

_EOS_RECHARGE_ADDRESS = {
    "dev": "luckyparkchn",
    "pd": "eosluckypark"
}

# 时区转换
_REQUEST_KEY_LIST = [
    "time",
    "begin_time",
    "end_time",
    "apply_time_start",
    "apply_time_end",
    "transfer_time_start",
    "transfer_time_end",
    "start_at",
    "end_at",
    "transfer_at",
    "update_at_start",
    "update_at_end",
    "transfer_at_start",
    "transfer_at_end",
    "operate_at_start",
    "operate_at_end",
    "confirm_at_start",
    "confirm_at_end",
    "part_in_time_start",
    "part_in_time_end",
    "release_time_start",
    "release_time_end",
    "full_load_time_start",
    "full_load_time_end",
    "bet_time",
    "start_time",
    "end_time"
]
_RESPONSE_KEY_LIST = [
    "time",
    "begin_time",
    "end_time",
    "apply_time",
    "transfer_time",
    "confirm_time",
    "finish_time",
    "created_at",
    "expect_at",
    "audit_at",
    "transfer_at",
    "confirm_at",
    "update_at",
    "bet_time",
    "lottery_time",
    "indiana_time",
    "release_time",
    "full_load_time",
    "end_of_plan_time",
    "end_of_real_time",
    "first_recharge_at",
    "create_at",
    "bet_plan_time",
    "start_of_plan_time",
    "part_in_time",
    "dice_time",
    "block_timestamp",
    "dice_timestamp",
    "received_time"
]
