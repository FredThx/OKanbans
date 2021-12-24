# coding: utf-8

import logging

from PyQt5.QtWidgets import QWidget, QLabel,  QGridLayout, QLineEdit, QPushButton, QComboBox
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtCore import Qt

from .qtutils import Qutil
import OKanban.okanban_app as OK_app #Evite circular import

class OKES(QWidget):
    '''Tableau des kanbans
    '''
    def __init__(self, parent = None):
        super().__init__(parent)
        self.app = parent
        self.bdd = None
        self.initUI()

    def initUI(self):
        self.font = QFont('Ubuntu', 36) #TODO : mettre dans css
        self.layout = QGridLayout()
        #self.setStyleSheet(self.style_sheet)
        self.layout.setVerticalSpacing(20)
        self.layout.setHorizontalSpacing(20)
        self.setLayout(self.layout)

    def connect(self):
        '''Connecte the database'''
        if not self.bdd:
            self.bdd = Qutil.get_parent(self, OK_app.OKanbanApp).bdd
    load = connect

class OKInput(OKES):
    '''Une zone de saisie d'entree en stock
    '''
    style_sheet = 'background-color: Yellow;'

    def __init__(self, parent = None):
        self.title = "Zone d'entrée"
        super().__init__(parent)

    def connect(self):
        super().connect()
        self.update()

    def update(self):
        '''Update the comboBox
        '''
        self.combo_ref.clear()
        self.combo_ref.addItems([ref.get('proref') for ref in self.bdd.get_references()])
        self.edit_reference.clear()

    def initUI(self):
        super().initUI()
        #Ligne 1 : Référence
        label_ref = QLabel("Référence :")
        label_ref.setFont(self.font)
        self.layout.addWidget(label_ref, 0,0)
        self.combo_ref = QComboBox()
        self.combo_ref.setFont(self.font)
        self.edit_reference = QLineEdit()
        self.edit_reference.setFont(self.font)
        self.edit_reference.textChanged.connect(self.on_edit_reference_change)
        self.edit_reference.returnPressed.connect(self.on_bt_clicked)
        self.combo_ref.setLineEdit(self.edit_reference)
        self.layout.addWidget(self.combo_ref,0,1)
        #Ligne 2 : Qté
        label_qty = QLabel("Quantité :")
        label_qty.setFont(self.font)
        self.layout.addWidget(label_qty, 1,0)
        self.edit_qty = QLineEdit()
        self.edit_qty.setFont(self.font)
        self.edit_qty.setValidator(QIntValidator())
        self.edit_qty.returnPressed.connect(self.on_bt_clicked)
        self.layout.addWidget(self.edit_qty,1,1)
        #Ligne 3 : Boutons
        bt = QPushButton("Création")
        bt.setFont(self.font)
        bt.clicked.connect(self.on_bt_clicked)
        self.layout.addWidget(bt,2,1)

    def on_bt_clicked(self):
        '''Création kanban selon champs complétés
        '''
        proref = self.edit_reference.text()
        qte = int(self.edit_qty.text())
        try:
            id = self.bdd.set_kanban(proref=proref, qte=qte)
            self.app.print(id, proref, qte)
        except AssertionError as e:
            logging.warning(e)
            #TODO : fenetre UI
        else:
            self.edit_reference.setText("")
            self.edit_qty.setText("")

    def on_edit_reference_change(self, text = ''):
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
        self.label_id = QLabel("N° de kanban :")
        self.label_id.setFont(self.font)
        self.layout.addWidget(self.label_id, 0,0)
        self.edit_kanban = QLineEdit()
        self.edit_kanban.setFont(self.font)
        self.edit_kanban.setValidator(QIntValidator())
        self.edit_kanban.textChanged.connect(self.on_edit_kanban_change)
        self.edit_kanban.returnPressed.connect(self.on_bt_clicked)
        self.layout.addWidget(self.edit_kanban,0,1)
        #Ligne 3 : Qté
        label_qty = QLabel("Quantité à enlever:")
        label_qty.setFont(self.font)
        self.layout.addWidget(label_qty, 1,0)
        self.edit_qty = QLineEdit()
        self.edit_qty.setFont(self.font)
        self.edit_qty.setValidator(QIntValidator())
        self.edit_qty.returnPressed.connect(self.on_bt_clicked)
        self.layout.addWidget(self.edit_qty,1,1)
        #Ligne 4 : Boutons et proref
        self.label_proref = QLabel()
        self.label_proref.setFont(self.font)
        self.label_proref.setAlignment(Qt.AlignCenter)
        self.label_proref.setStyleSheet("color : green;")
        self.layout.addWidget(self.label_proref,2,0)
        bt = QPushButton("Ok")
        bt.setFont(self.font)
        bt.clicked.connect(self.on_bt_clicked)
        self.layout.addWidget(bt,2,1)



    def on_bt_clicked(self):
        '''Consommation du kanban
        '''
        id = int(self.edit_kanban.text())
        qte_a_enlever = int(self.edit_qty.text())
        qte_kanban = self.bdd.get_kanbans(id=id)[0].get('qte')
        try:
            self.bdd.set_kanban(id=id, qte=qte_kanban - qte_a_enlever)
        except AssertionError as e:
            logging.warning(e)
            #TODO : status
        else:
            self.edit_kanban.setText("")
            self.edit_qty.setText("")

    def on_edit_kanban_change(self, text = ''):
        '''Quand le text est modifié :
            changement de couleur si n° de kanban ok
            initialisation de la qté
        '''
        if text == '':
            style = ""
        elif len(self.bdd.get_kanbans(int(text)))==1:
            style = "background-color: green;"
            kanban = self.bdd.get_kanbans(id=int(text))[0]
            self.edit_qty.setText(str(kanban.get('qte')))
            self.label_proref.setText(kanban.get('proref'))
        else:
            style = "background-color: red;"
            self.edit_qty.setText('')
            self.label_proref.setText('')
        self.edit_kanban.setStyleSheet(style)
