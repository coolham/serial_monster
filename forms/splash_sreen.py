import time
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSplashScreen



class SplashScreen(QSplashScreen):
    def __init__(self, splash_pic):
        super(SplashScreen, self).__init__(QPixmap(splash_pic))  #启动程序的图片

    #效果 fade =1 淡入   fade= 2  淡出，  t sleep 时间 毫秒
    def effect(self):
        self.setWindowOpacity(0)
        t = 0
        while t <= 50:
            newOpacity = self.windowOpacity() + 0.02     #设置淡入
            if newOpacity > 1:
                break

            self.setWindowOpacity(newOpacity)
            self.show()
            t -= 1
            time.sleep(0.04)

        time.sleep(1)
        t = 0
        while t <= 50:
            newOpacity = self.windowOpacity() - 0.02         #设置淡出
            if newOpacity < 0:
                break

            self.setWindowOpacity(newOpacity)
            t += 1
            time.sleep(0.04)

