[充值申请](#invest充值申请)

[提现申请](#invest提现申请)

[账户列表](#invest账户列表)

[后台用户流水](#admin后台用户流水)

[后台用户列表](#admin后台用户列表)

[后台用户资产列表](#admin后台用户资产列表)

[后台用户资产详情](#admin后台用户资产详情)

[后台提现相关](#admin后台提现相关)

[后台归集相关](#admin后台归集相关)

## admin后台用户列表
<a name = "admin后台用户列表">

URL: /bg/users/users/list

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* search_user_id 查询用户id

* user_name 查询用户名称

* email 查询 email

* user_mobile 查询用户手机号码

* register_time_start 查询注册开始时间

* register_time_end 查询注册结束时间

* source 信息来源 ['1'  # pc '2'  # wap '3'  # iphone '4'  # android]

* recharge_time_start 查询首充开始时间

* recharge_time_end 查询首充结束时间

Return:
仅展示解析后的数据形态

```
{
  "code": "00000",
  "desc": "success",
  "msg": "成功",
  "data": {
    "limit": 10,
    "offset": 1,
    "count": "1",
    "content": [
      {
        "id": 1,
        "user_mobile": "15600697337",
        "user_name": "15600697337",
        "email": "",
        "nick_name": "张维",
        "create_at": "2018-11-13 09:37:58",
        "source": "pc",
        "first_recharge_at": "2018-11-13 17:09:25"
      }
    ]
  }
}
```

## admin后台用户资产列表
<a name = "admin后台用户资产列表">

URL: /bg/users/users/tokens

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* search_user_id 查询用户id

* user_name 查询用户名称

* recharge_time_start 查询首充开始时间

* recharge_time_end 查询首充结束时间

Return:
仅展示解析后的数据形态

```
{
  "code": "00000",
  "desc": "success",
  "msg": "成功",
  "data": {
    "limit": 10,
    "offset": 1,
    "count": "1",
    "content": [
        {
            "user_mobile": "15600697337",
            "email": "",
            "user_name": "张维",
            "user_id": "7507a61d22f64ae29b9ce36585bcc289",
            "first_recharge_at": "2018-11-13 17:09:25",
            "USDT": 0,
            "ETH": "4.45830271",
            "BTC": "3.66238101"
        }
    ]
  }
}
```

## admin后台用户资产详情
<a name = "admin后台用户资产详情">

URL: /bg/users/users/tokens/detail

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* check_user_id  测试可用值为 7507a61d22f64ae29b9ce36585bcc289

Return:
仅展示解析后的数据形态

```
{
  "code": "00000",
  "desc": "success",
  "msg": "成功",
  "data": {
    "user_info": {
      "user_id": "7507a61d22f64ae29b9ce36585bcc289",
      "user_mobile": "15600697337",
      "email": "",
      "created_at": "2018-11-13 09:37:58",
      "source": "pc"
    },
    "token_info": [
      {
        "token_name": "error",
        "balance": 5.1767,
        "create_at": "2018-11-13 09:42:29",
        "address": ""
      }
    ]
  }
}
```

## invest充值申请
<a name = "invest充值申请">

URL: /users/recharge_apply

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id  测试可用值为 a4c32718c9004b56873731c86520e7e3

* coin_id 币种

* do_reset 是否重置地址

* access_token access_token

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "token_address": "123456",
        "coin_name": "BTC",
        "coin_id": "1",
        "balance": "6.637500"
    }
}
```

## invest提现申请
<a name = "invest提现申请">

URL: /users/withdraw_apply

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id  测试可用值为 a4c32718c9004b56873731c86520e7e3

* coin_id 币种

* pay_password 支付密码，测试环境111111必过

* withdraw_amount 提现金额

* withdraw_fee 提现fee

* withdraw_address 提现地址

* source 渠道

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
        "token_address": "fdafadfad",
        "coin_name": "BTC",
        "coin_id": "1",
        "balance": "8.658000"
    }
}
```

## invest账户列表
<a name = "invest账户列表">

URL: /users/account_water

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* user_id  测试可用值为 a4c32718c9004b56873731c86520e7e3

* change_type 流水类型，不区分类型则不传 1:充值 2:提现中 3:下注 4:提现完成 5:赢币 6:提现失败 7:提现完成 999：所有提现（包括提现中、提现完成、提现失败）998: 所有提现完成(包含4和7)

* start_id 开始查询id(比如用户做上划操作时，需要传入这个字段，以保证新信息与之前信息不重复)

* offset 所查询的页

* limit 每页信息条数

* access_token access_token

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "limit": "3",   # 当前页最大信息条数
        "offset": 1,  # 当前所在页
        "count": "3",  # 总页数
        "content": [
            {
                "id": 9,  # 本条记录id
                "token_id": "1",  #币种id
                "change_amount": "0.100000",  # 变化金额，注意提现的时候这个字段也是正值，客户端需要加负号
                "change_type": 6, # 变化类型
                "created_at": "2018-11-13 15:36:11", # 时间
                "change_fee": "0.010000",  # 变化费，比如提现会有手续费
                "token_name": "BTC",  # 币种名称
                "token_address": "123123" # 对于充值，则是打入token的地址，对于提现则是提出token的地址, 对于游戏则是期号
            },
            {
                "id": 8,
                "token_id": "1",
                "change_amount": "0.100000",
                "change_type": 4,
                "created_at": "2018-11-13 15:34:21",
                "change_fee": "0.010000",
                "token_name": "BTC",
                "token_address": "123123"
            },
            {
                "id": 4,
                "token_id": "1",
                "change_amount": "0.100000",
                "change_type": 4,
                "created_at": "2018-11-13 15:06:33",
                "change_fee": "0.010000",
                "token_name": "BTC",
                "token_address": "123123"
            }
        ]
    }
}
```

## admin后台用户流水
<a name = "admin后台用户流水">

URL: /bg/users/users/account_water

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* search_user_id  测试可用值为 a4c32718c9004b56873731c86520e7e3

* user_name  用户名

* change_type 流水类型，不区分类型则不传 1:充值 2:提现中 3:下注 4:提现完成 5:赢币 6:提现失败 7:提现完成 999：所有提现（包括提现中、提现完成、提现失败）998: 所有提现完成(包含4和7)

* offset 所查询的页

* limit 每页信息条数

* token_id 币种id

* water_id 流水号

* finish_time_start 入账时间起始

* finish_time_start 入账时间截止

* access_token access_token

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "limit": "1",   # 当前页最大信息条数
        "offset": 1,  # 当前所在页
        "count": "50",  # 总页数
        "content": [
            {
                "change_type": 3,  # 变化类型
                "id": 51,  # 本条记录id
                "water_id": "20181114160138181054661360369286",  # 流水号
                "user_id": "7507a61d22f64ae29b9ce36585bcc289",  # 用户id
                "user_name": "张维",  # 用户名
                "token_id": "1",  # 币种id
                "token_name": "BTC",  #币种
                "change_amount": "0.004400",  # 变化金额，注意提现的时候这个字段也是正值，客户端需要加负号
                "change_fee": "0.000000",  # 变化费，比如提现会有手续费
                "change_number": 1,  # 变化量，如下注的注数
                "begin_time": "2018-11-14 16:01:38", # 开始时间
                "finish_time": "2018-11-14 16:01:38", # 结束时间
                "address": "",  # 收款地址、下注的期号
            }
        ]
    }
}
```


韩梦--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## game实例列表

URL: /bg/users/game/game_instance_list

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* game_title  夺宝标题

* game_serial 期号

* release_time_start 发布时间起始

* release_time_end 发布时间结束

* full_load_time_start 满额时间起始

* full_load_time_end 满额时间结束

* status 状态 0:夺宝中 1:待揭晓 2:已完成

* release_type 发布方式 0:手动  1:自动

* offset 所查询的页

* limit 每页信息条数

* start_id 查询起始id

Return:
仅展示解析后的数据形态

```
{
  "code": "00000",
  "desc": "success",
  "msg": "成功",
  "data": {
    "limit": 10,
    "offset": "0",
    "count": "1",
    "content": [
      {
        "id": 7,
        "game_serial": "Test1811130060", # 期号
        "game_title": "BTCtest",  # 模板名称
        "bet_unit": 1,    # 投注单位
        "bet_token": "2", # 投注币种  1:BTC 2:USDT 3:ETH
        "reward_quantity": 2, # 奖励数量
        "reward_token": "1", # 奖励币种  1:BTC 2:USDT 3:ETH
        "release_time": "2018-11-13 16:55:00",  # 发布时间
        "status": 2,  # 实例状态 0:夺宝中 1:待揭晓 2:已完成
        "need": 2,   # 总需数
        "full_load_time": "2018-11-14 11:57:19", # 满标时间
        "lottery_time": "2018-11-14 11:57:19",  # 开奖时间
        "release_type": 0,  # 发布方式  0：手动   1：自动
        "participation": 1  # 参与人数
      },
      {
        "id": 10,
        "game_serial": "Test1811140011",
        "game_title": "BTCtest",
        "bet_unit": 1,
        "bet_token": "2",
        "reward_quantity": 2,
        "reward_token": "1",
        "release_time": "0000-00-00 00:00:00",
        "status": 2,
        "need": 150,
        "full_load_time": "2018-11-14 17:20:54",
        "lottery_time": "2018-11-14 17:20:54",
        "release_type": 1,
        "participation": 2
      }
    ],
    "total": 2
  }
}
```

## game模板标题列表

URL: /bg/users/game/game_template_name_list

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:
  无

Return:
仅展示解析后的数据形态

```
{
  "code": "00000",
  "desc": "success",
  "msg": "成功",
  "data": [
      {
        "id": 1,    # game模板id
        "name": "BTCtest" game模板名称
      }
  ]
}
```

## 用户参与列表

URL: /users/game/game_participate_in_list

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* offset 所查询的页

* limit 每页信息条数

Return:
仅展示解析后的数据形态

```
{
  "code": "00000",
  "desc": "success",
  "msg": "成功",
  "data": {
    "limit": "5",
    "offset": "0",
    "count": "1",
    "content": [
      {
        "user": "张维",  # 用户昵称
        "bet_time": "2018-11-14 17:20:34",  # 投注时间
        "channel": "4",   # 投注渠道
        "bet_token": 2,   # 投注币种  1:BTC 2:USDT 3:ETH
        "bet_number": 100, # 投注数量
        "pay_token": 1,   # 支付币种
        "pay_number": "0.015400000000000000"  # 支付数量
      },
      {
        "user": "张维",
        "bet_time": "2018-11-14 17:20:34",
        "channel": "4",
        "bet_token": 2,
        "bet_number": 100,
        "pay_token": 1,
        "pay_number": "0.015400000000000000"
      }
    ],
    "total": 2
  }
}
```

## 后台管理用户参与列表

URL: /bg/users/game/manage_participate_in

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:  全为可选参数

* offset 所查询的页

* limit 每页信息条数

* game_title  夺宝标题

* game_serial  期号

* part_in_time_start  参与起始时间

* part_in_time_end  参与终止时间

* channel  参与渠道

* bet_token  投入币种

* user_name  用户名

* start_id  记录起始id


Return:
仅展示解析后的数据形态

```
{
  "code": "00000",
  "desc": "success",
  "msg": "成功",
  "data": {
    "limit": 10,
    "offset": "0",
    "count": "3",
    "content": [
      {
        "id": 249,    # 流水号
        "game_serial": "RRTT0014", # 期号
        "game_title": "",  # 夺宝标题
        "user": "50796196@qq.com",  # 用户名
        "bet_time": "2018-12-02 17:21:12",  # 参与时间
        "channel": "1",  # 参与渠道  pc:1    wap:2   ios:3   android:4
        "release_type": 0,  # 发布方式  0:手动  1:自动
        "bet_number": 1,  # 参与注数
        "pay_token": 60,  # 支付币种
        "pay_number": "0.004600000000000000"  # 支付数量
      },
      {
        "id": 248,
        "game_serial": "RRTT0014",
        "game_title": "",
        "user": "50796196@qq.com",
        "bet_time": "2018-12-01 01:55:01",
        "channel": "1",
        "release_type": 0,
        "bet_number": 10,
        "pay_token": 60,
        "pay_number": "0.046900000000000000"
      }
    ],
    "total": 24
  }
}
```



## game实例详情(包括模板详情、中奖详情)

URL: /bg/users/game/current_period_info

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* instance_id  game实例id

Return:
仅展示解析后的数据形态

```
{
  "code": "00000",
  "desc": "success",
  "msg": "成功",
  "data": {
    "template_info": {
      "game_title": "BTCtest",   # 夺宝标题
      "created_at": "2018-11-13 16:12:39", # 创建时间
      "update_at": "2018-11-13 16:12:39",  # 最新修改时间
      "bet_token": 2,  # 投注币种  1:BTC 2:USDT 3:ETH
      "reward_token": 1, # 奖励币种  1:BTC 2:USDT 3:ETH
      "bet_unit": 1,  # 投注单位(定义多少个投注币种为一注)
      "reward_quantity": 2, # 奖励数量
      "support_token": 0,  # 支持币种 0:全部 1:BTC 2:USDT 3:ETH
      "need": "1~100000",  # 单价范围
      "phase": "TestYYMMDD0001",  # 期数命名
      "template_status": 1,  # 模板状态  0：停用  1：启用
      "auto_release": 1,     # 是否自动发布  0：否   1：是
      "handling_fee": "0.50",  # 获奖手续费
      "exceeded_ratio": "10",  # 超募比例
      "agreement": "协议",     # 协议文档地址
      "game_describe": "测试下看看会崩不"  # 规则描述
    },
    "instance_info": {
      "game_serial": "Test1811140011",  # 期号
      "release_time": "0000-00-00 00:00:00", # 发布时间
      "full_load_time": "2018-11-14 17:20:54",  # 满额时间
      "release_type": 1,  # 发布方式 0：手动   1：自动
      "need": 150,    # 总需额
      "lottery_time": "2018-11-14 17:20:54",  # 开奖时间
      "bet_serial": "79",  # 中奖号
      "user_name": "张维"  # 中奖人
    }
  }
}
```

## 获取手动发布game信息

URL: /bg/users/game/manual_release_info

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* template_id  game模板id

Return:
仅展示解析后的数据形态

```
{
  "template_info": {
    "game_title": "BTCtest",   # 模板名称
    "created_at": "2018-11-13 16:12:39",  # 创建时间
    "update_at": "2018-11-13 16:12:39",  # 最新修改时间
    "bet_token": 2,  # 投注币种   1:BTC 2:USDT 3:ETH
    "bet_unit": 1,   # 投注单位
    "reward_quantity": 2,  # 奖励数量
    "support_token": 0,   # 支持币种 0:全部 1:BTC 2:USDT 3:ETH
    "need": "1~100000",   # 单价范围
    "phase": "TestYYMMDD0001",  # 期数命名
    "template_status": 1,   # 模板状态
    "auto_release": 1,      # 是否自动发布
    "handling_fee": "0.50",  # 获奖手续费
    "exceeded_ratio": "10",  # 超募比例
    "agreement": "协议",     # 协议文档地址
    "game_describe": "测试下看看会崩不"  # 规则描述
  },
  "game_serial": "Test1811150001"  # 期号
}
```

## 手动发布game信息

URL: /bg/users/game/manual_release

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* template_id  game模板id

* game_serial  期号

* need  总需数

* game_describe  game描述

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

## 最新一期开奖信息

URL: /users/game/get_winning_record

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:
 无

Return:
仅展示解析后的数据形态

```
{
  "code": "00000",
  "desc": "success",
  "msg": "成功",
  "data": {
    "game_serial": "Test1811130060",   # 期号
    "winning_user": "张维",        #中奖人
    "lottery_time": "2018-11-14 11:57:19",  # 开奖时间
    "participation": 1,   # 参与人数
    "lottery_usdt": "0.00",   # 开奖时usdt价格
    "lottery_reward": "0.00"  # 开奖时奖励币种参考价格
  }
}
```

## 英雄榜

URL: /users/game/hero_list

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:
 无

Return:
仅展示解析后的数据形态

```
{
  "code": "00000",
  "desc": "success",
  "msg": "成功",
  "data": [
    {
      "user_name": "张维",  # 用户名
      "total_reward": "2"  # 获奖BTC个数
    }
  ]
}
```

## 发表评论

URL: /users/social/add_comment

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

* content  评论内容

* submit_image  上传图片地址  (可选)

* submit_thumbnail  上传图片缩略图地址  (可选)

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

## 点赞

URL: /users/social/add_praise

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

* comment_id  评论id

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

## 取消点赞

URL: /users/social/remove_praise

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

* comment_id  评论id

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

## 评论列表

URL: /users/social/get_comment_list

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

Return:
仅展示解析后的数据形态

```
{
  "code": "00000",
  "desc": "success",
  "msg": "成功",
  "data": {
    "limit": 10,
    "offset": "0",
    "count": "1",
    "content": [
      {
        "user": "张维",  # 用户名
        "submit_content": "asdadajld12112",    # 评论内容
        "submit_image": "",                    # 评论配图
        "submit_thumbnail": "",                # 评论缩略图
        "praise_number": 0,                    # 点赞人数
        "is_praise": 0,                        # 是否给此评论点过赞  0:没有  1:有
        "status": 1                            # 评论是否展示  0：隐藏  1：显示
      },
      {
        "user": "张维",
        "submit_content": "sadqqdw得2331231",
        "submit_image": "",
        "submit_thumbnail": "",
        "praise_number": 0,
        "is_praise": 0,
        "status": 1
      }
    ],
    "total": 2
  }
}
```

## 我的评论列表

URL: /users/social/get_mine_comment_list

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

Return:
仅展示解析后的数据形态

```
{
  "code": "00000",
  "desc": "success",
  "msg": "成功",
  "data": {
    "limit": 10,
    "offset": "0",
    "count": "1",
    "content": [
      {
        "user": "张维",  # 用户名
        "submit_content": "asdadajld12112",    # 评论内容
        "submit_image": "",                    # 评论配图
        "praise_number": 0,                    # 点赞人数
        "is_praise": 0                         # 是否给此评论点过赞  0:没有  1:有
      },
      {
        "user": "张维",
        "submit_content": "sadqqdw得2331231",
        "submit_image": "",
        "praise_number": 0,
        "is_praise": 0
      }
    ],
    "total": 2
  }
}
```

## 获取实时币价

URL: /bg/users/game/get_current_price

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

无

Return:
仅展示解析后的数据形态

```
{
  "code": "00000",
  "desc": "success",
  "msg": "成功",
  "data": {
    'eth': 1.0044,
    'btc': 102.4562
  }
}
```

## 首页接口

URL: /common/main/main_page

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

无

Return:
仅展示解析后的数据形态

```
{
  "code": "00000",
  "desc": "success",
  "msg": "成功",
  "data": {
        'banner_list': banners,
        'announcement_list': announcements,
        'instance': {
            'id': instance._id,
            'game_serial': instance.game_serial,
            'game_title': instance.game_title,
            'game_describe': instance.game_describe,
            'progress': progress,
            'remain': int(instance.need - instance.bet_number),
            'status': instance.status,
            'lottery_time': str(instance.lottery_time),
            'winners': winner,
            'bet_serial': bet_serial,
            'bet_token': self.get_coin_name(instance.bet_token),
            'merge_id': merge_id
        },
        'participate': participates
  }
}
```

## 本期合买列表

URL: /common/game/merge_participate_in_list

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* offset 所查询的页

* limit 每页信息条数

* instance_id 实例id

* start_id  记录起始id

Return:
仅展示解析后的数据形态

```
{
  "code": "00000",
  "desc": "success",
  "msg": "成功",
  "data": {
    "limit": 10,
    "offset": "0",
    "count": "1",
    "content": [
      {
        "id": 2,
        "initiate_user": "爸爸",   # 发起人名字
        "participation": 4,       # 参与人数
        "bet_number_total": 13,   # 投注额度
        "bet_token": 100000000,   # 投注币种
        "bet_unit": 1             # 投注单位
      },
      {
        "id": 1,
        "initiate_user": "爸爸",
        "participation": 3,
        "bet_number_total": 12,
        "bet_token": 100000000,
        "bet_unit": 1
      }
    ],
    "total": 2
  }
}
```

## 发起合买

URL: /users/game/initiate_merge

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

* instance_id 实例id

* part_in_id 参与记录id

Return:
仅展示解析后的数据形态

```
{
  "code": "00000",
  "desc": "success",
  "msg": "成功",
  "data": {
    "status": true
  }
}
```

## 合买获奖信息列表

URL: /common/game/merge_info_list

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* offset 所查询的页

* limit 每页信息条数

* instance_id 实例id

* merge_id  合买记录id

Return:
仅展示解析后的数据形态

```
{
  "code": "00000",
  "desc": "success",
  "msg": "成功",
  "data": {
    "status": true
  }
}
```

## 夺宝详情

URL: /common/main/indiana_detail

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

* participate_id 参与记录id

* instance_id 实例id


Return:
仅展示解析后的数据形态

```
{
  "code": "00000",
  "desc": "success",
  "msg": "成功",
  "data": {
    "game_serial": "0011812170002",  # 期号
    "status": 2,    # 项目状态
    "need": 3591,   # 总需
    "bet_token": 100000000,  # 投注币种
    "bet_unit": 1,           # 投注单位
    "reward_token": 0,       # 奖励币种
    "reward_quantity": 1,    # 奖励数量
    "release_time": "2018-12-17 16:30:02",  # 发布时间
    "full_load_time": "2018-12-19 11:18:02",# 满额时间
    "lottery_time": "2018-12-19 11:45:02",  # 开奖时间
    "participation": 55,                    # 参与人数
    "part_in_time": "2018-12-17 17:49:37",  # 参与时间
    "bet_number": 1,                        # 投注数量
    "merge_id": -1,                         # 合买id
    "pay_token": 60,                        # 支付币种
    "pay_number": "0.011500000000000000"    # 支付数量
  }
}
```

## 夺宝详情

URL: /common/game/latest_available_instance

Method: POST

Tips：

Header:
* User-Mobile  注册登陆前为用户名，登陆后为userid，需要做base64加密

* Source  渠道

* Timestamp  Signature 的 时间戳

* Signature  Signature 的 Signature

* Nonce  Signature 的 Nonce

Params:

无

Return:
仅展示解析后的数据形态

```
{
  "code": "00000",
  "desc": "success",
  "msg": "成功",
  "data": {
    "instance_id": 86
  }
}
```
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------














张维--------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 后台 添加GAME模版
<a name = "添加GAME模版">

URL: /bg/users/game/add_model

Method: POST

Params: (传递数据均为 字符串 string即可)

* game_title => 夺宝标题

* reward_token => 奖励币种 1:BTC  2:USDT   3:ETH

* bet_token => 投注币种

* bet_unit => 投注单位 最低加注额度

* reward_quantity => 奖励数量

* need_ceiling => 总需上限

* need_floor => 总需下限

* exceeded_ratio => 超募比例

* handling_fee => 手续费

* support_token => 支持币种 0:全部   1:BTC  2:USDT   3:ETH

* template_status => 模板状态 0：停用   1：启用

* auto_release => 是否自动发布 0：否   1：是

* game_describe => 夺宝描述

* phase_prefix => 期数前缀

* agreement => 协议

* agreement_name => 协议名称

Return:

```
{
    "code": "00000",
    "desc": "success",
    "msg": "创建成功",
}
```

## 后台 查询GAME模版
<a name = "查询GAME模版">

URL: /bg/users/game/search_model

Method: POST

Params: (传递数据均为 字符串 string即可)

* id => 模版id

* game_title => 夺宝标题

* reward_quantity => 奖励数量

* release_time_start => 创建时间起点

* release_time_end => 创建时间终点

* model_type => 模版类型 数字Game 实物Game   暂无实物Game

* template_status => 模板状态 0：停用   1：启用

* auto_release => 是否自动发布 0：否   1：是

* model_type => 模版类型 1:数字Game 2:实物GAME

* limit => 一次返回条目数量 默认20条

* offset => 篇数 默认第一篇

Return:

```
{
    "data":{
            'limit': 3  # 当前返回条数
            'offset': 1 # 当前页数
            'count': 3, # 总页数
            "number_games":
                [
                    {
                        "id": 3,
                        "game_title": "BTCtest2",
                        "reward_token": 1,
                        "bet_token": 2,
                        "bet_unit": 1,
                        "reward_quantity": 2,
                        "need_ceiling": 100000,
                        "need_floor": 1,
                        "exceeded_ratio": 10,
                        "handling_fee": "0.50",
                        "support_token": 0,
                        "template_status": 0,
                        "auto_release": 1,
                        "game_describe": "测试下看看会崩不",
                        "phase_prefix": "Test",
                        "phase_date": "2018.11.13",
                        "phase_serial": "888",
                        "agreement": "协议url"
                        "agreement_name": "协议名称"
                        "created_at":"2018-10-11 10:50:12"
                        "update_at":"2018-10-11 10:50:13"
                    }
                ]
           }
}
```

## 后台 修改GAME模版
<a name = "修改GAME模版">

URL: /bg/users/game/modify_model

Method: POST

Params: (传递数据均为 字符串 string即可)

* id => 模版id

* reward_token => 奖励币种 1:BTC  2:USDT   3:ETH

* bet_token => 投注币种

* bet_unit => 投注单位 最低加注额度

* reward_quantity => 奖励数量

* need_ceiling => 总需上限

* need_floor => 总需下限

* exceeded_ratio => 超募比例

* handling_fee => 手续费

* support_token => 支持币种 0:全部   1:BTC  2:USDT   3:ETH

* template_status => 模板状态 0：停用   1：启用

* auto_release => 是否自动发布 0：否   1：是

* game_describe => 夺宝描述

* phase_prefix => 期数前缀

* phase_date => 期数日期

* phase_serial => 期数序号

* agreement => 协议

* agreement_name => 协议名称

Return:

```
{
    "code": "00000",
    "desc": "success",
    "msg": "修改成功",
}
```

## 后台 删除GAME模版
<a name = "删除GAME模版">

URL: /bg/users/game/delete_model

Method: POST

Params: (传递数据均为 字符串 string即可)

* id => 模版id

Return:

```
{
    "code": "00000",
    "desc": "success",
    "msg": "删除成功",
}
```

## 后台 更改GAME模版启用停用状态
<a name = "更改GAME模版启用停用状态">

URL: /bg/users/game/modify_model_status

Method: POST

Params: (传递数据均为 字符串 string即可)

* id => 模版id

Return:

```
{
    "code": "00000",
    "desc": "success",
    "msg": "模版状态更改成功",
}
```

## 后台 币价查询
<a name = "币价查询">

URL: /bg/users/game/exchange_rate

Method: POST

Params: (传递数据均为 int类型)

* conin_id => 币种id # 1:BTC 3:ETH

Return:

```
{
    "code": "00000",
    "desc": "success",
    "msg": "查询成功",
    "data": {
        "price": 6455.97,
        "timestamp": "1541995252",
        "from": "huobi"
    }
}
```

## 后端 开奖
<a name = "开奖">

URL: /bg/users/game/publish_the_lottery

Method: POST

Params: (传递数据均为 字符串 string即可)

* id => 项目id

Return:

```
True
```

## 前端用户操作 下注
<a name = "下注">

URL: /users/game/bet_in

Method: POST

Params: (传递数据均为 字符串 string即可)

* id => 项目id

* user_id => 用户id

* user_channel_id => 用户来源渠道id

* transaction_password => 币种id # 1:BTC 3:ETH

* conin_id => 投入币种id

* bet_amount => 交易密码

Return:

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data":{
        "numbers":[   # 投注号码
            12,
            14,
            6,
            137,
            63,
            145,
            96
        ],
        "can_merge":true   # 是否可以发起合买
    }
}
```

## 后台 选择机器人
<a name = "选择机器人">

URL: /bg/users/game/robot/select

Method: POST

Params: (传递数据均为 字符串 string即可)

* game_serial => 项目期号

* robot_number => 投入机器人数量

Return:

```
[
    {"user_id":"1000","nick_name":"韩梦"},
    {"user_id":"2000","nick_name":"张维"},
    {"user_id":"3000","nick_name":"不知道1"}
]
```

## 后台 添加手动机器人配置
<a name = "添加机器人配置">

URL: /bg/users/game/robot/add_robot_config

Method: POST

Params: (传递数据均为 字符串 string即可)

* game_id => 项目id

* game_serial => 项目期号

* robot_number => 投入机器人数量

* robots => 机器人配置 json模式 例如:[{"user_id":"1000","nick_name":"韩梦","bet_number":"1","pay_token":"3","bet_time":"2018-11-20 17:21:12"},{"user_id":"2000","nick_name":"张维","bet_number":"2","pay_token":"1","bet_time":"2018-11-20 18:21:12"},{"user_id":"3000","nick_name":"不知道1","bet_number":"1","pay_token":"3","bet_time":"2018-11-20 19:21:12"}]

* created_user_id => 后台用户id

Return:

```
{
    "code": "00000",
    "desc": "success",
    "msg": "机器人配置成功",
}
```

## 后台 查询游戏机器人配置
<a name = "查询机器人配置">

URL: /bg/users/game/robot/search_game_robot_config

Method: POST

Params: (传递数据均为 字符串 string即可)

* game_serial => 项目期号

* plan_start_time_first => 计划开始时间起点

* plan_start_time_finish => 计划开始时间终点

* plan_end_time_first => 计划结束时间起点

* plan_end_time_finish => 计划结束时间终点

* status => 状态 #0:待执行 1:进行中 2:已完成 3:自动终止 4:手动终止

* real_end_time_first => 实际结束时间起点

* real_end_time_finish => 实际结束时间终点

* robot_bet_type => 发布方式 # 0:自动 1:手动

Return:

```
{
    "limit": 10,
    "offset": 1,
    "count": "1",
    "content": [
        {
            "id": "2",
            "game_serial": "test20",
            "robot_number": "3",
            "total_bet_number": "4",
            "start_of_plan_time": "2018-11-20 16:21:12",
            "end_of_plan_time": "2018-11-20 18:21:12",
            "end_of_real_time": "0000-00-00 00:00:00",
            "completion": "暂未开发",
            "status": "0",
            "robot_bet_type": "1"
        }
    ]
}
```

## 后台 根据游戏id查询机器人配置
<a name = "根据游戏id查询机器人配置">

URL: /bg/users/game/robot/search_robot_config

Method: POST

Params: (传递数据均为 字符串 string即可)

* id => 纪录id

Return:

```
{
    "limit": 10,
    "offset": 1,
    "count": "1",
    "content": [
         {
            "user_id": "7000",
            "nick_name": "不知道5",
            "bet_number": "1",
            "pay_token": "3",
            "bet_plan_time": "2018-11-23 11:55:30",
            "bet_status": "0"
        },

    ]
}
```

## 后台 停止游戏id机器人配置
<a name = "停止游戏id机器人配置">

URL: /bg/users/game/robot/cancel_robot_config

Method: POST

Params: (传递数据均为 字符串 string即可)

* id => 游戏机器人配置纪录id

Return:

```
{
    "code": "00000",
    "desc": "success",
    "msg": "停止成功",
}
```

## 后台 机器人下注
<a name = "机器人下注">

URL: /bg/users/game/robot/bet_in

Method: POST

Params: (传递数据均为 字符串 string即可)

* id => 项目id

* user_id => 机器人用户id

* conin_id => 币种类型

* bet_amount => 下注数量

Return:

```
{
    "code": "00000",
    "desc": "success",
    "msg": "下注成功",
}
```

## 后台 创建机器人
<a name = "机器人下注">

URL: /bg/users/game/robot/creat_robot

Method: POST

Params: (传递数据均为 字符串 string即可)

* account_id => 账户id

* user_id => 机器人用户id

* score => 积分数量

* id_card => 身份证id

* nick_name => 昵称

* source => 注册渠道

* avatar => 头像地址

* user_mobile => 手机号码

* email => 邮箱

* mobile_country_code => 手机号国家区号

* user_name => 用户名

* status => 状态 0:待机 1:使用中"

Return:

```
{
    "code": "00000",
    "desc": "success",
    "msg": "创建成功",
}
```







--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## admin后台提现相关
<a name = "admin后台提现相关">

#提现列表
URL: /bg/users/withdraw/list

Method: POST

Tips：提现申请列表、提现处理列表、提现已完成列表

Header:


Params:

* coin_id 币种

* withdraw_type 提现类型: 0-用户提现, 1-用户中奖, 2-归集, 3-归集转归集

* withdraw_status 提现状态: 0-未交易, 1-提现中, 2-提现成功, 3-提现失败, 4-交易失败, 5-提现拒绝(审核拒绝)

* audit_status 审核状态: 0-待审核, 1-审核通过, 2-审核拒绝

* source_status 来源: 0-线上, 1-线下

* user_name: 用户名

* withdraw_number: 最小提现数量

* apply_time_start: 申请时间start

* apply_time_end: 申请时间end

* from_address: 出账地址

* transfer_time_start: 转账时间start

* transfer_time_end: 转账时间end

* offset 所查询的页

* limit 每页信息条数

* page_flag

* 说明：
* 1、“提现申请列表”简称页面1，“提现处理列表”简称页面2，“提现已完成列表”简称页面3
* 2、页面1固定传参page_flag=1,其他参数以原型图为准,默认传空字符串
* 3、页面2固定传参page_flag=2,其他参数以原型图为准,默认传空字符串
* 4、页面3固定传参page_flag=3,其他参数以原型图为准,默认传空字符串

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "count": "2",
        "list": [
            {
                "order_no": "20181120150001556077548280099510",
                "coin_id": "0",#币种id
                "withdraw_address": "0x7a3b68377E44a20992713bda5236baF33B92Eb8f",#提现地址
                "withdraw_amount": "1.00000000000000000",#提现数量
                "withdraw_fee": "1.00000000000000000",#手续费
                "audit_status": "2",#审核状态
                "withdraw_status": "2",#提现状态
                "user_name": "反反复复",#用户名
                "apply_time": "2018-11-20 15:00:02",#申请时间
                "transfer_time": "2018-11-20 15:00:02",#转账时间
                "confirm_time": "2018-11-20 15:00:02",#到账时间
                "source_status": "1",#方式
                "from_address": "0x7a3b68377E44a20992713bda5236baF33B92Eb8f",#出账地址
                "account_id": "111"
            },
            {
                "order_no": "20181128164013509106061596146659",
                "coin_id": "60",
                "withdraw_address": "0x2E582e7bb78587B2f39215f016323Ae8497aB8DA",
                "withdraw_amount": "0.00100000000000000",
                "withdraw_fee": "0.00000000000000000",
                "audit_status": "1",
                "withdraw_status": "2",
                "user_name": "扎扎实实",
                "apply_time": "2018-11-28 16:40:14",
                "transfer_time": "2018-11-20 15:00:02",
                "confirm_time": "2018-11-20 15:00:02",
                 "source_status": "1",
                 "from_address": "0x7a3b68377E44a20992713bda5236baF33B92Eb8f",
                "account_id": "222"
            }
        ]
    }
}

```

#提现审核页面
URL: /bg/users/withdraw/apply

Method: POST

Tips：

Header:


Params:

* order_no order_no


Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "order_no": "20181120150001556077548280099510",
        "coin_id": "0",
        "withdraw_address": "0x7a3b68377E44a20992713bda5236baF33B92Eb8f",
        "user_name": "反反复复",
        "withdraw_amount": "1.00000000000000000",
        "audit_status": "1",#审核状态: 0-待审核, 1-审核通过, 2-审核拒绝
        "expect_at": "0000-00-00 00:00:00",
        "apply_time": "2018-11-20 15:00:02",
        "withdraw_fee": "1.00000000000000000",
        "account_id": "111",
        "audit_status": "2",
        "lately_time": "2018-11-21 15:50:32"
    }
}

```

#提现审核
URL: /bg/users/withdraw/audit_withdraw

Method: POST

Tips：

Header:


Params:

* order_no order_no
 
* audit_status 审核状态: 1-审核通过, 2-审核拒绝
 
* remark 审核意见
 
* audit_user 审核人账号


Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {}
}

```

#用户流水
URL: /bg/users/withdraw/user_record

Method: POST

Tips：

Header:


Params:

* account_id account_id

* start_at 操作时间start

* end_at 操作时间end
 
* coin_id 币种
 
* change_type 操作类型
 
* address 相关地址
 
* offset 所查询的页
 
* limit 每页信息条数


Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "limit": "2",
        "offset": "1",
        "count": "58",
        "content": [
            {
                "change_type": 2,
                "id": 306,
                "water_id": "20181203105820656154071314223617",
                "user_name": "张维",
                "token_name": "ETH",
                "finish_time": "0000-00-00 00:00:00",
                "address": "0x74735BaeF98eA37749B19bBe58860A50A8122553",
                "show_change_amount": "0.10000000",
                "source": ""
            },
            {
                "change_type": 2,
                "id": 272,
                "water_id": "20181130105504384553780704616225",
                "user_name": "张维",
                "token_name": "BTC",
                "finish_time": "0000-00-00 00:00:00",
                "address": "2NC2StrfDbrUXRESHbC4NyKMFXs6UgDrniB",
                "show_change_amount": "0.50000000",
                "source": ""
            }
        ]
    }
}

