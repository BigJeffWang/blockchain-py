from controllers.base_controller import BaseController
from services.transaction_service import TransactionService


class TransactionController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def post(self):
        must_keys = ["order_no", "parameter", "sign"]
        args = self.get_argument_dict(must_keys)
        ret = TransactionService().send_transaction(args)
        return ret
