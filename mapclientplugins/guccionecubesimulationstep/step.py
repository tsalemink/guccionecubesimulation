
'''
MAP Client Plugin Step
'''
from os import mkdir
from os import path
import sys
import json
import contextlib

from PySide6 import QtCore, QtGui, QtWidgets

from mapclient.mountpoints.workflowstep import WorkflowStepMountPoint
from mapclientplugins.guccionecubesimulationstep.configuredialog import ConfigureDialog

from mapclientplugins.guccionecubesimulationstep.simulation import simulate


class DummyIOConsumer(object):
    def write(self, x): pass


@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = DummyIOConsumer()
    yield
    sys.stdout = save_stdout


class GuccioneCubeSimulationStep(WorkflowStepMountPoint):
    '''
    Skeleton step which is intended to be a helpful starting point
    for new steps.
    '''

    def __init__(self, location):
        super(GuccioneCubeSimulationStep, self).__init__('Guccione Cube Simulation', location)
        self._configured = False # A step cannot be executed until it has been configured.
        self._category = 'Registration'
        # Add any other initialisation code here:
        self._icon = QtGui.QImage(':/guccionecubesimulationstep/images/registration.png')
        # Ports:
        self.addPort(('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#uses',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#file_location'))
        self.addPort(('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#uses',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#parameters_dict'))
        self.addPort(('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#uses',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#directory_location'))
        self.addPort(('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#provides',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#guccione_results_location'))
        # Port data:
        self._portData0 = None # http://physiomeproject.org/workflow/1.0/rdf-schema#file_location
        self._portData1 = None # python#dict
        self._portData2 = None # http://physiomeproject.org/workflow/1.0/rdf-schema#directory_location
        self._portData3 = None # http://physiomeproject.org/workflow/1.0/rdf-schema#directory_location
        # Config:
        self._config = {}
        self._config['identifier'] = ''

    def execute(self):
        """
        Add your code here that will kick off the execution of the step.
        Make sure you call the _doneExecution() method when finished.  This method
        may be connected up to a button in a widget for example.
        """
        # Put your execute step code here before calling the '_doneExecution' method.
        if self._portData2:
            self._portData3 = self._portData2
        else:
            output_dir = path.join(self._location, self.getIdentifier() + '_output')
            if not path.isdir(output_dir):
                mkdir(output_dir)

            self._portData3 = output_dir

        print('=======================')
        print(self._portData0)
        print(self._portData1)
        print(self._portData2)
        print(self._portData3)
        material_parameters = [float(self._portData1['c1']),
                               float(self._portData1['c2']),
                               float(self._portData1['c3']),
                               float(self._portData1['c4'])]
        resultsFibre = []
        resultsCross = []

        try:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            with nostdout():
                resultsFibre = simulate(0.0, material_parameters, self._portData0, output_dir=self._portData3)

                # by re-orienting the fibre direction in the unit cube we can simulate a cross fibre extension
                resultsCross = simulate(90.0, material_parameters, self._portData0, output_dir=self._portData3)
        finally:
            # Always unset
            QtWidgets.QApplication.restoreOverrideCursor()

        results = {}
        results["materialParameters"] = material_parameters
        results["fibre"] = resultsFibre
        results["cross"] = resultsCross

        results_file = path.join(self._portData3, 'results.json')
        with open(results_file, 'w') as f:
            json.dump(results, f)

        self._doneExecution()

    def setPortData(self, index, dataIn):
        '''
        Add your code here that will set the appropriate objects for this step.
        The index is the index of the port in the port list.  If there is only one
        uses port for this step then the index can be ignored.
        '''
        if index == 0:
            self._portData0 = dataIn
        elif index == 1:
            self._portData1 = dataIn # python#dict
        else:
            if not path.isabs(dataIn):
                dataIn = path.abspath(path.join(self._location, dataIn))
            self._portData2 = dataIn

    def getPortData(self, index):
        '''
        Add your code here that will return the appropriate objects for this step.
        The index is the index of the port in the port list.  If there is only one
        provides port for this step then the index can be ignored.
        '''
        return self._portData3 # http://physiomeproject.org/workflow/1.0/rdf-schema#directory_location

    def configure(self):
        '''
        This function will be called when the configure icon on the step is
        clicked.  It is appropriate to display a configuration dialog at this
        time.  If the conditions for the configuration of this step are complete
        then set:
            self._configured = True
        '''
        # dlg = ConfigureDialog(QtWidgets.QApplication.activeWindow().currentWidget())
        dlg = ConfigureDialog(QtWidgets.QApplication.activeWindow())
        dlg.identifierOccursCount = self._identifierOccursCount
        dlg.setConfig(self._config)
        dlg.validate()
        dlg.setModal(True)

        if dlg.exec_():
            self._config = dlg.getConfig()

        self._configured = dlg.validate()
        self._configuredObserver()

    def getIdentifier(self):
        '''
        The identifier is a string that must be unique within a workflow.
        '''
        return self._config['identifier']

    def setIdentifier(self, identifier):
        '''
        The framework will set the identifier for this step when it is loaded.
        '''
        self._config['identifier'] = identifier

    def serialize(self):
        '''
        Add code to serialize this step to string.  This method should
        implement the opposite of 'deserialize'.
        '''
        return json.dumps(self._config, default=lambda o: o.__dict__, sort_keys=True, indent=4)


    def deserialize(self, string):
        '''
        Add code to deserialize this step from string.  This method should
        implement the opposite of 'serialize'.
        '''
        self._config.update(json.loads(string))

        d = ConfigureDialog()
        d.identifierOccursCount = self._identifierOccursCount
        d.setConfig(self._config)
        self._configured = d.validate()