```

#提现操作
URL: /bg/users/withdraw/operation_withdraw

Method: POST

Tips：出款账号地址使用"/bg/users/gather/gather_address_list"接口,offset传"0",即不分页,取字段"amount"

Header:


Params:

* order_nos 多个order_no使用","隔开
* 
* source_status 方式: 0-线上, 1-线下
* 
* from_address 出款地址: if (source_status == 0):{出款地址}else{空字符串}
* 
* verification_code 验证码: if (source_status == 0):{验证码}else{空字符串}
* 
* coin_id 币种: if (source_status == 0):{币种}else{空字符串}



Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {}
}

```

#线下提现录入tx
URL: /bg/users/withdraw/offline_tx

Method: POST

Tips：

Header:


Params:

* order_no order_no

* from_address 出账地址

* txid 交易hash
* 
* transfer_at 转账时间
* 
* coin_id 币种
* 
* operation_user 操作人账号

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": null
}
```

#查看提现详情
URL: /bg/users/withdraw/details

Method: POST

Tips：

Header:


Params:

* order_no order_no


Return:
仅展示解析后的数据形态

```
{
    "coin_id": "0",#币种
    "withdraw_amount": "1.000000000000000000",#数量
    "withdraw_fee": "1.000000000000000000",#手续费
    "withdraw_address": "0x7a3b68377E44a20992713bda5236baF33B92Eb8f",#地址
    "created_at": "2018-11-20 15:00:02",#申请时间
    "expect_at": "0000-00-00 00:00:00",#期望到账时间
    "audit_at": "2018-11-28 17:55:01",#审核通过时间
    "audit_user": "666",#审核人
    "from_address": "1NGkY14mcWLB9U4U7HLbEoCmq6npxnHxKW",#转账地址
    "transfer_at": "0000-00-00 00:00:00",#出账时间
    "confirm_at": "0000-00-00 00:00:00",#到账时间
    "source_status": "0",#转账方式
    "withdraw_status": "2",#状态
    "operation_user": "",#操作人
    "remark": "555",#备注
    "txid": "1234"#交易哈希
}
```

--------------------归集--------------
#归集、出款地址列表
URL: /bg/users/withdraw/gather_address_list

Method: POST

Tips：

Header:


Params:

* coin_id 币种

* conditions 归集条件(大于等于xx个单位)

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "address_list": [
            {
                "address": "mktRQ7WHfLDWpzJACraT9dhiUqfsTSYbwG",# 钱包地址
                "amount": "0E-18"# 地址余额
            },
            {
                "address": "2N1SWxJBhhwzeknBTbXH52e6L8b1Zaj3hUA",
                "amount": "0E-18"
            },
            {
                "address": "n2vE2fiLJuM8C5dy6aarzDgGHMmptR5MjX",
                "amount": "0E-18"
            },
            {
                "address": "14mjHtnxvH9MNxADLV4NxT3XKP6YtCYjEg",
                "amount": "0E-18"
            },
            {
                "address": "19Qzn3H5jMcwmvtuvro9vdQcVm91AqLez6",
                "amount": "0E-18"
            }
        ],
        "totle_amount": "0E-18"# 地址总余额
    }
}
```

