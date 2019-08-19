from werkzeug.exceptions import HTTPException
import error_code_utils as error_code_utils
from common_settings import _SHARE_KEY, _NONCE


class BCustomException(HTTPException):
    def __init__(self, err_code, error_msg=None, status_code=None, share_key=None, nonce=None):
        Exception.__init__(self)

        self.error_code = err_code
        if error_msg:
            self.error_msg = error_msg
        else:
            self.error_msg = error_code_utils.get_error_msg(err_code)

        if status_code:
            self.code = status_code

        self.error_desc = error_code_utils.get_error_desc(err_code)

        self.share_key = share_key
        self.nonce = nonce
        """
        # 因为第一版要求后台用户不加密，前台用户加密，故而做此屏蔽，正式上线，需要放开这个屏蔽
        if share_key is None:
            self.share_key = _SHARE_KEY
        if nonce is None:
            self.nonce = _NONCE
        """


class InvalidUsageException(BCustomException):
    status_code = 400


class InvalidUsageHeaderException(BCustomException):
    status_code = 400


class FundamentalErrorException(BCustomException):
    status_code = 406


class ServerErrorException(BCustomException):
    status_code = 500


class OperateUsageException(BCustomException):
    status_code = 200
