# coding: utf-8

from PyQt5.QtWidgets import QVBoxLayout,QHBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt

from .qtutils import Qutil
import OKanban.okanban_app as OK_app #Evite circular import
from .bdd import BddOKanbans
from .okanban import OKanban, EmptyOKanban

class OKTab(QWidget):
    '''Tableau des kanbans
    '''
    def __init__(self, parent = None):
        super().__init__(parent)
        self.bdd = None
        self.initUI()
    
    def connect(self):
        '''Connecte the database'''
        if not self.bdd:
            self.bdd = Qutil.get_parent(self, OK_app.OKanbanApp).bdd

    def initUI(self):
        self.layout = QHBoxLayout(self)

    def load(self):
        '''Load or update
        '''
        if self.bdd is None:
            self.connect()
        for produit in self.bdd.get_references():
            ok_produit = OKProd(produit)
            self.layout.addWidget(ok_produit)
            ok_produit.load()
        self.layout.addStretch()
            

class OKProd(QWidget)        :
    ''' Un colonne contenant un produit
    '''
    def __init__(self, data, parent = None):
        super().__init__(parent)
        self.bdd = None
        self.data = data
        self.initUI()
    
    def connect(self):
        '''Connecte the database'''
        if not self.bdd:
            self.bdd = Qutil.get_parent(self, OK_app.OKanbanApp).bdd

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.lb_proref = QLabel(self.data.get('proref'))
        self.layout.addWidget(self.lb_proref)

    def load(self):
        '''Load or update
        '''
        if self.bdd is None:
            self.connect()
        nb_kanbans = 0
        for kanban in self.bdd.get_kanbans(proref=self.data.get('proref')):
            o_kanban = OKanban(kanban.get('id'))
            self.layout.addWidget(o_kanban)
            o_kanban.load()
            nb_kanbans +=1
        for i in range(nb_kanbans, self.data.get('nb_max',0)):
            o_kanban = EmptyOKanban(proref = self.data.get('proref'))
            self.layout.addWidget(o_kanban)
            o_kanban.load()#ne fait rien
        self.layout.addStretch()   