#ETH追加手续费
URL: /bg/users/common/append_gas

Method: POST

Tips：

Header:


Params:

* order_no order_no

* verification_code 验证码

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {}
}
```

#发送邮箱验证码
URL: /bg/users/common/send_code

Method: POST

Tips：

Header:


Params:

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
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## admin后台归集相关
<a name = "admin后台归集相关">

#归集地址列表
URL: /bg/users/gather/gather_address_list

Method: POST

Tips：

Header:


Params:

* sub_public_address 地址

* coin_id 币种(必填)

* update_at_start 最近一次变动时间start

* update_at_end 最近一次变动时间end

* status 启用状态:0-停用, 1-启用

* offset 所查询的页

* limit 每页信息条数

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "count": "10",
        "list": [
            {
                "sub_public_address": "2N6tEzA4SDHXzCeENy65C3u4bFA9mq25f4y",#钱包地址
                "coin_id": "0",#币种
                "amount": "0.000000000000000000",#可用余额
                "amount_change": "0.000000000000000000",#待找零数量
                "status": "0",#启用状态
                "update_at": "2018-11-29 10:11:24"#最近一次变动时间
            },
            {
                "sub_public_address": "1HxQm5z3T6Ad5gUu1aA1tTB2J4a63hrKqh",
                "coin_id": "0",
                "amount": "0.000000000000000000",
                "amount_change": "0.000000000000000000",
                "status": "0",
                "update_at": "2018-11-29 10:11:24"
            }
        ]
    }
}

```

