# coding: utf-8
import logging

from PyQt5.QtWidgets import QSpacerItem, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QWidgetItem
from PyQt5.QtCore import Qt

from .qtutils import Qutil
import OKanban.okanban_app as OK_app #Evite circular import
from .bdd import BddOKanbans
from .okanban import OKanban, EmptyOKanban

class OKbase(QWidget):
    def connect(self):
        '''Connecte the database'''
        if not self.bdd:
            self.bdd = Qutil.get_parent(self, OK_app.OKanbanApp).bdd
    
    def get_ok_widgets(self, w_class = None, strict = False, widget = True, index = False):
        '''Return all OKprod widgets
            strict      :   if True : type() is use vs isinstance()
            widget      :   if False, the item is use
                            if True, the item.widget is use
            index       :   if True return the list of index (vs the widget or the item)
        '''
        okprods = []
        indexs = []
        for i in range(self.layout.count()):
            if widget:
                w = self.layout.itemAt(i).widget()
            else:
                w = self.layout.itemAt(i)
            if strict:
                if w_class is None or type(w) == w_class:
                    okprods.append(w)
                    indexs.append(i)
            else:
                if w_class is None or isinstance(w, w_class):
                    okprods.append(w)
                    indexs.append(i)
        if index:
            return indexs
        else:
            return okprods

class OKTab(OKbase):
    '''Tableau des kanbans
    '''
    def __init__(self, parent = None):
        super().__init__(parent)
        self.bdd = None
        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout(self)

    def load(self):
        '''Load or update
        '''
        if self.bdd is None:
            self.connect()
        #Find new products
        for produit in self.bdd.get_references():
            existing_okprods = [w for w in self.get_ok_widgets(OKProd) if w.data.get('proref')==produit.get('proref')]
            if existing_okprods:
                existing_okprods[0].load()
            else:
                ok_produit = OKProd(produit)
                self.layout.addWidget(ok_produit)
                ok_produit.load()
        #Delete old products
            #TODO
        self.layout.addStretch()
            

class OKProd(OKbase)        :
    ''' Un colonne contenant un produit
    '''
    def __init__(self, data, parent = None):
        super().__init__(parent)
        self.bdd = None
        self.data = data
        self.initUI()
        
    def __str__(self):
        return f"OKProd({self.data.get('proref')})"

    def initUI(self):
        self.main_layout = QVBoxLayout(self)
        self.lb_proref = QLabel(self.data.get('proref'))
        self.main_layout.addWidget(self.lb_proref)
        self.layout = QVBoxLayout()
        self.main_layout.addLayout(self.layout)
        self.main_layout.addStretch()


    def load(self):
        '''Load or update
        '''
        logging.debug(f"load {self}")
        if self.bdd is None:
            self.connect()
        kanbans = self.bdd.get_kanbans(proref=self.data.get('proref'))
        exising_okkanbans = self.get_ok_widgets(OKanban, strict = True)
        for kanban in kanbans:
            if kanban.get('id') not in [w.id for w in exising_okkanbans]:
                #Ajoute les nouveaux kanbans
                o_kanban = OKanban(kanban.get('id'))
                self.layout.addWidget(o_kanban)
                o_kanban.load()
            else:
                #Modifie les kanbans existants
                [w for w in exising_okkanbans if w.id == kanban.get('id')][0].load()
        #Supprime les kanbans obsolètes
        for okanban in exising_okkanbans:
            if okanban.id not in [k.get('id') for k in kanbans]:
                okanban.deleteLater()
                okanban = None
        #Ajoute de nouveaux kanbans vides
        while len(kanbans) + len(self.get_ok_widgets(EmptyOKanban)) < self.data.get('nb_max',0):
            o_kanban = EmptyOKanban(proref = self.data.get('proref'))
            self.layout.addWidget(o_kanban)
            o_kanban.load()#ne fait rien
            logging.debug("add empty kanbans")
        #Suppression des Kanbans vide en trop
        nb_deleted_empty_kanbans = 0
        while self.get_ok_widgets(EmptyOKanban) and len(kanbans) + len(self.get_ok_widgets(EmptyOKanban)) - nb_deleted_empty_kanbans > self.data.get('nb_max',0):
            w = self.get_ok_widgets(EmptyOKanban)[-1]
            w.deleteLater()
            nb_deleted_empty_kanbans += 1
            logging.debug("delete empty kanbans")
        #Order layout
        i = 0
        size = max(self.data.get('nb_max',0),len(kanbans))
        #while i < len(kanbans):
        while i < size - len(kanbans):
            #if isinstance(self.layout.itemAt(i).widget(), EmptyOKanban):
            if type(self.layout.itemAt(i).widget()) == OKanban:
                self.layout.addItem(self.layout.takeAt(i)) #Put the EmptyOKAnban to the end
            else:
                i += 1
        #Colorisation des EmptyOKanbans
        for i in range(size):
            self.layout.itemAt(i).widget().set_alert(i > self.data.get('nb_alerte',0))
