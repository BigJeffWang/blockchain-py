from flask import Flask
from flask_cors import CORS
from flask_restful import Api
# test Jenkins
from common_settings import *
from controllers.account_controller import (
    AccountRechargeController,
    AccountWithdrawApplyController,
    AccountWaterController,
    AccountTokenWaterController,
    LotteryController,
    GetUserInviterCode,
    UserWinningsController,
    UserSetProfilePictureController,
    BgAccountWaterController,
    BgOperatingActivitiesController
)
from controllers.block_chain_info_controller import (
    BlockChainInfoController,
    BlockChainInfoDetailController,
    UserBlockChainInfoDetailController,
    UserBlockInfoController,
    NewestBlockInfoController
)
from controllers.dice_controller import *
from controllers.instant_game_controller import *
from controllers.game_controller import *
from controllers.game_model_controller import *
from controllers.game_robot_controller import GameRobotBetInController, \
    GameSelectRobotController, GameAddRobotCongifController, GameCreatRobotController, GameSearchRobotCongifController, \
    GameSearchGameRobotCongifController, GameCancelRobotCongifController, GameResetRobotCongifController, \
    GameAddAutoRobotCongifController
from controllers.main_controller import *
from controllers.operating_controller import *
from controllers.social_controller import *
from controllers.test_controller import *
from controllers.time_controller import *
from controllers.token_controller import TokenController
from controllers.user_controller import *
from controllers.withdraw_controller import *

app = Flask(__name__)
from errors import error

error.err_init()
CORS(app, expose_headers=_RESPONSE_HEADER)
app.template_folder = "templates"
api = Api(app)

# base
api.add_resource(TestController, "/test")  # 测试接口
# 获取服务器时间
api.add_resource(ApiTimestampController, "/timestamp")

# 账户
# ——————start——————以下接口，需要user_center项目启动后，被user_center调用
api.add_resource(UserGenerateAccountController, "/users/register", "/users/register/<string:inviter_code>")  # 用户生成账户
api.add_resource(UserLoginController, "/users/login")  # 用户生成账户
api.add_resource(UserAccountInfoController, "/users/user-info", "/users/user-account-info")  # 获取用户信息
api.add_resource(UserGeneratePayKeySaltController, "/users/get-pay-salt")  # 获取支付密码盐
api.add_resource(UserResetPayPasswordController, "/users/reset-pay-password", "/users/set-pay-password")  # 重置交易密码
api.add_resource(UserNickNameController, "/users/set-nick-name")  # 设置昵称
api.add_resource(UserAvatarController, "/users/set-avatar")  # 设置头像
api.add_resource(UserSetMobileController, "/users/set-user-mobile")  # 设置手机号
api.add_resource(UserSetEmailController, "/users/set-email")  # 设置email
# ——————end——————以上接口，需要user_center项目启动后，被user_center调用

api.add_resource(AccountRechargeController, "/users/recharge_apply")  # 充值申请
api.add_resource(AccountWithdrawApplyController, "/users/withdraw_apply")  # 提现申请
api.add_resource(AccountWaterController, "/users/account_water")  # 账户列表
api.add_resource(AccountTokenWaterController, "/users/account_token_water")  # 账户列表
api.add_resource(LotteryController, "/users/lottery")  # 抽奖
api.add_resource(UserWinningsController, "/users/winnings")
api.add_resource(GetUserInviterCode, "/users/inviter/code")
api.add_resource(UserSetProfilePictureController, "/users/set_profile_picture")
# 用户管理
api.add_resource(BgOperatingActivitiesController, "/bg/users/users/operating_activities")
api.add_resource(BgAccountWaterController, "/bg/users/users/account_water")  # 后台用户流水
api.add_resource(UserListController, "/bg/users/users/list")  # 用户列表
api.add_resource(UserTokenListController, "/bg/users/users/tokens")  # 用户资产
api.add_resource(UserTokenDetailController, "/bg/users/users/tokens/detail")  # 资产详情