#归集地址流水
URL: /bg/users/gather/gather_address_record

Method: POST

Tips：

Header:


Params:

* sub_public_address 地址(必填)

* relevant_address 相关地址

* transfer_at_start 操作时间start

* transfer_at_end 操作时间end

* operation_type 操作类型:1-收款, 2-出款

* offset 所查询的页

* limit 每页信息条数

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "count": "3",
        "list": [
            {
                "order_no": "20181120150001556077548280099510",#流水号
                "user_name": "反反复复",#用户名
                "transfer_at": "0000-00-00 00:00:00",#操作时间
                "withdraw_amount": "1.000000000000000000",#数量
                "withdraw_fee": "1.000000000000000000",#手续费
                "operation_type": "2",#操作状态
                "relevant_address": "0x7a3b68377E44a20992713bda5236baF33B92Eb8f",#相关地址
                "operation_user": ""#操作人
            },
            {
                "order_no": "20181120155035431422775862820231",
                "user_name": "反反复复",
                "transfer_at": "0000-00-00 00:00:00",
                "withdraw_amount": "0.100000000000000000",
                "withdraw_fee": "0.001000000000000000",
                "operation_type": "2",
                "relevant_address": "1NGkY14mcWLB9U4U7HLbEoCmq6npxnHxKW",
                "operation_user": ""
            }
        ]
    }
}

