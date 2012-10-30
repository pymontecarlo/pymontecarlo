#!/usr/bin/env python
"""
================================================================================
:mod:`updater` -- Options updater
================================================================================

.. module:: updater
   :synopsis: Options updater

.. inheritance-diagram:: pymontecarlo.input.updater

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import logging

# Third party modules.
import lxml.etree as etree

# Local modules.
from pymontecarlo.util.updater import _Updater
from pymontecarlo.input.options import Options

# Globals and constants variables.

class Updater(_Updater):

    def __init__(self):
        """
        Creates a new updater for the options.
        """
        _Updater.__init__(self)

        self._updaters[0] = self._update_noversion
        self._updaters[2] = self._update_version2
        self._updaters[3] = self._update_version3
        self._updaters[4] = self._update_version4

    def _get_version(self, filepath):
        root = etree.parse(filepath).getroot()
        return int(root.get('version', 0))

    def _validate(self, filepath):
        Options.load(filepath, validate=True)

    def _update_noversion(self, filepath):
        logging.debug('Updating from "no version"')

        root = etree.parse(filepath).getroot()

        if not root.nsmap and root.tag.startswith('pymontecarlo.'):
            content = open(filepath, 'r').read()

            lookup = {'<pymontecarlo.input.base.options.Options': '<mc:options xmlns:mc="http://pymontecarlo.sf.net" xmlns:mc-pen="http://pymontecarlo.sf.net/penelope" version="2"',
                      'pymontecarlo.input.base.options.Options>': 'mc:options>',

                      'pymontecarlo.input.base.beam.PencilBeam': 'mc:pencilBeam',
                      'pymontecarlo.input.base.beam.GaussianBeam': 'mc:gaussianBeam',

                      'pymontecarlo.input.base.body.Body': 'mc:body',
                      'pymontecarlo.input.base.body.Layer': 'mc:layer',

                      'pymontecarlo.input.base.detector.BackscatteredElectronEnergyDetector': 'mc:backscatteredElectronEnergyDetector',
                      'pymontecarlo.input.base.detector.TransmittedElectronEnergyDetector': 'mc:transmittedElectronEnergyDetector',
                      'pymontecarlo.input.base.detector.BackscatteredElectronPolarAngularDetector': 'mc:backscatteredElectronPolarAngularDetector',
                      'pymontecarlo.input.base.detector.TransmittedElectronPolarAngularDetector': 'mc:transmittedElectronPolarAngularDetector',
                      'pymontecarlo.input.base.detector.BackscatteredElectronAzimuthalAngularDetector': 'mc:backscatteredElectronAzimuthalAngularDetector',
                      'pymontecarlo.input.base.detector.TransmittedElectronAzimuthalAngularDetector': 'mc:transmittedElectronAzimuthalAngularDetector',
                      'pymontecarlo.input.base.detector.PhotonPolarAngularDetector': 'mc:photonPolarAngularDetector',
                      'pymontecarlo.input.base.detector.PhotonAzimuthalAngularDetector': 'mc:photonAzimuthalAngularDetector',
                      'pymontecarlo.input.base.detector.EnergyDepositedSpatialDetector': 'mc:energyDepositedSpatialDetector',
                      'pymontecarlo.input.base.detector.PhotonSpectrumDetector': 'mc:photonSpectrumDetector',
                      'pymontecarlo.input.base.detector.PhiRhoZDetector': 'mc:phiRhoZDetector',
                      'pymontecarlo.input.base.detector.PhotonIntensityDetector': 'mc:photonIntensityDetector',
                      'pymontecarlo.input.base.detector.TimeDetector': 'mc:timeDetector',
                      'pymontecarlo.input.base.detector.ElectronFractionDetector': 'mc:electronFractionDetector',

                      'pymontecarlo.input.base.geometry.Substrate': 'mc:substrate',
                      'pymontecarlo.input.base.geometry.Inclusion': 'mc:inclusion',
                      'pymontecarlo.input.base.geometry.MultiLayers': 'mc:multiLayers',
                      'pymontecarlo.input.base.geometry.GrainBoundaries': 'mc:grainBoundaries',

                      'pymontecarlo.input.base.limit.TimeLimit': 'mc:timeLimit',
                      'pymontecarlo.input.base.limit.ShowersLimit': 'mc:showersLimit',
                      'pymontecarlo.input.base.limit.UncertaintyLimit': 'mc:uncertaintyLimit',

                      'pymontecarlo.input.base.material.Material': 'mc:material',

                      'pymontecarlo.input.base.model.Model': 'mc:model',

                      'pymontecarlo.input.penelope.body.Body': 'mc-pen:body',
                      'pymontecarlo.input.penelope.body.Layer': 'mc-pen:layer',
                      'pymontecarlo.input.penelope.interactionforcing.InteractionForcing': 'mc-pen:interactionForcing',
                      'pymontecarlo.input.penelope.material.Material': 'mc-pen:material',

                      }

            for oldvalue, newvalue in lookup.items():
                content = content.replace(oldvalue, newvalue)

            with open(filepath, 'w') as fp:
                fp.write(content)
        else:
            root.set('version', '2')

            with open(filepath, 'w') as fp:
                fp.write(etree.tostring(root, pretty_print=True))

        self._update_version2(filepath)
        self._update_version3(filepath)

    def _update_version2(self, filepath):
        logging.debug('Updating from "version 2"')

        root = etree.parse(filepath).getroot()
        root.set('version', '3')

        element = list(root.find('beam'))[0]
        element.set('particle', 'electron')

        with open(filepath, 'w') as fp:
            fp.write(etree.tostring(root, pretty_print=True))

        self._update_version3(filepath)

    def _update_version3(self, filepath):
        logging.debug('Updating from "version 3"')

        root = etree.parse(filepath).getroot()
        root.set('version', '4')

        elements = list(list(root.find('geometry'))[0].find('materials'))
        for element in elements:
            element.set('absorptionEnergyPositron', '50.0')

        with open(filepath, 'w') as fp:
            fp.write(etree.tostring(root, pretty_print=True))

    def _update_version4(self, filepath):
        logging.info('Nothing to update')
