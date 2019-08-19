"""
-------------------------------------------------
   File Name：     block_chain_info_service
   Description:
   Author:        Zyt
   Date：          2018/11/21
-------------------------------------------------
"""

import binascii
import hashlib
import json
import time
from datetime import datetime

from web3 import Web3

from services.base_service import BaseService
from tools.mysql_tool import MysqlTools
from models.block_chain_info_model import BlockChainInfoModel, RECORD_TYPE_DICT
from utils.log import raise_logger
import config
from utils.util import (
    hexbytes_to_str,
    get_offset_by_page,
    get_page_by_offset,
    time_transform_from_zone
)


class BlockChainInfoService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config.get_private_block_chain_conf()
        self.host = self.config['uri']
        self.user = self.config['user']
        self.password = self.config['password']
        self.conn = self.connect_block_chain()

    def connect_block_chain(self):
        conn = Web3(Web3.HTTPProvider(self.host))
        return conn

    @staticmethod
    def info_to_hash(chain_info: dict) -> str:
        try:
            hash_data = hashlib.sha256(
                json.dumps(chain_info).encode("utf-8")).hexdigest()
            return hash_data
        except KeyError:
            raise

    def send_transaction(self, hash_data):
        node_status = self.conn.txpool.status
        pending = int(node_status.pending, 16)
        tx_count = self.conn.eth.getTransactionCount(self.conn.eth.coinbase)
        nonce = tx_count + pending
        transaction = {
            "from": self.conn.eth.coinbase,
            "to": self.conn.toChecksumAddress(self.user),
            "value": 0,
            "data": hash_data,
            "nonce": nonce,
            "gasPrice": self.conn.eth.gasPrice,
            "gas": 1000000,
        }
        signed_txn = self.conn.eth.account.signTransaction(
            transaction, binascii.unhexlify(self.password.encode("utf-8")))
        tx_hash_hex_bytes = self.conn.eth.sendRawTransaction(
            signed_txn.rawTransaction)
        tx_hash = binascii.hexlify(tx_hash_hex_bytes).decode('utf-8')
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "tx_hash": "0x" + tx_hash,
            "timestamp": timestamp
        }

    # store block chain information
    def insert_block_chain_info(self, user_id: str, instance_id: str,
                                record_type: int, on_chain_info: dict) -> bool:

        try:
            # compute information hash
            hash_data = self.info_to_hash(on_chain_info)
            # send transaction
            transaction_response = self.send_transaction(hash_data)
        except TypeError as type_error:
            raise_logger(type_error, 'rs', 'error')
            return False
        except Exception as send_error:
            raise_logger(send_error, 'rs', 'error')
            return False
        hash_hex = "0x" + hash_data

        # store information
        with MysqlTools().session_scope() as session:
            BlockChainInfoModel.store(
                session, user_id, instance_id, record_type, hash_hex,
                on_chain_info,
                transaction_hash=transaction_response['tx_hash'],
                on_chain_at=transaction_response['timestamp'],
                game_serial=on_chain_info.get("game_serial", ""),
                participate_id=on_chain_info.get("id", "-1")
            )
        return True

    def get_block_info(self):
        block_info = self.conn.eth.getBlock('latest')
        block_number = block_info['number']
        block_hash = binascii.hexlify(block_info['hash']).decode('utf-8')
        if block_number == 0:
            time_delta = 0
        else:
            time_delta = round(
                (block_info['timestamp'] - self.conn.eth.getBlock(0)['timestamp'])
                / block_number)
        block_generate_delta = int(time.time()) - block_info['timestamp']
        return {
            "block_number": block_number,
            "time_delta": time_delta,
            "block_hash": block_hash,
            "block_generate_delta": block_generate_delta
        }

    # 获取项目的区块链信息，用于开奖详情页
    @staticmethod
    def project_block_info(instance_id, timezone):
        with MysqlTools().session_scope() as session:
            # 查询发布信息
            q_publish = session.query(
                BlockChainInfoModel.on_chain_at,
                BlockChainInfoModel.transaction_hash
            ).filter(
                BlockChainInfoModel.instance_id == instance_id,
                BlockChainInfoModel.record_type == '2',
                BlockChainInfoModel.deleted == False
            ).first()

            # 查询夺宝记录
            q_record = session.query(
                BlockChainInfoModel.on_chain_at,
                BlockChainInfoModel.transaction_hash
            ).filter(
                BlockChainInfoModel.instance_id == instance_id,
                BlockChainInfoModel.record_type == '1',
                BlockChainInfoModel.deleted == False
            ).order_by(
                BlockChainInfoModel.on_chain_at.desc()
            ).first()

            # 查询揭晓信息
            q_announce = session.query(
                BlockChainInfoModel.on_chain_at,
                BlockChainInfoModel.transaction_hash
            ).filter(
                BlockChainInfoModel.instance_id == instance_id,
                BlockChainInfoModel.record_type == '0',
                BlockChainInfoModel.deleted == False
            ).first()

        # response info
        response_dict = {
            "publish": {
                "on_chain_at": "",
                "transaction_hash": ""
            },
            "record": {
                "on_chain_at": "",
                "transaction_hash": ""
            },
            "announce": {
                "on_chain_at": "",
                "transaction_hash": ""
            },
        }
        if q_publish:
            response_dict['publish'] = {
                "on_chain_at": time_transform_from_zone(
                    q_publish.on_chain_at.strftime("%Y-%m-%d %H:%M:%S"),
                    timezone),
                "transaction_hash": q_publish.transaction_hash
            }
        if q_record:
            response_dict['record'] = {
                "on_chain_at": time_transform_from_zone(
                    q_record.on_chain_at.strftime("%Y-%m-%d %H:%M:%S"),
                    timezone),
                "transaction_hash": q_record.transaction_hash
            }
        if q_announce:
            response_dict['announce'] = {
                "on_chain_at": time_transform_from_zone(
                    q_announce.on_chain_at.strftime("%Y-%m-%d %H:%M:%S"),
                    timezone),
                "transaction_hash": q_announce.transaction_hash
            }
        return response_dict

    # 获取详情信息
    def get_info_detail(self, info_type: str, instance_id: str, user_id: str,
                        participate_id: str, timezone):
        # response structure
        response_dict = {
            "data": []
        }

        if info_type in ('0', '2'):
            with MysqlTools().session_scope() as session:
                # 获取数据库信息
                query_info = session.query(
                    BlockChainInfoModel.info_hash,
                    BlockChainInfoModel.transaction_hash,
                    BlockChainInfoModel.on_chain_info
                ).filter(
                    BlockChainInfoModel.instance_id == instance_id,
                    BlockChainInfoModel.record_type == info_type,
                    BlockChainInfoModel.on_chain_status == 1,
                    BlockChainInfoModel.deleted == False
                ).first()

                # if info not exist, return not data
                if not query_info:
                    return response_dict
                else:
                    block_info = self.conn.eth.getTransaction(
                        query_info.transaction_hash
                    )
                    chain_info = json.loads(query_info.on_chain_info)
                    # 获取揭晓信息
                    if info_type == '0':
                        response_dict['data'] = [
                            {
                                "key": "hash_data",
                                "value": query_info.info_hash
                            },
                            {
                                "key": "Txhash",
                                "value": query_info.transaction_hash
                            },
                            {
                                "key": "blockHash",
                                "value": "0x" + hexbytes_to_str(
                                    block_info['blockHash'])
                            },
                            {
                                "key": "blockNumber",
                                "value": block_info.get('blockNumber', "")
                            },
                            {
                                "key": "transactionIndex",
                                "value": block_info.get('transactionIndex', "")
                            },
                            {
                                "key": "期号",
                                "value": chain_info.get('game_serial', "")
                            },
                            {
                                "key": "发布时间",
                                "value": time_transform_from_zone(
                                    chain_info.get('release_time', ""), timezone)
                            },
                            {
                                "key": "奖励币种",
                                "value": chain_info.get('reward_token', "")
                            },
                            {
                                "key": "奖励数量",
                                "value": chain_info.get('reward_quantity', "")
                            },
                            {
                                "key": "投入币种",
                                "value": chain_info.get('bet_token', "")
                            },
                            {
                                "key": "总需数",
                                "value": chain_info.get('need', "")
                            },
                            {
                                "key": "游戏规则",
                                "value": chain_info.get('game_describe', "")
                            },
                            {
                                "key": "满额时间",
                                "value": time_transform_from_zone(
                                    chain_info.get('full_load_time', ""),
                                    timezone)
                            },
                            {
                                "key": "参与人数",
                                "value": chain_info.get('participation', "")
                            },
                            {
                                "key": "第三方区块生成时间",
                                "value": chain_info.get('timestamp', "")
                            },
                            {
                                "key": "第三方区块类型",
                                "value": chain_info.get('block_type', "")
                            },
                            {
                                "key": "第三方区块 Hash 值不可逆时间",
                                "value": chain_info.get('received_time', "")
                            },
                            {
                                "key": "第三方区块上链不可逆 Hash 值",
                                "value": chain_info.get('bet_hash', "")
                            },
                            {
                                "key": "揭晓时间",
                                "value": time_transform_from_zone(
                                    chain_info.get('lottery_time', ""), timezone)
                            },
                            {
                                "key": "中奖号码",
                                "value": chain_info.get('bet_serial', "")
                            },
                            {
                                "key": "中奖用户",
                                "value": chain_info.get('nick_name', "")[0] if chain_info.get('nick_name', "") else ""
                            },
                        ]
                    # 获取发布信息
                    else:
                        response_dict['data'] = [
                            {
                                "key": "hash_data",
                                "value": query_info.info_hash
                            },
                            {
                                "key": "Txhash",
                                "value": query_info.transaction_hash
                            },
                            {
                                "key": "blockHash",
                                "value": "0x" + hexbytes_to_str(
                                    block_info['blockHash'])
                            },
                            {
                                "key": "blockNumber",
                                "value": block_info.get('blockNumber', "")
                            },
                            {
                                "key": "transactionIndex",
                                "value": block_info.get('transactionIndex', "")
                            },
                            {
                                "key": "期号",
                                "value": chain_info.get('game_serial', "")
                            },
                            {
                                "key": "发布时间",
                                "value": time_transform_from_zone(
                                    chain_info.get('release_time', ""), timezone)
                            },
                            {
                                "key": "奖励币种",
                                "value": chain_info.get('reward_token', "")
                            },
                            {
                                "key": "奖励数量",
                                "value": chain_info.get('reward_quantity', "")
                            },
                            {
                                "key": "投入币种",
                                "value": chain_info.get('bet_token', "")
                            },
                            {
                                "key": "总需数",
                                "value": chain_info.get('need', "")
                            },
                            {
                                "key": "游戏规则",
                                "value": chain_info.get('game_describe', "")
                            },
                        ]

        # 获取夺宝信息详情
        elif info_type == '1':
            with MysqlTools().session_scope() as session:
                query_info = session.query(
                    BlockChainInfoModel.info_hash,
                    BlockChainInfoModel.transaction_hash,
                    BlockChainInfoModel.on_chain_info,
                    BlockChainInfoModel.user_id
                ).filter(
                    BlockChainInfoModel.participate_id == participate_id,
                    BlockChainInfoModel.on_chain_status == 1,
                    BlockChainInfoModel.deleted == False
                ).order_by(
                    BlockChainInfoModel.on_chain_at.desc()
                ).first()

                block_info = self.conn.eth.getTransaction(
                    query_info.transaction_hash
                )
                chain_info = json.loads(query_info.on_chain_info)

                response_dict['data'] = [
                    {
                        "key": "hash_data",
                        "value": query_info.info_hash
                    },
                    {
                        "key": "Txhash",
                        "value": query_info.transaction_hash
                    },
                    {
                        "key": "blockHash",
                        "value": "0x" + hexbytes_to_str(
                            block_info['blockHash'])
                    },
                    {
                        "key": "blockNumber",
                        "value": block_info.get('blockNumber', "")
                    },
                    {
                        "key": "transactionIndex",
                        "value": block_info.get('transactionIndex', "")
                    },
                    {
                        "key": "流水号",
                        "value": chain_info.get('id', "")
                    },
                    {
                        "key": "参与时间",
                        "value": time_transform_from_zone(
                            chain_info.get('created_at', ""), timezone)
                    },
                    {
                        "key": "参与注数",
                        "value": chain_info.get('bet_number', "")
                    },
                    {
                        "key": "支付币种",
                        "value": chain_info.get('pay_token', "")
                    },
                    {
                        "key": "支付数量",
                        "value": chain_info.get('pay_number', "")
                    },
                    {
                        "key": "参与期号",
                        "value": chain_info.get('game_serial', "")
                    },
                    {
                        "key": "用户名",
                        "value": chain_info.get('nick_name', "")
                    },
                    {
                        "key": "夺宝号码",
                        "value": json.loads(chain_info.get('award_numbers', "[]"))
                    }
                ]
        else:
            raise ValueError("Type not found.")

        return response_dict

    # 我的夺宝记录
    @staticmethod
    def user_block_recode(user_id, game_serial, page_num, page_limit, start_id,
                          timezone, instance_id):
        # response structure
        response_dict = {
            'limit': page_limit,
            'offset': page_num,
            'count': 0,
            'content': [
            ]
        }
        page_offset = get_offset_by_page(page_num, page_limit)
        page_limit = str(page_limit)

        # query info
        with MysqlTools().session_scope() as session:
            query = session.query(
                BlockChainInfoModel._id,
                BlockChainInfoModel.game_serial,
                BlockChainInfoModel.participate_id,
                BlockChainInfoModel.on_chain_info,
                BlockChainInfoModel.on_chain_at
            ).filter(
                BlockChainInfoModel.user_id == user_id,
                BlockChainInfoModel.on_chain_status == 1,
                BlockChainInfoModel.deleted == False
            ).order_by(
                BlockChainInfoModel.on_chain_at.desc()
            )

            # 计算不分页的总页数
            record_count = query.count()
            response_dict['count'] = get_page_by_offset(record_count,
                                                        page_limit)

            if game_serial is not None:
                query = query.filter(
                    BlockChainInfoModel.game_serial == game_serial)

            if instance_id is not None:
                query = query.filter(
                    BlockChainInfoModel.game_serial == instance_id)

            if start_id is not None:
                start_id = str(start_id)
                query = query.filter(
                    BlockChainInfoModel._id < start_id)

            query = query.limit(page_limit).offset(
                page_offset)

            record_list = query.all()

            for one_record in record_list:
                on_chain_info = json.loads(one_record.on_chain_info)
                response_dict['content'].append({
                    'id': one_record._id,
                    "game_serial": one_record.game_serial,
                    "participate_id": one_record.participate_id,
                    "bet_number": on_chain_info.get("bet_number", ""),
                    "on_chain_at": time_transform_from_zone(
                        one_record.on_chain_at.strftime("%Y-%m-%d %H:%M:%S"),
                        timezone)
                })

            return response_dict

    # 最新上链信息
    @staticmethod
    def newest_online_record(
            game_serial, page_num, page_limit, start_id, record_type, timezone):
        # response structure
        response_dict = {
            'limit': page_limit,
            'offset': page_num,
            'count': 0,
            'content': [
            ]
        }
        page_offset = get_offset_by_page(page_num, page_limit)
        page_limit = str(page_limit)

        # query info
        with MysqlTools().session_scope() as session:
            query = session.query(
                BlockChainInfoModel._id,
                BlockChainInfoModel.instance_id,
                BlockChainInfoModel.record_type,
                BlockChainInfoModel.participate_id,
                BlockChainInfoModel.on_chain_info,
                BlockChainInfoModel.on_chain_at
            ).filter(
                BlockChainInfoModel.on_chain_status == 1,
                BlockChainInfoModel.deleted == False
            ).order_by(
                BlockChainInfoModel.on_chain_at.desc()
            )

            # 计算不分页的总页数
            record_count = query.count()
            response_dict['count'] = get_page_by_offset(record_count,
                                                        page_limit)

            if game_serial is not None:
                query = query.filter(
                    BlockChainInfoModel.game_serial == game_serial)

            if record_type is not None:
                query = query.filter(
                    BlockChainInfoModel.record_type == record_type)

            if start_id is not None:
                start_id = str(start_id)
                query = query.filter(
                    BlockChainInfoModel._id < start_id)

            query = query.limit(page_limit).offset(
                page_offset)

            record_list = query.all()

            for one_record in record_list:
                on_chain_info = json.loads(one_record.on_chain_info)
                response_dict['content'].append({
                    'id': one_record._id,
                    'instance_id': one_record.instance_id,
                    "record_type": RECORD_TYPE_DICT[one_record.record_type],
                    "nick_name": on_chain_info.get("nick_name", ""),
                    "bet_number": on_chain_info.get("bet_number", ""),
                    "participate_id": one_record.participate_id,
                    "on_chain_at": time_transform_from_zone(
                        one_record.on_chain_at.strftime("%Y-%m-%d %H:%M:%S"),
                        timezone)
                })

            return response_dict
