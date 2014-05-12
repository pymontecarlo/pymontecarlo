#!/usr/bin/env python
"""
================================================================================
:mod:`runner` -- Runner dialogs
================================================================================

.. module:: runner
   :synopsis: Runner dialogs

.. inheritance-diagram:: pymontecarlo.ui.gui.runner

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
try:
    cpu_count = os.cpu_count
except AttributeError:
    import multiprocessing
    cpu_count = multiprocessing.cpu_count #@UndefinedVariable
from operator import methodcaller

# Third party modules.
from PySide.QtGui import \
    (QDialog, QSpinBox, QPushButton, QListView, QFileDialog, QVBoxLayout,
     QLabel, QGridLayout, QSizePolicy, QToolBar, QWidget, QProgressDialog,
     QHBoxLayout, QCheckBox, QMessageBox, QTableView, QHeaderView,
     QItemDelegate, QKeySequence)
from PySide.QtCore import \
    (Qt, QAbstractItemModel, QModelIndex, QAbstractListModel,
     QAbstractTableModel, QTimer, QRect)

# Local modules.
from pymontecarlo.settings import get_settings

from pymontecarlo.ui.gui.util.widget import DirBrowseWidget
from pymontecarlo.ui.gui.util.tango import getIcon
import pymontecarlo.ui.gui.util.messagebox as messagebox
from pymontecarlo.ui.gui.wrapper import _OptionsReaderWrapperThread

from pymontecarlo.runner.local import LocalRunner

# Globals and constants variables.

class _OptionsModelMixin(object):

    def __init__(self):
        self._list_options = []
        self._uuids = set()

    def rowCount(self, *args, **kwargs):
        return len(self._list_options)

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractItemModel.flags(self, index))

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or \
                not (0 <= index.row() < len(self._list_options)):
            return False

        row = index.row()

        try:
            oldvalue = self._list_options[row]
            if oldvalue is not None:
                self._uuids.discard(oldvalue.uuid)
        except IndexError:
            pass

        self._list_options[row] = value
        self._uuids.add(value.uuid)

        self.dataChanged.emit(index, index)
        return True

    def insertRows(self, row, count=1, parent=None):
        if count == 0:
            return False
        if parent is None:
            parent = QModelIndex()
        self.beginInsertRows(parent, row, row + count - 1)

        for _ in range(count):
            self._list_options.insert(row, None)

        self.endInsertRows()
        return True

    def removeRows(self, row, count=1, parent=None):
        if count == 0:
            return False
        if parent is None:
            parent = QModelIndex()
        self.beginRemoveRows(parent, row, row + count - 1)

        for index in reversed(range(row, row + count)):
            options = self._list_options.pop(index)
            self._uuids.discard(options.uuid)

        self.endRemoveRows()
        return True

    def addOptions(self, options):
        if options.uuid in self._uuids:
            raise ValueError("Options already added")
        index = self.rowCount()
        self.insertRows(index)
        self.setData(self.createIndex(index, 0), options)

    def removeOptions(self, index):
        self.removeRows(index)

    def clearOptions(self):
        self.removeRows(0, self.rowCount())

    def resetOptions(self, options):
        index = self._list_options.index(options)
        self.dataChanged.emit(index, index)

    def options(self, index):
        return self._list_options[index]

class _AvailableOptionsListModel(_OptionsModelMixin, QAbstractListModel):

    def __init__(self):
        _OptionsModelMixin.__init__(self)
        QAbstractListModel.__init__(self)

    def columnCount(self, *args, **kwargs):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or \
                not (0 <= index.row() < len(self._list_options)):
            return None

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        if role != Qt.DisplayRole:
            return None

        return str(self._list_options[index.row()])

class _StateOptionsTableModel(_OptionsModelMixin, QAbstractTableModel):

    def __init__(self, runner=None):
        _OptionsModelMixin.__init__(self)
        QAbstractTableModel.__init__(self)

        self._runner = runner

        def _column0(runner, options):
            return str(options)
        def _column1(runner, options):
            STATE_ICONS = \
                {LocalRunner.STATE_QUEUED: getIcon('media-playback-pause'),
                 LocalRunner.STATE_RUNNING: getIcon('media-playback-start'),
                 LocalRunner.STATE_SIMULATED: getIcon('face-smile'),
                 LocalRunner.STATE_ERROR: getIcon('face-sad')}
            try:
                return STATE_ICONS.get(runner.options_state(options))
            except KeyError:
                return None
        def _column2(runner, options):
            try:
                progress = runner.options_progress(options) * 100
            except KeyError:
                progress = 0.0
            return '{0:n}%'.format(progress)
        def _column3(runner, options):
            try:
                return runner.options_status(options)
            except KeyError:
                return ''

        self._data_getter = {0: _column0, 1: _column1, 2: _column2, 3: _column3}

    def columnCount(self, *args, **kwargs):
        return 4

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or \
                not (0 <= index.row() < len(self._list_options)):
            return None

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        if self._runner is None:
            return ''

        options = self._list_options[index.row()]

        column = index.column()
        output = self._data_getter[column](self._runner, options)

        if role == Qt.ToolTipRole and column in [0, 3]:
            return output
        elif role == Qt.DisplayRole and column in [0, 2, 3]:
            return output
        elif role == Qt.DecorationRole and column == 1:
            return output
        else:
            return None

    def headerData(self, section , orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            if section == 0:
                return 'Options'
            elif section == 1:
                return 'State'
            elif section == 2:
                return 'Progress'
            elif section == 3:
                return 'Status'
        elif orientation == Qt.Vertical:
            return str(section + 1)

class _StateOptionsItemDelegate(QItemDelegate):

    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)

    def paint(self, painter, option, index):
        painter.save()

        column = index.column()
        if column == 1:
            icon = index.model().data(index, Qt.DecorationRole)
            pixmap = icon.pixmap(option.rect.size() * 0.9)
            x = option.rect.left() + option.rect.width() / 2 - pixmap.width() / 2
            rect = QRect(x, option.rect.top(), pixmap.width(), pixmap.height())
            painter.drawPixmap(rect, pixmap)
        else:
            QItemDelegate.paint(self, painter, option, index)

        painter.restore()

class RunnerDialog(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle('Runner')

        # Runner
        self._runner = None

        self._running_count = 0

        self._running_timer = QTimer()
        self._running_timer.setInterval(500)

        # Widgets
        self._dlg_progress = QProgressDialog()
        self._dlg_progress.setRange(0, 100)
        self._dlg_progress.setModal(True)
        self._dlg_progress.hide()

        lbl_outputdir = QLabel("Output directory")
        self._txt_outputdir = DirBrowseWidget()
        self._txt_outputdir.setPath('/tmp')

        max_workers = cpu_count() #@UndefinedVariable
        lbl_workers = QLabel('Number of workers')
        self._spn_workers = QSpinBox()
        self._spn_workers.setRange(1, max_workers)
        self._spn_workers.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        lbl_max_workers = QLabel('(max: %i)' % max_workers)

        self._chk_overwrite = QCheckBox("Overwrite existing results in output directory")
        self._chk_overwrite.setChecked(True)

        self._lbl_available = QLabel('Available')
        self._lst_available = QListView()
        self._lst_available.setModel(_AvailableOptionsListModel())
        self._lst_available.setSelectionMode(QListView.SelectionMode.MultiSelection)

        tlb_available = QToolBar()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tlb_available.addWidget(spacer)
        act_open = tlb_available.addAction(getIcon("document-open"), "&Open")
        act_open.setShortcut(QKeySequence.Open)

        self._btn_addtoqueue = QPushButton(getIcon("go-next"), "")
        self._btn_addtoqueue.setToolTip("Add to queue")
        self._btn_addtoqueue.setEnabled(False)

        self._btn_addalltoqueue = QPushButton(getIcon("go-last"), "")
        self._btn_addalltoqueue.setToolTip("Add all to queue")
        self._btn_addalltoqueue.setEnabled(False)

        self._lbl_options = QLabel('Queued/Running/Completed')
        self._tbl_options = QTableView()
        self._tbl_options.setModel(_StateOptionsTableModel())
        self._tbl_options.setItemDelegate(_StateOptionsItemDelegate())
        self._tbl_options.setSelectionMode(QListView.SelectionMode.NoSelection)
        self._tbl_options.setColumnWidth(1, 60)
        self._tbl_options.setColumnWidth(2, 80)
        header = self._tbl_options.horizontalHeader()
        header.setResizeMode(0, QHeaderView.Interactive)
        header.setResizeMode(1, QHeaderView.Fixed)
        header.setResizeMode(2, QHeaderView.Fixed)
        header.setResizeMode(3, QHeaderView.Stretch)

        self._btn_start = QPushButton(getIcon("media-playback-start"), "Start")

        self._btn_cancel = QPushButton("Cancel")
        self._btn_cancel.setEnabled(False)

        self._btn_close = QPushButton("Close")

        # Layouts
        layout = QVBoxLayout()

        sublayout = QGridLayout()
        sublayout.addWidget(lbl_outputdir, 0, 0)
        sublayout.addWidget(self._txt_outputdir, 0, 1)
        sublayout.addWidget(lbl_workers, 1, 0)

        subsublayout = QHBoxLayout()
        subsublayout.addWidget(self._spn_workers)
        subsublayout.addWidget(lbl_max_workers)
        sublayout.addLayout(subsublayout, 1, 1)
        layout.addLayout(sublayout)

        sublayout.addWidget(self._chk_overwrite, 2, 0, 1, 3)

        sublayout = QGridLayout()
        sublayout.setColumnStretch(0, 1)
        sublayout.setColumnStretch(2, 3)
        sublayout.addWidget(self._lbl_available, 0, 0)
        sublayout.addWidget(self._lst_available, 1, 0)
        sublayout.addWidget(tlb_available, 2, 0)

        subsublayout = QVBoxLayout()
        subsublayout.addStretch()
        subsublayout.addWidget(self._btn_addtoqueue)
        subsublayout.addWidget(self._btn_addalltoqueue)
        subsublayout.addStretch()
        sublayout.addLayout(subsublayout, 1, 1)

        sublayout.addWidget(self._lbl_options, 0, 2)
        sublayout.addWidget(self._tbl_options, 1, 2)
        layout.addLayout(sublayout)

        sublayout = QHBoxLayout()
        sublayout.addStretch()
        sublayout.addWidget(self._btn_start)
        sublayout.addWidget(self._btn_cancel)
        sublayout.addWidget(self._btn_close)
        layout.addLayout(sublayout)

        self.setLayout(layout)

        # Signal
        self._running_timer.timeout.connect(self._onRunningTimer)

        act_open.triggered.connect(self._onOpen)

        self._btn_addtoqueue.released.connect(self._onAddToQueue)
        self._btn_addalltoqueue.released.connect(self._onAddAllToQueue)
        self._btn_start.released.connect(self._onStart)
        self._btn_cancel.released.connect(self._onCancel)
        self._btn_close.released.connect(self._onClose)

    def _onDialogProgressProgress(self, progress, status):
        self._dlg_progress.setValue(progress * 100)
        self._dlg_progress.setLabelText(status)

    def _onDialogProgressCancel(self):
        self._dlg_progress.hide()
        if self._options_reader_thread is None:
            return
        self._options_reader_thread.cancel()
        self._options_reader_thread.quit()
        self._options_reader_thread.wait()

    def _onDialogProgressException(self, ex):
        self._dlg_progress.hide()
        self._options_reader_thread.quit()
        self._options_reader_thread.wait()
        messagebox.exception(self, ex)

    def _onRunningTimer(self):
        self._tbl_options.model().reset()

    def _onOpen(self):
        settings = get_settings()
        curdir = getattr(settings.gui, 'opendir', os.getcwd())

        filepath, namefilter = \
            QFileDialog.getOpenFileName(self, "Open", curdir,
                                        'Options [*.xml] (*.xml)')

        if not filepath or not namefilter:
            return
        settings.gui.opendir = os.path.dirname(filepath)

        if not filepath.endswith('.xml'):
            filepath += '.xml'

        self._options_reader_thread = _OptionsReaderWrapperThread(filepath)
        self._dlg_progress.canceled.connect(self._onDialogProgressCancel)
        self._options_reader_thread.resultReady.connect(self._onOpened)
        self._options_reader_thread.progressUpdated.connect(self._onDialogProgressProgress)
        self._options_reader_thread.exceptionRaised.connect(self._onDialogProgressException)
        self._options_reader_thread.start()

        self._dlg_progress.reset()
        self._dlg_progress.show()

    def _onOpened(self, options):
        self._dlg_progress.hide()
        self._options_reader_thread.quit()
        self._options_reader_thread.wait()
        self._options_reader_thread = None

        try:
            self._lst_available.model().addOptions(options)
        except Exception as ex:
            messagebox.exception(self, ex)

    def _onAddToQueue(self):
        selection = self._lst_available.selectionModel().selection().indexes()
        if len(selection) == 0:
            QMessageBox.warning(self, "Queue", "Select an options")
            return

        model = self._lst_available.model()
        for row in sorted(map(methodcaller('row'), selection), reverse=True):
            options = model.options(row)
            try:
                self._runner.put(options)
            except Exception as ex:
                messagebox.exception(self, ex)
                return
            else:
                model.removeOptions(row)

    def _onAddAllToQueue(self):
        model = self._lst_available.model()
        for row in reversed(range(0, model.rowCount())):
            options = model.options(row)
            try:
                self._runner.put(options)
            except Exception as ex:
                messagebox.exception(self, ex)
                return
            else:
                model.removeOptions(row)

    def _onStart(self):
        outputdir = self._txt_outputdir.path()
        if not outputdir:
            QMessageBox.critical(self, 'Start', 'Missing output directory')
            return
        max_workers = self._spn_workers.value()
        overwrite = self._chk_overwrite.isChecked()
        self._runner = LocalRunner(outputdir=outputdir,
                                   overwrite=overwrite,
                                   max_workers=max_workers)

        self._tbl_options.setModel(_StateOptionsTableModel(self._runner))

        self._spn_workers.setEnabled(False)
        self._txt_outputdir.setEnabled(False)
        self._chk_overwrite.setEnabled(False)
        self._btn_addtoqueue.setEnabled(True)
        self._btn_addalltoqueue.setEnabled(True)
        self._btn_start.setEnabled(False)
        self._btn_cancel.setEnabled(True)

        self._runner.options_added.connect(self._onOptionsAdded)
        self._runner.options_running.connect(self._onOptionsRunning)
        self._runner.options_simulated.connect(self._onOptionsSimulated)
        self._runner.options_error.connect(self._onOptionsError)

        self._runner.start()

    def _onCancel(self):
        self._runner.cancel()
        self._running_timer.stop()

        self._runner.options_added.disconnect(self._onOptionsAdded)
        self._runner.options_running.disconnect(self._onOptionsRunning)
        self._runner.options_simulated.disconnect(self._onOptionsSimulated)
        self._runner.options_error.disconnect(self._onOptionsError)

        self._runner = None

        self._spn_workers.setEnabled(True)
        self._txt_outputdir.setEnabled(True)
        self._chk_overwrite.setEnabled(True)
        self._btn_addtoqueue.setEnabled(False)
        self._btn_addalltoqueue.setEnabled(False)
        self._btn_start.setEnabled(True)
        self._btn_cancel.setEnabled(False)

    def _onClose(self):
        if self._runner is not None:
            self._runner.close()
        self._running_timer.stop()
        self.close()

    def _onOptionsAdded(self, options):
        self._tbl_options.model().addOptions(options)

    def _onOptionsRunning(self, options):
        self._running_count += 1
        self._running_timer.start()
        self._tbl_options.model().resetOptions(options)

    def _onOptionsSimulated(self, options):
        self._running_count -= 1
        if self._running_count == 0:
            self._running_timer.stop()
        self._tbl_options.model().resetOptions(options)

    def _onOptionsError(self, options, ex):
        self._running_count -= 1
        if self._running_count == 0:
            self._running_timer.stop()
        self._tbl_options.model().resetOptions(options)

    def closeEvent(self, event):
        self._dlg_progress.close()
        return QDialog.closeEvent(self, event)

def __run():
    import sys
    from PySide.QtGui import QApplication
    app = QApplication(sys.argv)
    dialog = RunnerDialog()
    dialog.exec_()
    app.exec_()

if __name__ == '__main__':
    __run()



