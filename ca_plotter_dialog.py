# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CAPlotterDialog
                                 A QGIS plugin
 Creates Concentration (z value)-area plots of rasters. A method of visualising the fractal dimension of a gridded property, and can be used to help determine background thresholds of geochemical datasets
                             -------------------
        begin                : 2015-03-03
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Alex Brown
        email                : sdfasdfsdfdfs
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic

import qgis.core
from qgis.utils import *
from qgis.gui import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import rcParams
from matplotlib import pyplot as plt

import numpy as np
import numpy.ma as ma

from osgeo import gdal
import GdalTools_utils as gTools

import ca_plotter_utils as utils

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'CAPLot.ui'))


class CAPlotterDialog(QtGui.QDialog, FORM_CLASS):

    caPlotFigure = None
   

    
    def __init__(self, parent=None):
        """Constructor."""
        super(CAPlotterDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        self.manageGui()
        unitItems = ['ppm','ppb','ppt','perc']
        self.selUnits.addItems(unitItems)
        #initialise matplot figure/canvas
        
        CAPlotterDialog.caPlotFigure = InitFigure(self.plotArea, self.plotToolbar)
        
        #button actions
        self.layerRef.clicked.connect(self.manageGui)
        self.calcBtn.clicked.connect(self.calc)
        self.plotrefBtn.clicked.connect(self.refreshPlot)
        self.thrBtn1.clicked.connect(self.getThresh1)
        self.thrBtn2.clicked.connect(self.getThresh2)
        self.thrBtn3.clicked.connect(self.getThresh3)
        self.threshplotBtn.clicked.connect(self.refreshPlot)
        self.fileBtn.clicked.connect(self.showFileBrowser)
        
    def manageGui(self):
		#populate the combo box
		self.layerCbx.clear()
		self.layerCbx.addItems(utils.getRasterLayerNames())
        
    def getInput(self):
        
        if self.layerRbtn.isChecked():
            input = self.layerCbx.currentText()
            targetLayer = utils.getRasterLayerByName(input)
           
        else:
            targetLayer = self.layerLedit.text()
            
        return targetLayer
            
        
    def calc(self):
        
        #get input layer from dialog
        inputLayer = self.getInput()
        analysis = FractalMethod(inputLayer)
        #extract data for analysis
        analysis.getData()
        #create points to plot
        analysis.createPoints()
        #get plot decoration parameters
        pTitle = self.titleLedit.text()
        units = self.selUnits.currentText()
        #placeholder threshold points ensures no threshold points are plotted before a curve has been seen
        threshX = []
        threshY = []
        #create the plot
        CreatePlot(pTitle, units, FractalMethod.xData, FractalMethod.yData, threshX, threshY)
        
        
    def refreshPlot(self):
    
        #get plot decoration parameters
        pTitle = self.titleLedit.text()
        units = self.selUnits.currentText()
        #get threshold points from user input
        threshX = self.thresholdListX()
        threshY = self.thresholdListY()
        #create the plot
        CreatePlot(pTitle, units, FractalMethod.xData, FractalMethod.yData, threshX, threshY)
        
    def showFileBrowser(self):
        #still to implement
             
        lastUsedFilter = gTools.FileFilter.lastUsedRasterFilter()
        inputFile = gTools.FileDialog.getOpenFileName(self, self.tr( "Select the input file for Polygonize" ), gTools.FileFilter.allRastersFilter(), lastUsedFilter )
        if not inputFile:
            return
        gTools.FileFilter.setLastUsedRasterFilter(lastUsedFilter)
        
        self.layerLedit.setText(inputFile)
        
    def getThresh1(self):
            
        guiTar = self.threshpoint1
        self.Thresh1 = PointPicker(guiTar)
        
    def getThresh2(self):
            
        guiTar = self.threshpoint2
        self.Thresh2 = PointPicker(guiTar)
        
    def getThresh3(self):
            
        guiTar = self.threshpoint3
        self.Thresh3 = PointPicker(guiTar)
        
    def thresholdListX(self):
        
        if self.thrChk3.isChecked():
            list = [self.Thresh1.xTar, self.Thresh2.xTar, self.Thresh3.xTar]
            
        elif self.thrChk2.isChecked():
            list = [self.Thresh1.xTar, self.Thresh2.xTar]
            
        elif self.thrChk1.isChecked():
            list = [self.Thresh1.xTar]
            
        else :
            list = []
            
        return list
      
    
    def thresholdListY(self):
    
        if self.thrChk3.isChecked():
            list = [self.Thresh1.yTar, self.Thresh2.yTar, self.Thresh3.yTar]
            
        elif self.thrChk2.isChecked():
            list = [self.Thresh1.yTar, self.Thresh2.yTar]
            
        elif self.thrChk1.isChecked():
            list = [self.Thresh1.yTar]
            
        else :
            list = []
            
        return list
    
        
    def printer(self):
        #mainly for debug purposes
        output = self.thresholdListX()
        print output
        
   
class PointPicker:
    def __init__(self,  guiTar):
        self.xTar = 0
        self.yTar = 0
        self.guiTar = guiTar
        self.cid = CAPlotterDialog.caPlotFigure.canvas.mpl_connect('button_press_event', self)
        guiTar.textEdited.connect(self.manualSet)
        
    def __call__(self, event):
        CAPlotterDialog.thrClick = [event.xdata, event.ydata]
        self.guiTar.setText("{0:.1f}".format(event.xdata))
        self.xTar = event.xdata
        self.yTar = event.ydata
        CAPlotterDialog.caPlotFigure.canvas.mpl_disconnect(self.cid)
    
         
    def manualSet(self):
        self.xTar = float(self.guiTar.text())
        
class InitFigure:
    
    def __init__(self, plotTarget, barTarget):
         # add matplotlib figure to dialog
        self.plotTarget = plotTarget  
        self.barTarget = barTarget
        
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        self.mpltoolbar = NavigationToolbar(self.canvas, self.barTarget)
        lstActions = self.mpltoolbar.actions()
        self.mpltoolbar.removeAction(lstActions[7])
        self.plotTarget.addWidget(self.canvas)
        self.plotTarget.addWidget(self.mpltoolbar)

        # and configure matplotlib params
        rcParams["font.serif"] = "Verdana, Arial, Liberation Serif"
        rcParams["font.sans-serif"] = "Tahoma, Arial, Liberation Sans"
        rcParams["font.cursive"] = "Courier New, Arial, Liberation Sans"
        rcParams["font.fantasy"] = "Comic Sans MS, Arial, Liberation Sans"
        rcParams["font.monospace"] = "Courier New, Liberation Mono"

        
class FractalMethod:

    xData = []
    yData = []
    tarLayer = 0
    cleanData =0
    #perhaps should move variables into constructor to make instance variables rather than class variables
    def __init__(self, inputLayer):
        
        FractalMethod.tarLayer = inputLayer
        
            
    
    def getData(self):
        try:
            rs =  gdal.Open(FractalMethod.tarLayer)
        except RuntimeError as ex:
            raise IOError(ex)
   
        band = rs.GetRasterBand(1)
        ndv = band.GetNoDataValue()
        myArray = np.array(band.ReadAsArray())
        #mask the array for the no data values, either use the ndv or less than 0,
        #as no grid should have a valid negative value
        maskArray = ma.masked_less_equal(myArray , 0)
        #compress the masked array so that it will work with histogram. 
        #This removes the masked values from the masked array
        FractalMethod.cleanData = maskArray.compressed()
    
    def createPoints(self):
        #initialise points to plot based on the distribution of pixel values. will be plotted on X
        FractalMethod.xData = np.percentile(FractalMethod.cleanData, [5,10,20,30,40,50,60,70,80,85,90,92.5,95,97,98,99,99.5,99.8])
        
        #populate pixel values with the number of pixels of that value or less. will be plotted on Y
        FractalMethod.yData=[]
        #print classbreak
        for i in FractalMethod.xData:
            cum = (FractalMethod.cleanData >= i ).sum()
            FractalMethod.yData.append( cum)
            
class CreatePlot:
    
    #class to plot the concentration area graph. inputs are concentration on X, number of pixels on Y
    def __init__(self, pTitle, units, xData, yData, threshX, threshY ):
        # create threshold string to print on plot from threshhold points
        if len(threshX) == 3:
            #for 3 thresholds
            threshstring = '{0:.1f}\n{1:.1f}\n{2:.1f}'.format(threshX[0], threshX[1], threshX[2])
        elif len(threshX) == 2:
            #for 2 thresholds
            threshstring = '{0:.1f}\n{1:.1f}'.format(threshX[0], threshX[1])
        elif   len(threshX) == 1:
             threshstring = '{0:.1f}'.format(threshX[0])
        else :
            threshstring = "Pick Thresholds"

        labelstring = 'Concentration ' + units
        
        CAPlotterDialog.caPlotFigure.axes.clear()
        CAPlotterDialog.caPlotFigure.axes.plot(xData, yData, c='b', marker='.', ms=10)
        CAPlotterDialog.caPlotFigure.axes.plot(threshX, threshY, 'rs', ms =9)
        CAPlotterDialog.caPlotFigure.axes.set_title(pTitle)
        CAPlotterDialog.caPlotFigure.axes.set_yscale('log')
        CAPlotterDialog.caPlotFigure.axes.set_xscale('log')
        CAPlotterDialog.caPlotFigure.axes.set_xlabel(labelstring)
        CAPlotterDialog.caPlotFigure.axes.set_ylabel('Area (# of pixels)')
        CAPlotterDialog.caPlotFigure.axes.text(0.75, 0.8, threshstring, transform=CAPlotterDialog.caPlotFigure.axes.transAxes)
        
        CAPlotterDialog.caPlotFigure.canvas.draw()
