from controllers.base_controller import BaseController
from config import get_env


class TestController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self):
        return get_env() + " service is running!"

    def post(self):
        args = self.get_argument_dict()
        ret = {
            "data": args,
            "msg": True
        }
        print(ret)
        return








