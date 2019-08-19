import logging


class LPrint(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
        # set console level and formatter
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)
        self.logger.addHandler(console)

    def log(self, msg):
        self.logger.info(str(msg))
