from controllers.base_controller import BaseController
from services.central_service import CentralService


class CentralController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def post(self):
        must_keys = ["order_no", "type", "address"]
        args = self.get_argument_dict(must_keys)
        ret = CentralService().get_private_key_from_address(args)
        return ret



