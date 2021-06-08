'''
MAP Client Plugin
'''

__version__ = '0.1.1'
__author__ = 'Hugh Sorby'
__stepname__ = 'Guccione Cube Simulation'
__location__ = 'https://github.com/mapclient-plugins/guccionecubesimulation/archive/v0.1.1.zip'

# import class that derives itself from the step mountpoint.
from mapclientplugins.guccionecubesimulationstep import step

# Import the resource file when the module is loaded,
# this enables the framework to use the step icon.
from . import resources_rc
