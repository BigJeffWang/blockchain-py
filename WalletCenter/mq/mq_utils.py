import pika

from config import get_config


def get_mq_parameters():
    conf = get_config()
    mq_conf = conf["mq"][conf["env"]]
    credentials = pika.PlainCredentials(mq_conf["user_name"], mq_conf["password"])
    parameters = pika.ConnectionParameters(mq_conf["host"],
                                           mq_conf["port"],
                                           mq_conf["vhost"],
                                           credentials)
    return parameters


if __name__ == "__main__":
    print(get_mq_parameters())
