################################################################################
#
#    pplotpy - a probability plotting tool for Python
#    Copyright (C) 2017,  Nicholas A. Reynolds
#
#    Full License Available in LICENSE file at
#    https://github.com/nicholasareynolds/pplotpy
#
################################################################################

from PyQt5 import QtCore, QtWidgets
from numpy import loadtxt
import matplotlib
matplotlib.rcParams['backend'] = "Qt5Agg"
matplotlib.rcParams['font.size'] = 6
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from pplotpy import distributions
from pplotpy import quantiles


class MainWindow(QtWidgets.QMainWindow):
    """Main window of pplotpy; no parent higher than this object"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize
        self.samples = None
        self.cDists = distributions.CandidateDistributions()
        self.aDists = distributions.SupportedDistributions.subclasses.keys()
        self.quantile_choices = quantiles.Quantiles.subclasses.keys()
        self.qmethod = list(self.quantile_choices)[0]
        self.table_headers = ["Distribution",
                              "Location",
                              "Scale",
                              "Shape",
                              "R^2"]
        self.initUI()
        

    def initUI(self):
        """Set up user interface"""

        # Main Window Area
        self.setWindowTitle("pplotpy")
        self.resize(566, 520)
        self.windowWidget = QtWidgets.QWidget(self)
        self.windowWidget.setGeometry(QtCore.QRect(10, 10, 541, 461))

        # --- Declare Widgets ---

        # Data Button (Open File Dialog)
        self.dataFileButton = QtWidgets.QPushButton()
        self.dataFileButton.setText("Data File")
        # action
        self.dataFileButton.clicked.connect(self.loadSamples)

        # File Path (Path to Data Sample File)
        self.dataFilePath = QtWidgets.QLineEdit()
        self.dataFilePath.setEnabled(False)


        # Quantiles (Combo Box)
        self.quantileLabel = QtWidgets.QLabel()
        self.quantileLabel.setText("Quantile Method:")
        self.quantileComboBox = QtWidgets.QComboBox()
        self.quantileComboBox.addItems(self.quantile_choices)
        # action
        self.quantileComboBox.activated.connect(self.updateQMethod) 

        # Available Distributions (List Box)
        self.availDistsLabel = QtWidgets.QLabel()
        self.availDistsLabel.setText("Available Distributions:")
        self.availDistsListWidget = QtWidgets.QListWidget()
        self.availDistsListWidget.setEnabled(False)
        self.availDistsListWidget.addItems(self.aDists)
        self.availDistsListWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.availDistsListWidget.setCurrentRow(0)
        # actions
        self.availDistsListWidget.itemClicked.connect(self.unlockLocTextBox)
        self.availDistsListWidget.itemDoubleClicked.connect(self.addDistByDClick)

        # Location Parameter (optional user-specified)
        self.locLabel = QtWidgets.QLabel()
        self.locLabel.setEnabled(False)
        self.locLabel.setText("Location:")
        self.locTextBox = QtWidgets.QLineEdit()
        self.locTextBox.setEnabled(False)
        self.locTextBox.setMaximumSize(QtCore.QSize(50, 16777215))
        self.locTextBox.setText("")

        # Remove All (Button)
        self.removeAllButton = QtWidgets.QPushButton()
        self.removeAllButton.setText("Remove All")
        # action
        self.removeAllButton.clicked.connect(self.rmAllDistributions)

        # Remove (Button)
        self.removeButton = QtWidgets.QPushButton()
        self.removeButton.setText("Remove")
        self.removeButton.setDisabled(True)
        # action
        self.removeButton.clicked.connect(self.rmDistribution)

        # Add (Button)
        self.addButton = QtWidgets.QPushButton()
        self.addButton.setText("Add")
        self.addButton.setDisabled(True)
        # action
        self.addButton.clicked.connect(self.addDistByButton)

        # Candidate Distributions (Table)
        self.candDistsLabel = QtWidgets.QLabel()
        self.candDistsLabel.setText("Candidate Distributions:")
        self.candListsTableWidget = QtWidgets.QTableWidget()
        self.candListsTableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.candListsTableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.candListsTableWidget.setColumnCount(5)
        self.candListsTableWidget.setRowCount(0)
        self.candListsTableWidget.setHorizontalHeaderLabels(self.table_headers)
        self.candListsTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        # action
        self.candListsTableWidget.itemDoubleClicked.connect(self.makePPlot)
        self.candListsTableWidget.itemClicked.connect(self.enablePrintScipy)
        

        # Print SciPy (button)
        self.printScipyButton = QtWidgets.QPushButton()
        self.printScipyButton.setText("Print SciPy")
        self.printScipyButton.setDisabled(True)
        self.printScipyButton.clicked.connect(self.showScipyDef)

        # Lines 
        #   (between Data File and Quantile Combo Box) 
        self.line_2 = QtWidgets.QFrame()
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        #   (between 1st (file/quantile) & 2nd (supported distributions)
        self.line_4 = QtWidgets.QFrame()
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.line = QtWidgets.QFrame()
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.line_3 = QtWidgets.QFrame()
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.line_5 = QtWidgets.QFrame()
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)

        # Spacer Items
        spacerItem  = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)


        # --- Organize Widgets via Layout Boxes (independent/small to large containers) ---

        # Add/Remove Distribution buttons
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.addWidget(self.removeAllButton)
        self.verticalLayout_5.addWidget(self.removeButton)
        self.verticalLayout_5.addWidget(self.addButton)
 
        # Available Distributions
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.addWidget(self.availDistsLabel)
        self.verticalLayout_4.addWidget(self.availDistsListWidget)

        # Data File Path
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.addItem(spacerItem)
        self.verticalLayout_3.addWidget(self.dataFilePath)
        self.verticalLayout_3.addItem(spacerItem1)

        # Data File
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.addWidget(self.dataFileButton)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)

        # Quantile Box
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.addItem(spacerItem2)
        self.verticalLayout_2.addWidget(self.quantileLabel, 0, QtCore.Qt.AlignHCenter)
        self.verticalLayout_2.addWidget(self.quantileComboBox, 0, QtCore.Qt.AlignTop)
        self.verticalLayout_2.addItem(spacerItem3)

        # Top Row of Widgets
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout.addWidget(self.line_2)
        self.horizontalLayout.addLayout(self.verticalLayout_2)

        # Center Row of Widgets
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.addLayout(self.verticalLayout_4)
        self.horizontalLayout_3.addWidget(self.locLabel)
        self.horizontalLayout_3.addWidget(self.locTextBox)
        self.horizontalLayout_3.addItem(spacerItem4)
        self.horizontalLayout_3.addWidget(self.line)
        self.horizontalLayout_3.addLayout(self.verticalLayout_5)

        # Print Buttons
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.addItem(spacerItem5)
        self.horizontalLayout_4.addWidget(self.printScipyButton)
        self.horizontalLayout_4.addItem(spacerItem6)

        # Main Organizer of the GUI 
        self.verticalLayout = QtWidgets.QVBoxLayout(self.windowWidget)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.line_4)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.verticalLayout.addWidget(self.line_3)
        self.verticalLayout.addWidget(self.candDistsLabel)
        self.verticalLayout.addWidget(self.candListsTableWidget)
        self.verticalLayout.addWidget(self.line_5)
        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.windowWidget.raise_()
        self.candListsTableWidget.raise_()

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 566, 19))
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

    # Wrapper Defintion for updating/re-calculating all distributions
    def updateExisting(function):
        def wrapper(self, *args):
            function(self, *args)
            if self.cDists.get_count() > 0 and self.samples != None:
                self.candListsTableWidget.clearContents()
                self.cDists.calc_all(self.samples, self.qmethod)
                self.updateResults()
        return wrapper      

    @updateExisting
    def loadSamples(self, *args):
        """Read samples from file, add error message to status bar if error"""

        fpath = QtWidgets.QFileDialog.getOpenFileName(self,
                                                      "Select data file",
                                                      '',
                                                      "Comma-Separated Values (*.csv)")[0]
        try:
            raw_data = loadtxt(fpath, delimiter=",")
            self.samples = raw_data.flatten()
            self.statusbar.clearMessage()
            self.availDistsListWidget.setEnabled(True)
            self.addButton.setEnabled(True)
            self.dataFilePath.setText(fpath)
        except:
            self.samples = None
            self.statusbar.showMessage("Error importing data")
            self.availDistsListWidget.setDisabled(True)
            self.addButton.setDisabled(True)
            self.dataFilePath.setText("")


    def unlockLocTextBox(self, item):
        """Enable location text field if permitted for highlighted distribution"""

        dist_name = item.text()
        if distributions.SupportedDistributions.has_optional_loc_param(dist_name) == True:
            self.locTextBox.setEnabled(True)
            self.locLabel.setEnabled(True)
            self.locTextBox.setText("0.0")
        else:
            self.locTextBox.setDisabled(True)
            self.locLabel.setDisabled(True)
            self.locTextBox.setText("")
   
 
    @updateExisting
    def updateQMethod(self, index):
        """Store the string assoc. with the quantile method selected in combo box"""

        self.qmethod =self.quantileComboBox.currentText()

        
    def updateResults(self):
        """Recalculate values from prob. plot and update the candidates table"""

        self.cDists.calc_all(self.samples, self.qmethod)
        for ii, dist in enumerate(self.cDists.dists):
            self.updateRow(ii, dist)

        
    def updateRow(self, row_index, dist_obj):
        """Query values from distr. object, and update cand. distr. table"""

        self.candListsTableWidget.setItem(row_index,
                                          0,
                                          QtWidgets.QTableWidgetItem(dist_obj.get_label()))
        self.candListsTableWidget.setItem(row_index,
                                          1,
                                          QtWidgets.QTableWidgetItem(dist_obj.get_loc_str()))
        self.candListsTableWidget.setItem(row_index,
                                          2,
                                          QtWidgets.QTableWidgetItem(dist_obj.get_scale_str()))
        self.candListsTableWidget.setItem(row_index,
                                          3,
                                          QtWidgets.QTableWidgetItem(dist_obj.get_shape_str()))
        self.candListsTableWidget.setItem(row_index,
                                          4,
                                          QtWidgets.QTableWidgetItem(dist_obj.get_coeff_of_determ_str()))


    def addRow(self):
        """Add a blank row to the candidate distributions table."""

        row_index = self.candListsTableWidget.rowCount()
        self.candListsTableWidget.insertRow(row_index)
        return row_index


    def addDistByButton(self):
        """Instantiate obj. from highlighted item; add to cand. distr. table."""
 
        dist_name = self.availDistsListWidget.currentItem().text()
        self.addDistribution(dist_name) 


    def addDistByDClick(self, item):
        """Instantiate obj. from double-clicked item; calc vals, & add to table"""

        dist_name = item.text()
        self.addDistribution(dist_name)        


    def addDistribution(self, dist_name):
        """Instantiate a dist. obj. by label; calc. values, and add to table."""

        dist_obj = distributions.SupportedDistributions.create_subclass_instance(dist_name)
        if dist_obj.loc_optional == True:
            loc_val = float(self.locTextBox.text())
            dist_obj.set_location(loc_val)
        self.cDists.add_distribution(dist_obj, self.samples, self.qmethod)
        
        row_index = self.addRow()
        self.updateRow(row_index, self.cDists.get_obj(-1))
        self.removeButton.setEnabled(True)
        

    def makePPlot(self, item):
        """Open a new window with prob. plot of double-clicked cand. distr."""

        row = item.row()
        dist_obj = self.cDists.get_obj(row)
        dist_name = dist_obj.get_label()
        PlotWindow(self,dist_obj, dist_name)


    def rmDistribution(self):
        """ Remove the selected distribution from the cand. distr. table."""

        try:
            row = self.candListsTableWidget.currentRow()
            self.cDists.remove_dist(row)
            self.candListsTableWidget.removeRow(row)
            if self.candListsTableWidget.rowCount() == 0:
                self.removeButton.setDisabled(True)
                self.printScipyButton.setDisabled(True)
        except:
            self.statusbar.showMessage("Select a cand. distri. to remove")


    def rmAllDistributions(self):
        """Clear all candidate distributions (empty table)"""

        self.candListsTableWidget.clearContents()
        self.candListsTableWidget.setRowCount(0)
        self.printScipyButton.setDisabled(True)
        self.cDists.remove_all()

    def showAbout(self):
        text = \
"""pplotpy v0.0.1
        
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

