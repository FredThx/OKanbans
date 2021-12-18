# coding: utf-8

import logging
import pandas as pd

from PyQt5.QtWidgets import  QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QMessageBox
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
        self.table.load(df)

    
    def initUI(self):
        #self.setStyleSheet('background-color: yellow;')
        self.layout = QVBoxLayout(self)
        title_layout = QHBoxLayout()
        self.label = QLabel(self.title, self, alignment = Qt.AlignLeft)
        self.label.setFont(self.font)
        title_layout.addWidget(self.label)
        button1 = QPushButton("Recharger les données")
        button1.clicked.connect(self.load)
        title_layout.addWidget(button1)
        button2 = QPushButton("Sauver les modifications")
        button2.clicked.connect(self.save)
        title_layout.addWidget(button2)
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
    
    def save(self):
        '''Save the data to the bdd
        '''
        logging.info(f"Save data : {self.table.df}")
        #Ajout & modifications
        for index, row in self.table.df.iterrows():
            self.bdd.set_params(row['param'], row['value'])
        #Suppression
        for o_param in self.bdd.get_params():
            param = o_param.get('param')
            if not param in self.table.df['param'].tolist():
                self.bdd.del_param(param)

class OKReferences(OKParams):
    '''Les références
    '''
    title = "Les produits"
    def get_datas(self):
        return self.bdd.get_references()

    def save(self):
        '''Save the data to the bdd
        '''
        logging.info(f"Save data : {self.table.df}")
        #Ajout et modifications
        result = True
        for index, row in self.table.df.iterrows():
            try:
                self.bdd.set_reference(row['proref'], int(row['qte_kanban_plein']), int(row['nb_max']), int(row['nb_alerte']))
            except ValueError:
                result = False
        #Suppression
        for o_rererence in self.bdd.get_references():
            proref = o_rererence.get('proref')
            if not proref in self.table.df['proref'].tolist():
                self.bdd.del_reference(proref)
        if not result: # Autre solution : des validators
            QMessageBox.warning(self, "Paramètres OKanbans", "Erreur dans les données : les valeurs doivent être des entiers")
        

