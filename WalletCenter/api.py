from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from common_settings import *
from controllers.test_controller import TestController
from controllers.transaction_controller import TransactionController

app = Flask(__name__)
from errors import error

error.err_init()
CORS(app, expose_headers=_RESPONSE_HEADER)
app.template_folder = "templates"
api = Api(app)

# base
api.add_resource(TestController, "/")  # 测试接口
# api.add_resource(CentralController, "/wallet/pk")  # 请求私钥接口
api.add_resource(TransactionController, "/wallet/transaction")  # 交易接口


