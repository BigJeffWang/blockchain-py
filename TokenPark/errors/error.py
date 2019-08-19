import base64
from tools.decorator_tools import FormatOutput
from flask import jsonify
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, Forbidden, MethodNotAllowed, \
    InternalServerError
from api import app

from errors.error_handler import InvalidUsageException, ServerErrorException, InvalidUsageHeaderException
from utils.log import raise_logger
# from models.header_model import HeaderModel
# from tools.mysql_tool import MysqlTools


@app.errorhandler(BadRequest)
def bad_request(error):
    raise_logger(error, 'rs', 'error')
    response = jsonify()
    response.headers["Error_Code"] = 400
    response.headers["Error_Desc"] = str(error)
    response.headers["Error_Msg"] = str(error)
    response.status_code = 400
    return response


@app.errorhandler(Unauthorized)
def unauthorized(error):
    raise_logger(error, 'rs', 'error')
    response = jsonify()
    response.headers["Error_Code"] = 401
    response.headers["Error_Desc"] = str(error)
    response.headers["Error_Msg"] = str(error)
    response.status_code = 401
    return response


@app.errorhandler(Forbidden)
def forbidden(error):
    raise_logger(error, 'rs', 'error')
    response = jsonify()
    response.headers["Error_Code"] = 403
    response.headers["Error_Desc"] = str(error)
    response.headers["Error_Msg"] = str(error)
    response.status_code = 403
    return response


@app.errorhandler(NotFound)
def not_found(error):
    raise_logger(error, 'rs', 'info')
    response = jsonify()
    response.headers["Error_Code"] = 404
    response.headers["Error_Desc"] = str(error)
    response.headers["Error_Msg"] = str(error)
    response.status_code = 404
    return response


@app.errorhandler(MethodNotAllowed)
def method_not_allow(error):
    raise_logger(error, 'rs', 'error')
    response = jsonify()
    response.headers["Error_Code"] = 405
    response.headers["Error_Desc"] = str(error)
    response.headers["Error_Msg"] = str(error)
    response.status_code = 405
    return response


@app.errorhandler(InternalServerError)
def server_error(error):
    raise_logger(error, 'rs', 'error')
    response = jsonify()
    response.headers["Error_Code"] = 400
    response.headers["Error_Desc"] = str(error)
    response.headers["Error_Msg"] = str(error)
    response.status_code = 400
    return response


@app.errorhandler(InvalidUsageException)
def handle_invalid_usage(error):
    error_dict = FormatOutput.make_body_return_error(str(error.error_code), error.error_desc, error.error_msg)
    response = jsonify(error_dict)
    response.status_code = error.status_code
    return response


@app.errorhandler(InvalidUsageHeaderException)
def handle_invalid_usage_header(error):
    response = jsonify()
    response.headers["Error_Code"] = error.error_code
    response.headers["Error_Desc"] = error.error_desc
    response.headers["Error_Msg"] = base64.b64encode(bytes(error.error_msg, encoding="utf8"))
    response.status_code = error.status_code
    return response


@app.errorhandler(ServerErrorException)
def handle_server_error_exception(error):
    response = jsonify()
    response.headers["Error_Code"] = error.error_code
    response.headers["Error_Desc"] = error.error_desc
    response.headers["Error_Msg"] = base64.b64encode(bytes(error.error_msg, encoding="utf8"))
    response.status_code = error.status_code
    return response


@app.before_first_request
def before_first_request():
    pass


# @app.before_request
# def before_request():
#     """
#     app=>对应版本    source=>对应设备例如ios android       channel=>渠道
#     :return:
#     """
#     req_header = request.headers
#     req_env = request.environ
#     remote_host = req_env["REMOTE_ADDR"] + ":" + str(req_env["REMOTE_PORT"])
#     http_host = req_env["HTTP_HOST"]
#     remote_request = str(req_env["werkzeug.request"])
#     user_agent = req_env["HTTP_USER_AGENT"]
#     user_app = req_header.get("App", "")
#     user_source = req_header.get("Source", "")
#     user_channel = req_header.get("Channel", "")
#     mysql_tool = MysqlTools()
#     with mysql_tool.session_scope() as session:
#         header = HeaderModel(
#             remote_request=remote_request,
#             http_host=http_host,
#             remote_host=remote_host,
#             user_agent=user_agent,
#             user_app=user_app,
#             user_source=user_source,
#             user_channel=user_channel
#         )
#         session.add(header)
#         session.commit()


def err_init():
    # 该方法勿删
    pass
