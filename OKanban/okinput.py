# coding: utf-8

import logging

from PyQt5.QtWidgets import QWidget, QLabel,  QGridLayout, QLineEdit, QPushButton
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtCore import Qt

from .qtutils import Qutil
import OKanban.okanban_app as OK_app #Evite circular import

class OKES(QWidget):
    '''Tableau des kanbans
    '''
    def __init__(self, parent = None):
        super().__init__(parent)
        self.bdd = None
        self.initUI()
    
    def initUI(self):
        self.font = QFont('Ubuntu', 36)
        self.layout = QGridLayout()
        #self.setStyleSheet(self.style_sheet)
        self.setLayout(self.layout)

    def connect(self):
        '''Connecte the database'''
        if not self.bdd:
            self.bdd = Qutil.get_parent(self, OK_app.OKanbanApp).bdd
    
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
        self.edit_reference.textChanged.connect(self.edit_reference_change)
        self.edit_reference.returnPressed.connect(self.bt_clicked)
        self.layout.addWidget(self.edit_reference,0,1)
        #Ligne 2 : Qté
        label_qty = QLabel("Quantité :")
        label_qty.setFont(self.font)
        self.layout.addWidget(label_qty, 1,0)
        self.edit_qty = QLineEdit()
        self.edit_qty.setFont(self.font)
        self.edit_qty.setValidator(QIntValidator())
        self.edit_qty.returnPressed.connect(self.bt_clicked)
        self.layout.addWidget(self.edit_qty,1,1)
        #Ligne 3 : Boutons
        bt = QPushButton("Création")
        bt.setFont(self.font)
        bt.clicked.connect(self.bt_clicked)
        self.layout.addWidget(bt,2,1)
    
    def bt_clicked(self):
        '''Création kanban selon champs complétés
        '''
        proref = self.edit_reference.text()
        qte = self.edit_qty.text()
        try:
            self.bdd.set_kanban(proref=proref, qte=qte)
        except AssertionError as e:
            logging.warning(e)
            #TODO : fenetre UI
        else:
            self.edit_reference.setText("")
            self.edit_qty.setText("")
    
    def edit_reference_change(self, text = ''):
        '''Quand le text est modifié : 
            changement de couleur si ref ok
            initialisation de la qté
        '''
        logging.debug(f"edit_reference_change : {text}")
        if text == '':
            style = ""
        elif len(self.bdd.get_references(text))==1:
            style = "background-color: green;"
            self.edit_qty.setText(str(self.bdd.get_references(text)[0].get('qte_kanban_plein')))
        else:
            style = "background-color: red;"
        self.edit_reference.setStyleSheet(style)
    

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