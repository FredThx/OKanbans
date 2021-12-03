# coding: utf-8

from PyQt5.QtWidgets import QApplication
from OKanban.okanban_app import OKanbanApp
import time, sys
import argparse
from FUTIL.my_logging import *

my_logging(console_level = DEBUG, logfile_level = INFO, details = True)
logging.info('FSTA gui start')

parser = argparse.ArgumentParser(description='La gestion des kanbans pour Olfa')
#parser.add_argument('img_path', action='store', help = 'images directory', nargs='?')

args = parser.parse_args()

app = QApplication([])
kanbans = OKanbanApp(app = app)
#app.processEvents()

if __name__ == '__main__':
    sys.exit(app.exec_())