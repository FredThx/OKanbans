import os, sys
from PyQt5 import QtCore, QtWidgets
from pathlib import Path
import openpyxl

class OKExport:
    '''Une classe pour exporter vers Excel
    '''
    def __init__(self, bdd = None):
        self.bdd = bdd
        self.path_name = None
        self.folder = os.path.expanduser('~')

    def export(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(None,"Export vers ...", self.folder, "Excel (*.xlsx)")
        if filename:
            p = Path(filename)
            self.folder = str(p.parent)
            classeur = openpyxl.Workbook()
            feuille = classeur.active
            feuille.title = "kanbans"
            feuille.append(["id","proref","qte","date_creation"])
            for kanban in self.bdd.get_kanbans():
                feuille.append([
                    kanban.get('id'),
                    kanban.get('proref'),
                    kanban.get('qte'),
                    kanban.get('date_creation'),
                ])
            classeur.save(filename)
            

if __name__ == '__main__':
    from bdd import BddOKanbans
    app = QtWidgets.QApplication([])
    bdd = BddOKanbans('192.168.0.11',27017)
    exporter = OKExport(bdd)
    window = QtWidgets.QWidget()
    window.setWindowTitle('Test')
    buttonPrint = QtWidgets.QPushButton('Export', window)
    buttonPrint.clicked.connect(exporter.export)
    layout = QtWidgets.QGridLayout(window)
    layout.addWidget(buttonPrint, 1, 1)
    window.show()
    sys.exit(app.exec_())