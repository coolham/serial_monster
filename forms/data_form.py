import logging
import random
import time
import threading
import random
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, QTimer
from PyQt5.QtChart import QChartView
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget
from utils.configs import ParamConfig
from designer.w_data import Ui_DataForm
import global_var
from uart_data.uart_device import UartDevice


class DataForm(QWidget, Ui_DataForm):
    """
    Class documentation goes here.
    """

    def __init__(self, parent=None, top_window=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(DataForm, self).__init__(parent)
        self.setupUi(self)
        self.logger = logging.getLogger('Data')
        self.config = ParamConfig()
        self.status_queue = global_var.get_value('status_queue')
        self.port_params = self.config.get_uart_params()
        self.status_queue = global_var.get_value('status_queue')
        self.cur_port = ''
        self.baud_rate = 0
        self.port_open = False
        self.uart_device = UartDevice()
        self.init_view()

    def init_view(self):
        port_list = self.query_port()
        for port in port_list:
            self.cmbPort.addItem(port)
        self.cmbPort.setCurrentText(self.port_params['port'])
        self.cmbBaudRate.setCurrentText(str(self.port_params['baud_rate']))
        self.cmbDataBits.setCurrentText(str(self.port_params['data_bits']))
        self.cmbParity.setCurrentText(str(self.port_params['parity']))
        self.cmbStopBits.setCurrentText(str(self.port_params['stop_bits']))
        self.btnPort.clicked.connect(self.btn_port_click)

    def query_port(self):
        port_list = list(serial.tools.list_ports.comports())
        port_list_name = []
        if len(port_list) <= 0:
            self.logger.info(f'can not find serial port')
            return
        else:
            for each_port in port_list:
                port_list_name.append(each_port[0])
        self.logger.info(port_list_name)
        return port_list_name

    def btn_port_click(self):
        self.cur_port = self.cmbPort.currentText()
        self.baud_rate = int(self.cmbBaudRate.currentText())
        port_time_out = 5
        if not self.port_open:
            if self.uart_device.open(self.cur_port, self.baud_rate):
                self.port_open = True
                msg = f'open port success'
            else:
                self.port_open = False
                msg = f'open port failed'
            self.logger.info(msg)
        else:
            self.uart_device.close()
            self.port_open = False
            self.btnPort.setText('打开串口')
            msg = f'close {self.cur_port}'
            self.logger.info(msg)
            self.status_queue.put(msg)

    def send_status_msg(self, msg):
        self.status_queue.put(msg)

    def release_resource(self):
        if self.port_open:
            self.serial_port.close()
        print("data form release resource")