```

#子账户地址列表
URL: /bg/users/gather/sub_address_list

Method: POST

Tips：

Header:


Params:

* user_name 用户名

* sub_public_address 钱包地址

* conditions 归集条件(大于等于xx个单位)

* coin_id 币种(必填)

* offset 所查询的页

* limit 每页信息条数

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "count": "17",
        "total_amount": "0.000000000000000000",
        "list": [
            {
                "user_name": "50796196@qq.com",#用户名
                "coin_id": "0",#币种
                "sub_public_address": "mktRQ7WHfLDWpzJACraT9dhiUqfsTSYbwG",#钱包地址
                "amount": "0.000000000000000000",#可归集数量
                "amount_frozen": "0.000000000000000000"#归集中数量
            },
            {
                "user_name": "50796196@qq.com",
                "coin_id": "0",
                "sub_public_address": "1MoWA1zVz7fz136V9969kcHiz4oGhHdy1V",
                "amount": "0.000000000000000000",
                "amount_frozen": "0.000000000000000000"
            }
        ]
    }
}

```

#归集操作
URL: /bg/users/gather/operation_gather

Method: POST

Tips：归集账户使用"/bg/users/gather/gather_address_list"接口,offset传"0",即不分页

Header:


Params:

* user_name 用户名

* sub_public_address 钱包地址

