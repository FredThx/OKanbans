# coding: utf-8

from PyQt5.QtWidgets import QApplication

from OKanban.okanban_app import OKanbanApp
from OKanban.nicelabel import HttpNiceLabel
import time, sys
import argparse
from FUTIL.my_logging import *

my_logging(console_level = DEBUG, logfile_level = INFO, details = True)
logging.info('OKanban gui start')

parser = argparse.ArgumentParser(description='La gestion des kanbans pour Olfa')
parser.add_argument('-t', '--title', action='store', help = "Titre de l'application", nargs='?')
parser.add_argument('-f', '--fullscreen', action='store_true', help = "fullscreen mode")
parser.add_argument('-m', '--mode', action='store', help = "mode : tab|input|output", nargs='?', default = 'tab')
parser.add_argument('-H', '--host', action='store', help = "IP bdd", nargs='?', default = '192.168.0.11')
parser.add_argument('-s', '--style', action = 'store', help = 'style (fichier css)', nargs = '?', default = 'okanbans.css')
parser.add_argument('-p', '--printer', action = 'store', dest = 'printer_name', help ='imprimante pour les étiquettes (chemin windows)', nargs = '?', default = '\\\\SRV-DATA\\ZEBRA PERCAGE')
parser.add_argument('-e', '--etiquette', action = 'store', help = "nom du format d'étiquette (Nicelabel)", nargs = '?', default = 'ET_PER_1')

args = parser.parse_args()

args.printer = HttpNiceLabel('http://192.168.0.6:56425')

app = QApplication([])

logging.info(f"Open okanbans with args : {vars(args)}")
kanbans = OKanbanApp(**(vars(args)))
kanbans.show()
if __name__ == '__main__':
    sys.exit(app.exec_())
