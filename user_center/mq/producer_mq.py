import pika
from mq.mq_utils import get_mq_parameters


def produce_object(message, queue):
    try:
        mq_conf, mq_queue = get_mq_parameters()
        connection = pika.BlockingConnection(mq_conf)
        channel = connection.channel()
        if queue is None:
            queue = mq_queue
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_publish(exchange='',
                              routing_key=queue,
                              body=message,
                              properties=pika.BasicProperties(
                                  delivery_mode=2,  # make message persistent
                              ))
        connection.close()
    except Exception as e:
        # print("exception", e)
        pass