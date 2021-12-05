# coding: utf-8

import logging

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QGraphicsOpacityEffect, QAction, qApp, QStackedWidget
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QSize, QTimer

from .oktab import OKTab
from .okinput import OKInput, OKOutput
from .okparams import OKParams
from .bdd import BddOKanbans


class OKanbanApp(QMainWindow):
    '''Une application pour Kanbans
    '''
    def __init__(self, parent=None, title = "OKanbans", fullscreen = False, mode = 'tab', host = None, port = None):
        super().__init__(parent)
        self.fullscreen = fullscreen
        self.setWindowTitle(title)
        #self.setWindowFlag(Qt.FramelessWindowHint)
        self.mode = mode
        self.host = host
        self.port = port
        self.bdd = BddOKanbans(host, port)
        self.initUI()
        self.show()

    def initUI(self):
        '''Création des composants graphiques
        '''
        self.setGeometry(0, 0, 1000,1200)#480, 320) #default size
        if self.fullscreen:
            self.showFullScreen()
        #Status barre
        self.statusBar()
        #Menu
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Fichier')
        exitAction = QAction('&Quitter', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip("Ferme l'application")
        exitAction.triggered.connect(qApp.quit)
        fileMenu.addAction(exitAction)
        modeMenu = menubar.addMenu('&Mode')
        self.mode_tabAction = QAction('Mode &Tableau', self, checkable = True)
        self.mode_tabAction.setShortcut('Ctrl+T')
        self.mode_tabAction.setStatusTip('Mode tableau pour vision planification')
        self.mode_tabAction.triggered.connect(self.toogle_mode_tab)
        modeMenu.addAction(self.mode_tabAction)
        self.mode_inputAction = QAction('Mode &Entrée', self, checkable = True)
        self.mode_inputAction.setShortcut('Ctrl+E')
        self.mode_inputAction.setStatusTip('Mode entrée pour saisie remplissage')
        self.mode_inputAction.triggered.connect(self.toogle_mode_input)
        modeMenu.addAction(self.mode_inputAction)
        self.mode_outputAction = QAction('Mode &Sortie', self, checkable = True)
        self.mode_outputAction.setShortcut('Ctrl+S')
        self.mode_outputAction.setStatusTip('Mode sortie pour saisie consommation')
        self.mode_outputAction.triggered.connect(self.toogle_mode_output)
        modeMenu.addAction(self.mode_outputAction)
        self.mode_parametres = QAction('Mode &Paramètres', self, checkable = True)
        self.mode_parametres.setShortcut('Ctrl+P')
        self.mode_parametres.setStatusTip('paramètres')
        self.mode_parametres.triggered.connect(self.toogle_mode_params)
        modeMenu.addAction(self.mode_parametres)
        #Central Widget
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.tab = OKTab()
        self.central_widget.addWidget(self.tab)
        self.input = OKInput()
        self.central_widget.addWidget(self.input)
        self.output = OKOutput()
        self.central_widget.addWidget(self.output)
        self.params = OKParams()
        self.central_widget.addWidget(self.params)
        self.params.load()
        self.update_mode()

    def update_mode(self, mode=None):
        ''' Change the mode
        '''
        if mode:
            self.mode = mode
        logging.debug(f"Change mode : {self.mode}")            
        self.central_widget.setCurrentIndex(['tab','input','output', 'params'].index(self.mode))
        self.mode_tabAction.setChecked(self.mode == 'tab')
        self.mode_inputAction.setChecked(self.mode == 'input')
        self.mode_outputAction.setChecked(self.mode == 'output')
        self.mode_parametres.setChecked(self.mode == 'params')


    def toogle_mode_tab(self, state=True):
        if state:
            self.mode = 'tab'
        self.update_mode()

    def toogle_mode_input(self, state=True):
        if state:
            self.mode = 'input'
        self.update_mode()
            
    def toogle_mode_output(self, state=True):
        if state:
            self.mode = 'output'
        self.update_mode()

    def toogle_mode_params(self, state = True):
        if state:
            self.mode = 'params'
        self.update_mode()


if __name__ == '__main__':
    app = QApplication([])
    fenetre = OKanbanApp(app)