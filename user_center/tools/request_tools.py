from errors.error_handler import InvalidUsageException, FundamentalErrorException, InvalidUsageHeaderException, \
    OperateUsageException


class RequestTools(object):
    def __init__(self):
        super(RequestTools, self).__init__()

    def return_error(self, err_code, error_msg=None, status_code=400):
        raise InvalidUsageException(err_code, error_msg, status_code)

    def return_operate_error(self, err_code, error_msg=None, status_code=200, share_key=None, nonce=None):
        raise OperateUsageException(err_code, error_msg, status_code, share_key, nonce)

    def return_fundamental_error(self, err_code, error_msg=None, status_code=406):
        raise FundamentalErrorException(err_code, error_msg, status_code)

    def return_error_by_header(self, err_code, error_msg=None, status_code=400):
        raise InvalidUsageHeaderException(err_code, error_msg, status_code)
