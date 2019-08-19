import sys
import logging

from web3 import Web3
import pymysql

sys.path.append("..")
from config import get_private_block_chain_conf, get_mysql_conf

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
# set console level and formatter
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)


def blockchain_connect():
    uri = get_private_block_chain_conf()['uri']
    w3 = Web3(Web3.HTTPProvider(uri))
    return w3


def mysql_connect():
    mysql_paras = get_mysql_conf()
    host = mysql_paras.get('host')
    port = mysql_paras.get('port')
    database = mysql_paras.get('db')
    username = mysql_paras.get('user')
    password = mysql_paras.get('psd')

    # connect to mongodb
    conn = pymysql.connect(host=host, user=username, password=password,
                           db=database, port=port,
                           cursorclass=pymysql.cursors.DictCursor)
    return conn


def miner_start(conn, count=1):
    try:
        conn.miner.start(count)
    except Exception as e:
        logger.error(f"Miner failed, because: {e}")
        raise


def miner_stop(conn):
    node_status = conn.txpool.status
    pending = int(node_status.pending, 16)
    while pending:
        conn.miner.start(1)
        node_status = conn.txpool.status
        pending = int(node_status.pending, 16)
    conn.miner.stop()
    return


def wait_for_transaction_receipt(conn, transaction_hash):
    try:
        conn.eth.waitForTransactionReceipt(transaction_hash, timeout=600)
    except Exception as error:
        logging.error(f"On chain failed, because: {error}")
        raise


if __name__ == '__main__':

    # --- use for test ---
    # add new data
    # --------------------

    # from services import block_chain_info_service
    #
    # sv = block_chain_info_service.BlockChainInfoService()
    # sv.insert_block_chain_info("123", "123", 1, {"test": "hello"})
    # from services import block_chain_info_service
    #
    # sv = block_chain_info_service.BlockChainInfoService()
    # mysql_conn = mysql_connect()
    #
    # with mysql_conn.cursor() as cursor:
    #     query_sql = "SELECT info_hash FROM block_chain_info WHERE _id='%s'"
    #     update_sql = "UPDATE block_chain_info SET transaction_hash='%s' WHERE _id='%s'"
    #     for i in range(14, 72):
    #         print(i)
    #         cursor.execute(query_sql % i)
    #         result = cursor.fetchone()
    #
    #         response = sv.send_transaction(result['info_hash'])
    #
    #         cursor.execute(update_sql % (response['tx_hash'], i))
    #         mysql_conn.commit()
    
    mysql_conn = mysql_connect()
    try:
        # 查询最新的交易信息
        with mysql_conn.cursor() as cursor:
            sql = ('SELECT transaction_hash, on_chain_at FROM block_chain_info '
                   'WHERE deleted=0 AND on_chain_status=0 '
                   'ORDER BY on_chain_at DESC limit 1')
            cursor.execute(sql)
            result = cursor.fetchone()

            ON_CHAIN_AT = result['on_chain_at']

        # 开始挖矿
        block_conn = blockchain_connect()
        miner_start(block_conn)
        wait_for_transaction_receipt(block_conn, result['transaction_hash'])
        miner_stop(block_conn)
    except Exception as miner_error:
        logging.error(f"Failed, because: {miner_error}")
        mysql_conn.close()
        exit(0)

    # 将成功挖矿的数据进行数据库修改
    try:
        with mysql_conn.cursor() as cursor:
            update_sql = ('UPDATE block_chain_info '
                          'SET on_chain_status=1 '
                          'WHERE deleted=0 AND '
                          'on_chain_status=0 AND '
                          'on_chain_at <= ON_CHAIN_AT ')
            cursor.execute(update_sql)
            mysql_conn.commit()
    except Exception as update_error:
        mysql_conn.rollback()
        logger.error(f"Update database failed, because: {update_error}")
    finally:
        mysql_conn.close()

    logger.info("Success!")
