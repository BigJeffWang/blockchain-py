import pika


from mq.mq_utils import get_mq_parameters


def produce_object(message, queue):
    try:
        connection = pika.BlockingConnection(get_mq_parameters())
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_publish(exchange='',
                              routing_key=queue,
                              body=message,
                              properties=pika.BasicProperties(
                                  delivery_mode=2,  # make message persistent
                              ))
        connection.close()
    except Exception as e:
        print("exception", e)
