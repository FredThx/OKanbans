# coding: utf-8

import sys

from PyQt5.QtWidgets import QLayout, QWidget,  QHBoxLayout, QLineEdit, QPushButton, QApplication
from PyQt5.QtGui import QIntValidator, QFont
from PyQt5.QtCore import pyqtSignal

from .number_pad import numberPopup

class NumberEntry(QWidget):
    '''Un widget de saisie de numérique avec clavier visuel
    '''
    returnPressed = pyqtSignal()
    textChanged = pyqtSignal(str)

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
        self.edit_line.textChanged.connect(self.on_textChanged)
        self.layout.addWidget(self.edit_line)
        self.button = QPushButton("...")
        self.button.setFixedWidth(50)#TODO : récupérer la taille de la font
        self.button.clicked.connect(self.open_number_pad)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

    def text(self):
        return self.edit_line.text()

    def setFocus(self):
        self.edit_line.setFocus()

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
        self.textChanged.emit(self.edit_line.text())
        self.returnPressed.emit()

    def on_textChanged(self):
        self.textChanged.emit(self.edit_line.text())

    def setFont(self, a0:QFont) -> None:
        self.edit_line.setFont(a0)
        self.button.setFont(a0)

    def setText(self, text) -> None:
        return self.edit_line.setText(text)

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
