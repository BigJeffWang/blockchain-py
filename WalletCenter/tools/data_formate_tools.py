def make_body_return_error(error_code, error_desc, error_msg):
    return {
        "code": str(error_code),
        "desc": error_desc,
        "msg": error_msg,
        "data": {},
    }


def make_body_return_success(datas):
    return {
        "code": "00000",
        "desc": "success",
        "msg": "成功",
        "data": datas
    }