* conditions 归集条件(大于等于xx个单位)

* coin_id 币种(必填)

* to_address 归集账户

* verification_code 验证码

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": null
}

```

#归集操作记录
URL: /bg/users/gather/gather_record

Method: POST

Tips：

Header:


Params:

* public_address 归集地址

* coin_id 币种

* operate_at_start 操作时间start

* operate_at_end 操作时间end

* offset 所查询的页

* limit 每页信息条数

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "count": "1",
        "list": [
            {
                "record_id": "20181129185923620912053717714020",#id
                "created_at": "2018-11-29 18:59:24",#操作时间
                "coin_id": "0",#币种
                "amount": "0.000000000000000000",#数量
                "fee": "0.000000000000000000",#归集手续费
                "number": "0.000000000000000000",#操作账号数量
                "public_address": "2N6tEzA4SDHXzCeENy65C3u4bFA9mq25f4y"#归集地址
            }
        ]
    }
}

```

#归集操作记录详情
URL: /bg/users/gather/gather_record_details

Method: POST

Tips：

Header:


Params:

* record_id 归集操作记录返回的record_id

* user_name 用户名

* from_address 用户钱包地址

* operate_at_start 操作时间start

* operate_at_end 操作时间end

* withdraw_status 状态: 1-归集中, 2-成功, 3-失败