As a courtesy, please acknowledge use of pplotpy in any publications/reports to which it contributes."""
        QtWidgets.QMessageBox.about(self,  "About pplotpy", text)


    def enablePrintScipy(self):
        "Enable 'Print SciPy'; activated once a candidate distribution is selected"
        
        self.printScipyButton.setEnabled(True)


    def showScipyDef(self):
        "Display syntax for declaring a RV using param values found with pplotpy"
        
        row = self.candListsTableWidget.currentRow()
        dist_obj = self.cDists.get_obj(row)
        text = """
import scipy.stats
        
%s""" % dist_obj.get_scipy_command()
        QtWidgets.QMessageBox.about(self,
                                    "SciPy Definition: " + dist_obj.get_label(),
                                    text)


class PlotWindow(QtWidgets.QMainWindow):
    """PlotWindow is a child window that hosts the probability plot canvas"""
    
    def __init__(self, parent, dist_obj, dist_name):
        super().__init__(parent=parent)
        self.dist_obj = dist_obj
        self.pplot_canvas = PlotCanvas(self)
        self.pplot_canvas.pplot(dist_obj)
        self.pdfcdf_canvas = PlotCanvas(self)
        self.pdfcdf_canvas.plot_pdfcdf(dist_obj)
        self.windowWidget = QtWidgets.QWidget(self)
        self.setWindowTitle(dist_name)
        self.initUI()


    def initUI(self):

        # --- Declare Items to go in window ---
        
        # Save Button (Save File Dialog)
        saveButton_pplot = QtWidgets.QPushButton()
        saveButton_pplot.setText("Save Plot")
        saveButton_pdfcdfplot = QtWidgets.QPushButton()
        saveButton_pdfcdfplot.setText("Save Plot")

        # action
        saveButton_pplot.clicked.connect(self.savePPlot)
        saveButton_pdfcdfplot.clicked.connect(self.savePdfCdfPlot)


        # Spacers
        spacerItem1  = QtWidgets.QSpacerItem(40, 20,
                                             QtWidgets.QSizePolicy.Expanding,
                                             QtWidgets.QSizePolicy.Minimum)
        spacerItem2  = QtWidgets.QSpacerItem(40, 20,
                                             QtWidgets.QSizePolicy.Expanding,
                                             QtWidgets.QSizePolicy.Minimum)
        spacerItem3  = QtWidgets.QSpacerItem(40, 20,
                                             QtWidgets.QSizePolicy.Expanding,
                                             QtWidgets.QSizePolicy.Minimum)
        spacerItem4  = QtWidgets.QSpacerItem(40, 20,
                                             QtWidgets.QSizePolicy.Expanding,
                                             QtWidgets.QSizePolicy.Minimum)



        # Labels
        pplotLabel = QtWidgets.QLabel()
        pplotLabel.setText("Probability Plot:")
        pdfcdfLabel = QtWidgets.QLabel()
        pdfcdfLabel.setText("Resulting SciPy Distribution:")

        # --- Assemble ---
        horizontalLayout_left = QtWidgets.QHBoxLayout()
        horizontalLayout_left.addItem(spacerItem1)
        horizontalLayout_left.addWidget(saveButton_pplot)
        horizontalLayout_left.addItem(spacerItem2)

        horizontalLayout_right = QtWidgets.QHBoxLayout()
        horizontalLayout_right.addItem(spacerItem3)
        horizontalLayout_right.addWidget(saveButton_pdfcdfplot)
        horizontalLayout_right.addItem(spacerItem4)

        verticalLayout_left = QtWidgets.QVBoxLayout()
        verticalLayout_left.addWidget(pplotLabel)
        verticalLayout_left.addWidget(self.pplot_canvas)
        verticalLayout_left.addLayout(horizontalLayout_left)

        verticalLayout_right = QtWidgets.QVBoxLayout()
        verticalLayout_right.addWidget(pdfcdfLabel)
        verticalLayout_right.addWidget(self.pdfcdf_canvas)
        verticalLayout_right.addLayout(horizontalLayout_right)

        horizontalLayout = QtWidgets.QHBoxLayout(self.windowWidget)
        horizontalLayout.addLayout(verticalLayout_left)
        horizontalLayout.addLayout(verticalLayout_right)

        self.windowWidget.setFocus()
        self.setCentralWidget(self.windowWidget)
        self.show()

    def savePPlot(self, *args):
        """Save a *.png of the present probability plot"""

        fpath = QtWidgets.QFileDialog.getSaveFileName(self.windowWidget,
                                                      "Specify destination",
                                                      '',
                                                      "Portable Networks Graphic (*.png)")[0]
        if fpath:
            try:
                import matplotlib.pyplot as plt
                axes = plt.axes()
                self.dist_obj.create_pplot(axes)
                plt.savefig(fpath, dpi=600)
                plt.close()
            except:
                pass
    

    def savePdfCdfPlot(self, *args):
        """Save a *.png of the present cdf-pdf plot"""

        fpath = QtWidgets.QFileDialog.getSaveFileName(self.windowWidget,
                                                      "Specify destination",
                                                      '',
                                                      "Portable Networks Graphic (*.png)")[0]
        if fpath:
            try:
                import matplotlib.pyplot as plt
                axes = plt.axes()
                self.dist_obj.plot_cpdfcdf(axes)
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
        #fig.tight_layout()
  
    def pplot(self, dist_obj):
        # Pass axes from canvas to the distr. obj. for plotting
        dist_obj.create_pplot(self.axes)
        self.draw()

    def plot_pdfcdf(self, dist_obj):
        # Pass axes from canvas to the distr. obj. for plotting
        dist_obj.plot_pdfcdf(self.axes)
        self.draw()
        

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    sys.exit(app.exec_())

