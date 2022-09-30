import sys
from PyQt5 import QtCore, QtWidgets, QtPrintSupport
from PyQt5.QtGui import QTextDocument

class OKPrinter:
    '''Une classe pour imprimer le tableau des kanbans
    '''
    def __init__(self, bdd = None):
        self.bdd = bdd
        self.document = QTextDocument()

    def print(self):
        dialog = QtPrintSupport.QPrintDialog()
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.set_document()
            self.document.print_(dialog.printer())

    def apercu(self):
        dialog = QtPrintSupport.QPrintPreviewDialog()
        dialog.paintRequested.connect(self._apercu)
        dialog.exec_()
    
    def _apercu(self, printer):
        self.set_document()
        self.document.print_(printer)

    def set_document(self):
        ''' Crée le texte à imprimer
        '''
        #En fait la mise en colonnes ne fonctionne pas
        html = """
            <head>
                <style>
                    #col {
                        column-count: 2;
                        column-width : 30%;
                    }
                </style>
            </head>"""
        html += "<H1>Liste des Kanbans</H1>"
        html += "<BR>"
        proref = None
        for kanban in sorted(self.bdd.get_kanbans(),key=lambda k:k['proref']):
            if proref != kanban.get('proref'):
                if proref:
                    html += '</div>'
                proref = kanban.get('proref')
                html += f"<H2>{proref}</H2>"
                html += '<div id="col">'
            html += str(HtmlKanban(kanban))
        html += "</div>"
        print(html)
        self.document.setHtml(html)


class HtmlKanban:
    ''' Une représentation en HLTM d'un kanban
    '''
    def __init__(self, kanban = ""):
        self.k = kanban

    def __str__(self):
        html = f"<div>n° {self.k.get('id')} : {self.k.get('qte')} {self.k.get('proref')} du {self.k.get('date_creation'):%d-%m-%Y %H:%M}</div>"
        return html



if __name__ == '__main__':
    from bdd import BddOKanbans
    app = QtWidgets.QApplication([])
    bdd = BddOKanbans('192.168.0.11',27017)
    printer = OKPrinter(bdd)
    window = QtWidgets.QWidget()
    window.setWindowTitle('Test')
    buttonPrint = QtWidgets.QPushButton('Print', window)
    buttonPrint.clicked.connect(printer.print)
    buttonPreview = QtWidgets.QPushButton('Preview', window)
    buttonPreview.clicked.connect(printer.apercu)
    layout = QtWidgets.QGridLayout(window)
    layout.addWidget(buttonPrint, 1, 1)
    layout.addWidget(buttonPreview, 1, 2)
    window.show()
    sys.exit(app.exec_())