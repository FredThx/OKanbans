# -*- coding: utf-8 -*-

import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, \
                            QPushButton, QItemDelegate, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator

class IntDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super().__init__()

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(QIntValidator())
        return editor

class DFTableWidget(QTableWidget):
    '''Table lié à un DataFrame
    '''
    def __init__(self, parent = None,df = None):
        super().__init__(parent)
        if not df is None:
            self.load(df)

    def load(self, df):
        '''Load dataFrame'''
        self.df = df
        #Clear table
        self.clear()
        # set table dimension
        nRows, nColumns = self.df.shape
        self.setColumnCount(nColumns)
        self.setRowCount(nRows)

        self.setHorizontalHeaderLabels(tuple(self.df.columns))
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        #self.setItemDelegateForColumn(1, IntDelegate())

        # data insertion
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                self.setItem(i, j, QTableWidgetItem(str(self.df.iloc[i, j])))

        self.cellChanged[int, int].connect(self.updateDF)   

    def updateDF(self, row, column):
        text = self.item(row, column).text()
        self.df.iloc[row, column] = text

    def newRow(self):
        '''Add a new row
        '''
        self.cellChanged[int, int].disconnect()
        i =self.rowCount()
        self.setRowCount(i+1)
        for j in range(self.columnCount()):
            self.setItem(i, j, QTableWidgetItem())
        #Insert in dataFrame
        new = list(range(self.columnCount()))
        insert_loc = self.df.index.max()
        if pd.isna(insert_loc):
            self.df.loc[0] = new
        else:
            self.df.loc[insert_loc + 1] = new
        self.cellChanged[int, int].connect(self.updateDF)

class DFEditor(QWidget):
    '''Un éditeur de DataFrame
    '''

    def __init__(self, parent=None, df = None):
        super().__init__(parent)
        self.df = df
        
        mainLayout = QVBoxLayout()

        self.table = DFTableWidget(self, self.df)
        mainLayout.addWidget(self.table)

        buttonLayout = QHBoxLayout()

        button_delete = QPushButton('Supprime ligne')
        button_delete.setStyleSheet('font-size: 24px')
        button_delete.clicked.connect(self.deleteRow)
        buttonLayout.addWidget(button_delete)

        button_new = QPushButton('Nouveau')
        button_new.setStyleSheet('font-size: 24px')
        button_new.clicked.connect(self.newRow)
        buttonLayout.addWidget(button_new)     

#        button_load = QPushButton('Actualiser')
#        button_load.setStyleSheet('font-size: 24px')
        #button_load.clicked.connect(self.load) #todo connecter 
#        buttonLayout.addWidget(button_load)   

        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)
        
    def load(self, df):
        self.df = df
        self.table.load(df)

    def deleteRow(self):
        row = self.table.currentRow()
        self.table.removeRow(row)
        self.df.drop([row], inplace = True)

    def newRow(self):
        self.table.newRow()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    data = {
        'Col X': list('ABCD'),
        'Col Y': [10, 20, 30, 40]
    }
    df = pd.DataFrame(data)
    demo = DFEditor(df=df)
    demo.resize(1200, 800)
    demo.show()
    
    sys.exit(app.exec_())