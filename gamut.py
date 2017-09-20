from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import scipy.stats as stats
from distributions import CandidateDistributions, SciPyContDist
import matplotlib
matplotlib.rcParams['backend'] = "Qt5Agg"
matplotlib.rcParams['font.size'] = 6
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys


pyVer = sys.version_info[0]  # i.e. 2 or 3
if pyVer < 3:
    import cPickle as pickle
else:
    import _pickle as pickle


class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self,
                 scipy_dist_file="scipy_cont_rvs.p"):
        self.pyVer = sys.version_info[0]
        self.distributions = pickle.load( open(scipy_dist_file, 'rb') )
        if pyVer >=3:
            super().__init__()
        
        #Initialize
        self.cDists = CandidateDistributions()
        self.shape1Value=None
        self.shape1Changed=False
        
        self.initUI()
        
    def initUI(self):
        
        # Main Window
        self.setWindowTitle("gamut")
        self.resize(739, 594)
        self.windowWidget = QtWidgets.QWidget(self)
        self.windowWidget.setGeometry(QtCore.QRect(10, 10, 729, 541))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        # --- Widgets ---
        
        # Data Label
        self.dataLabel = QtWidgets.QLabel()
        self.dataLabel.setText("Data:")
        self.dataLabel.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        
        # Open File Dialog Button
        self.selectFileButton = QtWidgets.QPushButton()
        self.selectFileButton.setText("Select File")
        self.selectFileButton.clicked.connect(self.loadSamples)

        # File Path Display        
        self.filePathLineEdit = QtWidgets.QLineEdit()
        self.filePathLineEdit.setEnabled(False)
        
        # Outliers Button
        self.outliersButton = QtWidgets.QPushButton()
        self.outliersButton.setEnabled(False)
        self.outliersButton.setText("Remove Outliers")

        # SciPy Distribution Label
        self.scipyDistsLabel = QtWidgets.QLabel()
        self.scipyDistsLabel.setText("SciPy Distributions:")
        
        # Supported Distributions Label
        self.scipyDistsList = QtWidgets.QListWidget()
        self.scipyDistsList.setEnabled(False)
        self.scipyDistsList.addItems(self.distributions.keys())
        self.scipyDistsList.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.scipyDistsList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.scipyDistsList.setCurrentRow(1)
        # Action
        #self.scipyDistsList.itemClicked.connect(self.unlockShapeBoxes)
        self.scipyDistsList.itemSelectionChanged.connect(self.unlockShapeBoxes)
        self.scipyDistsList.itemDoubleClicked.connect(self.addDistByDClick)

        
        # Shape Factors
        self.shape1Label = QtWidgets.QLabel()
        self.shape1Label.setEnabled(False)
        self.shape1Label.setText("Shape Factor 1")
        self.shape1Text = QtWidgets.QLineEdit()
        self.shape1Text.setEnabled(False)

        self.shape2Label = QtWidgets.QLabel()
        self.shape2Label.setEnabled(False)
        self.shape2Label.setText("Shape Factor 2")
        self.shape2Text = QtWidgets.QLineEdit()
        self.shape2Text.setEnabled(False)
        
        self.shape3Label = QtWidgets.QLabel()
        self.shape3Label.setEnabled(False)
        self.shape3Label.setText("Shape Factor 3")
        self.shape3Text = QtWidgets.QLineEdit()
        self.shape3Text.setEnabled(False)
        
        self.shape4Label = QtWidgets.QLabel()
        self.shape4Label.setEnabled(False)
        self.shape4Label.setText("Shape Factor 4")
        self.shape4Text = QtWidgets.QLineEdit()
        self.shape4Text.setEnabled(False)
        
        # PPCC Button
        self.PPCCButton = QtWidgets.QPushButton()
        self.PPCCButton.setEnabled(False)
        self.PPCCButton.setText("PPCC")
        self.PPCCButton.clicked.connect(self.calcPPCC)


        # Add/Rm Distributions Buttons        
        self.rmAllButton = QtWidgets.QPushButton()
        self.rmAllButton.setEnabled(False)
        self.rmAllButton.setText("Remove All")
        
        self.rmButton = QtWidgets.QPushButton()
        self.rmButton.setEnabled(False)
        self.rmButton.setText("Remove")
        
        self.addButton = QtWidgets.QPushButton()
        self.addButton.setEnabled(False)
        self.addButton.setText("Add")
        
        # Candidate Distributions
        self.probPlotLabel = QtWidgets.QLabel()
        self.probPlotLabel.setText("Probability Plotting:")
        self.candDistsTable = QtWidgets.QTableWidget()
        self.candDistsTable.setColumnCount(8)
        self.candDistsTable.setRowCount(0)
        self.candDistsTable.setHorizontalHeaderLabels(["Distribution",
                                                       "R^2",
                                                       "Location",
                                                       "Scale",
                                                       "Shape 1",
                                                       "Shape 2",
                                                       "Shape 3",
                                                       "Shape 4"])
        self.candDistsTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
                
        # MLE Label
        self.mleLabel = QtWidgets.QLabel()
        self.mleLabel.setText("Fit - Maximum Likelihood Estimation")
        
        # SciPy Call
        self.scipyCallButton = QtWidgets.QPushButton()
        self.scipyCallButton.setEnabled(False)
        self.scipyCallButton.setText("SciPy Call")
        
        # PDF/CDF
        self.pdfcdfButton = QtWidgets.QPushButton()
        self.pdfcdfButton.setEnabled(False)
        self.pdfcdfButton.setText("PDF/CDF")

        # Spacers
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
       
        # Lines
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)

        line_2 = QtWidgets.QFrame()
        line_2.setFrameShape(QtWidgets.QFrame.VLine)
        line_2.setFrameShadow(QtWidgets.QFrame.Sunken)

        line_3 = QtWidgets.QFrame()
        line_3.setFrameShape(QtWidgets.QFrame.HLine)
        line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        
        line_4 = QtWidgets.QFrame()
        line_4.setFrameShape(QtWidgets.QFrame.HLine)
        line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        
        # --- Organize Widgets into Layout Boxes (bottom->up) ---
        
        # Samples Horizontal
        horizontalLayout = QtWidgets.QHBoxLayout()
        horizontalLayout.addWidget(self.selectFileButton)
        horizontalLayout.addWidget(self.filePathLineEdit)
        horizontalLayout.addItem(spacerItem1)
        horizontalLayout.addWidget(self.outliersButton)
        
        # Samples Whole
        verticalLayout = QtWidgets.QVBoxLayout()
        verticalLayout.addWidget(self.dataLabel)
        verticalLayout.addLayout(horizontalLayout)
        
        verticalLayout_3 = QtWidgets.QVBoxLayout()
        verticalLayout_3.addWidget(self.scipyDistsLabel)
        verticalLayout_3.addWidget(self.scipyDistsList)

        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.addWidget(self.shape3Text, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.shape2Text, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.shape2Label, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.PPCCButton, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.shape1Label, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.shape1Text, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.shape4Label, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.shape3Label, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.shape4Text, 3, 1, 1, 1)

        verticalLayout_7 = QtWidgets.QVBoxLayout()
        verticalLayout_7.addItem(spacerItem1)
        verticalLayout_7.addLayout(self.gridLayout)
        verticalLayout_7.addItem(spacerItem2)

        verticalLayout_5 = QtWidgets.QVBoxLayout()
        verticalLayout_5.addItem(spacerItem3)
        verticalLayout_5.addWidget(self.rmAllButton)
        verticalLayout_5.addWidget(self.rmButton)
        verticalLayout_5.addWidget(self.addButton)
        verticalLayout_5.addItem(spacerItem4)
        
        horizontalLayout_2 = QtWidgets.QHBoxLayout()
        horizontalLayout_2.addLayout(verticalLayout_3)        
        horizontalLayout_2.addLayout(verticalLayout_7)
        horizontalLayout_2.addWidget(line_2)
        horizontalLayout_2.addLayout(verticalLayout_5)
        
        horizontalLayout_4 = QtWidgets.QHBoxLayout()
        horizontalLayout_4.addItem(spacerItem5)
        horizontalLayout_4.addWidget(self.scipyCallButton)
        horizontalLayout_4.addWidget(self.pdfcdfButton)
        horizontalLayout_4.addItem(spacerItem6)
        
        verticalLayout_9 = QtWidgets.QVBoxLayout()
        verticalLayout_9.addWidget(self.mleLabel)
        verticalLayout_9.addLayout(horizontalLayout_4)
        
        verticalLayout_8 = QtWidgets.QVBoxLayout()
        verticalLayout_8.setContentsMargins(0, -1, 0, -1)
        verticalLayout_8.addWidget(self.probPlotLabel)
        verticalLayout_8.addWidget(self.candDistsTable)
        verticalLayout_8.addWidget(line_4)
        verticalLayout_8.addLayout(verticalLayout_9)

        self.mainVerticalLayout = QtWidgets.QVBoxLayout(self.windowWidget)
        self.mainVerticalLayout.setContentsMargins(5, 5, 5, 5)
        self.mainVerticalLayout.addLayout(verticalLayout)
        self.mainVerticalLayout.addWidget(line)
        self.mainVerticalLayout.addLayout(horizontalLayout_2)
        self.mainVerticalLayout.addWidget(line_3)
        self.mainVerticalLayout.addLayout(verticalLayout_8)

        self.windowWidget.setFocus()
        self.setCentralWidget(self.windowWidget)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 729, 19))
        self.menuAbout = QtWidgets.QMenu(self.menubar)
        self.menuAbout.setTitle("Help")
        self.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        self.actionAbout = QtWidgets.QAction(self)
        self.actionAbout.setText("About")
        self.actionAbout.triggered.connect(self.showAbout)
        self.menuAbout.addAction(self.actionAbout)
        self.menubar.addAction(self.menuAbout.menuAction())

        QtCore.QMetaObject.connectSlotsByName(self)
        # Display GUI
        self.show()


    def updateExisting(function):
        def wrapper(self, *args):
            function(self, *args)
            if self.cDists.get_count() > 0 and self.samples != None:
                self.candListsTableWidget.clearContents()
                self.cDists.calc_all(self.samples, self.qmethod)
                self.updateResults()
        return wrapper   

    def showAbout(self):
        text = \
