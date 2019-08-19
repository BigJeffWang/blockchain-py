import requests
import json
from tools.request_tools import RequestTools


def transfer_to_platform(url, data=None, method="post", headers=None):
    request_body = {} if data is None else data
    request_headers = {} if headers is None else headers
    if "Content-Type" not in request_headers:
        request_headers["Content-Type"] = "application/json"
        request_body = json.dumps(request_body)
    response = requests.request(method, url, data=request_body, headers=request_headers)
    if response.status_code != 200:
        RequestTools().return_error(10019)
    response_json = response.content.decode('utf-8')
    response_dict = json.loads(response_json)
    return response_dict