# 第三方币价格查询
api.add_resource(GameExchangeRateController, "/bg/users/game/exchange_rate")  # Game查询币价格

# 账户余额查询


# 项目详情查询


# 用户操作相关
api.add_resource(GameBetInController, "/users/game/chip_in")

# game后台管理
api.add_resource(GameAddModelController, "/bg/users/game/add_model")  # Game模版添加
api.add_resource(GameSearchModelController, "/bg/users/game/search_model")  # Game模版查询
api.add_resource(GameModifyModelController, "/bg/users/game/modify_model")  # Game模版修改
api.add_resource(GameDeleteModelController, "/bg/users/game/delete_model")  # Game模版删除
api.add_resource(GameModifyModelStatusController, "/bg/users/game/modify_model_status")  # Game模版更改启动停用状态
api.add_resource(GameInstanceListController, "/bg/users/game/game_instance_list")  # game实例列表
api.add_resource(GameTemplateNameListController, "/bg/users/game/game_template_name_list")  # game模板标题列表
api.add_resource(CurrentPeriodInfoController, "/bg/users/game/current_period_info")  # game实例详情(包括模板详情、中奖详情)
api.add_resource(ManualReleaseInfoController, "/bg/users/game/manual_release_info")  # 获取手动发布game信息
api.add_resource(ManualReleaseController, "/bg/users/game/manual_release")  # 手动发布game信息
api.add_resource(GetCurrentPriceController, "/bg/users/game/get_current_price")  # 获取实时币价
api.add_resource(ManageParticipateInController, "/bg/users/game/manage_participate_in")  # 后台管理用户参与列表

api.add_resource(GamePublishTheLotteryController, "/bg/users/game/publish_the_lottery")  # 开奖

# 社交
api.add_resource(AddCommentController, "/users/social/add_comment")  # 发表评论
api.add_resource(RemoveCommentController, "/users/social/remove_comment")  # 删除评论
api.add_resource(AddPraiseController, "/users/social/add_praise")  # 点赞
api.add_resource(RemovePraiseController, "/users/social/remove_praise")  # 取消点赞
api.add_resource(CommentListController, "/users/social/get_comment_list")  # 评论列表
api.add_resource(MineCommentController, "/users/social/get_mine_comment_list")  # 我的评论列表

# 互动管理
api.add_resource(CommentManageListController, "/bg/users/operating/comment_manage_list")  # 互动管理列表
api.add_resource(ChangeCommentStatusController, "/bg/users/operating/change_status")  # 修改互动显示状态

# 公告管理
api.add_resource(CreateAnnounceController, "/bg/users/operating/create_announce")  # 创建公告
api.add_resource(AnnounceListController, "/bg/users/operating/get_announce_list")  # 获取公告管理列表
api.add_resource(AnnounceDetailsController, "/bg/users/operating/announce_details")  # 获取公告信息
api.add_resource(EditAnnounceController, "/bg/users/operating/edit_announce")  # 编辑公告信息
api.add_resource(ChangeAnnounceStatusController, "/bg/users/operating/change_announce_status")  # 编辑公告状态

# banner管理
api.add_resource(CreateBannerController, "/bg/users/operating/create_banner")  # 创建banner
api.add_resource(BannerListController, "/bg/users/operating/get_banner_list")  # 获取banner列表
api.add_resource(BannerDetailsController, "/bg/users/operating/banner_details")  # 获取banner信息
api.add_resource(ChangeBannerStatusController, "/bg/users/operating/change_banner_status")  # 编辑banner
api.add_resource(EditBannerController, "/bg/users/operating/edit_banner")  # 编辑banner状态

