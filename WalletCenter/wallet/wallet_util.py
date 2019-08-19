from wallet.crypto import HDPrivateKey, HDKey, checksum_encode
from utils.util import to_int
from common_settings import _BTC, _ETH, _ONE, _EOS


class Wallet(object):
    path = {
        _BTC: "m/44'/0'/0'",
        _ETH: "m/44'/60'/0'",
        _EOS: "m/44'/194'/0'"
    }

    def __init__(self, *args, **kwargs):
        self.symbol = kwargs["symbol"]
        self.path = Wallet.path[self.symbol]
        self.master_key = None
        self.acct_private_key = None

    def init_acct(self, mnemonic, passphrase=None):
        mnemonic = mnemonic if mnemonic else ""
        passphrase = str(passphrase) if passphrase else ""
        if self.symbol in [_BTC, _ETH]:
            self.master_key = HDPrivateKey.master_key_from_mnemonic(mnemonic, passphrase=passphrase)
            root_keys = HDKey.from_path(self.master_key, self.path)
            self.acct_private_key = root_keys[-1]
        elif self.symbol in [_EOS]:
            self.master_key = mnemonic  # EOS账户
            self.acct_private_key = passphrase  # EOS密码

    def get_acct_key(self):
        root_key_b58 = None
        acct_priv_key = None
        acct_pub_key_b58 = None
        acct_priv_key_b58 = None
        if self.symbol in [_BTC, _ETH]:
            root_key_b58 = self.master_key.to_b58check()
            acct_priv_key = self.acct_private_key._key.to_hex()
            acct_priv_key_b58 = self.acct_private_key.to_b58check()
            acct_pub_key_b58 = self.acct_private_key.public_key.to_b58check()
        elif self.symbol in [_EOS]:
            acct_pub_key_b58 = self.master_key
        return {"root_key_b58": root_key_b58, "acct_priv_key": acct_priv_key, "acct_pub_key_b58": acct_pub_key_b58, "acct_priv_key_b58": acct_priv_key_b58}

    def get_address_from_xpub(self, public_key, sub_index):
        acct_pub_key = HDKey.from_b58check(public_key)
        change, index = self.get_change_index(sub_index)
        keys = HDKey.from_path(acct_pub_key, '{change}/{index}'.format(change=change, index=index))
        address = keys[-1].address()
        return address

    def get_address_b58_to_hex(self, public_key_b58, sub_index):
        acct_pub_key = HDKey.from_b58check(public_key_b58)
        change, index = self.get_change_index(sub_index)
        keys = HDKey.from_path(acct_pub_key, '{change}/{index}'.format(change=change, index=index))
        return keys[-1].to_hex()

    @staticmethod
    def get_address_from_subpub(public_key):
        return HDKey.from_b58check(public_key).address()

    @staticmethod
    def get_change_index(sub_index):
        if isinstance(sub_index, str):
            sub_index = int(sub_index)
        slice_count = 10000
        change = sub_index // slice_count - 1
        index = sub_index % slice_count
        if index == 0:
            index = slice_count - 1
        else:
            change += 1

        return change, index

    def get_sub_key(self, count, begin=None):
        if begin is None:
            begin = _ONE
        count = to_int(count)
        begin = to_int(begin)
        end = begin + count
        change = 0
        subacct_info_dict = {}

        for j in range(begin, end):
                subacct_info_dict[str(j)] = self.generate_sub_info(change, j)
        return subacct_info_dict

    def generate_sub_info(self, change, index):
        change_index = '{change}/{index}'.format(change=change, index=index)
        ext_key = None
        if self.symbol in [_BTC, _ETH]:
            keys = HDKey.from_path(self.acct_private_key, change_index)
            ext_key = keys[-1]
        elif self.symbol in [_EOS]:
            ext_key = index

        if self.symbol == _BTC:
            sub_private_key, sub_public_key, sub_address = self.ext_info_btc(ext_key)
        elif self.symbol == _ETH:
            sub_private_key, sub_public_key, sub_address = self.ext_info_eth(ext_key)
        elif self.symbol in [_EOS]:
            sub_private_key, sub_public_key, sub_address = self.ext_info_eos(ext_key)
        else:
            raise Exception("Not have this symbol")
        return {"sub_private_key": sub_private_key, "sub_public_key": sub_public_key, "sub_address": sub_address, "change_index": change_index}

    @staticmethod
    def ext_info_btc(ext_key):
        sub_public = ext_key.public_key
        sub_private_key = ext_key._key.to_b58check_btc()
        sub_public_key = sub_public._key.get_public_key_btc()
        sub_address = sub_public._key.get_address_btc()
        return sub_private_key, sub_public_key, sub_address

    @staticmethod
    def ext_info_eth(ext_key):
        sub_public = ext_key.public_key
        sub_private_key = ext_key._key.to_hex()
        sub_public_key = sub_public._key.get_public_key_eth()
        sub_address = checksum_encode(sub_public.address())
        return sub_private_key, sub_public_key, sub_address

    @staticmethod
    def ext_info_eos(ext_key):
        sub_private_key = ""
        sub_public_key = ""
        sub_address = str(10000000 + int(ext_key))
        return sub_private_key, sub_public_key, sub_address

    @staticmethod
    def get_ext_from_private_key_btc(private_key):
        return HDKey.from_b58check_btc(private_key)

    @staticmethod
    def get_publick_key_from_ext(ext):
        return HDKey.get_public_key_from_ext(ext).get_public_key_btc()

    @staticmethod
    def get_address_from_ext(ext):
        return HDKey.get_public_key_from_ext(ext).get_address_btc()

    @staticmethod
    def get_address_from_private_key(private_key):
        return HDKey.get_public_key_from_ext(HDKey.from_b58check_btc(private_key)).get_address_btc()

    @staticmethod
    def check_private_key_and_address(private_key, relative_address):
        return True if Wallet.get_address_from_private_key(private_key) == relative_address else False


if __name__ == "__main__":
    pass
    # ext = Wallet.get_ext_from_private_key_btc("L1ZqduqQzKKRPeHiNTRdGf9duYZKeqgcJdRonSexxxXWutkDSHdD")
    # print(ext)
    # public_key = Wallet.get_publick_key_from_ext(ext)
    # print(public_key)
    # print("036e2d634834d504e492cfcd9baec2659a1c14fbfbcb00230b5205ae1757644483")
    # address = Wallet.get_address_from_ext(ext)
    # print(address)
    # print("1AuZJYSDQvuworPpac6y4YtMYeLzm95X6w")

    # check_res = Wallet.check_private_key_and_address("KyNYM81QDiV58VYyZmy9ksDVsGNjoiQHskZEVgcAv61fd79r1Uwa", "16sHYJPqUZKFNXKgSJdidSUZBueit8JzXK")
    # print(check_res)

    # symbol = "ETH"
    # mnemonic, passphrase = "evidence harsh exotic math capital inspire anxiety true unable bird salt shop", "123"
    # w = Wallet(symbol=symbol)
    # w.init_acct(mnemonic, passphrase)
    # res = w.get_sub_key(10)
    # print(res)
