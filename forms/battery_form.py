import logging
import random
import time
import threading
import random
import serial
import serial.tools.list_ports
from threading import Thread
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, QTimer
from PyQt5.QtChart import QChartView
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget
from utils.configs import ParamConfig
from designer.w_battery import Ui_BatteryForm
import global_var
from uart_data.uart_device import UartDevice


class BatteryForm(QWidget, Ui_BatteryForm):
    """
    Class documentation goes here.
    """

    def __init__(self, parent=None, top_window=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(BatteryForm, self).__init__(parent)
        self.setupUi(self)
        self.__exit_flag = False
        self.logger = logging.getLogger('Data')
        self.config = ParamConfig()
        self.status_queue = global_var.get_value('status_queue')
        self.port_params = self.config.get_uart_params()
        self.uart_data_queue = global_var.get_value('uart_data_queue')
        self.cur_port = ''
        self.baud_rate = 0
        self.port_open = False
        self.uart_device = UartDevice()
        self.init_view()
        self.data_thread = Thread(name='data_thread', target=self.recv_data_thread)
        self.data_thread.start()

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
        self.lblBat1.setText('-')
        self.lblBat2.setText('-')
        self.lblBat3.setText('-')
        self.lblLight1.setText('-')

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
                self.btnPort.setText('关闭串口')
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

    def update_battery(self, values):
        for data_dict in values:
            if 'BAT1' in data_dict:
                self.pbBat1.setValue(data_dict['BAT1'])
                self.lblBat1.setText(f"{data_dict['BAT1']}%")
            if 'BAT2' in data_dict:
                self.pbBat2.setValue(data_dict['BAT2'])
                self.lblBat2.setText(f"{data_dict['BAT2']}%")
            if 'BAT3' in data_dict:
                self.pbBat3.setValue(data_dict['BAT3'])
                self.lblBat3.setText(f"{data_dict['BAT3']}%")
            if 'LIGHT1' in data_dict:
                self.pbLight.setValue(data_dict['LIGHT1'])
                self.lblLight1.setText(f"{data_dict['LIGHT1']}%")


    def recv_data_thread(self):
        while True:
            if self.__exit_flag:
                break
            # if self.uart_data_queue.empty():
            #     continue
            # data_dict = self.uart_data_queue.get()
            if self.port_open and self.uart_device.in_waiting():
                data = self.uart_device.read()
                self.status_queue.put(data.decode('utf-8'))
                print(f'recv: {data}')
                data_s = data.decode('utf-8')
                d_list = data_s.split('\n')
                values = []
                for item in d_list:
                    if item:
                        one_v = {}
                        kvs = item[5:].split('=')
                        one_v[kvs[0]] = int(kvs[1])
                        values.append(one_v)
                print(f'values: {values}')
                if len(values) > 0:
                    self.update_battery(values)
            time.sleep(0.1)
        print(f'recv_data_thread exit.')

    def send_status_msg(self, msg):
        self.status_queue.put(msg)

    def release_resource(self):
        if self.port_open:
            self.uart_device.close()
        self.__exit_flag = True
        self.data_thread.join()
        print("data form release resource")