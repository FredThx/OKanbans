# coding: utf-8

import logging, time

from PyQt5.QtWidgets import QWidget, QLabel,  QGridLayout, QLineEdit, QPushButton, QComboBox, QHBoxLayout, QCheckBox, QVBoxLayout
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtCore import Qt

from .qtutils import Qutil
import OKanban.okanban_app as OK_app #Evite circular import
from .number_entry import NumberEntry
from .timer_message_box import TimerMessageBox

class OKES(QWidget):
    '''Tableau des kanbans
    '''
    def __init__(self, parent = None):
        super().__init__(parent)
        self.app = parent
        self.bdd = None
        self.auto = True
        self.initUI()

    def initUI(self):
        self.font = QFont('Ubuntu', 36) #TODO : mettre dans css
        main = QVBoxLayout()
        self.layout = QGridLayout()
        self.layout.setVerticalSpacing(20)
        self.layout.setHorizontalSpacing(20)
        main.addLayout(self.layout)
        self.check_auto = QCheckBox("Automatique")
        self.check_auto.setFont(self.font)
        self.check_auto.setCheckState(self.auto)
        self.check_auto.setTristate(False)
        self.check_auto.stateChanged.connect(self.change_auto)
        main.addWidget(self.check_auto)
        main.addStretch()
        self.setLayout(main)


    def stretch(self):
        '''Add stretch bottom and right
        '''
        self.layout.setRowStretch(self.layout.rowCount(),1)
        self.layout.setColumnStretch(self.layout.columnCount(),1)

    def connect(self):
        '''Connecte the database'''
        if not self.bdd:
            self.bdd = Qutil.get_parent(self, OK_app.OKanbanApp).bdd

    def load(self):
        self.connect()

    def change_auto(self, state):
        if state == Qt.Checked:
            self.auto = True
        else:
            self.auto = False
    def on_validate(self):
        if self.auto:
            self.on_bt_clicked()



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
        layout_ref = QHBoxLayout()
        self.combo_ref = QComboBox()
        self.combo_ref.setFont(self.font)
        self.edit_reference = QLineEdit()
        self.edit_reference.setFont(self.font)
        self.edit_reference.textChanged.connect(self.on_edit_reference_change)
        self.edit_reference.returnPressed.connect(self.on_validate)
        self.combo_ref.setLineEdit(self.edit_reference)
        layout_ref.addWidget(self.combo_ref)
        button_raz = QPushButton("RAZ")
        button_raz.setFont(self.font)
        button_raz.clicked.connect(self.raz)
        layout_ref.addWidget(button_raz)
        self.layout.addLayout(layout_ref,0,1)
        #Ligne 2 : Qté
        label_qty = QLabel("Quantité :")
        label_qty.setFont(self.font)
        self.layout.addWidget(label_qty, 1,0)
        self.edit_qty = NumberEntry(geometry = (50,50,400,300))
        self.edit_qty.setFont(self.font)
        self.edit_qty.returnPressed.connect(self.on_validate)
        self.layout.addWidget(self.edit_qty,1,1)
        #Ligne 3 : Boutons
        bt = QPushButton("Création")
        bt.setFont(self.font)
        bt.clicked.connect(self.on_bt_clicked)
        self.layout.addWidget(bt,2,1)
        #
        self.stretch()
        self.edit_reference.setFocus()

    def on_bt_clicked(self):
        '''Création kanban selon champs complétés
        '''
        proref = self.edit_reference.text()
        qte = int(self.edit_qty.text())
        try:
            id = self.bdd.set_kanban(proref=proref, qte=qte, type = "creation")
            self.app.print(id, proref, qte)
            messagebox = TimerMessageBox(f"Création du kanban n°{id} : {qte} {proref}.", 3, self)
            messagebox.exec_()
        except AssertionError as e:
            logging.warning(e)
            #TODO : fenetre UI
        else:
            self.raz()


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

    def raz(self):
        self.edit_reference.setText("")
        self.edit_qty.setText("")
        self.edit_reference.setFocus()


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
        self.edit_kanban = NumberEntry(geometry = (50,50,400,300))
        self.edit_kanban.setFont(self.font)
        self.edit_kanban.textChanged.connect(self.on_edit_kanban_change)
        self.edit_kanban.returnPressed.connect(self.on_validate)
        self.layout.addWidget(self.edit_kanban,0,1)
        #Ligne 3 : Qté
        label_qty = QLabel("Quantité à enlever:")
        label_qty.setFont(self.font)
        self.layout.addWidget(label_qty, 1,0)
        self.edit_qty = NumberEntry(geometry = (50,50,400,300))
        self.edit_qty.setFont(self.font)
        self.edit_qty.returnPressed.connect(self.on_validate)
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
        #
        self.stretch()
        self.edit_kanban.setFocus()


    def on_bt_clicked(self):
        '''Consommation du kanban
        '''
        try:
            id = int(self.edit_kanban.text())
            kanban = self.bdd.get_kanbans(id=id)[0]
        except IndexError:
            time.sleep(2)
            self.edit_kanban.setText("")
            self.edit_qty.setText("")
            self.edit_kanban.setFocus()
        except ValueError:
            pass
        else:
            qte_a_enlever = int(self.edit_qty.text())
            qte_kanban = kanban.get('qte')
            proref = kanban.get('proref')
            try:
                self.bdd.set_kanban(id=id, qte=qte_kanban - qte_a_enlever, type = "consommation")
                if qte_kanban - qte_a_enlever>0:
                    messagebox = TimerMessageBox(f"Le kanban n°{id} est partiellement consommé. Il reste {qte_kanban - qte_a_enlever} {proref}", 3, self)
                else:
                    messagebox = TimerMessageBox(f"Le kanban n°{id} ({proref}) est consommé.", 3, self)
                messagebox.exec_()
            except AssertionError as e:
                logging.warning(e)
                #TODO : status
            else:
                self.edit_kanban.setText("")
                self.edit_qty.setText("")
                self.edit_kanban.setFocus()

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
