from PyQt5 import QtCore, QtGui, QtWidgets
import scipy.stats as stats
import numpy as np
import datetime



class ShapeFactorBoundsWindow(QtWidgets.QDialog):

    def __init__(self,
                 parent,
                 samples,
                 dist_name):
        super().__init__(parent=parent)

        # Defaults
        self.value = None

        # Definite attributes
        self.samples = samples
        self.distribution = dist_name
        self.initUI()
        

    def initUI(self):
        """Set up user interface"""
        
        # Window Widget
        self.setWindowTitle("Shape Factor Bounds")
        self.resize(354, 153)
        self.windowWidget = QtWidgets.QWidget(self)
        self.windowWidget.setGeometry(QtCore.QRect(0, 0, 351, 131))
        

        # Labels
        self.lowerBoundLabel = QtWidgets.QLabel()
        self.lowerBoundLabel.setText("Lower Bound")
        self.upperBoundLabel = QtWidgets.QLabel()
        self.upperBoundLabel.setText("Upper Bound")
        
        # Line Edits
        self.lowerBoundLineEdit = QtWidgets.QLineEdit()
        self.upperBoundLineEdit = QtWidgets.QLineEdit()

        # Button
        self.calcPPCCButton = QtWidgets.QPushButton()
        self.calcPPCCButton.setText("Calculate PPCC")
        self.calcPPCCButton.clicked.connect(self.calcPPCC)


        # Spacers
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.addWidget(self.lowerBoundLabel, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.upperBoundLabel, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.lowerBoundLineEdit, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.upperBoundLineEdit, 1, 1, 1, 1)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.addItem(spacerItem2)
        self.horizontalLayout.addWidget(self.calcPPCCButton)
        self.horizontalLayout.addItem(spacerItem3)


        self.verticalLayout = QtWidgets.QVBoxLayout(self.windowWidget)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout.addLayout(self.horizontalLayout)

        #self.setCentralWidget(self.windowWidget)

        #self.statusbar = QtWidgets.QStatusBar(self)
        #self.setStatusBar(self.statusbar)

        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

    def calcPPCC(self):
        try:
            lowerBound = float(self.lowerBoundLineEdit.text()) 
            upperBound = float(self.upperBoundLineEdit.text()) 
            self.value = stats.ppcc_max(self.samples,
                                    brack=(lowerBound,
                                           upperBound),
                                    dist=self.distribution)
            self.accept()

        except ValueError:
            #self.statusbar.showMessage("Invalid entry for shape factors bounds")
            return
        except:
            #self.statusbar.showMessage("Error during calculation of shape factor")
            return


            
    def getValue(self):
        return self.value


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = ShapeFactorBoundsWindow(None, None)
    sys.exit(app.exec_())