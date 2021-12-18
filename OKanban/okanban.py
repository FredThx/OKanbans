# coding: utf-8

import logging

from PyQt5.QtWidgets import  QFrame, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, pyqtProperty
from PyQt5.QtGui import QFont

from .qtutils import Qutil
import OKanban.okanban_app as OK_app #Evite circular import
from .bdd import BddOKanbans

class OKanban(QFrame):
    '''Un kanban
    '''

    valueChanged = pyqtSignal(object)

    def __init__(self, id, parent = None):
        '''id : unique Id of the kanban
        '''
        super().__init__(parent)
        self.font = QFont('Ubuntu', 8)
        self.bdd = None
        self._qte = 0
        self._proref = None
        self.initUI()
        self.id = id
        self._alert = False
        self._alert_haut = False

    def __str__(self):
        return f"OKanban({self._proref}-{self._qte}-id={self._id})"

    @property
    def qte(self):
        return self._qte
    @qte.setter
    def qte(self, value):
        self._qte = value
        self.label_qte.setText(str(self._qte))
        self.valueChanged.emit(value)

    @property
    def proref(self):
        return self._proref
    @proref.setter
    def proref(self, value):
        self._proref = value
        self.label_proref.setText(self._proref)

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        self._id = value
        self.setToolTip(f"id:{self._id or 'vide'}")

    def initUI(self):
        layout = QHBoxLayout(self)
        #self.label_id = QLabel()
        #self.label_id.setFont(self.font)
        #layout.addWidget(self.label_id)
        self.label_qte = QLabel()
        self.label_qte.setFont(self.font)
        layout.addWidget(self.label_qte)
        self.label_proref = QLabel()
        self.label_proref.setFont(self.font)
        layout.addWidget(self.label_proref)
        #self.setFixedSize(80,60)

    def connect(self):
        '''Connecte the database'''
        if not self.bdd:
            self.bdd = Qutil.get_parent(self, OK_app.OKanbanApp).bdd

    def load(self):
        '''Read the database and get status => UI
        '''
        if self.bdd is None:
            self.connect()
        self.data = self.bdd.get_kanbans(self.id)[0]
        self.qte = self.data.get('qte')
        self.proref = self.data.get('proref')
    
    @pyqtProperty(bool)
    def alert(self):
        return self._alert
    
    @alert.setter
    def alert(self, value):
        self._alert = value
    
    @pyqtProperty(bool)
    def alert_haut(self):
        return self._alert_haut
    
    @alert_haut.setter
    def alert_haut(self, value):
        self._alert_haut = value

class EmptyOKanban(OKanban):
    '''Un kanban vide
    '''
    def __init__(self, proref, parent = None):
        super().__init__(None)
        self.proref = ""#proref
        self.qte = ""#0
        self.id = 0
        
    def __str__(self):
        return "EmptyOKanban"

    def load(self):
        if self.bdd is None:
            self.connect()    
    