import time
from controllers.base_controller import BaseController
from tools.decorator_tools import FormatOutput


class ApiTimestampController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def get(self):
        return {"timestamp": str(int(time.time()))}