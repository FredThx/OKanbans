# coding: utf-8

from PyQt5.QtWidgets import QWidget, QLabel,  QGridLayout, QLineEdit, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class OKES(QWidget):
    '''Tableau des kanbans
    '''
    def __init__(self, parent = None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        self.font = QFont('Ubuntu', 36)
        self.layout = QGridLayout()
        #self.setStyleSheet(self.style_sheet)
        self.setLayout(self.layout)

        
    
class OKInput(OKES):
    '''Une zone de saisie d'entree en stock
    '''
    style_sheet = 'background-color: Yellow;'

    def __init__(self, parent = None):
        self.title = "Zone d'entrée"
        super().__init__(parent)
    
    def initUI(self):
        super().initUI()
        #Ligne 1 : Référence
        label_ref = QLabel("Référence :")
        label_ref.setFont(self.font)
        self.layout.addWidget(label_ref, 0,0)
        self.edit_reference = QLineEdit()
        self.edit_reference.setFont(self.font)
        self.layout.addWidget(self.edit_reference,0,1)
        #Ligne 2 : Qté
        label_qty = QLabel("Quantité :")
        label_qty.setFont(self.font)
        self.layout.addWidget(label_qty, 1,0)
        self.edit_qty = QLineEdit()
        self.edit_qty.setFont(self.font)
        self.layout.addWidget(self.edit_qty,1,1)
        #Ligne 3 : Boutons
        bt = QPushButton("Imprimer")
        bt.setFont(self.font)
        self.layout.addWidget(bt,2,1)
        #

class OKOutput(OKES):
    '''Une zone de saisie de Sortie
    '''
    style_sheet = 'background-color: darkMagenta;'

    def __init__(self, parent = None):
        self.title = "Zone de sortie"
        super().__init__(parent)

    def initUI(self):
        super().initUI()
        #Ligne 1 : n° Kanban
        label_ref = QLabel("N° de kanban :")
        label_ref.setFont(self.font)
        self.layout.addWidget(label_ref, 0,0)
        self.edit_kanban = QLineEdit()
        self.edit_kanban.setFont(self.font)
        self.layout.addWidget(self.edit_kanban,0,1)
        #Ligne 2 : Qté
        label_qty = QLabel("Quantité à enlever:")
        label_qty.setFont(self.font)
        self.layout.addWidget(label_qty, 1,0)
        self.edit_qty = QLineEdit()
        self.edit_qty.setFont(self.font)
        self.layout.addWidget(self.edit_qty,1,1)
        #Ligne 3 : Boutons
        bt = QPushButton("Ok")
        bt.setFont(self.font)
        self.layout.addWidget(bt,2,1)
        #