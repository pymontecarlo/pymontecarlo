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
import uuid
import xml.etree.ElementTree as etree

# Third party modules.

# Local modules.
from pymontecarlo.util.updater import _Updater
import pymontecarlo.util.xmlutil as xmlutil

from pymontecarlo.options.options import Options

# Globals and constants variables.
from pymontecarlo.options.particle import ELECTRON, PHOTON, POSITRON
from pymontecarlo.options.collision import \
    (DELTA, HARD_ELASTIC, HARD_INELASTIC, HARD_BREMSSTRAHLUNG_EMISSION,
     INNERSHELL_IMPACT_IONISATION, COHERENT_RAYLEIGH_SCATTERING,
     INCOHERENT_COMPTON_SCATTERING, PHOTOELECTRIC_ABSORPTION,
     ELECTRON_POSITRON_PAIR_PRODUCTION, ANNIHILATION)

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
        self._updaters[5] = self._update_version5
        self._updaters[6] = self._update_version6

    def _get_version(self, filepath):
        root = xmlutil.parse(filepath)
        return int(root.get('version', 0))

    def _validate(self, filepath):
        Options.read(filepath)

    def _update_noversion(self, filepath):
        logging.debug('Updating from "no version"')

        root = xmlutil.parse(filepath)

        if not root.tag.startswith("{") and \
                root.tag.startswith('pymontecarlo.'):
            with open(filepath, 'r') as fp:
                content = fp.read()

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

            with open(filepath, 'wb') as fp:
                fp.write(xmlutil.tostring(root, pretty_print=True))

        return self._update_version2(filepath)

    def _update_version2(self, filepath):
        logging.debug('Updating from "version 2"')

        root = xmlutil.parse(filepath)
        root.set('version', '3')

        # Update beam
        element = list(root.find('beam'))[0]
        element.set('particle', 'electron')

        # Update interaction forcings
        _PARTICLES_REF = {1: ELECTRON, 2: PHOTON, 3: POSITRON}
        _COLLISIONS_REF = {ELECTRON: {2: HARD_ELASTIC,
                                      3: HARD_INELASTIC,
                                      4: HARD_BREMSSTRAHLUNG_EMISSION,
                                      5: INNERSHELL_IMPACT_IONISATION,
                                      7: DELTA},
                           PHOTON: {1: COHERENT_RAYLEIGH_SCATTERING,
                                    2: INCOHERENT_COMPTON_SCATTERING,
                                    3: PHOTOELECTRIC_ABSORPTION,
                                    4: ELECTRON_POSITRON_PAIR_PRODUCTION,
                                    7: DELTA},
                           POSITRON: {2: HARD_ELASTIC,
                                      3: HARD_INELASTIC,
                                      4: HARD_BREMSSTRAHLUNG_EMISSION,
                                      5: INNERSHELL_IMPACT_IONISATION,
                                      6: ANNIHILATION,
                                      7: DELTA}}

        geometry_element = root.find('geometry')[0]
        bodies_element = geometry_element.find('bodies')[0]
        intforcings_element = bodies_element.find('interactionForcings')

        if intforcings_element is not None:
            for element in list(intforcings_element):
                particle = _PARTICLES_REF[int(element.get('particle'))]
                element.set('particle', str(particle))

                collision = _COLLISIONS_REF[particle][int(element.get('collision'))]
                element.set('collision', str(collision))

        with open(filepath, 'wb') as fp:
            fp.write(xmlutil.tostring(root, pretty_print=True))

        return self._update_version3(filepath)

    def _update_version3(self, filepath):
        logging.debug('Updating from "version 3"')

        root = xmlutil.parse(filepath)
        root.set('version', '4')

        elements = list(list(root.find('geometry'))[0].find('materials'))
        for element in elements:
            element.set('absorptionEnergyPositron', '50.0')

        with open(filepath, 'wb') as fp:
            fp.write(xmlutil.tostring(root, pretty_print=True))

        return self._update_version4(filepath)

    def _update_version4(self, filepath):
        logging.debug('Updating from "version 4"')

        root = xmlutil.parse(filepath)
        root.set('version', '5')

        for element in root.find('detectors'):
            if element.tag == '{http://pymontecarlo.sf.net}phiRhoZDetector':
                element.tag = '{http://pymontecarlo.sf.net}photonDepthDetector'

        with open(filepath, 'wb') as fp:
            fp.write(xmlutil.tostring(root, pretty_print=True))

        return self._update_version5(filepath)

    def _update_version5(self, filepath):
        logging.debug('Updating from "version 5"')

        root = xmlutil.parse(filepath)

        # Header
        root.set('version', '6')
        if 'uuid' not in root.attrib:
            root.set('uuid', uuid.uuid4().hex)

        # Beam
        element = root.find('beam/*/direction')
        element.set('u', element.attrib.pop('x'))
        element.set('v', element.attrib.pop('y'))
        element.set('w', element.attrib.pop('z'))

        # Geometry
        element = root.find('geometry/')

        materials_lookup = {}
        for subelement in element.findall('bodies/*'):
            materials_lookup[subelement.get('index')] = subelement.get('material')

        if element.tag == '{http://pymontecarlo.sf.net}substrate':
            material = materials_lookup[element.attrib.pop('substrate')]
            etree.SubElement(element, 'body', {'material': material})

        elif element.tag == '{http://pymontecarlo.sf.net}inclusion':
            material = materials_lookup[element.attrib.pop('substrate')]
            etree.SubElement(element, 'substrate', {'material': material})

            material = materials_lookup[element.attrib.pop('inclusion')]
            diameter = element.attrib.pop('diameter')
            etree.SubElement(element, 'inclusion',
                             {'material': material, 'diameter': diameter})

        elif element.tag == '{http://pymontecarlo.sf.net}multiLayers':
            element.tag = '{http://pymontecarlo.sf.net}horizontalLayers'

            if 'substrate' in element.attrib:
                material = materials_lookup[element.attrib.pop('substrate')]
                etree.SubElement(element, 'substrate', {'material': material})

            thicknesses_lookup = {}
            for subelement in element.findall('bodies/*'):
                thicknesses_lookup[subelement.get('index')] = subelement.get('thickness')

            subelement = etree.SubElement(element, 'layers')

            for layer in element.get('layers').split(','):
                etree.SubElement(subelement, layer,
                                 {'material': materials_lookup[layer],
                                  'thickness': thicknesses_lookup[layer]})

        elif element.tag == '{http://pymontecarlo.sf.net}grainBoundaries' or \
                element.tag == '':
            element.tag = '{http://pymontecarlo.sf.net}verticalLayers'

            depth = element.get('thickness', str(float('inf')))

            material = materials_lookup[element.attrib.pop('left_substrate')]
            etree.SubElement(element, 'leftSubstrate',
                             {'material': material, 'depth': depth})

            material = materials_lookup[element.attrib.pop('right_substrate')]
            etree.SubElement(element, 'rightSubstrate',
                             {'material': material, 'depth': depth})

            thicknesses_lookup = {}
            for subelement in element.findall('bodies/*'):
                thicknesses_lookup[subelement.get('index')] = subelement.get('thickness')

            subelement = etree.SubElement(element, 'layers')

            for layer in element.get('layers').split(','):
                etree.SubElement(subelement, layer,
                                 {'material': materials_lookup[layer],
                                  'thickness': thicknesses_lookup[layer],
                                  'depth': depth})

        elif element.tag == '{http://pymontecarlo.sf.net}sphere':
            material = materials_lookup[element.attrib.pop('substrate')]
            diameter = element.attrib.pop('diameter')
            etree.SubElement(element, 'body',
                             {'material': material, 'diameter': diameter})

        else:
            raise ValueError('Unknown geometry to update: %s' % element.tag)

        element.remove(element.find('bodies'))

        # Detectors
        for element in root.findall('detectors/*'):
            if 'elevation_min' in element.attrib and \
                    'elevation_max' in element.attrib:
                lower = element.attrib.pop('elevation_min')
                upper = element.attrib.pop('elevation_max')
                etree.SubElement(element, 'elevation',
                                 {'lower': min(lower, upper),
                                  'upper': max(lower, upper)})

            if 'azimuth_min' in element.attrib and \
                    'azimuth_max' in element.attrib:
                lower = element.attrib.pop('azimuth_min')
                upper = element.attrib.pop('azimuth_max')
                etree.SubElement(element, 'azimuth',
                                 {'lower': min(lower, upper),
                                  'upper': max(lower, upper)})

            if 'channels' in element.attrib:
                subelement = etree.SubElement(element, 'channels')
                subelement.text = element.attrib.pop('channels')

            if 'xlimit_min' in element.attrib and \
                    'xlimit_max' in element.attrib:
                lower = element.attrib.pop('xlimit_min')
                upper = element.attrib.pop('xlimit_max')
                etree.SubElement(element, 'xlimits',
                                 {'lower': min(lower, upper),
                                  'upper': max(lower, upper)})

            if 'ylimit_min' in element.attrib and \
                    'ylimit_max' in element.attrib:
                lower = element.attrib.pop('ylimit_min')
                upper = element.attrib.pop('ylimit_max')
                etree.SubElement(element, 'ylimits',
                                 {'lower': min(lower, upper),
                                  'upper': max(lower, upper)})

            if 'zlimit_min' in element.attrib and \
                    'zlimit_max' in element.attrib:
                lower = element.attrib.pop('zlimit_min')
                upper = element.attrib.pop('zlimit_max')
                etree.SubElement(element, 'zlimits',
                                 {'lower': min(lower, upper),
                                  'upper': max(lower, upper)})

            if 'limit_min' in element.attrib and \
                    'limit_max' in element.attrib:
                lower = element.attrib.pop('limit_min')
                upper = element.attrib.pop('limit_max')
                etree.SubElement(element, 'limits',
                                 {'lower': min(lower, upper),
                                  'upper': max(lower, upper)})

            if 'secondary' in element.attrib:
                subelement = etree.SubElement(element, 'secondary')
                subelement.text = element.attrib.pop('secondary')

        with open(filepath, 'wb') as fp:
            fp.write(xmlutil.tostring(root, pretty_print=True))

        return self._update_version6(filepath)

    def _update_version6(self, filepath):
        logging.info('Nothing to update')
        return filepath
