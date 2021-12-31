import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, qApp, QWidget, QAction, QStackedWidget, QVBoxLayout, QScrollArea, QLabel
#from PyQt5.QtGui import x
from PyQt5.QtCore import QTimer, QThread, QObject, Qt

app = QApplication([])
w = QLabel("Salut")
w.show()
if __name__ == '__main__':
    sys.exit(app.exec_())