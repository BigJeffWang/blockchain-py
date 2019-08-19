from config import get_mongodb_conf
from pymongo import MongoClient


class MongodbTools(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conf = get_mongodb_conf()
        self.client = self.mongodb_client()
        self.db = self.client[self.conf.get("database")]

    def mongodb_client(self):
        host = self.conf.get('host')
        port = self.conf.get('port')
        username = self.conf.get('username')
        password = self.conf.get('password')

        database_url = host + ":" + str(port)
        if username and password:
            database_url = username + ":" + password + "@" + database_url
        uri = "mongodb://" + database_url
        client = MongoClient(uri)
        return client

    def collection(self, collect):
        return self.db[self.conf.get(collect)]


if __name__ == "__main__":
    mongodb = MongodbTools()
    eth = mongodb.collection("ETH")
    res = eth.find_one({'_id': 1})
    print(res)
    # with mongodb.client.start_session() as session:
    #     eth = mongodb.collection("WalletEthModel")
    #     res = eth.find_one({'_id': 1}, session=session)
    #     print(res)
