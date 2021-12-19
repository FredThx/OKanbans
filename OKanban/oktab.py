# coding: utf-8
import logging

from PyQt5.QtWidgets import QVBoxLayout,QHBoxLayout, QWidget, QLabel, QFrame
#from PyQt5.QtCore import Qt

from .qtutils import Qutil
import OKanban.okanban_app as OK_app #Evite circular import
from .bdd import BddOKanbans
from .okanban import OKanban, EmptyOKanban

class OKbase(QFrame):
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
        #self.rearrange()
        self.layout.addStretch()
            
    def rearrange(self):
        '''Pour gagner place et lisibilité
        déplace les "petits" OKProd dans des colonnes multi produits
        '''
        okprods = self.get_ok_widgets(OKProd)
        max_size = max([p.size for p in okprods])
        index = 0
        offset = 0
        while index < len(okprods)-1:
            if okprods[index].size + okprods[index+1].size < max_size -2:
                p1 = self.layout.takeAt(index-offset)
                p2 = self.layout.takeAt(index-offset)
                layout = QVBoxLayout(self)
                layout.addItem(p1)
                layout.addItem(p2)
                layout.addStretch()
                self.layout.addLayout(layout)
                index += 2
                offset +=2
            else:
                index +=1

        


class OKProd(OKbase)        :
    ''' Un colonne contenant un produit
    '''
    def __init__(self, data, parent = None):
        super().__init__(parent)
        self.bdd = None
        self.data = data
        self.size = 0
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
        #Suppression des Kanbans vide en trop
        nb_deleted_empty_kanbans = 0
        while self.get_ok_widgets(EmptyOKanban) and len(kanbans) + len(self.get_ok_widgets(EmptyOKanban)) - nb_deleted_empty_kanbans > self.data.get('nb_max',0):
            w = self.get_ok_widgets(EmptyOKanban)[-1]
            w.deleteLater()
            nb_deleted_empty_kanbans += 1
        ##Finitions
        self.size = max(self.data.get('nb_max',0),len(kanbans))
        #Order layout
        i = 0
        #while i < len(kanbans):
        while i < self.size - len(kanbans):
            if type(self.layout.itemAt(i).widget()) == OKanban:
                self.layout.addItem(self.layout.takeAt(i)) #Put the EmptyOKAnban to the end
            else:
                i += 1
        #Colorisation des Kanbans
        seuil_alerte = self.data.get('nb_max',0) - self.data.get('nb_alerte',0)
        for i in range(self.size):
            #Zone d'alerte stock bas
            self.layout.itemAt(i).widget().alert = (i >= seuil_alerte)
            #Zone d'alerte stock trop haut
            self.layout.itemAt(i).widget().alert_haut = (i >= self.data.get('nb_max',0))