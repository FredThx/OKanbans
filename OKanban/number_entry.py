# coding: utf-8

import sys

from PyQt5.QtWidgets import QLayout, QWidget,  QHBoxLayout, QLineEdit, QPushButton, QApplication
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import pyqtSignal

from number_pad import numberPopup

class NumberEntry(QWidget):
    '''Un widget de saisie de numérique avec clavier visuel
    '''
    returnPressed = pyqtSignal()

    def __init__(self, parent = None, title = "Number", geometry = (130,320,400,300)):
        super().__init__(parent)
        self.title = title
        self.geometry = geometry
        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout()
        self.edit_line = QLineEdit()
        self.edit_line.setValidator(QIntValidator())
        self.edit_line.returnPressed.connect(self.on_validate)
        self.layout.addWidget(self.edit_line)
        self.button = QPushButton("...")
        self.button.clicked.connect(self.open_number_pad)
        self.button.adjustSize()
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

    def text(self):
        return self.edit_line.text()

    def open_number_pad(self):
        '''Open the keypad
        '''
        self.parent().setEnabled(False)
        self.exPopup = numberPopup(self.parent(),self.edit_line, "", self.on_validate)
        self.exPopup.setGeometry(*self.geometry)
        self.exPopup.show()

    def on_validate(self):
        '''When entre is pressed or keypad button pressed
        '''
        self.returnPressed.emit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QHBoxLayout()  
    number_entry = NumberEntry()
    def show():
        print(number_entry.text())
    number_entry.returnPressed.connect(show)
    layout.addWidget(number_entry)
    window.setLayout(layout)
    window.show()
    sys.exit(app.exec_())