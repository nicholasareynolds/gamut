###############################################################################
#
#    gamut
#    Copyright (C) 2017,  Nicholas A. Reynolds
#
#    Full License Available in LICENSE file at
#    https://github.com/nicholasareynolds/gamut
#
###############################################################################

from PyQt5 import QtCore, QtGui, QtWidgets
import matplotlib
matplotlib.rcParams['backend'] = "Qt5Agg"
matplotlib.rcParams['font.size'] = 6
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PlotWindow(QtWidgets.QMainWindow):
    """
    PlotWindow is a child window to gamut that hosts plot canvases
    
    """
    
    def __init__(self,
                 parent,
                 dist_obj,
                 dist_name,
                 plot_type="pplot"):
        super().__init__(parent=parent)
        self.dist_obj = dist_obj
        self.plot_type = plot_type
        if self.plot_type == "pplot":
            self.plot_canvas = ProbabilityPlot(self,
                                               dist_obj=dist_obj)
        elif self.plot_type == "pdfcdf":
            self.plot_canvas = PDFCDFPlot(self,
                                          dist_obj=dist_obj)
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
    """
    Surfaces/axes onto which a matplotlib plot is made, and which can be
    embedded in a GUI child-window
    
    PlotCanvas is a master class
    """
 
    def __init__(self,
                 parent=None,
                 dist_obj=None):
        self.dist_obj=dist_obj
        fig = Figure()
        self.axes = fig.add_subplot(111) 
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
     
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self._plot()
        self.draw()

class ProbabilityPlot(PlotCanvas):
    
    def _plot(self):
        """
        Draw  probability plot on provided axes
        """
        self.dist_obj.create_pplot(self.axes)
        self.draw()

  
    
class PDFCDFPlot(PlotCanvas):
    
    def _plot(self):
        """
        Call on distribution object to draw combined PDF/CDF on class axes
        """
        self.dist_obj.plot_pdfcdf(self.axes)
        self.draw()