* confirm_at_start 结束时间start

* confirm_at_end 结束时间end

* offset 所查询的页

* limit 每页信息条数

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "info": {#归集信息
            "coin_id": "0",
            "amount": "0.000000000000000000",
            "fee": "0.000000000000000000",
            "number": "0.000000000000000000",
            "created_at": "2018-11-29 18:59:24",
            "public_address": "2N6tEzA4SDHXzCeENy65C3u4bFA9mq25f4y"
        },
        "count": 8,
        "list": [#归集记录
            {
                "record_id": "20181129185923620912053717714020",#id
                "user_name": "张维",#用户名
                "from_address": "0x630D7dC95C2BB0baFcd748B017741ec434Fd3d65",#用户钱包地址
                "created_at": "2018-11-28 16:40:14",#操作时间
                "coin_id": "60",#币种
                "withdraw_amount": "0.001000000000000000",#数量
                "withdraw_fee": "0.000000000000000000",#手续费
                "confirm_at": "0000-00-00 00:00:00",#结束时间
                "withdraw_address": "0x2E582e7bb78587B2f39215f016323Ae8497aB8DA",#归集地址
                "withdraw_status": "1"#状态
            }
        ]
    }
}

```

#全部归集操作记录详情
URL: /bg/users/gather/gather_record_all

Method: POST

Tips：

Header:


Params:

* user_name 用户名

* from_address 用户钱包地址

* operate_at_start 操作时间start

* operate_at_end 操作时间end

* withdraw_address 归集地址

* coin_id 币种

* confirm_at_start 结束时间start

* confirm_at_end 结束时间end
 
* withdraw_status 状态: 1-归集中, 2-成功, 3-失败

* offset 所查询的页

* limit 每页信息条数

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "count": 8,
        "list": [
            {
                "user_name": "反反复复",#用户名
                "from_address": "1NGkY14mcWLB9U4U7HLbEoCmq6npxnHxKW",#用户钱包地址
                "created_at": "2018-11-20 15:00:02",#操作时间
                "coin_id": "0",#归集币种
                "withdraw_amount": "1.000000000000000000",#数量
                "withdraw_fee": "1.000000000000000000",#手续费
                "confirm_at": "0000-00-00 00:00:00",#结束时间
                "withdraw_address": "0x7a3b68377E44a20992713bda5236baF33B92Eb8f",#归集地址
                "withdraw_status": "2"#状态
            }
        ]
    }
}

```

#归集转归集
URL: /bg/users/gather/gather_to_gather

Method: POST

Tips：

Header:


Params:

* coin_id 币种

* from_address 待归集地址

* amount 归集数量

* to_address 收款地址

* verification_code 验证码

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": null
}

```

#app获取提现手续费
URL: /users/common/get_gas

Method: POST

Tips：

Header:


Params:

* coin_id 币种
* user_id

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "gas_lag": "0.000000",# 缓慢
        "gas_routine": "0.000000",# 常规
        "gas_prior": "0.000000"# 优先
    }
}
```

#判断提现地址是否为平台地址
URL: /users/common/check_address

Method: POST

Tips：

Header:


Params:

* coin_id 币种
* user_id
* address 地址

Return:
仅展示解析后的数据形态

```
{
    "code": "00000",
    "desc": "success",
    "msg": "成功",
    "data": {
        "result": "1" # 1=是平台账号,0=非平台账号
    }
}
```