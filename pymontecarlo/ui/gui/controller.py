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
import uuid
import logging

# Third party modules.
from PySide.QtCore import Qt, QObject, Signal

# Local modules.
from pymontecarlo.options.options import Options
from pymontecarlo.results.results import Results

from pymontecarlo.settings import get_settings

from pymontecarlo.ui.gui.wrapper import \
    (_OptionsReaderWrapperThread, _OptionsWriterWrapperThread,
     _ResultsReaderWrapperThread, _ResultsWriterWrapperThread)

# Globals and constants variables.

class Controller(QObject):

    optionsNewRequested = Signal()

    optionsOpenRequested = Signal()
    optionsOpen = Signal(str) # filepath
    optionsOpenCancel = Signal()
    optionsOpenProgress = Signal(float, str) # progress, status
    optionsOpenException = Signal(Exception) # exception
    optionsOpened = Signal(Options, str) # options, filepath

    optionsReloadRequested = Signal(str) # uid
    optionsReloadRequestApproved = Signal(str) # uid
    optionsReload = Signal(str) # uid
    optionsReloaded = Signal(str, Options) # uid, options

    optionsAddRequested = Signal(Options, str) # options, filepath (optional)
    optionsAddRequestApproved = Signal(Options, str) # options, filepath (optional)
    optionsAdd = Signal(Options, str) # options, filepath (optional)
    optionsAdded = Signal(str, Options) # uid, options

    optionsRemoveRequested = Signal(str) # uid
    optionsRemoveRequestApproved = Signal(str) # uid
    optionsRemove = Signal(str) # uid
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

    resultsReloadRequested = Signal(str) # uid
    resultsReloadRequestApproved = Signal(str) # uid
    resultsReload = Signal(str) # uid
    resultsReloaded = Signal(str, Results) # uid, results

    resultsAddRequested = Signal(Results, str) # results, filepath (optional)
    resultsAddRequestApproved = Signal(Results, str) # results, filepath (optional)
    resultsAdd = Signal(Results, str) # results, filepath (optional)
    resultsAdded = Signal(str, Results) # uid, results

    resultsRemoveRequested = Signal(str) # uid
    resultsRemoveRequestApproved = Signal(str) # uid
    resultsRemove = Signal(str) # uid
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

    summaryDisplayRequested = Signal(str) # uid
    summaryDisplayed = Signal(str) # uid
    summaryDisplayedClosed = Signal(str) # uid

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
        self.optionsReload.connect(self._onOptionsReload)
        self.optionsSave.connect(self._onOptionsSave)
        self.optionsSaveCancel.connect(self._onOptionsSaveCancel)
        self.optionsSaveException.connect(self._onOptionsSaveException)
        self.optionsAddRequestApproved.connect(self._onOptionsAddRequestApproved, Qt.QueuedConnection)
        self.optionsAdd.connect(self._onOptionsAdd)
        self.optionsRemoveRequestApproved.connect(self._onOptionsRemoveRequestApproved, Qt.QueuedConnection)
        self.optionsRemove.connect(self._onOptionsRemove)
        self.optionsModified.connect(self._onOptionsModified)

        self.resultsOpen.connect(self._onResultsOpen)
        self.resultsOpenCancel.connect(self._onResultsOpenCancel)
        self.resultsOpenException.connect(self._onResultsOpenException)
        self.resultsReload.connect(self._onResultsReload)
        self.resultsSave.connect(self._onResultsSave)
        self.resultsSaveCancel.connect(self._onResultsSaveCancel)
        self.resultsSaveException.connect(self._onResultsSaveException)
        self.resultsAddRequestApproved.connect(self._onResultsAddRequestApproved, Qt.QueuedConnection)
        self.resultsAdd.connect(self._onResultsAdd)
        self.resultsRemoveRequestApproved.connect(self._onResultsRemoveRequestApproved, Qt.QueuedConnection)
        self.resultsRemove.connect(self._onResultsRemove)

    def _onOptionsOpen(self, filepath):
        logging.debug('controller: optionsOpen')
        if not self.canOpenOptions(filepath):
            raise IOError('Options is already opened')

        self._options_reader_thread = _OptionsReaderWrapperThread(filepath)
        func = lambda ops, f = filepath: self._onOptionsOpenReady(ops, f)
        self._options_reader_thread.resultReady.connect(func)
        self._options_reader_thread.progressUpdated.connect(self.optionsOpenProgress)
        self._options_reader_thread.exceptionRaised.connect(self.optionsOpenException)
        self._options_reader_thread.start()

    def _onOptionsOpenCancel(self):
        logging.debug('controller: optionsOpenCancel')
        if self._options_reader_thread is None:
            return
        self._options_reader_thread.cancel()
        self._options_reader_thread.quit()
        self._options_reader_thread.wait()

    def _onOptionsOpenException(self):
        logging.debug('controller: optionsOpenException')
        self._options_reader_thread.quit()
        self._options_reader_thread.wait()

    def _onOptionsOpenReady(self, options, filepath):
        logging.debug('controller: optionsOpenReady')
        self._options_reader_thread.quit()
        self._options_reader_thread.wait()
        self._options_reader_thread = None
        self.optionsOpened.emit(options, filepath)
        self.optionsAddRequested.emit(options, filepath)

    def _onOptionsReload(self, uid):
        logging.debug('controller: optionsReload')
        filepath = self._options_filepath.get(uid)
        if filepath is None:
            return

        self._options_reader_thread = _OptionsReaderWrapperThread(filepath)
        func = lambda ops, u = uid: self._onOptionsReloadReady(uid, ops)
        self._options_reader_thread.resultReady.connect(func)
        self._options_reader_thread.progressUpdated.connect(self.optionsOpenProgress)
        self._options_reader_thread.exceptionRaised.connect(self.optionsOpenException)
        self._options_reader_thread.start()

    def _onOptionsReloadReady(self, uid, options):
        logging.debug('controller: optionsReloadReady')
        self._options_reader_thread.quit()
        self._options_reader_thread.wait()
        self._options_reader_thread = None

        filepath = self._options_filepath[uid]
        self._removeOptions(uid)
        self._addOptions(options, uid)
        self._options_filepath[uid] = filepath

        self.optionsReloaded.emit(uid, options)

    def _onOptionsSave(self, uid, filepath):
        logging.debug('controller: optionsSave')
        options = self._list_options[uid]
        self._options_writer_thread = _OptionsWriterWrapperThread(options, filepath)
        func = lambda s, f = filepath, u = uid: self._onOptionsSaveReady(u, f)
        self._options_writer_thread.resultReady.connect(func)
        self._options_writer_thread.progressUpdated.connect(self.optionsSaveProgress)
        self._options_writer_thread.exceptionRaised.connect(self.optionsSaveException)
        self._options_writer_thread.start()

    def _onOptionsSaveCancel(self):
        logging.debug('controller: optionsSaveCancel')
        if self._options_writer_thread is None:
            return
        self._options_writer_thread.cancel()
        self._options_writer_thread.quit()
        self._options_writer_thread.wait()

    def _onOptionsSaveException(self):
        logging.debug('controller: optionsSaveException')
        self._options_writer_thread.quit()
        self._options_writer_thread.wait()

    def _onOptionsSaveReady(self, uid, filepath):
        logging.debug('controller: optionsSaveReady')
        self._options_writer_thread.quit()
        self._options_writer_thread.wait()
        self._options_writer_thread = None

        self._options_edited[uid] = False
        self._options_filepath[uid] = filepath
        self.optionsSaved.emit(uid, filepath)

    def _onOptionsAddRequestApproved(self, options, filepath):
        logging.debug('controller: optionsAddRequestApproved')
        self.optionsAdd.emit(options, filepath)

    def _onOptionsAdd(self, options, filepath):
        logging.debug('controller: optionsAdd')
        uid = self._addOptions(options)
        self._options_filepath[uid] = filepath
        self.optionsAdded.emit(uid, options)

    def _onOptionsRemoveRequestApproved(self, uid):
        logging.debug('controller: optionsRemoveRequestApproved')
        self.optionsRemove.emit(uid)

    def _onOptionsRemove(self, uid):
        logging.debug('controller: optionsRemove')
        self._removeOptions(uid)
        self.optionsRemoved.emit(uid)

    def _onOptionsModified(self, uid, options):
        logging.debug('controller: optionsModified')
        self._list_options[uid] = options
        self._options_edited[uid] = True

    def _onResultsOpen(self, filepath):
        logging.debug('controller: resultsOpen')
        if not self.canOpenResults(filepath):
            raise IOError('Results is already opened')

        self._results_reader_thread = _ResultsReaderWrapperThread(filepath)
        func = lambda results, f = filepath: self._onResultsOpenReady(results, f)
        self._results_reader_thread.resultReady.connect(func)
        self._results_reader_thread.progressUpdated.connect(self.resultsOpenProgress)
        self._results_reader_thread.exceptionRaised.connect(self.resultsOpenException)
        self._results_reader_thread.start()

    def _onResultsOpenCancel(self):
        logging.debug('controller: resultsOpenCancel')
        if self._results_reader_thread is None:
            return
        self._results_reader_thread.cancel()
        self._results_reader_thread.quit()
        self._results_reader_thread.wait()

    def _onResultsOpenException(self):
        logging.debug('controller: resultsOpenException')
        self._results_reader_thread.quit()
        self._results_reader_thread.wait()

    def _onResultsOpenReady(self, results, filepath):
        logging.debug('controller: resultsOpenReady')
        self._results_reader_thread.quit()
        self._results_reader_thread.wait()
        self._results_reader_thread = None
        self.resultsOpened.emit(results, filepath)
        self.resultsAddRequested.emit(results, filepath)

    def _onResultsReload(self, uid):
        logging.debug('controller: resultsReload')
        filepath = self._results_filepath.get(uid)
        if filepath is None:
            return

        self._results_reader_thread = _ResultsReaderWrapperThread(filepath)
        func = lambda results, u = uid: self._onResultsReloadReady(u, results)
        self._results_reader_thread.resultReady.connect(func)
        self._results_reader_thread.progressUpdated.connect(self.resultsOpenProgress)
        self._results_reader_thread.exceptionRaised.connect(self.resultsOpenException)
        self._results_reader_thread.start()

    def _onResultsReloadReady(self, uid, results):
        logging.debug('controller: resultsReloadReady')
        self._results_reader_thread.quit()
        self._results_reader_thread.wait()
        self._results_reader_thread = None

        filepath = self._results_filepath[uid]
        self._removeResults(uid)
        self._addResults(results, uid)
        self._results_filepath[uid] = filepath

        self.resultsReloaded.emit(uid, results)

    def _onResultsSave(self, uid, filepath):
        logging.debug('controller: resultsSave')
        results = self._list_results[uid]
        self._results_writer_thread = _ResultsWriterWrapperThread(results, filepath)
        func = lambda g, f = filepath, u = uid: self._onResultsSaveReady(u, f)
        self._results_writer_thread.resultReady.connect(func)
        self._results_writer_thread.progressUpdated.connect(self.resultsSaveProgress)
        self._results_writer_thread.exceptionRaised.connect(self.resultsSaveException)
        self._results_writer_thread.start()

    def _onResultsSaveCancel(self):
        logging.debug('controller: resultsSaveCancel')
        if self._results_writer_thread is None:
            return
        self._results_writer_thread.cancel()
        self._results_writer_thread.quit()
        self._results_writer_thread.wait()

    def _onResultsSaveException(self):
        logging.debug('controller: resultsSaveException')
        self._results_writer_thread.quit()
        self._results_writer_thread.wait()

    def _onResultsSaveReady(self, uid, filepath):
        logging.debug('controller: resultsSaveReady')
        self._results_writer_thread.quit()
        self._results_writer_thread.wait()
        self._results_writer_thread = None

        self._results_filepath[uid] = filepath
        self.resultsSaved.emit(uid, filepath)

    def _onResultsAddRequestApproved(self, results, filepath):
        logging.debug('controller: resultsAddRequested')
        self.resultsAdd.emit(results, filepath)

    def _onResultsAdd(self, results, filepath):
        logging.debug('controller: resultsAdd')
        uid = self._addResults(results)
        self._results_filepath[uid] = filepath
        self.resultsAdded.emit(uid, results)

    def _onResultsRemoveRequestApproved(self, uid):
        logging.debug('controller: resultsRemoveRequestApproved')
        self.resultsRemove.emit(uid)

    def _onResultsRemove(self, uid):
        logging.debug('controller: resultsRemoved')
        self._removeResults(uid)
        self.resultsRemoved.emit(uid)

    def _addOptions(self, options, uid=None):
        if uid is None:
            uid = uuid.uuid4().hex
        if uid in self._list_options:
            raise ValueError('Already opened')
        self._list_options[uid] = options
        self._options_edited[uid] = False
        return uid

    def _removeOptions(self, uid):
        options = self._list_options.pop(uid)
        self._options_edited.pop(uid, None)
        self._options_filepath.pop(uid, None)
        return options

    def _addResults(self, results, uid=None):
        if uid is None:
            uid = uuid.uuid4().hex
        if uid in self._list_results:
            raise ValueError('Already opened')
        if uid in self._list_options:
            raise ValueError('Options for this results is opened')

        self._list_results[uid] = results
        self._results_options.setdefault(uid, {})

        # Add options
        options_uid = self._addOptions(results.options)
        self._results_options[uid]['base'] = options_uid

        for index, container in enumerate(results):
            options_uid = self._addOptions(container.options)
            self._results_options[uid][index] = options_uid

        return uid

    def _removeResults(self, uid):
        self._list_results.pop(uid)
        self._results_filepath.pop(uid, None)

        # Remove options
        for options_uid in self._results_options.pop(uid).values():
            self._removeOptions(options_uid)

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

    def resultsUIDFromFilepath(self, filepath):
        r = {v: k for k, v in self._results_filepath.items()}
        return r[filepath]

    def resultsContainer(self, uid, index):
        return self._list_results[uid][index]

    def result(self, uid, index, key):
        return self._list_results[uid][index][key]


