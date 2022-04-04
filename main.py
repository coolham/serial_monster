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
from utils.set_log import setup_logging




HIDE_SETUP_TAB = True

status_queue = Queue(maxsize=100)
global_var.init()
global_var.set_value('status_queue', status_queue)



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
        self.data_form = DataForm()
        self.data_vLayout.addWidget(self.data_form)

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

    def release_resource(self):
        print("release_resource")
        self.__exit_flag = True
        self.status_thread.join()

    def closeEvent(self, event):
        result = QMessageBox.question(self, "提示", "确认是否退出?",
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
        # 如果连接成功，表明server已经存在，当前已有实例在运行
        if socket.waitForConnected(500):
            app.quit()
        else:
            localServer = QLocalServer()  # 没有实例运行，创建服务器
            localServer.listen(serverName)

            # splash = SplashScreen('./icon/splash.jpg')
            # splash.effect()
            app.processEvents()  # ＃设置启动画面不影响其他效果
            # 初始化
            myWin = MyMainForm()
            # 将窗口控件显示在屏幕上
            myWin.show()

            # ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)

            # 程序运行，sys.exit方法确保程序完整退出。
            sys.exit(app.exec_())
    except Exception as e:
        print("main start error:", e)
