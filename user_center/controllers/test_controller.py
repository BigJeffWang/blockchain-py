from controllers.base_controller import BaseController
from crypto_utils import *
import binascii
from config import get_conf
from common_settings import *
from tools.decorator_tools import AESOutput, FormateOutput
from config import get_transfer_to_platform_path
from tools.transfer_tools import transfer_to_platform


class TestController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def post(self):
        env = get_conf('env')
        if env != 'dev':
            return 'Hello'
        result = 'xxx'

        """
        password = 'gxFC123'
        bcrypt_salt = '$2a$12$sMjL4E/pmce4u8pHCMz2fu'
        bcypt_password = get_bcrypt_pwd(password, bcrypt_salt)
        print('****', bcypt_password)
        passwd_salt = '03d220105fd0f8bf52d944af'
        result = sha512(str(bcypt_password), str(passwd_salt))
        """
        """
        data = 'fa35f834c4e7b730d1965340e10f32ec2cb8f0495095c4b7ccb0ae26d5c6768465abb10e68134cb9133abe5d198039bc56c12427f1c607abc5d2c642126aaed1a823556142545dc25e17470c5d52ec26ac1e8d0725f5dfaa0ec09bdd1a59cf00c1ffbcb3df79b65e605ed677e0840d4f5ee69d0bbc180df6d801b72f55186f5d263e6cf91dd375264dd7b8f0510ffd966b26788214c08368da26c19d5cbc8c7c781eb2189b9bbd5aef7ae12c347dee94ff138460f4b76645420c7e228502843500c7c20cd27eca50fbac973b9bd38680738417504b105d8fce917e7fc991882ca9ebd2b7e4a2b39a889a0a6cff536bd4e8617a65ab09077362cc4a9c6572dcd443dfc59285d9efbde6c2f23cb99df3752366'
        b_nonce = '3b57837cc6ede19b48981110'
        b_share_key = 'AiqknICHx7QYnbDFdLLu8VzHRWrsoH299MQBLiBUAvWJ+JeakXgPHmgv50IB3lWH'
        from services.decrypt_service import DecryptService
        decrypt_service = DecryptService()
        result = decrypt_service.decrypt_data(data, b_share_key, b_nonce)
        """
        """
        from services.base_service import BaseService
        aa = BaseService(aes_share_key="0CJdc9+O+EtCXKBi7sE9GN1zbavvk1aIlfX2HFaXt9A9Z/ZfqamrKt+AhpLUIP4a", aes_nonce="1afdb5e41a2ba1d43f86aec3")
        # aa.return_aes_error(10036)

        print(base64.b64encode(bytes('擎天柱', encoding="utf8")), base64.b64encode(bytes('18500223172', encoding="utf8")))
        result, _, _ = self.get_argument_dict(check_token=False,
                                               invariable_key=True, api_type=_USER_TYPE_ADMIN,
                                               request_type=_REQUEST_TYPE_LOGIN,
                                               decode_by_inner=_DECODE_TYPE_DEFAULT, verify_timeliness=False,
                                              encrypt=True)
        """

        """
        # 加密算法
        data = str({
            'a': 'a',
            'access_token': '510523126359c503d5c75146909d6d7d21b74ac51958cba8703b6e4b7f95824653f5a510be',
        })

        data = str({
            # 'user_name': '13366071982',
            # 'user_mobile': '13366071980',
            # 'pvcode': '111111',
            # 'vcode': '111111',
            # 'password': 1234567,
            # 'old_password': 1234567,
            # 'new_password': 7654321,
            # 'level': 10,
            # 'register_signature': '111111',
            # 'user_id': 'f475d29208eb4fedb0934122caa84a6f',
            # 'refresh_token': 'f1457356d02595280389eb4fedb0934122caa84a6f64fa90b0d5c7405f90ebbe587500b64e',
            # 'access_token': 'f1457356d02596240889eb4fedb0934122caa84a6f7f5c98eee321474eb3edc613a4fb503e',
            # 'client_public_key': "-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAEyeOGHG7cH1WhkzpuIcvHxvgG/X/aaiDT\n4M/V6BEUzBw0zHdoX2xyupo+wFlyHhkoaPo3Z9HC2nk2tOEDZ1qMmx8oryGlAB/8\ndCmvEzT720NQHgIKw21Q8+fUumv5c8DF\n-----END PUBLIC KEY-----\n",
            'id_card': '989498994',
            'real_name': '花屋小五郎',
            "user_level": 10,
        })
        # b_nonce = binascii.unhexlify(str(_NONCE))
        # b_share_key = str(_SHARE_KEY)

        # b_nonce = binascii.unhexlify(str(_INNER_NONCE))
        # b_share_key = str(_INNER_SHARE_KEY)

        b_nonce = binascii.unhexlify(str('1afdb5e41a2ba1d43f86aec3'))
        b_share_key = str('0CJdc9+O+EtCXKBi7sE9GN1zbavvk1aIlfX2HFaXt9A9Z/ZfqamrKt+AhpLUIP4a')

        b_data = data
        send_password = binascii.hexlify(AES(b_data, sha256(b_share_key), b_nonce))
        print("send_password----\n", str(send_password))
        receive_data = binascii.unhexlify(send_password)
        print('receive_data', receive_data)

        # 3.   下次登录 ==> 服务端操作, 校验
        aa = deAES(receive_data, sha256(str(b_share_key)), b_nonce)
        result = eval(aa.decode('utf-8'))
        result['send_password'] = str(send_password)
        print("AES校验----\n", aa, type(aa))
        print(base64.b64encode(bytes('擎天柱', encoding="utf8")), base64.b64encode(bytes('c9490f7e1e75499582fe3083811432c4', encoding="utf8")))
        """

        """
        from tools.check_tools import check_bg_ip
        result = check_bg_ip("cHez5S8F")
        """

        """
        from utils import generate_str
        result = generate_str()
        """

        """
        result = self.get_argument_dict(must_keys=[], verify_timeliness=True, encrypt=True, check_token=False,
                                        invariable_key=False, api_type=_USER_TYPE_ADMIN,
                                        request_type=_REQUEST_TYPE_LOGIN, decode_by_inner=_DECODE_TYPE_DEFAULT,
                                        check_user_id=False)
        """

        """
        from tools.check_tools import check_bg_ip
        result = check_bg_ip('cHez5S8F')
        """
        """
        from services.vcode_service import VcodeService
        aa = VcodeService(aes_share_key="0CJdc9+O+EtCXKBi7sE9GN1zbavvk1aIlfX2HFaXt9A9Z/ZfqamrKt+AhpLUIP4a",
                         aes_nonce="1afdb5e41a2ba1d43f86aec3")
        aa.send_aws_sms('7247059134', '123456', mobile_country_code='001', template='您的验证码为：789456，时效5分钟')
        """
        return result

    """
    def get(self):
        from services.user_base_service import UserBaseService
        user_service = UserBaseService()
        user_mobile = "13366072001"
        password = "12345"
        user_type = _USER_TYPE_INVEST
        result = user_service.register(user_mobile, password, 0, user_type=user_type)
        print("****1", result)

        transfer_url = get_transfer_to_platform_path("invest", "generate_account")
        account_response_dict = transfer_to_platform(transfer_url, data={
            "user_id": result['user_id'],
            "user_mobile": user_mobile
        })

        print("****2", account_response_dict)

        user_service.register_on(user_mobile)

        login_result = user_service.login(user_mobile, password, user_type)
        print("****3", login_result)

        result = dict(result, **login_result)

        return result
    """




