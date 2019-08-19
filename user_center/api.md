# 时间
[获取服务的时间](#获取服务的时间)

# admin_user
[获取注册salt](#admin获取注册salt)

[获取登录salt](#admin获取登录salt)

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

## admin获取注册salt

<a name = "admin获取注册salt">

URL: /bg/users/get-register-salt

Method: POST

Params:

* user_name  用户名

* client_public_key 客户端公钥

Return:

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "server_public_key": server_public_key_pem,
        "user_name": user_name,
        "bcrypt_salt": bcrypt_salt,
        "nonce": nonce,
        "time_stamp": str(int(time.time()))
    }
}
```

<a name = "admin获取登录salt">

## admin获取登录salt

URL: /bg/users/get-login-salt

Method: POST

Params:

* User-Mobile  用户名(base64加密后放入header)

* user_name  用户名

* client_public_key 客户端公钥

Return:

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "server_public_key": server_public_key_pem,
        "user_name": user_name,
        "bcrypt_salt": bcrypt_salt,
        "nonce": nonce,
        "time_stamp": str(int(time.time()))
    }
}
```

# invest_user
[注册salt](#invest注册)

<a name = "invest注册">

## invest注册

URL: /users/register

Method: POST

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_mobile  手机号

* vcode 验证码

* password 密码

* register_by 注册方法 1手机号 2email

* user_name 用户名

* mobile_country_code 国家区号

* form_token 表单防止重复提交的随机字符串


Return:
# 仅展示解析后的数据形态

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

