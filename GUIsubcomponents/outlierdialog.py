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

class OutlierWindow(QtWidgets.QDialog):
    """
    OutlierWindow is a dialog from the main gamut window.  A user can toggle
    whether or not to remove outliers by the generalized extreme Studentized
    deviated (ESD) test.  If so, the user specifies the significance level to 
    use in determining what constitutes an outlier.
    
    The main attributes are 'is_testing_for_outliers' and 'significance level',
    which can be retrieved with the 'getSelection' method.  This informs
    gamut what to do with the data set.
    """

    def __init__(self,
                 parent,
                 outlier_boolean,
                 significance_level):
        super().__init__(parent=parent)

        # Open window the current settings from gamut window
        self.is_testing_for_outliers = outlier_boolean
        self.significance_level = significance_level
        
        self.initUI()
                

    def initUI(self):
        """
        Set up user interface
        """
        
        # Window Widget
        self.setWindowTitle("Outlier Removal Options")
        self.resize(354, 153)
        self.windowWidget = QtWidgets.QWidget(self)
        self.windowWidget.setGeometry(QtCore.QRect(0, 0, 351, 131))

        self.testLabel= QtWidgets.QLabel()
        self.testLabel.setText("Generalized ESD (Iterative Maximum Residual Normed) Test:")

        self.outlierCheckbox = QtWidgets.QCheckBox()
        self.outlierCheckbox.setText("Remove outliers")
        self.outlierCheckbox.setChecked(self.is_testing_for_outliers)
        #action
        self.outlierCheckbox.clicked.connect(self.turnOffOnOutlierWidgets)
        
        self.signlevelLabel = QtWidgets.QLabel()
        self.signlevelLabel.setText("Significance Level")
        if self.is_testing_for_outliers == False:
            self.signlevelLabel.setHidden(True)

        self.signlevSpinBox = QtWidgets.QDoubleSpinBox()
        self.signlevSpinBox.setValue(0.05)
        self.signlevSpinBox.setRange(0.001,0.999)
        self.signlevSpinBox.setDecimals(3)
        self.signlevSpinBox.setSingleStep(0.001)
        self.signlevSpinBox.setSingleStep(0.001)
        if self.is_testing_for_outliers == False:
            self.signlevSpinBox.setHidden(True)
        else:
            self.signlevSpinBox.setValue(self.significance_level)

        # Button
        self.savesettingsButton = QtWidgets.QPushButton()
        self.savesettingsButton.setText("Save Outlier Settings")
        self.savesettingsButton.clicked.connect(self.setOutlierSettings)

        # Spacers
        spacerItem2 = QtWidgets.QSpacerItem(40, 20,
                                            QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Minimum)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20,
                                            QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Minimum)

        # Lines
        self.line = QtWidgets.QFrame()
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        if self.is_testing_for_outliers == False:
            self.line.setHidden(True)
    
        self.line_1 = QtWidgets.QFrame()
        self.line_1.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_1.setFrameShadow(QtWidgets.QFrame.Sunken)
        if self.is_testing_for_outliers == False:
            self.line_1.setHidden(True)

        # Layout Items
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.addWidget(self.signlevelLabel)
        self.horizontalLayout.addWidget(self.signlevSpinBox)

        self.horizontalLayout_1 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_1.addItem(spacerItem2)
        self.horizontalLayout_1.addWidget(self.savesettingsButton)
        self.horizontalLayout_1.addItem(spacerItem3)

        self.verticalLayout = QtWidgets.QVBoxLayout(self.windowWidget)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.addWidget(self.testLabel)
        self.verticalLayout.addWidget(self.outlierCheckbox)
        self.verticalLayout.addWidget(self.line)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.line_1)
        self.verticalLayout.addLayout(self.horizontalLayout_1)

        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

    def setOutlierSettings(self):
        """
        Save user specified re: outlier options as attributes; close window
        """
        if self.outlierCheckbox.isChecked():
            self.is_testing_for_outliers = True
            self.significance_level = self.signlevSpinBox.value()
        else:
            self.is_testing_for_outliers = False
            self.significance_level = None
        self.accept()
                
    def turnOffOnOutlierWidgets(self, *args):
        """
        Hide/unhide labels/widgets re: outliers based on self.outlierCheckbox
        """
        if self.outlierCheckbox.isChecked():
            self.signlevelLabel.setHidden(False)
            self.signlevSpinBox.setHidden(False)
            self.line.setHidden(False)
            self.line_1.setHidden(False)
        else:
            self.signlevelLabel.setHidden(True)
            self.signlevSpinBox.setHidden(True)
            self.line.setHidden(True)
            self.line_1.setHidden(True)
                        
    def getSelection(self):
        """
        Return boolean of whether to remove outliers, if so the significance level
        """
        return self.is_testing_for_outliers, self.significance_level
