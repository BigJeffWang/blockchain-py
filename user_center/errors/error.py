import base64
from tools.data_formate_tools import make_body_return_error, make_body_return_encode_error
from flask import jsonify
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, Forbidden, MethodNotAllowed, \
    InternalServerError
from api import app
from errors.error_handler import InvalidUsageException, ServerErrorException, InvalidUsageHeaderException, \
    OperateUsageException


@app.errorhandler(BadRequest)
def bad_request(error):
    response = jsonify()
    response.headers["Error_Code"] = 400
    response.headers["Error_Desc"] = str(error)
    response.headers["Error_Msg"] = str(error)
    response.status_code = 400
    return response


@app.errorhandler(Unauthorized)
def unauthorized(error):
    response = jsonify()
    response.headers["Error_Code"] = 401
    response.headers["Error_Desc"] = str(error)
    response.headers["Error_Msg"] = str(error)
    response.status_code = 401
    return response


@app.errorhandler(Forbidden)
def forbidden(error):
    response = jsonify()
    response.headers["Error_Code"] = 403
    response.headers["Error_Desc"] = str(error)
    response.headers["Error_Msg"] = str(error)
    response.status_code = 403
    return response


@app.errorhandler(NotFound)
def not_found(error):
    response = jsonify()
    response.headers["Error_Code"] = 404
    response.headers["Error_Desc"] = str(error)
    response.headers["Error_Msg"] = str(error)
    response.status_code = 404
    return response


@app.errorhandler(MethodNotAllowed)
def method_not_allow(error):
    response = jsonify()
    response.headers["Error_Code"] = 405
    response.headers["Error_Desc"] = str(error)
    response.headers["Error_Msg"] = str(error)
    response.status_code = 405
    return response


@app.errorhandler(InternalServerError)
def server_error(error):
    response = jsonify()
    response.headers["Error_Code"] = 400
    response.headers["Error_Desc"] = str(error)
    response.headers["Error_Msg"] = str(error)
    response.status_code = 400
    return response


@app.errorhandler(OperateUsageException)
def handle_operate_usage(error):
    error_dict = make_body_return_encode_error(str(error.error_code), error.error_desc, error.error_msg,
                                               error.share_key, error.nonce)
    response = jsonify(error_dict)
    response.status_code = error.status_code
    return response


@app.errorhandler(InvalidUsageException)
def handle_invalid_usage(error):
    error_dict = make_body_return_error(str(error.error_code), error.error_desc, error.error_msg)
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




