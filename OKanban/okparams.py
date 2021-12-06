# coding: utf-8

import logging
import pandas as pd

from PyQt5.QtWidgets import  QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from .pandas_table import DFEditor
from .bdd import BddOKanbans
from .qtutils import Qutil
import OKanban.okanban_app as OK_app #Evite circular import

class OKParams(QWidget):
    '''paramètres pour kanbans
    '''
    def __init__(self, parent = None):
        super().__init__(parent)
        self.font = QFont('Ubuntu', 18)
        self.bdd = None
        self.initUI()

    def connect(self):
        '''Connecte the database'''
        if not self.bdd:
            self.bdd = Qutil.get_parent(self, OK_app.OKanbanApp).bdd

    def load(self):
        '''Load datas
        '''
        self.connect()        
        df = pd.DataFrame(self.get_datas())
        if not df.empty:
            df = df.drop('_id', axis=1)
        logging.debug(df)
        self.table.load(df)
    
    def initUI(self):
        #self.setStyleSheet('background-color: yellow;')
        self.layout = QVBoxLayout(self)
        title_layout = QHBoxLayout()
        self.label = QLabel(self.title, self, alignment = Qt.AlignLeft)
        self.label.setFont(self.font)
        title_layout.addWidget(self.label)
        button = QPushButton("MAJ")
        button.clicked.connect(self.load)
        title_layout.addWidget(button)
        self.layout.addLayout(title_layout)
        self.table = DFEditor(self)
        self.table.setStyleSheet('font-size: 18px;')
        #self.table.setSortingEnabled(True)
        self.layout.addWidget(self.table)

class OKGenParams(OKParams):
    '''les paramètres généraux
    '''
    title = "Les paramètres"
    def get_datas(self):
        return self.bdd.get_params()

class OKReferences(OKParams):
    '''Les références
    '''
    title = "Les produits"
    def get_datas(self):
        return self.bdd.get_references()


