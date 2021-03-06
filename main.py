import sys
import time
import logging
import logging.config
import global_var
from PyQt5.QtNetwork import QLocalSocket, QLocalServer
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal
import multiprocessing
from multiprocessing import Queue
from threading import Thread
from designer.w_main import Ui_MainWindow
from forms.setup_form import SetupForm
from forms.data_form import DataForm
from forms.battery_form import BatteryForm
from utils.set_log import setup_logging




HIDE_SETUP_TAB = True

status_queue = Queue(maxsize=100)
uart_data_queue = Queue(maxsize=100)
global_var.init()
global_var.set_value('status_queue', status_queue)
global_var.set_value('uart_data_queue', uart_data_queue)


class MyMainForm(QMainWindow, Ui_MainWindow):

    info_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)
        self.__exit_flag = False
        self.status_queue = global_var.get_value('status_queue')
        # check config file
        self.logger = logging.getLogger("Main")
        self.logger.info("start...")
        self.status_thread = Thread(name='status_thread', target=self.show_status_thread)
        self.status_thread.start()
        self.init_win()
        self.init_data_tab()
        self.init_setup_tab()
        self.tab_control()

    def init_win(self):
        self.setFixedSize(self.width(), self.height())
        self.setWindowTitle('Windows')

    def tab_control(self):
        tab_count = self.tabWidget.count()
        if HIDE_SETUP_TAB:
            self.tabWidget.removeTab(1)

    def init_data_tab(self):
        #self.data_form = DataForm()
        self.battery_form = BatteryForm()
        self.data_vLayout.addWidget(self.battery_form)

    def init_setup_tab(self):
        self.setup_form = SetupForm()
        self.setup_vLayout.addWidget(self.setup_form)

    def show_status_thread(self):
        while True:
            if self.__exit_flag:
                break
            if self.status_queue.empty():
                continue
            msg = status_queue.get()
            self.statusBar().showMessage(msg, msecs=5000)
            time.sleep(0.1)
        print(f'show_status_thread exit.')

    def release_resource(self):
        self.battery_form.release_resource()
        self.__exit_flag = True
        self.status_thread.join()
        print("release_resource finished.")


    def closeEvent(self, event):
        result = QMessageBox.question(self, "??????", "???????????????????",
                                      QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            self.release_resource()
            t_app = QApplication.instance()
            t_app.quit()
            print('app quit.')
        else:
            event.ignore()


if __name__ == '__main__':
    multiprocessing.freeze_support()

    setup_logging(default_path="./conf/logging.json")
    logging.info("main start...")

    try:
        app = QApplication(sys.argv)
        #app.setWindowIcon(QIcon('./icon/icon.ico'))
        serverName = 'testServer'
        socket = QLocalSocket()
        socket.connectToServer(serverName)
        # ???????????????????????????server??????????????????????????????????????????
        if socket.waitForConnected(500):
            app.quit()
        else:
            localServer = QLocalServer()  # ????????????????????????????????????
            localServer.listen(serverName)

            # splash = SplashScreen('./icon/splash.jpg')
            # splash.effect()
            app.processEvents()  # ??????????????????????????????????????????
            # ?????????
            myWin = MyMainForm()
            # ?????????????????????????????????
            myWin.show()

            # ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)

            # ???????????????sys.exit?????????????????????????????????
            sys.exit(app.exec_())
    except Exception as e:
        print("main start error:", e)
