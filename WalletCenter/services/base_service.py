from tools.request_tools import RequestTools


class BaseService(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_tools = RequestTools()

    def return_error(self, error_code, error_msg=None, status_code=200):
        self.request_tools.return_error(error_code, error_msg, status_code)
