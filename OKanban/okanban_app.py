# coding: utf-8

import logging, time, datetime, os, pathlib

from PyQt5.QtWidgets import QApplication, QMainWindow, qApp, QWidget, QAction, QVBoxLayout, QScrollArea, QMessageBox
#from PyQt5.QtGui import x
from PyQt5.QtCore import QTimer, QThread, QObject, Qt, QRect, QPoint

from .oktab import OKTab
from .okinput import OKInput, OKOutput
from .okparams import OKGenParams, OKReferences
from .bdd import BddOKanbans
from .okprinter import OKPrinter
from .okexport import OKExport
from .version import __version__, __repo__, __owner__
from .fgithub import FGithub

class OKanbanApp(QMainWindow):
    '''Une application pour Kanbans
    '''
    def __init__(self, parent=None, title = "OKanbans", fullscreen = False, mode = 'tab', host = None, port = None, style = None, printer = None, printer_name = None, etiquette = None):
        '''
            - fullscreen        :    False or True
            - mode              :    'tab' or 'input' or 'output'
            - host              :    database host
            - port              :    database ip port
            - style             :   css file name
            - printer           :   Nicelabel printer
            - printer_name      :   path of the printer (ex : '\\\\SERVEUR\\imprimante') si non spécifié : selon paramètre
        '''
        super().__init__(parent)
        self.fullscreen = fullscreen
        self.setWindowTitle(f"{title} - {__version__}")
        #self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlags(
            Qt.WindowCloseButtonHint |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint
        )
        self.mode = mode
        self.host = host
        self.port = port
        self.style = style
        # printer pour étiquettes
        self.printer = printer
        self.printer_name = printer_name
        self.etiquette = etiquette
        self.bdd = BddOKanbans(host, port)
        self.id = self.bdd.create_new_instance()
        # Printer pour tableau
        self.okprinter = OKPrinter(self.bdd)
        # Pour Export
        self.exporter = OKExport(self.bdd)
        self.on_start()
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(1000)
        # Mise à jour de l'application
        okgithub = FGithub(__owner__, __repo__)
        if okgithub.get_lastest_tag() != __version__: #todo : faire un <
            if QMessageBox.question(self,
                            "Mise à jour",
                            "Une nouvelle version est disponible. Voulez vous l'installer?",
                            QMessageBox.Yes | QMessageBox.Cancel,
                            QMessageBox.Cancel) == QMessageBox.Yes:
                path = pathlib.Path().resolve()
                if okgithub.update_from_lastest(path):
                    QMessageBox.information(self,
                                            "Mise à jour",
                                            "La mise a jour à aboutie. Merci de femer et reouvrir l'application.")

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
        screen = QApplication.primaryScreen()
        rect = QRect(
                QPoint(
                    (screen.size()/10).width(),
                    (screen.size()/10).height())
                , screen.size()*0.7)
        self.setGeometry(rect)
        #Status barre
        self.statusBar()
        # Menus
        menubar = self.menuBar()
        ## Menu Fichier
        fileMenu = menubar.addMenu('&Fichier')
        ### Imprime
        self.menu_imprime = QAction('&Imprime', self)
        self.menu_imprime.setShortcut('Ctrl+I')
        self.menu_imprime.setStatusTip('Imprime la liste des kanbans')
        self.menu_imprime.triggered.connect(self.okprinter.print)
        fileMenu.addAction(self.menu_imprime)
        ### Aperçu avnt impression
        self.menu_apercu = QAction('Aperçu avant impression', self)
        self.menu_apercu.setStatusTip('Aperçu de la liste des kanbans')
        self.menu_apercu.triggered.connect(self.okprinter.apercu)
        fileMenu.addAction(self.menu_apercu)
        ### Export Excel
        self.menu_export = QAction('&Export..', self)
        self.menu_export.setShortcut('Ctrl+E')
        self.menu_export.setStatusTip('Export vers Excel')
        self.menu_export.triggered.connect(self.exporter.export)
        fileMenu.addAction(self.menu_export)
        ### Quitter
        exitAction = QAction('&Quitter', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip("Ferme l'application")
        exitAction.triggered.connect(qApp.quit)
        fileMenu.addAction(exitAction)
        ### Eteindre
        haltAction = QAction("&Eteindre", self)
        haltAction.setShortcut('CTRl+E')
        exitAction.setStatusTip("Eteindre")
        haltAction.triggered.connect(self.halt)
        fileMenu.addAction(haltAction)
        ## Menu Mode
        modeMenu = menubar.addMenu('&Mode')
        ### Mode Tableau
        self.mode_tabAction = QAction('Mode &Tableau', self, checkable = True)
        self.mode_tabAction.setShortcut('Ctrl+T')
        self.mode_tabAction.setStatusTip('Mode tableau pour vision planification')
        self.mode_tabAction.triggered.connect(self.toogle_mode_tab)
        modeMenu.addAction(self.mode_tabAction)
        ### Mode Entrée
        self.mode_inputAction = QAction('Mode &Entrée', self, checkable = True)
        self.mode_inputAction.setShortcut('Ctrl+E')
        self.mode_inputAction.setStatusTip('Mode entrée pour saisie remplissage')
        self.mode_inputAction.triggered.connect(self.toogle_mode_input)
        modeMenu.addAction(self.mode_inputAction)
        ### Mode Sortie
        self.mode_outputAction = QAction('Mode &Sortie', self, checkable = True)
        self.mode_outputAction.setShortcut('Ctrl+S')
        self.mode_outputAction.setStatusTip('Mode sortie pour saisie consommation')
        self.mode_outputAction.triggered.connect(self.toogle_mode_output)
        modeMenu.addAction(self.mode_outputAction)
        # Mode paramètres
        self.mode_parametres = QAction('Mode &Paramètres', self, checkable = True)
        self.mode_parametres.setShortcut('Ctrl+P')
        self.mode_parametres.setStatusTip('paramètres')
        self.mode_parametres.triggered.connect(self.toogle_mode_params)
        modeMenu.addAction(self.mode_parametres)
        #Central Widget
        self.update_mode()

    def load(self):
        '''Load the active view
        '''
        if self.mode == 'params':
            self.params.load()
            self.references.load()
        else:
            self.main_widget.load()
        self.set_style()
        isFullScreen = self.isFullScreen()
        isMaximized = self.isMaximized()
        self.showNormal() #Un peu con, mais ça fonctionne TODO: améliorer
        if self.fullscreen or isFullScreen:
            self.showFullScreen()
        if isMaximized:
            self.showMaximized()


    def set_style(self, style = None):
        '''Applique le style
        '''
        style = style or self.style
        if style:
            try:
                self.setStyleSheet(open(style).read())
            except FileNotFoundError as e:
                logging.error(e)

    def update_mode(self, mode=None):
        ''' Change the mode
        '''
        if mode:
            self.mode = mode
        logging.debug(f"Change mode : {self.mode}")
        self.mode_tabAction.setChecked(self.mode == 'tab')
        self.mode_inputAction.setChecked(self.mode == 'input')
        self.mode_outputAction.setChecked(self.mode == 'output')
        self.mode_parametres.setChecked(self.mode == 'params')
        if self.mode == 'tab':
            self.main_widget = OKTab()
        elif self.mode == 'input':
            self.main_widget = OKInput(self)
        elif self.mode == 'output':
            self.main_widget = OKOutput(self)
        elif self.mode == 'params':
            self.main_widget = QWidget()
            params_layout = QVBoxLayout(self.main_widget)
            ###Genparams
            self.params = OKGenParams()
            params_layout.addWidget(self.params)
            ###Refsparams
            self.references = OKReferences()
            params_layout.addWidget(self.references)
        self.setCentralWidget(self.main_widget)
        self.load()

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
        if self.id:
            news, drops = self.bdd.get_messages(self.id)
            if news or drops:
                logging.info(f"New data on bdd : {news}, {drops}")
                self.bdd.cache_clear()
                self.load()
            self.set_style()

    def print(self, id, proref, qte, date_creation = None):
        '''Imprime une étiquette kanban
        '''
        printer_name = self.printer_name or self.bdd.get_param("printer")
        if self.printer and printer_name and self.etiquette:
            if date_creation is None:
                date_creation = datetime.date.today()
            if isinstance(date_creation, datetime.date):
                date_creation = date_creation.strftime("%d/%m/%Y")
            datas = {'id':id, 'proref':proref, 'qte' : qte, 'date_creation':date_creation}
            datas['printer'] = printer_name
            datas['qty'] = 1
            datas['etiquette'] = self.etiquette
            logging.debug(f"nicelabel.print({datas})")
            self.printer.print(**datas)
        else:
            logging.warning("Paramètres d'impression non ou mal définis")

    def halt(self):
        '''halt the system
        '''
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Voulez vous vraiment éteindre le system?")
        msg.setWindowTitle("Eteindre le système.")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        if msg.exec_() == QMessageBox.Ok:
            os.system("sudo halt")

    #TODO demander un nom de fichier + path et créer le fichier


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
