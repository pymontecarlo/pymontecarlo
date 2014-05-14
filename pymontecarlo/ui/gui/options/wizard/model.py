#!/usr/bin/env python
"""
================================================================================
:mod:`model` -- Model wizard page
================================================================================

.. module:: model
   :synopsis: Model wizard page

.. inheritance-diagram:: pymontecarlo.ui.gui.options.wizard.model

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from operator import attrgetter

# Third party modules.
from PySide.QtGui import \
    (QComboBox, QToolBar, QPushButton, QSizePolicy, QWidget, QHBoxLayout,
     QMessageBox)
from PySide.QtCore import Qt, QAbstractListModel

# Local modules.
from pymontecarlo.ui.gui.options.model import ModelTableWidget
from pymontecarlo.ui.gui.options.wizard.options import \
    _ExpandableOptionsWizardPage
from pymontecarlo.ui.gui.util.tango import getIcon

# Globals and constants variables.

class ModelWizardPage(_ExpandableOptionsWizardPage):

    class _ModelTypeComboBoxModel(QAbstractListModel):

        def __init__(self, model_types=None):
            QAbstractListModel.__init__(self)
            if model_types is None:
                model_types = []
            self._model_types = list(model_types)

        def rowCount(self, *args, **kwargs):
            return len(self._model_types)

        def data(self, index, role=Qt.DisplayRole):
            if not index.isValid() or \
                    not (0 <= index.row() < self.rowCount()):
                return None

            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter

            if role != Qt.DisplayRole:
                return None

            return str(self._model_types[index.row()])

        def modelType(self, index):
            return self._model_types[index]

    class _ModelComboBoxModel(QAbstractListModel):

        def __init__(self, models_text=None):
            QAbstractListModel.__init__(self)

            if models_text is None:
                models_text = {}
            self._models_text = models_text.copy()

            self._models = {}
            for model in models_text.keys():
                self._models.setdefault(model.type, []).append(model)

            self._model_type = None

        def rowCount(self, *args, **kwargs):
            return len(self._models.get(self._model_type, []))

        def data(self, index, role=Qt.DisplayRole):
            if not index.isValid() or \
                    not (0 <= index.row() < self.rowCount()):
                return None

            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter

            if role != Qt.DisplayRole:
                return None

            model = self._models[self._model_type][index.row()]
            return self._models_text[model]

        def setModelType(self, model_type):
            self._model_type = model_type
            self.reset()

        def model(self, index):
            return self._models[self._model_type][index]

        def add(self, model):
            if model not in self._models_text:
                raise ValueError('No text defined for model: %s' % model)
            self._models[model.type].append(model)
            self.reset()

        def remove(self, model):
            self._models[model.type].remove(model)
            self.reset()

    def __init__(self, options, parent=None):
        _ExpandableOptionsWizardPage.__init__(self, options, parent)
        self.setTitle('Model')

    def _initUI(self):
        # Widgets
        self._cb_model_type = QComboBox()
        self._cb_model_type.setModel(self._ModelTypeComboBoxModel())

        self._cb_model = QComboBox()
        self._cb_model.setModel(self._ModelComboBoxModel())
        self._cb_model.setMaxVisibleItems(10)

        btn_model_add = QPushButton()
        btn_model_add.setIcon(getIcon("list-add"))

        self._tbl_model = ModelTableWidget()

        tlb_model = QToolBar()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tlb_model.addWidget(spacer)
        act_remove = tlb_model.addAction(getIcon("list-remove"), "Remove model")
        act_clear = tlb_model.addAction(getIcon("edit-clear"), "Clear")

        # Layouts
        layout = _ExpandableOptionsWizardPage._initUI(self)

        sublayout = QHBoxLayout()
        sublayout.addWidget(self._cb_model_type, 1)
        sublayout.addWidget(self._cb_model, 1)
        sublayout.addWidget(btn_model_add)
        layout.addRow("Select", sublayout)

        layout.addRow(self._tbl_model)
        layout.addRow(tlb_model)

        # Signals
        btn_model_add.released.connect(self._onModelAdd)
        act_remove.triggered.connect(self._onModelRemove)
        act_clear.triggered.connect(self._onModelClear)

        self._cb_model_type.currentIndexChanged.connect(self._onModelTypeChanged)

        self._tbl_model.dataChanged.connect(self.valueChanged)

        return layout

    def _onModelTypeChanged(self):
        cb_model = self._cb_model.model()

        index = self._cb_model_type.currentIndex()
        model_type = self._cb_model_type.model().modelType(index)
        cb_model.setModelType(model_type)

        self._cb_model.setCurrentIndex(0)

    def _onModelAdd(self):
        cb_model = self._cb_model.model()

        index = self._cb_model.currentIndex()
        try:
            model = cb_model.model(index)
        except IndexError: # No entry
            return
        self._tbl_model.addModel(model)
        cb_model.remove(model) # Remove model from combo box

        self._cb_model.setCurrentIndex(index)

    def _onModelRemove(self):
        models = self._tbl_model.currentModels()
        if len(models) == 0:
            QMessageBox.warning(self, "Model", "Select a row")
            return

        cb_model = self._cb_model.model()

        for model in models:
            cb_model.add(model) # Show model in combo box
            self._tbl_model.removeModel(model)

        if self._cb_model.currentIndex() < 0:
            self._cb_model.setCurrentIndex(0)

    def _onModelClear(self):
        models = self._tbl_model.models()
        cb_model = self._cb_model.model()

        for model in models:
            cb_model.add(model) # Show model in combo box
            self._tbl_model.removeModel(model)

        if self._cb_model.currentIndex() < 0:
            self._cb_model.setCurrentIndex(0)

    def _iter_models(self):
        allmodels = {}
        default_models = {}
        for program in self.options().programs:
            converter = program.converter_class

            for models in converter.MODELS.values():
                for model in models:
                    allmodels.setdefault(model, set()).add(program)

                    if model == converter.DEFAULT_MODELS[model.type]:
                        default_models.setdefault(model, set()).add(program)

        for model, programs in allmodels.items():
            defaults = default_models.get(model, [])
            yield model, programs, defaults

    def initializePage(self):
        _ExpandableOptionsWizardPage.initializePage(self)

        # Populate combo boxes
        model_types = set()
        models_text = {}

        for model, programs, defaults in self._iter_models():
            programs_text = []
            for program in programs:
                program_text = program.name
                if program in defaults:
                    program_text += '*'
                programs_text.append(program_text)

            program_text = ', '.join(programs_text)
            text = '{0} ({1})'.format(str(model), program_text)

            model_types.add(model.type)
            models_text[model] = text

        model_types = sorted(model_types, key=attrgetter('name'))
        cb_model_type = self._ModelTypeComboBoxModel(model_types)
        self._cb_model_type.setModel(cb_model_type)
        self._cb_model_type.setCurrentIndex(0)

        cb_model = self._ModelComboBoxModel(models_text)
        self._cb_model.setModel(cb_model)
        cb_model.setModelType(cb_model_type.modelType(0))
        self._cb_model.setCurrentIndex(0)

        # Add model(s)
        self._tbl_model.clear()
        self._tbl_model.addModels(self.options().models)

    def validatePage(self):
        self.options().models.clear()
        for model in self._tbl_model.models():
            self.options().models.add(model)

        return True

    def expandCount(self):
        try:
            count = 1

            models = {}
            for model in self._tbl_model.models():
                models.setdefault(model.type, []).append(model)

            for values in models.values():
                count *= len(values)

            return count
        except:
            return 0
