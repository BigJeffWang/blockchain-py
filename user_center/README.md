# 配置文件
1. config.json 基础配置包含本项目mysql、redis等 用例为config.json.demo
2. transfer_to_platform.yaml 链接usercenter与其他平台等配置，已保证客户端等访问可以被传输到其他平台 用例为transfer_to_platform.yaml.demo
3. api.py 客户端访问路由，不同的项目，允许访问的功能不同，因此需要配置不同的路由入口。所有的路由应该都更新到 api.py.all  以方便查看，防止重复开发
4. UsersTransferToPlatformController,将前台用户对请求从usercenter转给tokenpark，路由格式为 /users/...且不能与usercenter重名
5. UsersTransferToPlatformController,将后台用户对请求从usercenter转给tokenpark，路由格式为 /bg/users/模块名/...且不能与usercenter重名
同时后台用户对模块操作权限也在这里进行了校验
6. InvestUserRegisterSignatureController提供了表单对随机字符串，防止表单对重复提交，usercenter的校验在get_argument_dict中进行，由参数check_form_token决定；
tokenpark的校验需要在其代码中的basecontroller中回调PlatformCheckFormTokenController才能实现

# 建议部署流程
1. 更新mysql，不同项目的开发可能会扩充数据库，因此需要更新alembic
2. 生成 config.json transfer_to_platform.yaml api.py 等配置文件
3. 运行代码
4. 配置路由，增加客户端通过usercenter访问其他plat的路由
5. basecontroller 的
verify_timeliness=True, encrypt=True, check_token=True, invariable_key=True, check_form_token = False
这五个参数上线必须为true，只有环境为dev可以被设置为False，方便调试
