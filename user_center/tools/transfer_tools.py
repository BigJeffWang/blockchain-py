import requests
import json
from tools.request_tools import RequestTools
from flask import request


def transfer_to_platform(url, data=None, method="post", headers=None, decode_type='json'):
    request_body = {} if data is None else data
    request_headers = {} if headers is None else headers
    if "Content-Type" not in request_headers:
        request_headers["Content-Type"] = "application/json"
        request_body = json.dumps(request_body)
    if 'TimeZone' not in request_headers:
        request_headers["TimeZone"] = request.headers.get("TimeZone", '')
    response = requests.request(method, url, data=request_body, headers=request_headers)
    if response.status_code != 200:
        RequestTools().return_error(10042)
    if decode_type == 'json':
        response_json = response.content.decode('utf-8')
        response_dict = json.loads(response_json)
    else:
        response_dict = response.content.decode('utf-8')
    return response_dict

