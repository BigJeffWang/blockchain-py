import binascii

from web3 import Web3

from web3.middleware import geth_poa_middleware


def convert_info_to_json(info):
    if info is None:
        return
    info_dict = dict(info)
    for key, value in info_dict.items():
        if key == "logs":
            info_dict[key] = []
        elif not isinstance(value, (str, int, float, list)):
            if value is None:
                info_dict[key] = ""
            else:
                info_dict[key] = binascii.hexlify(value).decode('utf-8')
        elif isinstance(value, list) and len(value) != 0:
            for i, v in enumerate(value):
                if not isinstance(v, (str, int, float)):
                    value[i] = binascii.hexlify(v).decode('utf-8')
            info_dict[key] = value

    return info_dict


# node_uri = "http://13.115.154.149:8545"  # 测试
# node_uri = "http://3.16.26.56:8545"  # 测试俄亥俄
# node_uri = "http://52.194.21.55:8545"  # 正式

# w3 = Web3(Web3.HTTPProvider(node_uri))

from models.token_node_conf_model import TokenNodeConfModel

coin_id = "60"
mold = "server"
w3 = TokenNodeConfModel.get_eth_node_server()

w3.middleware_stack.inject(geth_poa_middleware, layer=0)

block_num = w3.eth.blockNumber

print(block_num)

# block = convert_info_to_json(w3.eth.getBlock(block_num))
#
# print(block)


# node_status = w3.txpool.status
# pending = int(node_status.pending, 16)  # 16进制转10进制
# tx_count = w3.eth.getTransactionCount("0x630D7dC95C2BB0baFcd748B017741ec434Fd3d65")
# tx_count_pending = w3.eth.getTransactionCount("0x630D7dC95C2BB0baFcd748B017741ec434Fd3d65", "pending")
# # tx_count = w3.eth.getTransactionCount(w3.eth.coinbase)
# nonce = tx_count + pending  # 完成和未完成相加
#
# print("w3.eth.coinbase")
# print(w3.eth.coinbase)
# print("pending:")
# print(pending)
# print("tx_count_pending:")
# print(tx_count_pending)
# print("tx_count")
# print(tx_count)

# tx_info = convert_info_to_json(w3.eth.getTransaction("e9ddcbd455b3fecea3b018076aafd80334551a03c55bcc0f143d97e4bceb3ff0"))
# print(tx_info)
#
# tx_info_receipt = convert_info_to_json(w3.eth.getTransactionReceipt("e9ddcbd455b3fecea3b018076aafd80334551a03c55bcc0f143d97e4bceb3ff0"))
# print(tx_info_receipt)
#
# tx_info2 = convert_info_to_json(w3.eth.getTransaction("95b7172be76ba44bbcd1a2a52c5d8551ca61a0b5cdc24edb62c07517ce76fbde"))
# print(tx_info2)
#
# tx_info_receipt2 = convert_info_to_json(w3.eth.getTran sactionReceipt("95b7172be76ba44bbcd1a2a52c5d8551ca61a0b5cdc24edb62c07517ce76fbde"))
# print(tx_info_receipt2)

# tx_info3 = convert_info_to_json(w3.eth.getTransaction("0xd991caea4693b62e0058bf1105f1f2e0788f3b53a26b12a3cb303d9b28398e93"))
# print(tx_info3)
#
# tx_info_receipt3 = convert_info_to_json(w3.eth.getTransactionReceipt("0xd991caea4693b62e0058bf1105f1f2e0788f3b53a26b12a3cb303d9b28398e93"))
# print(tx_info_receipt3)

# tx_info4 = convert_info_to_json(w3.eth.getTransaction("8181f90d82a5329629d3a3d2c6ad59843dd0d8fc22e8c771477e7e2b2244d105"))
# print(tx_info4)
#
# tx_info_receipt4 = convert_info_to_json(w3.eth.getTransactionReceipt("8181f90d82a5329629d3a3d2c6ad59843dd0d8fc22e8c771477e7e2b2244d105"))
# print(tx_info_receipt4)

# tx_info5 = convert_info_to_json(w3.eth.getTransaction("0x4c1174dcf183fea8ccb3a5d7861a777fc471d04d5b35ae22db19a49c21e54c59"))
# print(tx_info5)
#
# tx_info_receipt5 = convert_info_to_json(w3.eth.getTransactionReceipt("0x4c1174dcf183fea8ccb3a5d7861a777fc471d04d5b35ae22db19a49c21e54c59"))
# print(tx_info_receipt5)
