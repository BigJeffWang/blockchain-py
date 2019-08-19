import time
from controllers.base_controller import BaseController
from tools.decorator_tools import FormateOutput


class ApiTimestampController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormateOutput(default_value=20000, return_type='return_error')
    def get(self):
        return {"timestamp": str(int(time.time()))}