"""gamut v0.0.1
        
Copyright (c) 2017 Nicholas A. Reynolds
        
Licensed under the MIT License.
        
To report bugs, request features, or see license information, please go to the GitHub repository:  https://github.com/nicholasareynolds/pplotpy
        
This project uses probability plotting both (1) to help scientists and
engineers identify the underlying distribution for his or her set of random
samples, and (2) to predict the values of the parameters in that distribution.  More detail can be found in the references cited in the source code.
        
This project was tested using Python v3.6, and the following libraries:
    - NumPy v1.11.3
    - SciPy v0.19.0
    - matplotlib v2.0.2
    - pyqt5 v5.6.0

As a courtesy, please acknowledge use of gamut in any publications/reports to which it contributes."""
        QtWidgets.QMessageBox.about(self,  "About gamut", text)


    @updateExisting
    def loadSamples(self, *args):
        """Read samples from file, add error message to status bar if error"""

        fpath = QtWidgets.QFileDialog.getOpenFileName(self,
                                                      "Select data file",
                                                      '',
                                                      "Comma-Separated Values (*.csv)")[0]
        try:
            raw_data = np.loadtxt(fpath, delimiter=",")
            self.samples = raw_data.flatten()
            self.statusbar.clearMessage()
            self.scipyDistsList.setEnabled(True)
            self.addButton.setEnabled(True)
            self.filePathLineEdit.setText(fpath)
        except:
            self.samples = None
            self.statusbar.showMessage("Error importing data")
            self.scipyDistsList.setDisabled(True)
            self.addButton.setDisabled(True)
            self.filePathLineEdit.setText("")


    def unlockShapeBoxes(self):
        
        dist_name = self.scipyDistsList.currentItem().text()
        num_shape_params = self.distributions[dist_name]
        self.shape1Text.setText("")
        self.shape2Text.setText("")
        self.shape3Text.setText("")
        self.shape4Text.setText("")

        if num_shape_params == 0:
            self.shape1Label.setEnabled(False)
            self.shape1Text.setEnabled(False)
            self.shape2Label.setEnabled(False)
            self.shape2Text.setEnabled(False)
            self.shape3Label.setEnabled(False)
            self.shape3Text.setEnabled(False)
            self.shape4Label.setEnabled(False)
            self.shape4Text.setEnabled(False)
            self.PPCCButton.setEnabled(False)
        elif num_shape_params == 1:
            self.shape1Label.setEnabled(True)
            self.shape1Text.setEnabled(True)
            self.shape2Label.setEnabled(False)
            self.shape2Text.setEnabled(False)
            self.shape3Label.setEnabled(False)
            self.shape3Text.setEnabled(False)
            self.shape4Label.setEnabled(False)
            self.shape4Text.setEnabled(False)
            self.PPCCButton.setEnabled(True)
        elif num_shape_params == 2:
            self.shape1Label.setEnabled(True)
            self.shape1Text.setEnabled(True)
            self.shape2Label.setEnabled(True)
            self.shape2Text.setEnabled(True)
            self.shape3Label.setEnabled(False)
            self.shape3Text.setEnabled(False)
            self.shape4Label.setEnabled(False)
            self.shape4Text.setEnabled(False)
            self.PPCCButton.setEnabled(False)
        elif num_shape_params == 3:
            self.shape1Label.setEnabled(True)
            self.shape1Text.setEnabled(True)
            self.shape2Label.setEnabled(True)
            self.shape2Text.setEnabled(True)
            self.shape3Label.setEnabled(True)
            self.shape3Text.setEnabled(True)
            self.shape4Label.setEnabled(False)
            self.shape4Text.setEnabled(False)
            self.PPCCButton.setEnabled(False)
        elif num_shape_params == 4:
            self.shape1Label.setEnabled(True)
            self.shape1Text.setEnabled(True)
            self.shape2Label.setEnabled(True)
            self.shape2Text.setEnabled(True)
            self.shape3Label.setEnabled(True)
            self.shape3Text.setEnabled(True)
            self.shape4Label.setEnabled(True)
            self.shape4Text.setEnabled(True)
            self.PPCCButton.setEnabled(False)



    def updateResults(self):
        """Recalculate values from prob. plot and update the candidates table"""

        self.cDists.calc_all(self.samples, self.qmethod)
        for ii, dist in enumerate(self.cDists.dists):
            self.updateRow(ii, dist)
        
        
    def updateRow(self, row_index, dist_obj):
        """Query values from distr. object, and update cand. distr. table"""

        self.candDistsTable.setItem(row_index,
                                    0,
                                    QtWidgets.QTableWidgetItem(dist_obj.get_label()))
        self.candDistsTable.setItem(row_index,
                                    1,
                                    QtWidgets.QTableWidgetItem(str(dist_obj.get_r2())))
        self.candDistsTable.setItem(row_index,
                                    2,
                                    QtWidgets.QTableWidgetItem(str(dist_obj.get_loc())))
        self.candDistsTable.setItem(row_index,
                                    3,
                                    QtWidgets.QTableWidgetItem(str(dist_obj.get_scale())))
        # Shape Parameters
        num_shapes = dist_obj.get_shape_count()
        shape_params = dist_obj.get_shapes()
        for ii in range(4,8):
            if ii - 4 < num_shapes:
                text = str(shape_params[ii-4])
            else:
                text = "NA"
            self.candDistsTable.setItem(row_index,
                                        ii,
                                        QtWidgets.QTableWidgetItem(text))


    def addRow(self):
        """Add a blank row to the candidate distributions table."""

        row_index = self.candDistsTable.rowCount()
        self.candDistsTable.insertRow(row_index)
        return row_index


    def updateShape1(self, value):
        self.shape1Changed = False
        self.shape1Value

    def calcPPCC(self):
        dist_name = self.scipyDistsList.currentItem().text()
        print(self.shape1Value)
        ShapeFactorBoundsWindow(self,
                                self.samples,
                                dist_name,
                                self.shape1Value,
                                self.shape1Changed)
        print(self.shape1Value)
        if self.shape1Changed == True:
            self.shape1Changed = False
            self.shape1Text.setText(str(self.shape1Value))

    def addDistByButton(self):
        """Instantiate obj. from highlighted item; add to cand. distr. table."""
        dist_name = self.scipyDistsList.currentItem().text()
        self.addDistribution(dist_name) 


    def addDistByDClick(self, item):
        """Instantiate obj. from double-clicked item; calc vals, & add to table"""
        dist_name = item.text()
        self.addDistribution(dist_name) 


    def addDistribution(self, dist_name):
        """Instantiate a dist. obj. by label; calc. values, and add to table."""

        shape_factors = list()  # Initialize

        num_shape_facs = self.distributions[dist_name]

        # Check for valid number of shape factors specified
        for index, textBox in zip(range(num_shape_facs),
                                  [self.shape1Text,
                                   self.shape2Text,
                                   self.shape3Text,
                                   self.shape4Text]):
            try:
                shape_factors.append( float(textBox.text()) )
            except ValueError:
                self.statusbar.showMessage("All shape factors must be validly defined")
                return
            
        # Ready-to-go
        self.statusbar.clearMessage()
        dist_obj = SciPyContDist(label=dist_name,
                                 shape_count=num_shape_facs)
        dist_obj.set_shapes(*shape_factors)
        dist_obj.MLE_fit()
        self.cDists.add_distribution(dist_obj, self.samples)
        row_index = self.addRow()
        self.updateRow(row_index, self.cDists.get_obj(-1))
        self.rmButton.setEnabled(True)
        self.rmAllButton.setEnabled(True)
        self.scipyCallButton.setEnabled(True)
        self.pdfcdfButton.setEnabled(True)


    def rmDistribution(self):
        """ Remove the selected distribution from the cand. distr. table."""

        try:
            row = self.candDistsTable.currentRow()
            self.cDists.remove_dist(row)
            self.candDistsTable.removeRow(row)
            if self.candDistsTable.rowCount() == 0:
                self.rmButton.setEnabled(False)
                self.rmAllButton.setEnabled(False)
                self.scipyCallButton.setEnabled(False)
                self.pdfcdfButton.setEnabled(False)
        except:
            self.statusbar.showMessage("Select a cand. distri. to remove")


    def rmAllDistributions(self):
        """Clear all candidate distributions (empty table)"""

        self.candDistsTable.clearContents()
        self.candDistsTable.setRowCount(0)
        self.cDists.remove_all()
        self.rmButton.setEnabled(False)
        self.rmAllButton.setEnabled(False)
        self.scipyCallButton.setEnabled(False)
        self.pdfcdfButton.setEnabled(False)


    def makePPlot(self, item):
        """Open a new window with prob. plot of double-clicked cand. distr."""

        row = item.row()
        dist_obj = self.cDists.get_obj(row)
        dist_name = dist_obj.get_label()
        PlotWindow(self,dist_obj, dist_name, plot_type="pplot")


    def makePDFCDF(self, item):

        row = self.candDistsTable.currentRow()
        dist_obj = self.cDists.get_obj(row)
        dist_name = dist_obj.get_label()
        PlotWindow(self,dist_obj, dist_name, plot_type="pdfcdf")

    def showScipyDef(self):
        "Display syntax for declaring a RV using param values found with pplotpy"
        
        row = self.candDistsTable.currentRow()
        dist_obj = self.cDists.get_obj(row)
        text = """
import scipy.stats
        
%s""" % dist_obj.get_scipy_command()
        QtWidgets.QMessageBox.about(self,
                                    "SciPy Definition: " + dist_obj.get_label(),
                                    text)


