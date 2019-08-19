import pika
import config


def get_mq_parameters():
    conf = config.get_conf('mq')
    credentials = pika.PlainCredentials(conf["user_name"], conf["password"])
    parameters = pika.ConnectionParameters(conf["host"],
                                           5672,
                                           conf["vhost"],
                                           credentials)
    return parameters, conf['queue']




