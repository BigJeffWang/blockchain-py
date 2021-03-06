from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from controllers.time_controller import *
from controllers.test_controller import *
from controllers.api_token_controller import *
from controllers.invest_user_controller import *
from controllers.vcode_controller import *
from controllers.show_controller import *
from controllers.transfer_controller import *
from controllers.admin_user_controller import *
from controllers.file_controller import *


app = Flask(__name__)
# 这个from必须放这里，否则代码顺序就乱了
from errors import error

CORS(app)
api = Api(app)


# 测试
api.add_resource(TestController, "/test")  # 测试接口
# api.add_resource(ShowController, "/show")  # 测试接口

# 获取服务器时间
api.add_resource(ApiTimestampController, "/timestamp")

# invest_user
api.add_resource(InvestUserGenerateRegisterKeySaltController, "/users/get-register-salt")  # 获取注册salt
api.add_resource(InvestUserGetPictureVCodeController, "/users/send-picture-vcode")  # 发送注册图形验证码
api.add_resource(InvestUserSendRegisterVCodeController, "/users/send-register-vcode")  # 发送注册验证码
api.add_resource(InvestUserRegisterSignatureController, "/users/send-register-signature")  # 获取表单提交校验码
api.add_resource(InvestUserRegisterController, "/users/register")  # 用户注册
api.add_resource(InvestGenerateLoginKeySaltController, "/users/get-login-salt")  # 获取登录salt
api.add_resource(InvestUserLoginController, "/users/login")  # 用户登录
api.add_resource(InvestUserGetLoginPictureVCodeController, "/users/send-login-picture-vcode")  # 发送手机号验证码登陆图形验证码
api.add_resource(InvestUserSendLoginVCodeController, "/users/send-login-vcode")  # 发送手机号验证码登陆的验证码
api.add_resource(InvestUserLoginByMobileController, "/users/login-by-mobile")  # 用户手机号验证码登录
api.add_resource(InvestRefreshAccessTokenController, "/users/refresh-token")  # 刷新access_token
api.add_resource(InvestUserClientInfoController, "/users/user-info")  # 客户端投资用户个人信息
api.add_resource(InvestGeneratePayKeySaltController, "/users/get-pay-salt")  # 获取交易密码salt
api.add_resource(InvestUserGetPictureVCodeSetPayPDController, "/users/send-set-pay-password-picture-vcode")  # 发送设置交易密码图形验证码
api.add_resource(InvestUserSendSetPayPDVCodeController, "/users/send-set-pay-pd-vcode")  # 发送设置交易密码的验证码
api.add_resource(InvestUserPayPWDController, "/users/set-pay-password")  # 设置支付密码
api.add_resource(InvestUserGetPictureVCodeResetPayPDController, "/users/send-reset-pay-password-picture-vcode")  # 发送重制交易密码图形验证码
api.add_resource(InvestUserSendResetPayPDVCodeController, "/users/send-reset-pay-pd-vcode")  # 发送重制交易密码的验证码
api.add_resource(InvestUserResetPayPasswordController, "/users/reset-pay-password")  # 重置交易密码
api.add_resource(InvestUserGetPictureVCodeSetMobileController, "/users/send-set-mobile-picture-vcode")  # 发送设置手机号图形验证码
api.add_resource(InvestUserSendSetMobileVCodeController, "/users/send-set-mobile-vcode")  # 发送设置手机号的验证码
api.add_resource(InvestUserSetMobileController, "/users/set-user-mobile")  # 设置手机号
api.add_resource(InvestUserGetPictureVCodeSetEmailController, "/users/send-set-email-picture-vcode")  # 发送设置email图形验证码
api.add_resource(InvestUserSendSetEmailVCodeController, "/users/send-set-email-vcode")  # 发送设置email的验证码
api.add_resource(InvestUserEmailController, "/users/set-email")  # 设置email
api.add_resource(InvestUserNickNameController, "/users/set-nick-name")  # 设置昵称
api.add_resource(InvestUserAvatarController, "/users/set-avatar")  # 设置头像
api.add_resource(InvestUserGetResetPWDPictureVCodeController, "/users/send-resetpwd-picture-vcode")  # 发送重置密码图形验证码
api.add_resource(InvestUserSendResetPWDVCodeController, "/users/send-resetpwd-vcode")  # 发送重置密码验证码
api.add_resource(InvestUserResetLoginPasswordController, "/users/reset-login-password")  # 重置登陆密码
api.add_resource(InvestUserChangeLoginPasswordController, "/users/change-login-password")  # 登录状态下修改登录密码
api.add_resource(InvestLoginGenerateLoginKeySaltController, "/users/get-change-login-password-salt")  # 登陆状态下获取密码盐
api.add_resource(InvestUnLoginGenerateLoginKeySaltController, "/users/get-change-unlogin-password-salt")  # 非登陆状态下获取密码盐


# admin_user
api.add_resource(BgGenerateLoginKeySaltController, "/bg/users/get-login-salt")  # 获取登录salt
api.add_resource(AdminUserLoginController, "/bg/users/login")  # 后台用户登录
api.add_resource(BgRefreshAccessTokenController, "/bg/users/refresh-token")  # 刷新access_token
api.add_resource(BgGetUserInfoController, "/bg/users/info")  # 这个是平台用的获取用户信息
api.add_resource(AdminUserRegisterByAdminController, "/bg/users/new-user")  # 后台高权限用户生成普通后台用户
api.add_resource(AdminUserDeleteByAdminController, "/bg/users/delete-user")  # 后台高权限用户删除普通后台用户
api.add_resource(AdminUserChangeRightsByAdminController, "/bg/users/change-user-right")  # 后台高权限用户修改普通后台用户
api.add_resource(AdminUserListRightsByAdminController, "/bg/users/list-user-right")  # 后台高权限用户获取普通后台用户
api.add_resource(AdminListRightsByAdminController, "/bg/users/list-right")  # 后台高权限用户获取所有的模块

# 交互
api.add_resource(PlatformCheckFormTokenController, "/transfer/<string:token>")  # 后台用户与其他平台交互
api.add_resource(UsersTransferToPlatformController, "/users/<path:path>")  # 用户与其他平台交互
api.add_resource(BgUsersTransferToPlatformController, "/bg/users/<path:path>")  # 用户与其他平台交互
api.add_resource(CommonTransferToPlatformController, "/common/<path:path>")  # 用户与其他平台交互


# 文件上传
api.add_resource(UploadPhotoController, "/up_photo")  # 图片上传

# 仅开发环境使用
api.add_resource(DevInvestUserGenerateRegisterKeySaltController, "/users/dev-get-register-salt")  # 获取注册salt
api.add_resource(DevInvestGenerateLoginKeySaltController, "/users/dev-get-login-salt")  # 获取登录salt