class PlotWindow(QtWidgets.QMainWindow):
    """PlotWindow is a child window that hosts the probability plot canvas"""
    
    def __init__(self,
                 parent,
                 dist_obj,
                 dist_name,
                 plot_type="pplot"):
        super().__init__(parent=parent)
        self.dist_obj = dist_obj
        self.plot_canvas = PlotCanvas(self)
        self.plot_type == plot_type
        if self.plot_type == "pplot":
            self.plot_canvas.pplot(dist_obj)
        elif self.plot_type == "pdfcdf":
            self.plot_canvas.plot_pdfcdf(dist_obj)
        self.windowWidget = QtWidgets.QWidget(self)
        self.setWindowTitle(dist_name)
        self.initUI()


    def initUI(self):

        # --- Declare Items to go in window ---
        
        # Save Button (Save File Dialog)
        saveButton_plot = QtWidgets.QPushButton()
        saveButton_plot.setText("Save Plot")

        # action
        saveButton_plot.clicked.connect(self.savePlot)

        # Spacers
        spacerItem1  = QtWidgets.QSpacerItem(40, 20,
                                             QtWidgets.QSizePolicy.Expanding,
                                             QtWidgets.QSizePolicy.Minimum)
        spacerItem2  = QtWidgets.QSpacerItem(40, 20,
                                             QtWidgets.QSizePolicy.Expanding,
                                             QtWidgets.QSizePolicy.Minimum)

        # --- Assemble ---
        horizontalLayout = QtWidgets.QHBoxLayout()
        horizontalLayout.addItem(spacerItem1)
        horizontalLayout.addWidget(saveButton_plot)
        horizontalLayout.addItem(spacerItem2)

        verticalLayout = QtWidgets.QVBoxLayout(self.windowWidget)
        verticalLayout.addWidget(self.plot_canvas)
        verticalLayout.addLayout(horizontalLayout)

        self.windowWidget.setFocus()
        self.setCentralWidget(self.windowWidget)
        self.show()

    def savePlot(self, *args):
        """Save a *.png of the present probability plot"""

        fpath = QtWidgets.QFileDialog.getSaveFileName(self.windowWidget,
                                                      "Specify destination",
                                                      '',
                                                      "Portable Networks Graphic (*.png)")[0]
        if fpath:
            try:
                import matplotlib.pyplot as plt
                axes = plt.axes()
                
                if self.plot_type == "pplot":
                    self.dist_obj.create_pplot(axes)
                elif self.plot_type == "pdfcdf":
                    self.dist_obj.plot_pdfcdf(axes)
                plt.savefig(fpath, dpi=600)
                plt.close()
            except:
                pass
    



