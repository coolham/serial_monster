import random
import time
import threading
import random
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, QTimer
from PyQt5.QtChart import QChartView
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QApplication, QMainWindow, QLCDNumber, QMessageBox
from PyQt5.QtWidgets import QVBoxLayout, QSizePolicy


from designer.w_setup import Ui_SetupForm


class SetupForm(QWidget, Ui_SetupForm):
    """
    Class documentation goes here.
    """

    def __init__(self, parent=None, top_window=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(SetupForm, self).__init__(parent)
        self.setupUi(self)

        self.init_view()

    def init_view(self):
        pass

    def release_resource(self):
        print("setup form release resource")


