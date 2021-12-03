# coding: utf-8

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QGraphicsOpacityEffect, QAction, qApp
from PyQt5.QtCore import Qt

class OKParams(QWidget):
    '''paramètres pour kanbans
    '''
    def __init__(self, parent = None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        self.setStyleSheet('background-color: yellow;')
        self.label = QLabel("Les paramètres", self, alignment = Qt.AlignCenter)
        