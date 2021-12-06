# coding: utf-8

from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt

from .qtutils import Qutil
import OKanban.okanban_app as OK_app #Evite circular import
from .bdd import BddOKanbans
from .okanban import OKanban

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
        self.layout = QVBoxLayout(self)

    def load(self):
        '''Load or update
        '''
        if self.bdd is None:
            self.connect()
        for kanban in self.bdd.get_kanbans():
            o_kanban = OKanban(kanban.get('id'))
            self.layout.addWidget(o_kanban)
            o_kanban.load()
        self.layout.addStretch()
            

        

