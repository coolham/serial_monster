import os
import logging
from configparser import ConfigParser, NoSectionError, NoOptionError




def singleton(cls, *args, **kwargs):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return _singleton


@singleton
class ParamConfig(object):

    def __init__(self):
        self.logger = logging.getLogger('Main.Conf')
        self.cur_path = os.path.dirname(os.path.realpath(__file__))
        self.config_file = os.path.join(self.cur_path, '..', 'conf', 'config.ini')
        self.logger.info(f'read config file: {self.config_file}')
        self.cf = ConfigParser()
        ret_list = self.cf.read(self.config_file, encoding='utf-8')
        if len(ret_list) == 0:
            print(f'Error: can not read config file:{self.config_file}')
        self.section_uart = 'uart'

    def get_uart_params(self):
        port = self.cf.get(self.section_uart, 'port')
        baud_rate = self.cf.getint(self.section_uart, 'baud_rate')
        data_bits = self.cf.getint(self.section_uart, 'data_bits')
        parity = self.cf.get(self.section_uart, 'parity')
        stop_bits = self.cf.get(self.section_uart, 'stop_bits')
        uart_params = {
            'port': port,
            'baud_rate': baud_rate,
            'data_bits': data_bits,
            'parity': parity,
            'stop_bits': stop_bits
        }
        return uart_params