# 机器人相关
api.add_resource(GameCreatRobotController, "/bg/users/game/robot/creat_robot")  # 创建机器人
api.add_resource(GameSelectRobotController, "/bg/users/game/robot/select")  # 选择指定数量机器人
api.add_resource(GameAddRobotCongifController, "/bg/users/game/robot/add_robot_config")  # 添加手动机器人配置
api.add_resource(GameAddAutoRobotCongifController, "/bg/users/game/robot/add_auto_robot_config")  # 添加自动机器人配置
api.add_resource(GameResetRobotCongifController, "/bg/users/game/robot/reset_robot_config")  # 重置手动机器人状态
api.add_resource(GameSearchGameRobotCongifController, "/bg/users/game/robot/search_game_robot_config")  # 查询游戏机器人配置
api.add_resource(GameSearchRobotCongifController, "/bg/users/game/robot/search_robot_config")  # 查询机器人配置
api.add_resource(GameCancelRobotCongifController, "/bg/users/game/robot/cancel_robot_config")  # 停止游戏机器人配置
api.add_resource(GameRobotBetInController, "/bg/users/game/robot/bet_in")  # 机器人投注

# 提现管理后台
api.add_resource(WithdrawListController, "/bg/users/withdraw/list")  # 提现列表
api.add_resource(WithdrawApplyController, "/bg/users/withdraw/apply")  # 提现审核页面
api.add_resource(UserRecordController, "/bg/users/withdraw/user_record")  # 用户提现流水
api.add_resource(AuditWithdrawController, "/bg/users/withdraw/audit_withdraw")  # 提现审核
api.add_resource(OperationWithdrawController, "/bg/users/withdraw/operation_withdraw")  # 提现操作
api.add_resource(WithdrawDetailsController, "/bg/users/withdraw/details")  # 查看提现详情
api.add_resource(OfflineTxController, "/bg/users/withdraw/offline_tx")  # 线下提现录入tx

# 其他
api.add_resource(GetGasController, "/users/common/get_gas")  # app获取提现手续费
api.add_resource(CheckAddressController, "/users/common/check_address")  # 判断提现地址是否为平台地址
api.add_resource(AppendGasController, "/bg/users/common/append_gas")  # 后台ETH追加手续费
api.add_resource(SendCodeController, "/bg/users/common/send_code")  # 后台发送邮箱验证码

# 归集管理后台
api.add_resource(GatherAddressListController, "/bg/users/gather/gather_address_list")  # 归集地址列表
api.add_resource(GatherAddressRecordController, "/bg/users/gather/gather_address_record")  # 归集地址流水
api.add_resource(SubAddressListController, "/bg/users/gather/sub_address_list")  # 子账户地址列表
api.add_resource(OperationGatherController, "/bg/users/gather/operation_gather")  # 归集操作
api.add_resource(GatherRecordController, "/bg/users/gather/gather_record")  # 归集操作记录
api.add_resource(GatherRecordDetailsController, "/bg/users/gather/gather_record_details")  # 归集操作记录详情
api.add_resource(GatherRecordAllController, "/bg/users/gather/gather_record_all")  # 全部归集操作记录详情
api.add_resource(GatherToGatherController, "/bg/users/gather/gather_to_gather")  # 归集转归集

# Block Chain Information
api.add_resource(BlockChainInfoController, "/common/blockchain/info")  # 区块链 浏览器头部信息
api.add_resource(BlockChainInfoDetailController, "/common/blockchain/info/detail")  # get投注记录
api.add_resource(UserBlockChainInfoDetailController, "/users/blockchain/info/detail")  # post投注记录
api.add_resource(UserBlockInfoController, "/users/blockchain/info/user")  # 区块链 我的投注记录列表
api.add_resource(NewestBlockInfoController, "/common/blockchain/info/new")  # 区块链 浏览器最新区块

