# coding: utf-8

from PyQt5.QtWidgets import  QWidget, QLabel, QHBoxLayout, QVBoxLayout, QTableView, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from .pandas_model import PandasModel
import pandas as pd
from .bdd import BddOKanbans
import logging

class OKParams(QWidget):
    '''paramètres pour kanbans
    '''
    def __init__(self, parent = None):
        super().__init__(parent)
        self.font = QFont('Ubuntu', 18)
        self.bdd = BddOKanbans('192.168.0.11')#TODO remonter ça en haut
        self.initUI()
        self.load()
        
    def load(self):
        '''Load datas
        '''
        df = pd.DataFrame(self.bdd.get_params())
        df = df.drop('_id', axis=1)
        logging.debug(df)
        model = PandasModel(df)
        self.table.setModel(model)
    
    def initUI(self):
        self.setStyleSheet('background-color: yellow;')
        self.layout = QVBoxLayout(self)
        title_layout = QHBoxLayout()
        self.label = QLabel("Les paramètres", self, alignment = Qt.AlignLeft)
        self.label.setFont(self.font)
        title_layout.addWidget(self.label)
        button = QPushButton("MAJ")
        button.clicked.connect(self.load)
        title_layout.addWidget(button)
        self.layout.addLayout(title_layout)
        self.table = QTableView (self)
        self.table.setSortingEnabled(True)
        self.layout.addWidget(self.table)






