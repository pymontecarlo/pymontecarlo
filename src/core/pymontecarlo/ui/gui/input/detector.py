#!/usr/bin/env python
"""
================================================================================
:mod:`detector` -- Wizard page for detectors
================================================================================

.. module:: detector
   :synopsis: Wizard page for detectors

.. inheritance-diagram:: pymontecarlo.ui.gui.input.detector

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import math
import warnings
from operator import itemgetter, attrgetter

# Third party modules.
import wx

# Local modules.
from pymontecarlo.input.detector import \
    (TrajectoryDetector,
     PhotonIntensityDetector,
     BackscatteredElectronEnergyDetector,
     TransmittedElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector,
     TransmittedElectronPolarAngularDetector,
     BackscatteredElectronAzimuthalAngularDetector,
     TransmittedElectronAzimuthalAngularDetector,
     BackscatteredElectronRadialDetector,
     PhotonPolarAngularDetector,
     PhotonAzimuthalAngularDetector,
     PhotonSpectrumDetector,
     PhotonDepthDetector,
     PhotonRadialDetector,
     PhotonEmissionMapDetector,
     TimeDetector,
     ElectronFractionDetector,
     ShowersStatisticsDetector,
     )

from pymontecarlo.util.manager import ClassManager
from pymontecarlo.util.human import camelcase_to_words

from pymontecarlo.ui.gui.input.wizardpage import WizardPage

from wxtools2.combobox import PyComboBox
from wxtools2.list import \
    PyListCtrl, StaticColumn, PyListCtrlValidator, EVT_LIST_ROW_ACTIVATED
from wxtools2.validator import form_validate, TextValidator
from wxtools2.dialog import show_error_dialog, show_exclamation_dialog
from wxtools2.floatspin import FloatSpin, EVT_FLOATSPIN
from wxtools2.exception import catch_all

# Globals and constants variables.
from pymontecarlo.ui.gui.art import \
    ART_LIST_REMOVE, ART_LIST_CLEAR, ART_LIST_EDIT

DetectorDialogManager = ClassManager()

class DetectorWizardPage(WizardPage):

    def __init__(self, wizard):
        WizardPage.__init__(self, wizard, 'Detector(s) definition')

        # Controls
        ## Type
        lbltype = wx.StaticText(self, label='Type')
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD)
        lbltype.SetFont(font)
        getter = lambda t: camelcase_to_words(t.__name__)[:-9]
        self._cbtype = PyComboBox(self, getter)
        btnadd = wx.Button(self, label='Add')

        ## List
        c2 = lambda r: camelcase_to_words(r[1].__class__.__name__)[:-9]
        columns = [StaticColumn('Key', lambda r: r[0], width=100),
                   StaticColumn('Detector', c2, width= -3)]
        self._lstdetectors = PyListCtrl(self, columns, name="detectors")
        self._lstdetectors.SetValidator(PyListCtrlValidator(allow_empty=False))

        ## Action buttons
        toolbar = wx.ToolBar(self)

        self._TOOL_REMOVE = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(ART_LIST_REMOVE, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_REMOVE, bitmap,
                              "Remove selected detector")

        self._TOOL_CLEAR = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(ART_LIST_CLEAR, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_CLEAR, bitmap, "Remove all detectors")

        self._TOOL_EDIT = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(ART_LIST_EDIT, wx.ART_TOOLBAR)
        toolbar.AddSimpleTool(self._TOOL_EDIT, bitmap, "Edit detector")

        toolbar.Realize()

        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        szr_type = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(szr_type, 0, wx.EXPAND | wx.ALL, 5)
        szr_type.Add(lbltype, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        szr_type.Add(self._cbtype, 1, wx.GROW | wx.RIGHT, 5)
        szr_type.Add(btnadd, 0)

        sizer.Add(self._lstdetectors, 1, wx.EXPAND | wx.ALL, 5)

        sizer.Add(toolbar, 0, wx.ALIGN_RIGHT)

        self.SetSizer(sizer)

        # Bind
        self.Bind(wx.EVT_BUTTON, self.OnAdd, btnadd)
        self.Bind(wx.EVT_TOOL, self.OnRemove, id=self._TOOL_REMOVE)
        self.Bind(wx.EVT_TOOL, self.OnClear, id=self._TOOL_CLEAR)
        self.Bind(wx.EVT_TOOL, self.OnEdit, id=self._TOOL_EDIT)
        self.Bind(EVT_LIST_ROW_ACTIVATED, self.OnEdit, self._lstdetectors)

        # Add types
        for clasz in sorted(wizard.available_detectors, key=attrgetter('__name__')):
            try:
                DetectorDialogManager.get(clasz)
            except KeyError:
                warnings.warn("No dialog for detector %s" % clasz.__name__)
                continue
            self._cbtype.append(clasz)

        if self._cbtype:
            self._cbtype.selection = self._cbtype[0]

    def OnAdd(self, event):
        clasz = self._cbtype.selection
        dialog_class = DetectorDialogManager.get(clasz)
        keys = map(itemgetter(0), self._lstdetectors)

        dialog = dialog_class(self)
        while True: # Keep showing dialog until valid key or cancel
            if dialog.ShowModal() != wx.ID_OK: break

            key = dialog.GetKey()
            if key not in keys:
                detector = dialog.GetDetector()
                self._lstdetectors.append([key, detector])
                break

            show_error_dialog(self, "Key (%s) already exists" % key)

        dialog.Destroy()

        self.OnValueChanged()

    def OnRemove(self, event):
        if not self._lstdetectors: # No detectors
            return

        if not self._lstdetectors.selection:
            show_exclamation_dialog(self, "Please select a detector to delete")
            return

        del self._lstdetectors[self._lstdetectors.index(self._lstdetectors.selection)]

        self.OnValueChanged()

    def OnClear(self, event):
        self._lstdetectors.clear()
        self.OnValueChanged()

    def OnEdit(self, event):
        if not self._lstdetectors: # No detectors
            return

        if not self._lstdetectors.selection:
            show_exclamation_dialog(self, "Please select a detector to edit")
            return

        rowobj = self._lstdetectors.selection
        row = self._lstdetectors.index(rowobj)
        key, detector = rowobj
        dialog_class = DetectorDialogManager.get(detector.__class__)
        keys = map(itemgetter(0), self._lstdetectors)

        dialog = dialog_class(self, key, detector)
        while True: # Keep showing dialog until valid key or cancel
            if dialog.ShowModal() != wx.ID_OK: break

            newkey = dialog.GetKey()
            if newkey not in keys or newkey == key:
                newdetector = dialog.GetDetector()
                self._lstdetectors[row] = [newkey, newdetector]
                break

            show_error_dialog(self, "Key (%s) already exists" % newkey)

        dialog.Destroy()

        self.OnValueChanged()

    def get_options(self):
        if not self._lstdetectors:
            return []
        return [dict(self._lstdetectors)]

class _DetectorDialog(wx.Dialog):

    def __init__(self, parent, key=None, detector=None):
        wx.Dialog.__init__(self, parent)
        self.SetTitle(camelcase_to_words(self.__class__.__name__)[:-6])

        # Variables
        self._key = key
        self._detector = detector

        # Controls
        lblkey = wx.StaticText(self, label='Key', size=(80, -1))
        self._txtkey = wx.TextCtrl(self, name="key")
        self._txtkey.SetValidator(TextValidator(allow_empty=False))
        if key is not None:
            self._txtkey.SetValue(key)

        btnok = wx.Button(self, wx.ID_OK)
        btnok.SetDefault()
        btncancel = wx.Button(self, wx.ID_CANCEL)

        # Sizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        sizer = wx.GridBagSizer(5, 5)
        mainsizer.Add(sizer, 1, wx.EXPAND | wx.ALL, 5)
        sizer.AddGrowableCol(1)

        sizer.Add(lblkey, pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._txtkey, pos=(0, 1), flag=wx.GROW)
        sizer.Add(wx.StaticLine(self), pos=(1, 0), span=(1, 2), flag=wx.GROW)

        self._setup_layout(sizer, 2)

        szr_buttons = wx.StdDialogButtonSizer()
        mainsizer.Add(szr_buttons, 0, wx.GROW | wx.ALIGN_RIGHT)
        szr_buttons.AddButton(btnok)
        szr_buttons.AddButton(btncancel)
        szr_buttons.SetAffirmativeButton(btnok)
        szr_buttons.SetCancelButton(btncancel)
        szr_buttons.Realize()

        self.SetSizerAndFit(mainsizer)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_BUTTON, self.OnOk, id=wx.ID_OK)

        if detector is not None:
            self._load_detector(detector)

    def _setup_layout(self, sizer, row):
        return row

    def _load_detector(self, detector):
        pass

    def _create_detector(self):
        raise NotImplementedError

    def _modify_detector(self):
        pass

    def get_options(self):
        wizardpage = self.GetParent()
        wizard = wizardpage.GetParent()
        return wizard.get_options()

    def Validate(self):
        return form_validate(self)

    def OnClose(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnOk(self, event):
        if not self.Validate():
            event.StopPropagation()
        else:
            self._key = self._txtkey.GetValue()

            with catch_all(self) as success:
                if self._detector is None:
                    self._detector = self._create_detector()
                else:
                    self._modify_detector()

            if success:
                self.EndModal(wx.ID_OK)

    def GetKey(self):
        return self._key

    def GetDetector(self):
        return self._detector

class _DelimitedDetectorDialog(_DetectorDialog):

    def _setup_layout(self, sizer, row):
        row = _DetectorDialog._setup_layout(self, sizer, row)

        # Control
        lblelevation = wx.StaticText(self, label=u'Elevation (\u00b0)')
        self._txtelevation_min = \
            FloatSpin(self, value=0, min_val= -90, max_val=90, increment=5, digits=1)
        self._txtelevation_max = \
            FloatSpin(self, value=90, min_val= -90, max_val=90, increment=5, digits=1)

        lblazimuth = wx.StaticText(self, label=u'Azimuth (\u00b0)')
        self._txtazimuth_min = \
            FloatSpin(self, value=0, min_val=0, max_val=360, increment=5, digits=1)
        self._txtazimuth_max = \
            FloatSpin(self, value=360, min_val=0, max_val=360, increment=5, digits=1)

        lblsolidangle = wx.StaticText(self, label='Solid angle (sr)')
        lblsolidangle.Enable(False)
        self._txtsolidangle = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_RIGHT)

        lbltakeoffangle = wx.StaticText(self, label=u'Take-off angle (\u00b0)')
        lbltakeoffangle.Enable(False)
        self._txttakeoffangle = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_RIGHT)

        # Sizer
        sizer.Add(lblelevation, pos=(row, 0))

        szr_elevation = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(szr_elevation, pos=(row, 1), flag=wx.GROW)
        szr_elevation.Add(self._txtelevation_min, 1, wx.GROW)
        szr_elevation.Add(wx.StaticText(self, label='-'), 0, wx.ALIGN_CENTER_VERTICAL)
        szr_elevation.Add(self._txtelevation_max, 1, wx.GROW)

        sizer.Add(lblazimuth, pos=(row + 1, 0))

        szr_azimuth = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(szr_azimuth, pos=(row + 1, 1), flag=wx.GROW)
        szr_azimuth.Add(self._txtazimuth_min, 1, wx.GROW)
        szr_azimuth.Add(wx.StaticText(self, label='-'), 0, wx.ALIGN_CENTER_VERTICAL)
        szr_azimuth.Add(self._txtazimuth_max, 1, wx.GROW)

        sizer.Add(lblsolidangle, pos=(row + 2, 0))
        sizer.Add(self._txtsolidangle, pos=(row + 2, 1), flag=wx.GROW)


        sizer.Add(lbltakeoffangle, pos=(row + 3, 0))
        sizer.Add(self._txttakeoffangle, pos=(row + 3, 1), flag=wx.GROW)

        # Bind
        self.Bind(EVT_FLOATSPIN, self._onchanged, self._txtelevation_min)
        self.Bind(EVT_FLOATSPIN, self._onchanged, self._txtelevation_max)
        self.Bind(EVT_FLOATSPIN, self._onchanged, self._txtazimuth_min)
        self.Bind(EVT_FLOATSPIN, self._onchanged, self._txtazimuth_max)
        self._onchanged()

        return row + 4

    def _load_detector(self, detector):
        elevation = detector.elevation_deg
        self._txtelevation_min.SetValue(elevation[0])
        self._txtelevation_max.SetValue(elevation[1])

        azimuth = detector.azimuth_deg
        self._txtazimuth_min.SetValue(azimuth[0])
        self._txtazimuth_max.SetValue(azimuth[1])

    def _modify_detector(self):
        self._detector.elevation_deg = (self._txtelevation_min.GetValue(),
                                        self._txtelevation_max.GetValue())
        self._detector.azimuth_deg = (self._txtazimuth_min.GetValue(),
                                      self._txtazimuth_max.GetValue())

    def _onchanged(self, event=None):
        elevation = map(math.radians, (self._txtelevation_min.GetValue(),
                                     self._txtelevation_max.GetValue()))
        azimuth = map(math.radians, (self._txtazimuth_min.GetValue(),
                                     self._txtazimuth_max.GetValue()))

        solidangle = abs((azimuth[1] - azimuth[0]) * \
                   (math.cos(elevation[0]) - math.cos(elevation[1])))
        self._txtsolidangle.SetValue('%.3f' % solidangle)

        takeoffangle = math.degrees(sum(elevation) / 2.0)
        self._txttakeoffangle.SetValue('%.1f' % takeoffangle)

class _ChannelsDetectorDialog(_DetectorDialog):

    def _setup_layout(self, sizer, row):
        row = _DetectorDialog._setup_layout(self, sizer, row)

        lblchannels = wx.StaticText(self, label='# of channels')
        self._txtchannels = \
            FloatSpin(self, value=100, min_val=1, increment=10, digits=0)

        sizer.Add(lblchannels, pos=(row, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._txtchannels, pos=(row, 1), flag=wx.GROW)

        return row + 1

    def _load_detector(self, detector):
        self._txtchannels.SetValue(int(detector.channels))

    def _modify_detector(self):
        self._detector.channels = int(self._txtchannels.GetValue())

class _BoundedChannelsDetectorDialog(_ChannelsDetectorDialog):

    def __init__(self, parent, extremums, units, key=None, detector=None):
        self._extremums = tuple(extremums)
        self._units = units
        _ChannelsDetectorDialog.__init__(self, parent, key, detector)

    def _setup_layout(self, sizer, row):
        row = _ChannelsDetectorDialog._setup_layout(self, sizer, row)

        lbllimits = wx.StaticText(self, label='Limits (%s)' % self._units)
        self._txtlimit_min = \
            FloatSpin(self, value=0, min_val=self._extremums[0],
                      max_val=self._extremums[1], digits=1)
        self._txtlimit_max = \
            FloatSpin(self, value=0, min_val=self._extremums[0],
                      max_val=self._extremums[1], digits=1)

        sizer.Add(lbllimits, pos=(row, 0))

        szr_limits = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(szr_limits, pos=(row, 1), flag=wx.GROW)
        szr_limits.Add(self._txtlimit_min, 1, wx.GROW)
        szr_limits.Add(wx.StaticText(self, label='-'), 0, wx.ALIGN_CENTER_VERTICAL)
        szr_limits.Add(self._txtlimit_max, 1, wx.GROW)

        return row + 1

    def _load_detector(self, detector):
        _ChannelsDetectorDialog._load_detector(self, detector)

        limits = detector._get_limits()
        self._txtlimit_min.SetValue(limits[0])
        self._txtlimit_max.SetValue(limits[1])

    def _modify_detector(self):
        limits = (self._txtlimit_min.GetValue(), self._txtlimit_max.GetValue())
        self._detector._set_limits(limits)

class _EnergyDetectorDialog(_BoundedChannelsDetectorDialog):

    def __init__(self, parent, key=None, detector=None):
        _BoundedChannelsDetectorDialog.__init__(self, parent, (0.0, None),
                                                  'eV', key, detector)

        maxvalue = max(map(attrgetter('beam.energy_eV'), self.get_options()))
        self._txtlimit_max.SetValue(maxvalue)

class _AngularDetectorDialog(_BoundedChannelsDetectorDialog):

    def __init__(self, parent, extremums, key=None, detector=None):
        _BoundedChannelsDetectorDialog.__init__(self, parent, extremums,
                                                   u'\u00b0', key, detector)

    def _modify_detector(self):
        limits = map(math.radians, (self._txtlimit_min.GetValue(),
                                    self._txtlimit_max.GetValue()))
        self._detector.limits_rad(limits)

class _PolarAngularDetectorDialog(_AngularDetectorDialog):

    def __init__(self, parent, key=None, detector=None):
        extremums = (-90.0, 90.0)
        _AngularDetectorDialog.__init__(self, parent, extremums, key, detector)

class _AzimuthalAngularDetectorDialog(_AngularDetectorDialog):

    def __init__(self, parent, key=None, detector=None):
        extremums = (0.0, 360.0)
        _AngularDetectorDialog.__init__(self, parent, extremums, key, detector)

class BackscatteredElectronEnergyDetectorDialog(_EnergyDetectorDialog):

    def _create_detector(self):
        limits = (self._txtlimit_min.GetValue(), self._txtlimit_max.GetValue())
        channels = self._txtchannels.GetValue()
        return BackscatteredElectronEnergyDetector(limits, channels)

DetectorDialogManager.register(BackscatteredElectronEnergyDetector, BackscatteredElectronEnergyDetectorDialog)

class TransmittedElectronEnergyDetectorDialog(_EnergyDetectorDialog):

    def _create_detector(self):
        limits = (self._txtlimit_min.GetValue(), self._txtlimit_max.GetValue())
        channels = self._txtchannels.GetValue()
        return TransmittedElectronEnergyDetector(limits, channels)

DetectorDialogManager.register(TransmittedElectronEnergyDetector, TransmittedElectronEnergyDetectorDialog)

class BackscatteredElectronPolarAngularDetectorDialog(_PolarAngularDetectorDialog):

    def _create_detector(self):
        channels = self._txtchannels.GetValue()
        limits = map(math.radians, (self._txtlimit_min.GetValue(),
                                    self._txtlimit_max.GetValue()))
        return BackscatteredElectronPolarAngularDetector(channels, limits)

DetectorDialogManager.register(BackscatteredElectronPolarAngularDetector, BackscatteredElectronPolarAngularDetectorDialog)

class TransmittedElectronPolarAngularDetectorDialog(_PolarAngularDetectorDialog):

    def _create_detector(self):
        channels = self._txtchannels.GetValue()
        limits = map(math.radians, (self._txtlimit_min.GetValue(),
                                    self._txtlimit_max.GetValue()))
        return TransmittedElectronPolarAngularDetector(channels, limits)

DetectorDialogManager.register(TransmittedElectronPolarAngularDetector, TransmittedElectronPolarAngularDetectorDialog)

class BackscatteredElectronAzimuthalAngularDetectorDialog(_AzimuthalAngularDetectorDialog):

    def _create_detector(self):
        channels = self._txtchannels.GetValue()
        limits = map(math.radians, (self._txtlimit_min.GetValue(),
                                    self._txtlimit_max.GetValue()))
        return BackscatteredElectronAzimuthalAngularDetector(channels, limits)

DetectorDialogManager.register(BackscatteredElectronAzimuthalAngularDetector, BackscatteredElectronAzimuthalAngularDetectorDialog)

class TransmittedElectronAzimuthalAngularDetectorDialog(_AzimuthalAngularDetectorDialog):

    def _create_detector(self):
        channels = self._txtchannels.GetValue()
        limits = map(math.radians, (self._txtlimit_min.GetValue(),
                                    self._txtlimit_max.GetValue()))
        return TransmittedElectronAzimuthalAngularDetector(channels, limits)

DetectorDialogManager.register(TransmittedElectronAzimuthalAngularDetector, TransmittedElectronAzimuthalAngularDetectorDialog)

class BackscatteredElectronRadialDetectorDialog(_ChannelsDetectorDialog):

    def _create_detector(self):
        channels = self._txtchannels.GetValue()
        return BackscatteredElectronRadialDetector(channels)

DetectorDialogManager.register(BackscatteredElectronRadialDetector, BackscatteredElectronRadialDetectorDialog)

class PhotonPolarAngularDetectorDialog(_PolarAngularDetectorDialog):

    def _create_detector(self):
        channels = self._txtchannels.GetValue()
        limits = map(math.radians, (self._txtlimit_min.GetValue(),
                                    self._txtlimit_max.GetValue()))
        return PhotonPolarAngularDetector(channels, limits)

DetectorDialogManager.register(PhotonPolarAngularDetector, PhotonPolarAngularDetectorDialog)

class PhotonAzimuthalAngularDetectorDialog(_AzimuthalAngularDetectorDialog):

    def _create_detector(self):
        channels = self._txtchannels.GetValue()
        limits = map(math.radians, (self._txtlimit_min.GetValue(),
                                    self._txtlimit_max.GetValue()))
        return PhotonAzimuthalAngularDetector(channels, limits)

DetectorDialogManager.register(PhotonAzimuthalAngularDetector, PhotonAzimuthalAngularDetectorDialog)

class PhotonSpectrumDetectorDialog(_DelimitedDetectorDialog, _EnergyDetectorDialog):

    def _setup_layout(self, sizer, row):
        row = _DelimitedDetectorDialog._setup_layout(self, sizer, row)
        return _EnergyDetectorDialog._setup_layout(self, sizer, row)

    def _load_detector(self, detector):
        _DelimitedDetectorDialog._load_detector(self, detector)
        _EnergyDetectorDialog._load_detector(self, detector)

    def _modify_detector(self):
        _DelimitedDetectorDialog._modify_detector(self)
        _EnergyDetectorDialog._modify_detector(self)

    def _create_detector(self):
        elevation_rad = map(math.radians, (self._txtelevation_min.GetValue(),
                                           self._txtelevation_max.GetValue()))
        azimuth_rad = map(math.radians, (self._txtazimuth_min.GetValue(),
                                         self._txtazimuth_max.GetValue()))
        limits_eV = (self._txtlimit_min.GetValue(), self._txtlimit_max.GetValue())
        channels = self._txtchannels.GetValue()
        return PhotonSpectrumDetector(elevation_rad, azimuth_rad,
                                      limits_eV, channels)

DetectorDialogManager.register(PhotonSpectrumDetector, PhotonSpectrumDetectorDialog)

class PhotonRadialDetectorDialog(_DelimitedDetectorDialog, _ChannelsDetectorDialog):

    def _setup_layout(self, sizer, row):
        row = _DelimitedDetectorDialog._setup_layout(self, sizer, row)
        return _ChannelsDetectorDialog._setup_layout(self, sizer, row)

    def _load_detector(self, detector):
        _DelimitedDetectorDialog._load_detector(self, detector)
        _ChannelsDetectorDialog._load_detector(self, detector)

    def _modify_detector(self):
        _DelimitedDetectorDialog._modify_detector(self)
        _ChannelsDetectorDialog._modify_detector(self)

    def _create_detector(self):
        elevation_rad = map(math.radians, (self._txtelevation_min.GetValue(),
                                           self._txtelevation_max.GetValue()))
        azimuth_rad = map(math.radians, (self._txtazimuth_min.GetValue(),
                                         self._txtazimuth_max.GetValue()))
        channels = self._txtchannels.GetValue()
        return PhotonRadialDetector(elevation_rad, azimuth_rad, channels)

DetectorDialogManager.register(PhotonRadialDetector, PhotonRadialDetectorDialog)

class PhotonDepthDetectorDialog(_DelimitedDetectorDialog, _ChannelsDetectorDialog):

    def _setup_layout(self, sizer, row):
        row = _DelimitedDetectorDialog._setup_layout(self, sizer, row)
        return _ChannelsDetectorDialog._setup_layout(self, sizer, row)

    def _load_detector(self, detector):
        _DelimitedDetectorDialog._load_detector(self, detector)
        _ChannelsDetectorDialog._load_detector(self, detector)

    def _modify_detector(self):
        _DelimitedDetectorDialog._modify_detector(self)
        _ChannelsDetectorDialog._modify_detector(self)

    def _create_detector(self):
        elevation_rad = map(math.radians, (self._txtelevation_min.GetValue(),
                                           self._txtelevation_max.GetValue()))
        azimuth_rad = map(math.radians, (self._txtazimuth_min.GetValue(),
                                         self._txtazimuth_max.GetValue()))
        channels = self._txtchannels.GetValue()
        return PhotonDepthDetector(elevation_rad, azimuth_rad, channels)

DetectorDialogManager.register(PhotonDepthDetector, PhotonDepthDetectorDialog)

class PhotonIntensityDetectorDialog(_DelimitedDetectorDialog):

    def _create_detector(self):
        elevation_rad = map(math.radians, (self._txtelevation_min.GetValue(),
                                           self._txtelevation_max.GetValue()))
        azimuth_rad = map(math.radians, (self._txtazimuth_min.GetValue(),
                                         self._txtazimuth_max.GetValue()))
        return PhotonIntensityDetector(elevation_rad, azimuth_rad)

DetectorDialogManager.register(PhotonIntensityDetector, PhotonIntensityDetectorDialog)

class PhotonEmissionMapDetectorDialog(_DelimitedDetectorDialog):

    def _setup_layout(self, sizer, row):
        row = _DelimitedDetectorDialog._setup_layout(self, sizer, row)

        # Controls
        lblxbins = wx.StaticText(self, label='Channels in x')
        self._txtxbins = FloatSpin(self, name='x channels',
                                   value=100, min_val=1, increment=10, digits=0)

        lblybins = wx.StaticText(self, label='Channels in y')
        self._txtybins = FloatSpin(self, name='y channels',
                                   value=100, min_val=1, increment=10, digits=0)

        lblzbins = wx.StaticText(self, label='Channels in z')
        self._txtzbins = FloatSpin(self, name='z channels',
                                   value=100, min_val=1, increment=10, digits=0)

        # Sizer
        sizer.Add(lblxbins, pos=(row, 0))
        sizer.Add(self._txtxbins, pos=(row, 1), flag=wx.GROW)

        sizer.Add(lblybins, pos=(row + 1, 0))
        sizer.Add(self._txtybins, pos=(row + 1, 1), flag=wx.GROW)

        sizer.Add(lblzbins, pos=(row + 2, 0))
        sizer.Add(self._txtzbins, pos=(row + 2, 1), flag=wx.GROW)

        return row + 3

    def _load_detector(self, detector):
        _DelimitedDetectorDialog._load_detector(self, detector)

        self._txtxbins.SetValue(detector.xbins)
        self._txtybins.SetValue(detector.ybins)
        self._txtzbins.SetValue(detector.zbins)

    def _create_detector(self):
        elevation_rad = map(math.radians, (self._txtelevation_min.GetValue(),
                                           self._txtelevation_max.GetValue()))
        azimuth_rad = map(math.radians, (self._txtazimuth_min.GetValue(),
                                         self._txtazimuth_max.GetValue()))
        xbins = self._txtxbins.GetValue()
        ybins = self._txtybins.GetValue()
        zbins = self._txtzbins.GetValue()

        return PhotonEmissionMapDetector(elevation_rad, azimuth_rad,
                                         xbins, ybins, zbins)

    def _modify_detector(self):
        _DelimitedDetectorDialog._modify_detector(self)

        self._detector.xbins = self._txtxbins.GetValue()
        self._detector.ybins = self._txtybins.GetValue()
        self._detector.zbins = self._txtzbins.GetValue()

DetectorDialogManager.register(PhotonEmissionMapDetector, PhotonEmissionMapDetectorDialog)

class ShowersStatisticsDetectorDialog(_DetectorDialog):

    def _create_detector(self):
        return ShowersStatisticsDetector()

DetectorDialogManager.register(ShowersStatisticsDetector, ShowersStatisticsDetectorDialog)

class TimeDetectorDialog(_DetectorDialog):

    def _create_detector(self):
        return TimeDetector()

DetectorDialogManager.register(TimeDetector, TimeDetectorDialog)

class ElectronFractionDetectorDialog(_DetectorDialog):

    def _create_detector(self):
        return ElectronFractionDetector()

DetectorDialogManager.register(ElectronFractionDetector, ElectronFractionDetectorDialog)

class TrajectoryDetectorDialog(_DetectorDialog):

    def _setup_layout(self, sizer, row):
        row = _DetectorDialog._setup_layout(self, sizer, row)

        self._chksecondary = \
            wx.CheckBox(self, label='Simulate secondary particles')

        sizer.Add(self._chksecondary, pos=(row, 0), span=(1, 2))

        return row + 1

    def _load_detector(self, detector):
        self._chksecondary.SetValue(detector.secondary)

    def _create_detector(self):
        return TrajectoryDetector(self._chksecondary.GetValue())

    def _modify_detector(self):
        self._detector.secondary = self._chksecondary.GetValue()

DetectorDialogManager.register(TrajectoryDetector, TrajectoryDetectorDialog)
