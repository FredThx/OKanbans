# coding: utf-8

import logging, time

from PyQt5.QtWidgets import QApplication, QMainWindow, qApp, QWidget, QAction, QStackedWidget, QVBoxLayout
#from PyQt5.QtGui import x
from PyQt5.QtCore import QTimer, QThread, QObject

from .oktab import OKTab
from .okinput import OKInput, OKOutput
from .okparams import OKGenParams, OKReferences
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
        self.id = None
        self.on_start()
        self.widgets = []
        self.initUI()
        self.show()
        self.load()
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(1000)

    def closeEvent(self, event):
        '''Supprime inscription à la bdd
        '''
        self.bdd.delete_instance(self.id)

    def on_start(self):
        '''Lance le thread on_start()
        '''
        self.worker = OKanbanWorker(self)
        self.on_start_thread = QThread()
        self.worker.moveToThread(self.on_start_thread)
        self.on_start_thread.started.connect(self.worker.on_start)
        self.on_start_thread.start()

    def initUI(self):
        '''Création des composants graphiques
        '''
        self.setGeometry(50, 50, 800,800)#480, 320) #default size
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
        ##tab
        self.tab = OKTab()
        self.central_widget.addWidget(self.tab)
        self.widgets.append(self.tab)
        ##Input
        self.input = OKInput()
        self.central_widget.addWidget(self.input)
        self.widgets.append(self.input)
        ##Output
        self.output = OKOutput()
        self.central_widget.addWidget(self.output)
        self.widgets.append(self.output)
        ##Params
        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        self.central_widget.addWidget(params_widget)
        ###Genparams
        self.params = OKGenParams()
        params_layout.addWidget(self.params)
        self.widgets.append(self.params)
        ###Refsparams
        self.references = OKReferences()
        params_layout.addWidget(self.references)
        self.widgets.append(self.references)
        self.update_mode()

    def load(self):
        '''Load all widgets with data
        '''
        if self.id is None:
            self.id = self.bdd.create_new_instance()
        for w in self.widgets:
            w.load()

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

    def on_timer(self):
        '''Vérifie s'il y a des modification dans la bdd
        '''
        news, drops = self.bdd.get_messages(self.id)
        if news or drops:
            logging.info(f"New data on bdd : {news}, {drops}")
            self.bdd.cache_clear()
            self.load()

class OKanbanWorker(QObject):
    '''Un objet pour executer du code en //
    '''
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self.app = parent
        logging.debug(f"{self} created.")

    def on_start(self):
        '''Taches à la connection :
        - clean instances
        '''
        logging.info("on_start thread start...")
        while self.app.id is None:
            time.sleep(1)
        self.app.bdd.clean_instances(self.app.id)


if __name__ == '__main__':
    app = QApplication([])
    fenetre = OKanbanApp(app)




