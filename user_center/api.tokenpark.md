
# 基类

# 时间
[获取服务的时间](#获取服务的时间)

# 表单提交随机字符串
[表单提交随机字符串](#表单提交随机字符串)

# 图片上传
[图片上传](#图片上传)

# invest_user

[获取注册salt](#invest获取注册salt)

[获取注册图形验证码](#invest获取注册图形验证码)

[获取注册验证码](#invest获取注册验证码)

[注册](#invest注册)

[获取登陆salt](#invest获取登陆salt)

[登陆](#invest登陆)

[手机号验证码登陆获取图形验证码](#invest手机号验证码登陆获取图形验证码)

[手机号验证码登陆获取证码](#invest手机号验证码登陆获取验证码)

[手机号验证码登陆](#invest手机号验证码登陆)

[刷新accesstoken](#invest刷新accesstoken)

[获取支付密码加密salt](#invest获取支付密码加密salt)

[发送设置支付密码图形验证码](#invest发送设置支付密码图形验证码)

[发送设置支付密码的验证码](#invest发送设置支付密码的验证码)

[设置支付密码](#invest设置支付密码)

[发送重置支付密码图形验证码](#invest发送重置支付密码图形验证码)

[发送重置支付密码的验证码](#invest发送重置支付密码的验证码)

[重置支付密码](#invest重置支付密码)

[设置手机号获取图形验证码](#invest设置手机号获取图形验证码)

[设置手机号获取证码](#invest设置手机号获取证码)

[设置手机号](#invest设置手机号)

[修改email获取图形验证码](#invest修改email获取图形验证码)

[修改email获取证码](#invest修改email获取证码)

[修改email](#invest修改email)

[修改昵称](#invest修改昵称)

[修改头像](#invest修改头像)

[用户信息](#invest用户信息)

[未登陆状态下获取重置登陆密码的图形验证码](#invest未登陆状态下获取重置登陆密码的图形验证码)

[未登陆状态下获取重置登陆密码的验证码](#invest未登陆状态下获取重置登陆密码的验证码)

[未登陆状态下重置登陆密码](#invest未登陆状态下重置登陆密码)

[登陆状态下修改登陆密码](#invest登陆状态下修改登陆密码)

[登陆状态下获取密码盐](#invest登陆状态下获取密码盐)

[非登陆状态下获取密码盐](#invest非登陆状态下获取密码盐)

# admin_user

Tips：
1. 可供测试用的管理员为，mysql第12行的数据，用户名为管理员1，密码为gxFC123 level 为9999
2. 后台用户会校验操作系统所在ip，其白名单为配置文件config.json 的whitelist
3. rights_list 为后台用户包含的模块管理权限，其中的rights_id_list，标志着该用户在该模块的权限，目前暂定为[1],表示权限都有

[登陆](#admin登陆)

[获取登陆salt](#admin获取登陆salt)

[刷新accesstoken](#admin刷新accesstoken)

[用户信息](#admin用户信息)

[后台高权限用户获取所有的模块](#后台高权限用户获取所有的模块)

[后台高权限用户生成普通后台用户](#后台高权限用户生成普通后台用户)

[后台高权限用户删除普通后台用户](#后台高权限用户删除普通后台用户)

[后台高权限用户获取普通后台用户](#后台高权限用户获取普通后台用户)

[后台高权限用户修改普通后台用户](#后台高权限用户修改普通后台用户)

# 基类

## 获取服务的时间
<a name = "获取服务的时间">

URL: /timestamp

Method: GET

Params:

Return:

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "timestamp": "1536718735"
    }
}
```

## 表单提交随机字符串
<a name = "表单提交随机字符串">

URL: /users/send-register-signature

Method: POST

Params:

Return:

```
"6138971626if19g122U87739762062I0659886532J46051L3863600K109243694732255D3130IC448796292778N0983928153P409U9225590q42729I68678P69"
```

## 图片上传
<a name = "图片上传">

URL: /up_photo

Method: POST

Tips：

返回图片路径前拼“http://mshc-finance.oss-cn-beijing.aliyuncs.com/”即可打开图片

Params: 

* files 图片

Return:

```
[
    {
        "ori": "test/2018-11/2018-11-14/c95e2e9ca3e541be93a563b492c3b71e.png",  # 原图
        "thumb": "test/2018-11/2018-11-14/98a90117f7cf466b9bc0562b9a487e09.png"  # 缩略图
    }
]
```

# invest_user

## invest获取注册salt
<a name = "invest获取注册salt">

URL: /users/get-register-salt

Method: POST

Tips：


Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_name  手机号注册则为手机号，email注册则为email

* client_public_key 客户端公钥

* register_by 注册方法 1手机号 2email

* mobile_country_code 国家区号

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "server_public_key": "-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAEa/fHyxwSNWDNHeQ27jcJ/j/W2CTy3dYo\n3xDqHlGnmUieo9CoLRMDf/YM8JmPHcgEHpxqc9Wsgie7JzLI0vtpBoHQzyYnwZAF\nsWLzjeq6604VyvlQJDgr5CSoYaQ9jqsl\n-----END PUBLIC KEY-----\n",
        "user_name": "前台用户2",
        "bcrypt_salt": "$2a$12$vdIbUYOZIc8BHi1cXuFtge",
        "nonce": "d74d91156be83c04eb68a1ba",
        "time_stamp": "1541998258"
    }
}
```

## invest获取注册图形验证码
<a name = "invest获取注册图形验证码">

URL: /users/send-picture-vcode

Method: POST

Tips：

Header:

Params:

Return:

```
二进制流，客户端可解
```

## invest获取注册验证码
<a name = "invest获取注册验证码">

URL: /users/send-register-vcode

Method: POST

Tips：


Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_mobile  手机号注册则为手机号，email注册则为email

* pvcode 图形验证码，测试环境可以传111111

* register_by 注册方法 1手机号 2email

* mobile_country_code 国家区号

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "status": "true"
    }
}
```

## invest注册
<a name = "invest注册">

URL: /users/register

Method: POST

Tips：需要usercenter和tokenpark项目都开


Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_mobile  手机号

* vcode 验证码  测试环境可以传111111

* password 密码

* register_by 注册方法 1手机号 2email

* mobile_country_code 国家区号

* form_token 表单防止重复提交的随机字符串， 测试环境可以传111111


Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "status": "true",
        "user_id": "706f524adfec4eaf83650d1435b70ef0",
        "access_token": "710564f1592941a8d9f5ec4eaf83650d1435b70ef0b0283f2a82e84e0ea140a04082210647",
        "access_token_expire_time": "2018-11-12 12:04:55",
        "refresh_token": "710564f1592941a8d9f5ec4eaf83650d1435b70ef0481895cbcc9e479abd697a821b961b31",
        "refresh_token_expire_time": "2018-11-13 11:04:55"
    }
}
```

## invest获取登陆salt
<a name = "invest获取登陆salt">

URL: /users/get-login-salt

Method: POST

Tips：


Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_name  手机号注册则为手机号，email注册则为email

* client_public_key 客户端公钥

* register_by 注册方法 1手机号 2email

* mobile_country_code 国家区号

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "server_public_key": "-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAEa/fHyxwSNWDNHeQ27jcJ/j/W2CTy3dYo\n3xDqHlGnmUieo9CoLRMDf/YM8JmPHcgEHpxqc9Wsgie7JzLI0vtpBoHQzyYnwZAF\nsWLzjeq6604VyvlQJDgr5CSoYaQ9jqsl\n-----END PUBLIC KEY-----\n",
        "user_name": "前台用户2",
        "bcrypt_salt": "$2a$12$vdIbUYOZIc8BHi1cXuFtge",
        "nonce": "d74d91156be83c04eb68a1ba",
        "time_stamp": "1541998258"
    }
}
```

## invest登陆
<a name = "invest登陆">

URL: /users/login

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* password 密码 测试环境可以传111111

* register_by 注册方法 1手机号 2email 9 用户名登陆

* mobile_country_code 国家区号

* form_token 表单防止重复提交的随机字符串， 测试环境可以传111111

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "access_token": "710564f2502041a1d8f7ec4eaf83650d1435b70ef01bcfe3d2083f4ff8925fc66dc39e3710",
        "access_token_expire_time": "2018-11-12 14:39:47",
        "refresh_token": "710564f2502041a1d8f7ec4eaf83650d1435b70ef0d769df758ba34086bd2c72b2f95cf066",
        "refresh_token_expire_time": "2018-11-13 13:39:47",
        "user_id": "706f524adfec4eaf83650d1435b70ef0"
    }
}
```

## invest手机号验证码登陆获取图形验证码
<a name = "invest手机号验证码登陆获取图形验证码">

URL: /users/send-login-picture-vcode

Method: POST

Tips：

Header:

Params:

Return:

```
二进制流，客户端可解
```

## invest手机号验证码登陆获取验证码
<a name = "invest手机号验证码登陆获取验证码">

URL: /users/send-login-vcode

Method: POST

Tips：


Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* pvcode 图形验证码，测试环境可以传111111

* mobile_country_code 国家区号

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "status": "true"
    }
}
```

## invest手机号验证码登陆
<a name = "invest手机号验证码登陆">

URL: /users/login-by-mobile

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* vcode 验证码 测试环境可以传111111

* mobile_country_code 国家区号

* form_token 表单防止重复提交的随机字符串， 测试环境可以传111111

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "access_token": "710564f2502041a1d8f7ec4eaf83650d1435b70ef01bcfe3d2083f4ff8925fc66dc39e3710",
        "access_token_expire_time": "2018-11-12 14:39:47",
        "refresh_token": "710564f2502041a1d8f7ec4eaf83650d1435b70ef0d769df758ba34086bd2c72b2f95cf066",
        "refresh_token_expire_time": "2018-11-13 13:39:47",
        "user_id": "706f524adfec4eaf83650d1435b70ef0"
    }
}
```

## invest刷新accesstoken
<a name = "invest刷新accesstoken">

URL: /users/refresh-token

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id 用户id

* refresh_token refresh_token

* form_token 表单防止重复提交的随机字符串， 测试环境可以传111111

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "access_token": "a145d4d1b7a218023997144a60bb85ebebf789a5bf33a19c975bbf4896b26ebd5a21ac7ecd",
        "access_token_expire_time": "2018-11-16 09:51:37"
    }
}
```

## invest获取支付密码加密salt
<a name = "invest获取支付密码加密salt">

URL: /users/get-pay-salt

Method: POST

Tips：需要usercenter和tokenpark项目都开

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id 用户id

* access_token access_token

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "bcrypt_salt": "$2a$12$npqb2yp0iOcGUJCJBZazgu"
    }
}
```

## invest发送设置支付密码图形验证码
<a name = "invest发送设置支付密码图形验证码">

URL: /users/send-set-pay-password-picture-vcode

Method: POST

Tips：

Header:

Params:

Return:

```
二进制流，客户端可解
```

## invest发送设置支付密码的验证码
<a name = "invest发送设置支付密码的验证码">

URL: /users/send-set-pay-pd-vcode

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id 用户id

* register_by 注册方法 5手机号 6email

* access_token access_token

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "status": "true"
    }
}
```

## invest设置支付密码
<a name = "invest设置支付密码">

URL: /users/set-pay-password

Method: POST

Tips：需要usercenter和tokenpark项目都开

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id  用户id

* pay_password 支付salt加密的用户支付密码

* login_password 登陆salt加密的用户支付密码，用以校验支付密码与加密密码是否一致，产品要求支付密码和加密密码不能一致

* vcode 验证码

* register_by 注册方法 5手机号 6email

* form_token 表单防止重复提交的随机字符串， 测试环境可以传111111

* access_token access_token

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "status": "true"
    }
}
```

## invest发送重置支付密码图形验证码
<a name = "invest发送重置支付密码图形验证码">

URL: /users/send-reset-pay-password-picture-vcode

Method: POST

Tips：

Header:

Params:

Return:

```
二进制流，客户端可解
```

## invest发送重置支付密码的验证码
<a name = "invest发送重置支付密码的验证码">

URL: /users/send-reset-pay-pd-vcode

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id 用户id

* register_by 注册方法 10手机号 11email

* access_token access_token

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "status": "true"
    }
}
```

## invest重置支付密码
<a name = "invest重置支付密码">

URL: /users/reset-pay-password

Method: POST

Tips：
1.需要usercenter和tokenpark项目都开
2.前端先根据userinfo获取用户是否有手机号，若有手机号则register_by为10，否则为11

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id  用户id

* pay_password 支付salt加密的用户支付密码

* login_password 登陆salt加密的用户支付密码，用以校验支付密码与加密密码是否一致，产品要求支付密码和加密密码不能一致

* vcode 验证码

* register_by 注册方法 10手机号 11email

* form_token 表单防止重复提交的随机字符串， 测试环境可以传111111

* access_token access_token

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "status": "true"
    }
}
```

## invest设置手机号获取图形验证码
<a name = "invest设置手机号获取图形验证码">

URL: /users/send-set-mobile-picture-vcode

Method: POST

Tips：

Header:

Params:

Return:

```
二进制流，客户端可解
```

## invest设置手机号获取证码
<a name = "invest设置手机号获取证码">

URL: /users/send-set-mobile-vcode

Method: POST

Tips：


Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id 用户id

* mobile 所设置的手机号

* pvcode 图形验证码，测试环境可以传111111

* mobile_country_code 国家区号

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "status": "true"
    }
}
```

## invest设置手机号
<a name = "invest设置手机号">

URL: /users/set-user-mobile

Method: POST

Tips：需要usercenter和tokenpark项目都开

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id  用户id

* mobile 手机号

* mobile_country_code 国家区号

* vcode 验证码

* form_token 表单防止重复提交的随机字符串， 测试环境可以传111111

* access_token access_token

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "status": "true"
    }
}
```

## invest修改email获取图形验证码
<a name = "invest修改email获取图形验证码">

URL: /users/send-set-email-picture-vcode

Method: POST

Tips：

Header:

Params:

Return:

```
二进制流，客户端可解
```

## invest修改email获取证码
<a name = "invest修改email获取证码">

URL: /users/send-set-email-vcode

Method: POST

Tips：


Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id 用户id

* email email

* pvcode 图形验证码，测试环境可以传111111

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "status": "true"
    }
}
```

## invest修改email
<a name = "invest修改email">

URL: /users/set-email

Method: POST

Tips：需要usercenter和tokenpark项目都开

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id  用户id

* email 邮箱

* vcode 验证码

* form_token 表单防止重复提交的随机字符串， 测试环境可以传111111

* access_token access_token

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "status": "true"
    }
}
```

## invest修改昵称
<a name = "invest修改昵称">

URL: /users/set-email

Method: POST

Tips：需要usercenter和tokenpark项目都开

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id  用户id

* nick_name 昵称

* form_token 表单防止重复提交的随机字符串， 测试环境可以传111111

* access_token access_token

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "status": "true"
    }
}
```

## invest修改头像
<a name = "invest修改头像">

URL: /users/set-email

Method: POST

Tips：需要usercenter和tokenpark项目都开

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id  用户id

* avatar 头像地址

* form_token 表单防止重复提交的随机字符串， 测试环境可以传111111

* access_token access_token

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "status": "true"
    }
}
```

## invest用户信息
<a name = "invest用户信息">

URL: /users/user-info

Method: POST

Tips：需要usercenter和tokenpark项目都开

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id  用户id

* access_token access_token

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "user_id": "706f524adfec4eaf83650d1435b70ef0",
        "user_mobile": "13366071990",
        "option1": "",
        "email": "444@qq.com",
        "password": "******",
        "nick_name": "前台用户1",
        "score": 10000,
        "account": {
            "BTC": {
                "coin_id": "1",
                "coin_name": "BTC",
                "coin_des": "比特币",
                "total_recharge": "0.000000000000000000",  # 总充值
                "total_withdraw": "3.000000000000000000",  # 总提现
                "total_withdraw_fee": "0.000000000000000000",  #总提现fee
                "balance": "2.000000000000000000",  # 余额
                "frozon_amount": "0.000000000000000000",  # 冻结金额
                "investment_amount": "0.000000000000000000"  # 下注金额
            }
        },
        "transaction_password": "",  # 未设置支付密码则此项为空，否则为 ******
        "avatar": "",  # 头像url
        "user_name": "前台用户1"
    }
}
```

## invest未登陆状态下获取重置登陆密码的图形验证码
<a name = "invest获invest未登陆状态下获取重置登陆密码的图形验证码取注册图形验证码">

URL: /users/send-resetpwd-picture-vcode

Method: POST

Tips：

Header:

Params:

Return:

```
二进制流，客户端可解
```

## invest未登陆状态下获取重置登陆密码的验证码
<a name = "invest未登陆状态下获取重置登陆密码的验证码">

URL: /users/send-resetpwd-vcode

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* pvcode 图形验证码

* register_by 注册方法 7手机号 8email

* mobile_country_code 国家区号

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "status": "true"
    }
}
```

## invest未登陆状态下重置登陆密码
<a name = "invest未登陆状态下重置登陆密码">

URL: /users/reset-login-password

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* vcode 验证码

* register_by 注册方法 7手机号 8email

* mobile_country_code 国家区号

* password 新密码

* form_token 表单防止重复提交的随机字符串， 测试环境可以传111111

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "status": "true"
    }
}
```

## invest登陆状态下修改登陆密码
<a name = "invest登陆状态下修改登陆密码">

URL: /users/change-login-password

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id 用户id

* old_password 旧密码

* new_password 新密码

* form_token 表单防止重复提交的随机字符串， 测试环境可以传111111

* access_token access_token

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "status": "true"
    }
}
```

## invest登陆状态下获取密码盐
<a name = "invest登陆状态下获取密码盐">

URL: /users/get-change-login-password-salt

Method: POST

Tips：登陆状态，故而采用用户登陆后生成的 key和nonce加密

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* access_token access_token

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "bcrypt_salt": "123"
    }
}
```

## invest非登陆状态下获取密码盐
<a name = "invest非登陆状态下获取密码盐">

URL: /users/get-change-unlogin-password-salt

Method: POST

Tips：非登陆状态，故而采用默认的 key和nonce加密

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* register_by 用户名类型 1手机号 2email

* mobile_country_code 国家区号

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "bcrypt_salt": "123"
    }
}
```


# admin_user

## admin登陆
<a name = "admin登陆">

URL: /bg/users/login

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* password 密码 测试环境可以传111111

* level 最高权限管理员为9999，普通管理员为0

* form_token 表单防止重复提交的随机字符串， 测试环境可以传111111

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "access_token": "a145c43220711288c897004b56873731c86520e7e3cc404fc8a14c4885b72d3ce53655f5b4",
        "access_token_expire_time": "2018-11-12 17:54:47",
        "refresh_token": "a145c43220711288c897004b56873731c86520e7e302f524687784452ab696e730ac47432f",
        "refresh_token_expire_time": "2018-11-13 16:54:47",
        "user_id": "a4c32718c9004b56873731c86520e7e3"
    }
}
```

## admin获取登陆salt
<a name = "admin获取登陆salt">

URL: /bg/users/get-login-salt

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* client_public_key 客户端公钥

* level 最高权限管理员为9999，普通管理员为0

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "server_public_key": "-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAEa/fHyxwSNWDNHeQ27jcJ/j/W2CTy3dYo\n3xDqHlGnmUieo9CoLRMDf/YM8JmPHcgEHpxqc9Wsgie7JzLI0vtpBoHQzyYnwZAF\nsWLzjeq6604VyvlQJDgr5CSoYaQ9jqsl\n-----END PUBLIC KEY-----\n",
        "user_name": "前台用户2",
        "bcrypt_salt": "$2a$12$vdIbUYOZIc8BHi1cXuFtge",
        "nonce": "d74d91156be83c04eb68a1ba",
        "time_stamp": "1541998258"
    }
}
```

## admin刷新accesstoken
<a name = "admin刷新accesstoken">

URL: /users/refresh-token

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id 用户id

* refresh_token refresh_token

* form_token 表单防止重复提交的随机字符串， 测试环境可以传111111

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "access_token": "a145d4d1b7a218023997144a60bb85ebebf789a5bf33a19c975bbf4896b26ebd5a21ac7ecd",
        "access_token_expire_time": "2018-11-16 09:51:37"
    }
}
```

## admin用户信息
<a name = "admin用户信息">

URL: /users/user-info

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id  用户id

* level 最高权限管理员为9999，普通管理员为0

* access_token access_token

Return:
仅展示解析后的数据形态

```
{
    "user_id": "a4c32718c9004b56873731c86520e7e3",
    "user_name": "管理员1",
    "level": 9999,
    "rights_list": [
        {
            "module_name": "用户管理",
            "module_id": "1",
            "rights_id_list": "[1]"
        },
        {
            "module_name": "运营管理",
            "module_id": "3",
            "rights_id_list": "[1]"
        }
    ]
}
```

## 后台高权限用户获取所有的模块
<a name = "后台高权限用户获取所有的模块">

URL: /bg/users/list-right

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id  后台高级用户的用户id， 测试可用值为 a4c32718c9004b56873731c86520e7e3

* access_token access_token

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "rights_list": {
            "1": {    # 建为模块id
                "module_id": "1",
                "module_name": "用户管理",
                "sub_module_list": {}      # 为此模块下包含的子模块
            },
            "2": {
                "module_id": "2",
                "module_name": "game管理",
                "sub_module_list": {
                    "6": {
                        "module_id": "6",
                        "module_name": "发布新的game",
                        "sub_module_list": {}
                    }
                }
            },
            "3": {
                "module_id": "3",
                "module_name": "运营管理",
                "sub_module_list": {}
            },
            "4": {
                "module_id": "4",
                "module_name": "数字资产管理",
                "sub_module_list": {}
            },
            "5": {
                "module_id": "5",
                "module_name": "权限管理",
                "sub_module_list": {}
            }
        }
    }
}
```

## 后台高权限用户生成普通后台用户
<a name = "后台高权限用户生成普通后台用户">

URL: /bg/users/new-user

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id  后台高级用户的用户id， 测试可用值为 a4c32718c9004b56873731c86520e7e3

* user_name 新用户名

* password 密码

* rights_list [{'module_id': 1}, {'module_id': 2}] 给哪个模块增加权限

* access_token access_token

* form_token 表单防止重复提交的随机字符串， 测试环境可以传111111

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "user_name": "管理员3"
    }
}
```

## 后台高权限用户删除普通后台用户
<a name = "后台高权限用户删除普通后台用户">

URL: /bg/users/delete-user

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id  后台高级用户的用户id， 测试可用值为 a4c32718c9004b56873731c86520e7e3

* user_name 被操作的用户的用户名

* access_token access_token

* form_token 表单防止重复提交的随机字符串， 测试环境可以传111111

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "user_name": "管理员3"
    }
}
```

## 后台高权限用户获取普通后台用户
<a name = "后台高权限用户获取普通后台用户">

URL: /bg/users/list-user-right

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id  后台高级用户的用户id， 测试可用值为 a4c32718c9004b56873731c86520e7e3

* user_name 被操作的用户的用户名

* access_token access_token

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "user_name": "管理员3",
        "rights_list": [
            {
                "module_name": "用户管理",
                "module_id": "1",
                "rights_id_list": "[1]"
            },
            {
                "module_name": "game管理",
                "module_id": "2",
                "rights_id_list": "[1]"
            }
        ]
    }
}
```

## 后台高权限用户修改普通后台用户
<a name = "后台高权限用户修改普通后台用户">

URL: /bg/users/change-user-right

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id  后台高级用户的用户id， 测试可用值为 a4c32718c9004b56873731c86520e7e3

* user_name 被操作的后台用户的用户名

* password 密码 若只修改权限则随便传个字符串就行，否则传用户手输的密码即可

* rights_list [{'module_id': 1}, {'module_id': 2}] 给哪个模块增加权限

* change_type 修改类型，0所有，1权限，2密码

* access_token access_token

* form_token 表单防止重复提交的随机字符串， 测试环境可以传111111

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "user_name": "管理员3"
    }
}
```