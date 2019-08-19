from werkzeug.exceptions import HTTPException
from utils import error_code_utils


class BCustomException(HTTPException):
    def __init__(self, err_code, error_msg=None, status_code=None):
        Exception.__init__(self)

        self.error_code = err_code
        if error_msg:
            self.error_msg = error_code_utils.get_error_msg(err_code) + error_msg
        else:
            self.error_msg = error_code_utils.get_error_msg(err_code)

        print("==================\nerror_code: %s  \n error_msg: %s" % (self.error_code, self.error_msg))

        if status_code:
            self.code = status_code

        self.error_desc = error_code_utils.get_error_desc(err_code)


class InvalidUsageException(BCustomException):
    status_code = 200


class InvalidUsageHeaderException(BCustomException):
    status_code = 400


class FundamentalErrorException(BCustomException):
    status_code = 406


class ServerErrorException(BCustomException):
    status_code = 500
