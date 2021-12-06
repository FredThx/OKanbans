# coding: utf-8


from PyQt5.QtWidgets import  QFrame, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
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
        self.id = id
        self.font = QFont('Ubuntu', 8)
        self.bdd = None
        self._qte = 0
        self._proref = None
        self.initUI()

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

    def initUI(self):
        layout = QVBoxLayout(self)
        self.label_qte = QLabel()
        self.label_qte.setFont(self.font)
        layout.addWidget(self.label_qte)
        self.label_proref = QLabel()
        self.label_proref.setFont(self.font)
        layout.addWidget(self.label_proref)
        self.setFixedSize(80,50)

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


