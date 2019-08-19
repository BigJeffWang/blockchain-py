from tools.request_tools import RequestTools


class BaseService(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_tools = RequestTools()

    def return_error(self, error_code, error_msg=None, status_code=200):
        self.request_tools.return_error(error_code, error_msg, status_code)

    @staticmethod
    def check_args(keys, args, judge=None, judge_args=(None, "")):
        """
        校验参数在字典中是否存在,并且判断是否为空
        :param keys: 必填字段列表,可以是字符串也可以是列表
        :param args:
        :param judge: 是否开启 是否为空的 校验, 默认不开启
        :param judge_args: 校验值类型列表, 默认包含 None "", 可以自定义
        :return: True 校验通过
        """
        must_keys = []
        if isinstance(keys, str):
            must_keys.append(keys)
        else:
            must_keys = keys
        for key in keys:
            if not judge:
                if key not in args:
                    return False
            else:
                if key in args:
                    if args.get(key) in judge_args:
                        return False
                else:
                    return False
        return True
