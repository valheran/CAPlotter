# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CAPlotter
                                 A QGIS plugin
 Creates Concentration (z value)-area plots of rasters. A method of visualising the fractal dimension of a gridded property, and can be used to help determine background thresholds of geochemical datasets
                             -------------------
        begin                : 2015-03-03
        copyright            : (C) 2015 by Alex Brown
        email                : sdfasdfsdfdfs
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load CAPlotter class from file CAPlotter.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .ca_plotter import CAPlotter
    return CAPlotter(iface)
