import pika
import sys
import datetime
from multiprocessing import Pool
from email.mime.text import MIMEText
from email.header import Header
import smtplib

mq_config = {
    "username": "hqbuser",
    "password": "", # 密码为rabbit的密码，部署到线上时不能在这里暴露出来！！！
    "host": "172.17.98.149",
    "port": 5672,
    "vhost": {
        "/mine_dev": {
            "dev_queue": 2,  # Values control the number of processes, You may configure multiple key!
        },
        "/mine_pro": {
            "pro_queue": 1,
        },
        "/mine_test": {
            "test_queue": 1,  # This is default 5,temp change to 1.
        },

    },
    "queuename_2_filename": {
        'rs_error': 'errors.log',
        'rs_info': 'info.log',
        'ess_error': 'ess_errors.log',
        'ess_info': 'ess_info.log',
        'match_error': 'match_errors.log',
        'match_info': 'match_info.log',
        'payback_error': 'payback_errors.log',
        'payback_info': 'payback_info.log',
        'repay_error': 'repay_errors.log',
        'repay_info': 'repay_info.log',
    },
    "local_save_dir": "/data/logs/mq/",
    "email": {
        "name": "Mq exception reports",
        "ip": "10.10.105.185",
        "port": "80",
        "email_user": "232227686@qq.com",
        "email_pwd": "dituffpgdssmbjcd",
        "email_subject": "Mq exception reports",
        "email_to": [
            "wangye@hiqianbao.com",
            "liuwei@hiqianbao.com",
            "chenym@hiqianbao.com"
        ]
    }
}


def get_pika_mq_parameters(vhost):
    """
    Configure the mq link parameters
    :param vhost:
    :return:
    """
    credentials = pika.PlainCredentials(mq_config["username"], mq_config["password"])
    parameters = pika.ConnectionParameters(mq_config["host"], mq_config["port"], vhost, credentials)
    return parameters


def consume_call(vhost=None, queue=None, callback=None):
    """
    Consumer object
    :param vhost:
    :param queue:
    :param callback:
    :return:
    """
    if not vhost:
        vhost = list(mq_config["vhost"].keys())[0]
    if not queue:
        queue = list(mq_config["vhost"][vhost].keys())[0]
    if not callback:
        callback = globals().get("__callback_log")
    connection = pika.BlockingConnection(get_pika_mq_parameters(vhost))
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_consume(callback, queue=queue)
    channel.basic_qos(prefetch_count=1)
    try:
        channel.start_consuming()
    except Exception as e:
        pass


def consume_call_mult():
    """
    Consumer object mult
    :return:
    """
    if len(sys.argv) > 1:
        if sys.argv[1] != 'server':
            exit(0)

    process_count = 0

    for item in mq_config["vhost"].keys():
        for _, v in mq_config["vhost"][item].items():
            process_count += v

    if process_count == 0:
        except_process("process_count sum equal to 0")
        exit(0)

    pool = Pool(processes=process_count)

    for vhost, v in mq_config["vhost"].items():
        for queue in v.keys():
            pool.apply_async(consume_call, args=(vhost, queue, __callback_log))

    pool.close()
    pool.join()


def __callback_log(ch, method, properties, body):
    """
    Mq callbacks are logged to local files
    :param ch:
    :param method:
    :param properties:
    :param body:
    :return:
    """

    queue_name = method.routing_key if hasattr(method, 'routing_key') else ""
    try:
        vhost = ch._impl.connection.params.virtual_host
    except:
        vhost = ""

    if not (queue_name and vhost):
        except_process("Get queue_name or vhost, and there is an exception!")
    else:
        message = body
        if local_save_log(vhost, message):
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            pass


def local_save_log(vhost, msg):
    """
    Mq messages are saved locally
    :param vhost:
    :param queue_name:
    :param message:
    :return:
    """
    msg = str(msg, encoding='utf-8') if isinstance(msg, bytes) else msg
    try:
        file_name = mq_config["queuename_2_filename"][msg[msg.rfind("===") + 3:]]
        put_file(detect_file(vhost, file_name), msg)
        return True
    except Exception as e:
        except_process("Cache local file, there is an exception! " + str(e))
    return False


def detect_file(vhost="/mq_log", file_name="mq_errors.log"):
    """
    Monitor and build files if not exists
    :param vhost:
    :param file_name:
    :return:
    """
    import os
    if len(sys.argv) == 1:
        dir_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), mq_config["local_save_dir"].split("data/")[1], vhost[1:] if vhost[0] == "/" else vhost))
    else:
        dir_path = os.path.abspath(os.path.join(mq_config["local_save_dir"], vhost[1:] if vhost[0] == "/" else vhost))

    file_path = os.path.abspath(os.path.join(dir_path, file_name))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        if not os.path.isfile(file_path):
            file = open(file_path, "w")
            file.close()

    return file_path


def put_file(file_name, msg):
    """
    write file append
    :param file_name:
    :param msg:
    :return:
    """
    with open(file_name, 'a')as f:
        f.writelines(msg + '\n')


def except_process(msg):
    """
    except process
    :param msg:
    :return:
    """
    msg = str(datetime.datetime.utcnow())[:-4] + " " + msg
    send_mail(msg)
    put_file(detect_file(), msg)


def send_mail(mail_body):
    """
    Need to config mq_config["email_to"],to define the receiver
    :param msg:
    :return:
    """
    website_data = mq_config["email"]
    _user = website_data['email_user']
    _pwd = website_data['email_pwd']
    _to = website_data['email_to']
    _subject = website_data['email_subject']

    msg = MIMEText(mail_body, 'html', 'utf-8')

    msg['Subject'] = Header(_subject, "utf-8")
    msg["From"] = _user
    msg["To"] = Header(",".join(_to), 'utf-8')

    # try:
    s = smtplib.SMTP_SSL("smtp.qq.com", 465)
    s.login(_user, _pwd)
    s.sendmail(_user, _to, msg.as_string())
    s.quit()


if __name__ == "__main__":
    # If the python3 mq_consume_script.py server needs to be executed this way while running on the server,
    # if no parameters are added, the logs directory is created in the directory where the current file is located
    consume_call_mult()
    pass
