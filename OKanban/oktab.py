# coding: utf-8

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QGraphicsOpacityEffect, QAction, qApp
from PyQt5.QtCore import Qt

class OKTab(QWidget):
    '''Tableau des kanbans
    '''
    def __init__(self, parent = None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        self.setStyleSheet('background-color: darkCyan;')
        self.label = QLabel("le tableau des kanbans", self, alignment = Qt.AlignCenter)
        