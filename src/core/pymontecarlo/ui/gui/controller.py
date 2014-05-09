#!/usr/bin/env python
"""
================================================================================
:mod:`controller` -- Controller
================================================================================

.. module:: controller
   :synopsis: Controller

.. inheritance-diagram:: pymontecarlo.ui.gui.controller

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import time
import uuid

# Third party modules.
from PySide.QtCore import Qt, QObject, Signal, QThread

# Local modules.
from pymontecarlo.options.options import Options
from pymontecarlo.results.results import Results

from pymontecarlo.fileformat.options.options import OptionsReader, OptionsWriter
from pymontecarlo.fileformat.results.results import ResultsReader, ResultsWriter

from pymontecarlo.settings import get_settings

# Globals and constants variables.

class _MonitorableWrapperThread(QThread):

    resultReady = Signal(object)
    progressUpdated = Signal(float, str)
    exceptionRaised = Signal(Exception)

    def __init__(self, monitorable, args=(), kwargs=None):
        QThread.__init__(self)
        self._monitorable = monitorable
        self._args = args
        if kwargs is None:
            kwargs = {}
        self._kwargs = kwargs
        self._is_cancelled = False

    def _start_monitorable(self):
        raise NotImplementedError

    def run(self):
        self._start_monitorable()

        try:
            while self._monitorable.is_alive():
                self.progressUpdated.emit(self._monitorable.progress,
                                          self._monitorable.status)
                time.sleep(0.1)
        except Exception as ex:
            self.exceptionRaised.emit(ex)
            return
        finally:
            if not self._is_cancelled:
                self.progressUpdated.emit(self._monitorable.progress,
                                          self._monitorable.status)

        if not self._is_cancelled:
            try:
                result = self._monitorable.get()
            except Exception as ex:
                self.exceptionRaised.emit(ex)
            else:
                self.resultReady.emit(result)

    def cancel(self):
        self._is_cancelled = True
        self._monitorable.cancel()

class _OptionsReaderWrapperThread(_MonitorableWrapperThread):

    def __init__(self, filepath):
        monitorable = OptionsReader()
        args = (filepath,)
        _MonitorableWrapperThread.__init__(self, monitorable, args=args)

    def _start_monitorable(self):
        self._monitorable.read(*self._args, **self._kwargs)

class _OptionsWriterWrapperThread(_MonitorableWrapperThread):

    def __init__(self, options, filepath):
        monitorable = OptionsWriter()
        args = (options, filepath)
        _MonitorableWrapperThread.__init__(self, monitorable, args=args)

    def _start_monitorable(self):
        self._monitorable.write(*self._args, **self._kwargs)

class _ResultsReaderWrapperThread(_MonitorableWrapperThread):

    def __init__(self, filepath):
        monitorable = ResultsReader()
        args = (filepath,)
        _MonitorableWrapperThread.__init__(self, monitorable, args=args)

    def _start_monitorable(self):
        self._monitorable.read(*self._args, **self._kwargs)

class _ResultsWriterWrapperThread(_MonitorableWrapperThread):

    def __init__(self, results, filepath):
        monitorable = ResultsWriter()
        args = (results, filepath)
        _MonitorableWrapperThread.__init__(self, monitorable, args=args)

    def _start_monitorable(self):
        self._monitorable.write(*self._args, **self._kwargs)

class Controller(QObject):

    optionsNewRequested = Signal()

    optionsOpen = Signal(str) # filepath
    optionsOpenCancel = Signal()
    optionsOpenProgress = Signal(float, str) # progress, status
    optionsOpenException = Signal(Exception) # exception
    optionsOpened = Signal(Options, str) # options, filepath

    optionsAddRequested = Signal(Options, str) # options, filepath (optional)
    optionsAdded = Signal(str, Options) # uid, options
    optionsRemoveRequested = Signal(str) # uid
    optionsRemoved = Signal(str) # uid
    optionsModifyRequested = Signal(str) # uid
    optionsModified = Signal(str, Options) # uid, options

    optionsSaveRequested = Signal(str) # uid
    optionsSaveAsRequested = Signal(str) # uid
    optionsSave = Signal(str, str) # uid, filepath
    optionsSaveCancel = Signal()
    optionsSaveProgress = Signal(float, str) # progress, status
    optionsSaveException = Signal(Exception) # exception
    optionsSaved = Signal(str, str) # uid, filepath

    resultsOpen = Signal(str) # filepath
    resultsOpenCancel = Signal()
    resultsOpenProgress = Signal(float, str) # progress, status
    resultsOpenException = Signal(Exception) # exception
    resultsOpened = Signal(Results, str) # results, filepath

    resultsAddRequested = Signal(Results, str) # results, filepath (optional)
    resultsAdded = Signal(str, Results) # uid, results
    resultsRemoveRequested = Signal(str) # uid
    resultsRemoved = Signal(str) # uid

    resultsSaveAsRequested = Signal(str) # uid
    resultsSave = Signal(str, str) # uid, filepath
    resultsSaveCancel = Signal()
    resultsSaveProgress = Signal(float, str) # progress, status
    resultsSaveException = Signal(Exception) # exception
    resultsSaved = Signal(str, str) # uid, filepath

    beamDisplayRequested = Signal(str) # uid
    beamDisplayed = Signal(str) # uid
    beamDisplayClosed = Signal(str) # uid

    geometryDisplayRequested = Signal(str) # uid
    geometryDisplayed = Signal(str) # uid
    geometryDisplayClosed = Signal(str) # uid

    detectorsDisplayRequested = Signal(str) # uid
    detectorsDisplayed = Signal(str) # uid
    detectorsDisplayClosed = Signal(str) # uid

    limitsDisplayRequested = Signal(str) # uid
    limitsDisplayed = Signal(str) # uid
    limitsDisplayClosed = Signal(str) # uid

    modelsDisplayRequested = Signal(str) # uid
    modelsDisplayed = Signal(str) # uid
    modelsDisplayClosed = Signal(str) # uid

    resultDisplayRequested = Signal(str, int, str) # uid, index, key
    resultDisplayed = Signal(str, int, str) # uid, index, key
    resultDisplayClosed = Signal(str, int, str) # uid, index, key

    def __init__(self):
        QObject.__init__(self) # Required to activate signals

        # Variables
        self._list_options = {}
        self._options_edited = {}
        self._options_filepath = {}
        self._options_reader_thread = None
        self._options_writer_thread = None

        self._list_results = {}
        self._results_options = {}
        self._results_filepath = {}
        self._results_reader_thread = None
        self._results_writer_thread = None

        # Signals
        self.optionsOpen.connect(self._onOptionsOpen)
        self.optionsOpenCancel.connect(self._onOptionsOpenCancel)
        self.optionsOpenException.connect(self._onOptionsOpenException)
        self.optionsOpened.connect(self._onOptionsOpened)
        self.optionsSave.connect(self._onOptionsSave)
        self.optionsSaveCancel.connect(self._onOptionsSaveCancel)
        self.optionsSaveException.connect(self._onOptionsSaveException)
        self.optionsSaved.connect(self._onOptionsSaved)
        self.optionsAddRequested.connect(self._onOptionsAddRequested)
        self.optionsRemoveRequested.connect(self._onOptionsRemoveRequested)
        self.optionsRemoved.connect(self._onOptionsRemoved, Qt.QueuedConnection)
        self.optionsModified.connect(self._onOptionsModified)

        self.resultsOpen.connect(self._onResultsOpen)
        self.resultsOpenCancel.connect(self._onResultsOpenCancel)
        self.resultsOpenException.connect(self._onResultsOpenException)
        self.resultsOpened.connect(self._onResultsOpened)
        self.resultsSave.connect(self._onResultsSave)
        self.resultsSaveCancel.connect(self._onResultsSaveCancel)
        self.resultsSaveException.connect(self._onResultsSaveException)
        self.resultsSaved.connect(self._onResultsSaved)
        self.resultsAddRequested.connect(self._onResultsAddRequested)
        self.resultsRemoveRequested.connect(self._onResultsRemoveRequested)
        self.resultsRemoved.connect(self._onResultsRemoved, Qt.QueuedConnection)

    def _onOptionsOpen(self, filepath):
        if not self.canOpenOptions(filepath):
            raise IOError('Options is already opened')

        self._options_reader_thread = _OptionsReaderWrapperThread(filepath)
        func = lambda ops, f = filepath: self.optionsOpened.emit(ops, f)
        self._options_reader_thread.resultReady.connect(func)
        self._options_reader_thread.progressUpdated.connect(self.optionsOpenProgress)
        self._options_reader_thread.exceptionRaised.connect(self.optionsOpenException)
        self._options_reader_thread.start()

    def _onOptionsOpenCancel(self):
        if self._options_reader_thread is None:
            return
        self._options_reader_thread.cancel()
        self._options_reader_thread.quit()
        self._options_reader_thread.wait()

    def _onOptionsOpenException(self):
        self._options_reader_thread.quit()
        self._options_reader_thread.wait()

    def _onOptionsOpened(self, options, filepath):
        self._options_reader_thread.quit()
        self._options_reader_thread.wait()
        self._options_reader_thread = None
        self.optionsAddRequested.emit(options, filepath)

    def _onOptionsSave(self, uid, filepath):
        options = self._list_options[uid]
        self._options_writer_thread = _OptionsWriterWrapperThread(options, filepath)
        func = lambda f, u = uid: self.optionsSaved.emit(u, f)
        self._options_writer_thread.resultReady.connect(func)
        self._options_writer_thread.progressUpdated.connect(self.optionsSaveProgress)
        self._options_writer_thread.exceptionRaised.connect(self.optionsSaveException)
        self._options_writer_thread.start()

    def _onOptionsSaveCancel(self):
        if self._options_writer_thread is None:
            return
        self._options_writer_thread.cancel()
        self._options_writer_thread.quit()
        self._options_writer_thread.wait()

    def _onOptionsSaveException(self):
        self._options_writer_thread.quit()
        self._options_writer_thread.wait()

    def _onOptionsSaved(self, uid, filepath):
        self._options_writer_thread.quit()
        self._options_writer_thread.wait()
        self._options_writer_thread = None
        self._options_edited[uid] = False
        self._options_filepath[uid] = filepath

    def _onOptionsAddRequested(self, options, filepath):
        uid = self._addOptions(options)
        self._options_edited[uid] = False
        self._options_filepath[uid] = filepath
        self.optionsAdded.emit(uid, options)

    def _onOptionsRemoveRequested(self, uid):
        self.optionsRemoved.emit(uid)

    def _onOptionsRemoved(self, uid):
        self._removeOptions(uid)

    def _onOptionsModified(self, uid, options):
        self._list_options[uid] = options
        self._options_edited[uid] = True

    def _onResultsOpen(self, filepath):
        if not self.canOpenResults(filepath):
            raise IOError('Results is already opened')

        self._results_reader_thread = _ResultsReaderWrapperThread(filepath)
        func = lambda ops, f = filepath: self.resultsOpened.emit(ops, f)
        self._results_reader_thread.resultReady.connect(func)
        self._results_reader_thread.progressUpdated.connect(self.resultsOpenProgress)
        self._results_reader_thread.exceptionRaised.connect(self.resultsOpenException)
        self._results_reader_thread.start()

    def _onResultsOpenCancel(self):
        if self._results_reader_thread is None:
            return
        self._results_reader_thread.cancel()
        self._results_reader_thread.quit()
        self._results_reader_thread.wait()

    def _onResultsOpenException(self):
        self._results_reader_thread.quit()
        self._results_reader_thread.wait()

    def _onResultsOpened(self, results, filepath):
        self._results_reader_thread.quit()
        self._results_reader_thread.wait()
        self._results_reader_thread = None
        self.resultsAddRequested.emit(results, filepath)

    def _onResultsSave(self, uid, filepath):
        results = self._list_results[uid]
        self._results_writer_thread = _ResultsWriterWrapperThread(results, filepath)
        func = lambda f, u = uid: self.resultsSaved.emit(u, f)
        self._results_writer_thread.resultReady.connect(func)
        self._results_writer_thread.progressUpdated.connect(self.resultsSaveProgress)
        self._results_writer_thread.exceptionRaised.connect(self.resultsSaveException)
        self._results_writer_thread.start()

    def _onResultsSaveCancel(self):
        if self._results_writer_thread is None:
            return
        self._results_writer_thread.cancel()
        self._results_writer_thread.quit()
        self._results_writer_thread.wait()

    def _onResultsSaveException(self):
        self._results_writer_thread.quit()
        self._results_writer_thread.wait()

    def _onResultsSaved(self, uid, filepath):
        self._results_writer_thread.quit()
        self._results_writer_thread.wait()
        self._results_writer_thread = None
        self._results_filepath[uid] = filepath

    def _onResultsAddRequested(self, results, filepath):
        uid = uuid.uuid4().hex
        if uid in self._list_results:
            raise ValueError('Already opened')
        if uid in self._list_options:
            raise ValueError('Options for this results is opened')

        self._list_results[uid] = results
        self._results_filepath[uid] = filepath
        self._results_options.setdefault(uid, {})

        # Add options
        options_uid = self._addOptions(results.options)
        self._results_options[uid]['base'] = options_uid

        for index, container in enumerate(results):
            options_uid = self._addOptions(container.options)
            self._results_options[uid][index] = options_uid

        self.resultsAdded.emit(uid, results)

    def _onResultsRemoveRequested(self, uid):
        self.resultsRemoved.emit(uid)

    def _onResultsRemoved(self, uid):
        self._list_results.pop(uid)
        self._results_filepath.pop(uid, None)

        # Remove options
        for options_uid in self._results_options.pop(uid).values():
            self._removeOptions(options_uid)

    def _addOptions(self, options):
        uid = uuid.uuid4().hex
        if uid in self._list_options:
            raise ValueError('Already opened')
        self._list_options[uid] = options
        return uid

    def _removeOptions(self, uid):
        options = self._list_options.pop(uid)
        self._options_edited.pop(uid, None)
        self._options_filepath.pop(uid, None)
        return options

    def _resultsOptionsUID(self, uid, key='base'):
        return self._resultsOptionsUIDs(uid)[key]

    def _resultsOptionsUIDs(self, uid):
        return self._results_options[uid]

    def settings(self):
        return get_settings()

    def options(self, uid):
        return self._list_options[uid]

    def isOptionsEdited(self, uid):
        return self._options_edited.get(uid, False)

    def optionsFilepath(self, uid):
        return self._options_filepath.get(uid)

    def canOpenOptions(self, filepath):
        return filepath not in self._options_filepath.values()

    def results(self, uid):
        return self._list_results[uid]

    def resultsFilepath(self, uid):
        return self._results_filepath.get(uid)

    def canOpenResults(self, filepath):
        return filepath not in self._results_filepath.values()

    def resultsContainer(self, uid, index):
        return self._list_results[uid][index]

    def result(self, uid, index, key):
        return self._list_results[uid][index][key]


