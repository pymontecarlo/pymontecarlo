#!/usr/bin/env python
"""
================================================================================
:mod:`controller` -- Control loaded simulations
================================================================================

.. module:: controller
   :synopsis: Control loaded simulations

.. inheritance-diagram:: pymontecarlo.ui.gui.controller

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
from operator import attrgetter

# Third party modules.
import wx
from wx.lib.pubsub import Publisher as pub

# Local modules.
from pymontecarlo.settings import get_settings
from pymontecarlo.input.options import Options
from pymontecarlo.output.results import Results
import pymontecarlo.util.progress as progress
from pymontecarlo.ui.gui.input.wizard import NewSimulationWizard

from wxtools2.dialog import show_open_filedialog, show_progress_dialog, show_error_dialog
from wxtools2.exception import catch_all

# Globals and constants variables.

class _Simulation(object):

    def __init__(self, filepath, options, results=None):
        self._filepath = os.path.splitext(os.path.abspath(filepath))[0]

        self._options = options

        if results is None:
            results = Results()
        self._results = results

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__, self._options.name)

    def __eq__(self, other):
        return self._filepath == other._filepath

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(('Simulation', self._filepath))

    @property
    def filepath(self):
        return self._filepath

    @property
    def options(self):
        return self._options

    @property
    def results(self):
        return self._results

class _Controller(object):

    def __init__(self):
        self._simulations = set()
        self._basedir = getattr(get_settings().pymontecarlo, 'basedir', os.getcwd())

    def __len__(self):
        return len(self._simulations)

    def __contains__(self, other):
        if isinstance(other, basestring):
            return other in map(attrgetter('filepath'), self._simulations)
        else:
            return other in self._simulations

    def __iter__(self):
        return iter(self._simulations)

    def add(self, sim):
        if sim in self:
            raise ValueError, 'Simulation %s already registered' % sim
        self._simulations.add(sim)
        pub.sendMessage('controller.simulation.add', sim)

    def remove(self, sim):
        self._simulations.remove(sim)
        pub.sendMessage('controller.simulation.remove', sim)

    def clear(self):
        self._simulations.clear()
        pub.sendMessage('controller.simulation.clear')

    def create(self, parent):
        programs = sorted(get_settings().get_programs(), key=attrgetter('name'))
        choices = map(attrgetter('name'), programs)
        message = "Please select the program(s) with which the new simulation\nshould be compatible"
        caption = "New simulation"

        dialog = wx.MultiChoiceDialog(parent, message, caption, choices)
        if dialog.ShowModal() == wx.ID_OK:
            selections = [programs[i] for i in dialog.GetSelections()]

            if selections:
                wizard = NewSimulationWizard(parent, selections)
                wizard.ShowModal()
                wizard.Destroy()

        dialog.Destroy()

    def open(self, parent):
        filetypes = [('Results (*.h5)', 'h5'), ('Options (*.xml)', 'xml')]
        filepaths = show_open_filedialog(parent, filetypes, self._basedir, True)

        for filepath in filepaths:
            self._load(parent, filepath)
            self._basedir = os.path.dirname(filepath)

    def _load(self, parent, filepath):
        basepath, ext = os.path.splitext(filepath)

        # Check if simulation exists
        if basepath in self:
            show_error_dialog(parent, 'Simulation already loaded',
                              'Duplicate simulation')
            return

        if ext == '.xml':
            target = Options.load
            progress_method = progress.progress
            status_method = progress.status
            title = 'Loading options'
            args = (filepath,)
            with catch_all(parent) as success:
                options = show_progress_dialog(parent, target, progress_method,
                                               status_method, title, args)
                results = None
            if not success:
                return
        elif ext == '.h5':
            target = Results.load
            progress_method = progress.progress
            status_method = progress.status
            title = 'Loading results'
            args = (filepath,)

            with catch_all(parent) as success:
                results = show_progress_dialog(parent, target, progress_method,
                                               status_method, title, args)
                options = results.options
            if not success:
                return
        else:
            raise ValueError, 'Unknown extension'

        sim = _Simulation(filepath, options, results)
        self.add(sim)

    def close(self):
        settings = get_settings()
        settings.pymontecarlo.basedir = self._basedir
        settings.write()

controller = _Controller()



