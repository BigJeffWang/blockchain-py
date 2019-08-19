"""
本表用于存储用于区块链浏览器相关的信息

目前表的设计：
user_id          用户 id
instance_id      项目实例 id
record_type      记录类型
info_hash        信息 hash 值
transaction_hash 交易 hash 值
game_serial      期号
on_chain_status  上链状态
on_chain_at      上链时间
on_chain_info    上链信息
"""

import json
from datetime import datetime

from sqlalchemy import Column, String, DateTime, BigInteger
from sqlalchemy.dialects.mysql import TINYINT, LONGTEXT
from sqlalchemy.sql.expression import text

from models.base_model import BaseModel

RECORD_TYPE_DICT = {
    0: "揭晓信息",
    1: "夺宝记录",
    2: "发布信息"
}


class BlockChainInfoModel(BaseModel):
    __tablename__ = "block_chain_info"

    user_id = Column(String(64), nullable=False, server_default="",
                     comment="用户ID")
    instance_id = Column(String(64), nullable=False, server_default="",
                         comment="项目实例ID")
    record_type = Column(TINYINT(1), nullable=False, server_default=text("0"),
                         comment="记录类型 0-揭晓信息 1-夺宝记录 2-发布信息")
    info_hash = Column(String(256), nullable=False, server_default="",
                       comment="信息 hash 值")
    transaction_hash = Column(String(256), nullable=False, server_default="",
                              comment="交易 hash 值")
    game_serial = Column(String(64), nullable=False, server_default="",
                         comment="期号")
    participate_id = Column(BigInteger, nullable=False, server_default=text("-1"),
                            comment="投注 id")
    on_chain_status = Column(TINYINT(1), nullable=False,
                             server_default=text("0"),
                             comment="上链状态 0-失败 1-成功")
    on_chain_at = Column(DateTime, nullable=False, default=datetime.now,
                         comment="上链时间")
    on_chain_info = Column(LONGTEXT, comment="上链信息")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # store block information into database
    # First on_chain_info's type is dict, so you need serialize information.
    # Second store information into database.
    @staticmethod
    def store(session, user_id: str, instance_id: str, record_type: int,
              info_hash: str, on_chain_info: dict, transaction_hash: str,
              on_chain_at: str, game_serial: str, participate_id: str):
        # serialize information
        serialize_info = json.dumps(on_chain_info)

        # insert data
        data = BlockChainInfoModel(
            user_id=user_id,
            instance_id=instance_id,
            record_type=record_type,
            info_hash=info_hash,
            on_chain_info=serialize_info,
            transaction_hash=transaction_hash,
            on_chain_at=on_chain_at,
            game_serial=game_serial,
            participate_id=participate_id
        )
        session.add(data)
        session.commit()
        return