class PlotCanvas(FigureCanvas):
    """Surfaces/axes onto which prob. plot is made, embedded in matplotlib window"""
 
    def __init__(self,
                 parent=None):
        fig = Figure()
        self.axes = fig.add_subplot(111)
 
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
     
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

  
    def pplot(self, dist_obj):
        # Pass axes from canvas to the distr. obj. for plotting
        dist_obj.create_pplot(self.axes)
        self.draw()

    def plot_pdfcdf(self, dist_obj):
        # Pass axes from canvas to the distr. obj. for plotting
        dist_obj.plot_pdfcdf(self.axes)
        self.draw()


class ShapeFactorBoundsWindow(QtWidgets.QMainWindow):

    def __init__(self,
                 parent,
                 samples,
                 dist_name,
                 shape_fac_value,
                 isChanged=False):
        super().__init__(parent=parent)
        
        # Definite attributes
        self.value = shape_fac_value
        self.samples = samples
        self.distribution = dist_name
        self.changeBool = isChanged

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

        self.setCentralWidget(self.windowWidget)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

    def calcPPCC(self):
        #try:
            lowerBound = float(self.lowerBoundLineEdit.text()) 
            upperBound = float(self.upperBoundLineEdit.text()) 
            value = stats.ppcc_max(self.samples,
                                        brack=(lowerBound,
                                               upperBound),
                                        dist=self.distribution)
            super().updateShape1(value)
            self.changeBool = True
            self.statusbar.clearMessage()

            self.close()
            
        #except ValueError:
        #    self.statusbar.showMessage("Invalid entry for shape factors bounds")
        #    return

        #except:
            #self.statusbar.showMessage("Error during calculation of shape factor")
            #return


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    sys.exit(app.exec_())
        
        