# game模块前台展示接口
api.add_resource(MainPageController, "/common/main/main_page")  # 首页接口
api.add_resource(GamePageController, "/common/main/game_page")  # game专区首页接口
api.add_resource(IndianaRecordController, "/users/main/indiana_record")  # 我的夺宝记录
api.add_resource(IndianaRecordNewController, "/users/main/indiana_record_new")  # 我的夺宝记录
api.add_resource(IndianaNumberController, "/users/main/indiana_number")  # 我的夺宝号码
api.add_resource(IndianaNumberNewController, "/users/main/indiana_number_new")  # 我的夺宝号码
api.add_resource(NewWinningRecordController, "/common/game/get_winning_record")  # 开奖信息
api.add_resource(HeroListController, "/common/game/hero_list")  # 英雄榜
api.add_resource(GameParticipateInListController, "/common/game/game_participate_in_list")  # 用户参与列表
api.add_resource(GameInstanceController, "/users/game/game_instance")  # 获取game实例信息
api.add_resource(MergeGameInstanceController, "/common/game/merge_game_instance")  # 非登录状态下获取game实例信息
api.add_resource(GameInstanceNoneUserController, "/common/game/game_instance")  # 获取game实例信息 (非登录)
api.add_resource(InstanceBlockchainInfoController, "/common/game/instance_blockchain_info")  # 获取game实例信息和对应的区块链信息
api.add_resource(MergeParticipateInListController, "/common/game/merge_participate_in_list")  # 本期合买列表
api.add_resource(MergeDetailListController, "/common/game/merge_detail_list")  # 本期合买参与列表
api.add_resource(InitiateMergeController, "/users/game/initiate_merge")  # 发起合买
api.add_resource(MergeInfoListController, "/common/game/merge_info_list")  # 合买获奖信息列表
api.add_resource(IndianaDetailController, "/common/main/indiana_detail")  # 夺宝详情
api.add_resource(LatestAvailableInstanceController, "/common/game/latest_available_instance")  # 获取最新可投项目id

# dice相关接口
api.add_resource(DiceRecordsController, "/users/dice/dice_records")  # dice参与列表
api.add_resource(DiceRecordsGetController, "/common/dice/dice_records")  # dice参与列表 不需要登录
api.add_resource(DiceInfoController, "/common/dice/dice_info")  # dice对决信息
api.add_resource(DiceChipInController, "/users/dice/dice_chip_in")  # dice对决下注
api.add_resource(DiceChipInCallbackController, "/users/dice/dice_sold_out_new")  # dice对决下注结果回调
api.add_resource(GetDiceAwardRateController, "/users/dice/get_dice_award_rate")  # dice对决胜率统计

# 平台通用信息
api.add_resource(TokenController, "/users/common/coin_list")  # 币种信息列表,POST方法
api.add_resource(GameStatisticalController, "/users/common/game_statistical")  # 开奖数据统计
api.add_resource(UserStatisticalController, "/users/common/user_statistical")  # 用户数据分析
api.add_resource(AppVersionCheckController, "/common/main/app_version_check")  # app版本检查

# 一元夺宝即时开
api.add_resource(InstantGameAddModelController, "/bg/users/instant_game/add_model")  # Game模版添加
api.add_resource(InstantGameSearchModelController, "/bg/users/instant_game/search_model")  # Game模版查询
api.add_resource(InstantGameModifyModelController, "/bg/users/instant_game/modify_model")  # Game模版修改
api.add_resource(InstantGameDeleteModelController, "/bg/users/instant_game/delete_model")  # Game模版删除
api.add_resource(InstantGameListController, "/bg/users/instant_game/instant_game_list")  # Game列表
api.add_resource(GetInstantPartInListController, "/bg/users/instant_game/instant_part_in_list")  # 即时开参与列表

api.add_resource(InstantGameBetController, "/users/instant_game/chip_in")  # 即时开下注

api.add_resource(InstantGameNoneUserController, "/common/instant_game/game_instance")  # 即时开非登录项目信息
api.add_resource(InstantGameController, "/users/instant_game/game_instance")  # 即时开项目信息
api.add_resource(GetInstantResultController, "/users/instant_game/get_instant_result")  # 获取即时开参与信息

# OTC 充值
api.add_resource(UserAddTokenController, "/OTCExchange")
