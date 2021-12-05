# coding: utf-8

from PyQt5.QtWidgets import QApplication
from OKanban.okanban_app import OKanbanApp
import time, sys
import argparse
from FUTIL.my_logging import *

my_logging(console_level = DEBUG, logfile_level = INFO, details = True)
logging.info('OKanban gui start')

parser = argparse.ArgumentParser(description='La gestion des kanbans pour Olfa')
parser.add_argument('title', action='store', help = "Titre de l'application", nargs='?')
parser.add_argument('fullscreen', action='store_false', help = "fullscreen mode")
parser.add_argument('mode', action='store', help = "mode : tab|input|output", nargs='?', default = 'tab')
parser.add_argument('host', action='store', help = "IP bdd", nargs='?', default = '192.168.0.11')

args = parser.parse_args()

app = QApplication([])
kanbans = OKanbanApp( **(vars(args)))

if __name__ == '__main__':
    sys.exit(app.exec_())