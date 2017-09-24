###############################################################################
#
#    gamut
#    Copyright (C) 2017,  Nicholas A. Reynolds
#
#    Full License Available in LICENSE file at
#    https://github.com/nicholasareynolds/gamut
#
###############################################################################

from PyQt5 import QtCore, QtWidgets
import scipy.stats as stats

class ShapeFactorBoundsWindow(QtWidgets.QDialog):
    """
    ShapeFactorBoundsWindow enables a user to specify the bounds of a
    distribution's shape factor (provided it only has one shape factor), in
    order to use the 'scipy.statsppcc_max' to compute the maximum likely shape
    factor.
    
    ShapeFactorBoundsWindow is subordinate to the main gamut window, and
    accepts the samples and the name if the distribution as arguments.
    """

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
        """
        Set up user interface
        """
        # Window Widget
        self.setWindowTitle("Shape Factor Bounds")
        self.resize(354, 110)
        self.windowWidget = QtWidgets.QWidget(self)
        self.windowWidget.setGeometry(QtCore.QRect(0, 0, 351, 90))
        

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
        spacerItem2 = QtWidgets.QSpacerItem(40, 20,
                                            QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Minimum)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20,
                                            QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Minimum)

        # Layout Objects
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

        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

    def calcPPCC(self):
        """
        Calculate the prob. plot correlation coeff. and store as self.value
        """
        try:
            lowerBound = float(self.lowerBoundLineEdit.text()) 
            upperBound = float(self.upperBoundLineEdit.text()) 
            self.value = stats.ppcc_max(self.samples,
                                    brack=(lowerBound,
                                           upperBound),
                                    dist=self.distribution)
            self.accept()

        except ValueError:
            return
        except:
            return

    def getValue(self):
        """
        Return the value of the probability plot correlation coefficient.
        """
        return self.value


