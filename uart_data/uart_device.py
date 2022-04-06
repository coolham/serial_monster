import logging
import serial
from utils.configs import ParamConfig



class UartDevice():
    def __init__(self):
        self.logger = logging.getLogger('Uart')
        self.serial_port = None
        self.cur_port = ''
        self.baud_rate = 0
        self.port_open = False
        self.port_time_out = 5

    def open(self, port, baud_rate):
        self.cur_port = port
        self.baud_rate = baud_rate
        try:
            self.serial_port = serial.Serial(self.cur_port, self.baud_rate, timeout=self.port_time_out)
        except Exception as e:
            self.logger.error(f'open {self.cur_port} failed')
            return False
        self.port_open = True
        msg = f'open {self.cur_port} success'
        self.logger.info(msg)
        return True

    def in_waiting(self):
        if self.serial_port:
            return self.serial_port.in_waiting
        return -1

    def read(self):
        data = self.serial_port.read(self.serial_port.in_waiting)
        return data
    def write(self, data):
        self.serial_port.write(data)

    def close(self):
        self.serial_port.close()
        self.logger.info(f'serial {self.serial_port} closed.')