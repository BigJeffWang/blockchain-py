from crypto_utils import *
import binascii
from config import get_conf
import json


def make_body_return_encode_error(error_code, error_desc, error_msg, share_key, nonce):
    result_dict = {
        "code": str(error_code),
        "desc": error_desc,
        "msg": error_msg,
        "data": {},
    }

    if get_conf('env') == 'dev' and not get_conf('aes_to_client'):
        return result_dict
    if share_key is None or nonce is None:
        return result_dict
    result_dict = json.dumps(result_dict)
    # print('make_body_return_error', result_dict, share_key, nonce)
    b_data = result_dict
    send_data = binascii.hexlify(AES(b_data, sha256(share_key), binascii.unhexlify(nonce)))
    return {
        "data": str(send_data, encoding='utf-8')
    }


def make_body_return_success(datas, share_key, nonce):
    result_dict =  {
        "code": "00000",
        "desc": "success",
        "msg": "成功",
        "data": datas
    }

    if get_conf('env') == 'dev' and not get_conf('aes_to_client'):
        return result_dict
    if share_key is None or nonce is None:
        return result_dict
    result_dict = json.dumps(result_dict)
    # print('make_body_return_success', result_dict, share_key, nonce)
    b_data = result_dict
    send_data = binascii.hexlify(AES(b_data, sha256(share_key), binascii.unhexlify(nonce)))
    return {
        "data": str(send_data, encoding='utf-8')
    }


def make_body_return_error(error_code, error_desc, error_msg):
    result_dict = {
        "code": str(error_code),
        "desc": error_desc,
        "msg": error_msg,
        "data": {},
    }
    return result_dict


def make_body_tranfer_return_success(datas, share_key, nonce):
    if isinstance(datas, dict):
        result_dict = json.dumps(datas)
    else:
        result_dict = str(datas)
    # print('make_body_tranfer_return_success', result_dict, share_key, nonce)
    b_data = result_dict
    send_data = binascii.hexlify(AES(b_data, sha256(share_key), binascii.unhexlify(nonce)))
    return {
        "data": str(send_data, encoding='utf-8')
    }