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
import locale

from PyQt4 import QtGui, uic

from qgis.core import *
from qgis.gui import *

def getRasterLayerNames():
    layerMap = QgsMapLayerRegistry.instance().mapLayers()
    layerNames = []
    for name, layer in layerMap.iteritems():
        if layer.type() == QgsMapLayer.RasterLayer:
            layerNames.append(unicode(layer.name()))
    return sorted(layerNames, cmp=locale.strcoll)
    
def getRasterLayerByName(layerName):
    layerMap = QgsMapLayerRegistry.instance().mapLayers()
    for name, layer in layerMap.iteritems():
        if layer.type() == QgsMapLayer.RasterLayer and layer.name() == layerName:
            if layer.isValid():
                layerPath = layer.source()
                return layerPath
            else:
                return None