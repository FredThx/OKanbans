# coding: utf-8
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox, QApplication, QWidget, QPushButton


class TimerMessageBox(QMessageBox):
    ''' A Popup Message box with with autoclose timeout
    '''
    def __init__(self, text = "", timeout=3, parent=None):
        '''
            text     :   str. can contain "{time_to_wait}" to show the time counter.
            timeout :   in seconds
        '''
        super(TimerMessageBox, self).__init__(parent)
        self.setWindowTitle("wait")
        self.time_to_wait = timeout
        self.msgtext = text
        self.setText(self.msgtext.format(time_to_wait = self.time_to_wait))
        self.setStandardButtons(QMessageBox.NoButton)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.changeContent)
        self.timer.start()

    def changeContent(self):
        self.time_to_wait -= 1
        self.setText(self.msgtext.format(time_to_wait = self.time_to_wait))
        if self.time_to_wait <= 0:
            self.close()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()


if __name__ == '__main__':
    class Example(QWidget):
        def __init__(self):
            super(Example, self).__init__()
            btn = QPushButton('Test me', self)
            btn.resize(btn.sizeHint())
            btn.move(50, 50)
            self.setWindowTitle('Example')
            btn.clicked.connect(self.warning)
        def warning(self):
            messagebox = TimerMessageBox("Attends {time_to_wait} secondes", 5, self)
            messagebox.exec_()

    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())
