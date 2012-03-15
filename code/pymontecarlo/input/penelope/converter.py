#!/usr/bin/env python
"""
================================================================================
:mod:`converter` -- PENELOPE conversion from base options
================================================================================

.. module:: converter
   :synopsis: PENELOPE conversion from base options

.. inheritance-diagram:: pymontecarlo.input.penelope.converter

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import warnings

# Third party modules.

# Local modules.
from pymontecarlo.input.base.converter import \
    Converter as _Converter, ConversionWarning, ConversionException

from pymontecarlo.input.penelope.material import Material
from pymontecarlo.input.penelope.body import Body, Layer
from pymontecarlo.input.base.beam import GaussianBeam, PencilBeam
from pymontecarlo.input.base.geometry import \
    Substrate, MultiLayers, GrainBoundaries, Inclusion
from pymontecarlo.input.base.limit import TimeLimit, ShowersLimit, UncertaintyLimit
from pymontecarlo.input.base.detector import \
    (
#     BackscatteredElectronAzimuthalAngularDetector,
#     BackscatteredElectronEnergyDetector,
#     BackscatteredElectronPolarAngularDetector,
#     EnergyDepositedSpatialDetector,
#     PhiRhoZDetector,
#     PhotonAzimuthalAngularDetector,
     PhotonIntensityDetector,
#     PhotonPolarAngularDetector,
     PhotonSpectrumDetector,
#     TransmittedElectronAzimuthalAngularDetector,
#     TransmittedElectronEnergyDetector,
#     TransmittedElectronPolarAngularDetector
     ElectronFractionDetector,
     TimeDetector,
     )
from pymontecarlo.input.base.model import \
    (ELASTIC_CROSS_SECTION, INELASTIC_CROSS_SECTION, IONIZATION_CROSS_SECTION,
     BREMSSTRAHLUNG_EMISSION, PHOTON_SCATTERING_CROSS_SECTION,
     MASS_ABSORPTION_COEFFICIENT)

# Globals and constants variables.

class Converter(_Converter):
    BEAMS = [GaussianBeam]
    GEOMETRIES = [Substrate, MultiLayers, GrainBoundaries, Inclusion]
    DETECTORS = [
#                 BackscatteredElectronAzimuthalAngularDetector,
#                 BackscatteredElectronEnergyDetector,
#                 BackscatteredElectronPolarAngularDetector,
#                 EnergyDepositedSpatialDetector,
#                 PhiRhoZDetector,
#                 PhotonAzimuthalAngularDetector,
#                 PhotonPolarAngularDetector,
                 PhotonSpectrumDetector,
#                 TransmittedElectronAzimuthalAngularDetector,
#                 TransmittedElectronEnergyDetector,
#                 TransmittedElectronPolarAngularDetector,
                 ElectronFractionDetector,
                 TimeDetector,
                 ]
    LIMITS = [TimeLimit, ShowersLimit, UncertaintyLimit]
    MODELS = {ELASTIC_CROSS_SECTION.type: [ELASTIC_CROSS_SECTION.elsepa2005],
              INELASTIC_CROSS_SECTION.type: [INELASTIC_CROSS_SECTION.sternheimer_liljequist1952],
              IONIZATION_CROSS_SECTION.type: [IONIZATION_CROSS_SECTION.bote_salvat2008],
              BREMSSTRAHLUNG_EMISSION.type: [BREMSSTRAHLUNG_EMISSION.seltzer_berger1985],
              PHOTON_SCATTERING_CROSS_SECTION.type: [PHOTON_SCATTERING_CROSS_SECTION.brusa1996],
              MASS_ABSORPTION_COEFFICIENT.type: [MASS_ABSORPTION_COEFFICIENT.llnl1989]}
    DEFAULT_MODELS = {ELASTIC_CROSS_SECTION.type: ELASTIC_CROSS_SECTION.elsepa2005,
                      INELASTIC_CROSS_SECTION.type: INELASTIC_CROSS_SECTION.sternheimer_liljequist1952,
                      IONIZATION_CROSS_SECTION.type: IONIZATION_CROSS_SECTION.bote_salvat2008,
                      BREMSSTRAHLUNG_EMISSION.type: BREMSSTRAHLUNG_EMISSION.seltzer_berger1985,
                      PHOTON_SCATTERING_CROSS_SECTION.type: PHOTON_SCATTERING_CROSS_SECTION.brusa1996,
                      MASS_ABSORPTION_COEFFICIENT.type: MASS_ABSORPTION_COEFFICIENT.llnl1989}


    def __init__(self, elastic_scattering=(0.0, 0.0),
                 cutoff_energy_inelastic=50.0,
                 cutoff_energy_bremsstrahlung=50.0):
        """
        Converter from base options to PENELOPE options.
        
        During the conversion, the materials are converted to :class:`PenelopeMaterial`. 
        For this, the specified elastic scattering and cutoff energies are used
        as the default values in the conversion.
        """
        _Converter.__init__(self)

        self._elastic_scattering = elastic_scattering
        self._cutoff_energy_inelastic_eV = cutoff_energy_inelastic
        self._cutoff_energy_bremsstrahlung_eV = cutoff_energy_bremsstrahlung

    def _convert_beam(self, options):
        try:
            _Converter._convert_beam(self, options)
        except ConversionException as ex:
            if isinstance(options.beam, PencilBeam):
                old = options.beam
                options.beam = GaussianBeam(old.energy_eV, 0.0, old.origin_m,
                                            old.direction, old.aperture_rad)

                message = "Pencil beam converted to Gaussian beam with 0 m diameter"
                warnings.warn(message, ConversionWarning)
            else:
                raise ex

    def _convert_geometry(self, options):
        _Converter._convert_geometry(self, options)

        geometry = options.geometry

        materials_lookup = self._create_penelope_materials(geometry.get_materials())

        if isinstance(geometry, Substrate):
            geometry._props['body'] = \
                self._create_penelope_body(geometry.body, materials_lookup)

        elif isinstance(geometry, Inclusion):
            geometry._props['substrate'] = \
                self._create_penelope_body(geometry.substrate_body, materials_lookup)
            geometry._props['inclusion'] = \
                self._create_penelope_body(geometry.inclusion_body, materials_lookup)

        elif isinstance(geometry, MultiLayers):
            if geometry.has_substrate():
                geometry._props['substrate'] = \
                    self._create_penelope_body(geometry.substrate_body, materials_lookup)

            newlayers = \
                self._create_penelope_layers(geometry.layers, materials_lookup)
            geometry.clear()
            geometry.layers.extend(newlayers)

        elif isinstance(geometry, GrainBoundaries):
            geometry._props['left'] = \
                self._create_penelope_body(geometry.left_body, materials_lookup)
            geometry._props['right'] = \
                self._create_penelope_body(geometry.right_body, materials_lookup)

            newlayers = \
                self._create_penelope_layers(geometry.layers, materials_lookup)
            geometry.clear()
            geometry.layers.extend(newlayers)
        else:
            raise ConversionException, "Cannot convert geometry"

    def _create_penelope_materials(self, oldmaterials):
        materials_lookup = {}

        for oldmaterial in oldmaterials:
            materials_lookup[oldmaterial] = self._create_penelope_material(oldmaterial)

        return materials_lookup

    def _create_penelope_material(self, old):
        if old.is_vacuum():
            return old

        return Material(old.name, old.composition, old.density_kg_m3,
                        old.absorption_energy_electron_eV, old.absorption_energy_photon_eV,
                        self._elastic_scattering,
                        self._cutoff_energy_inelastic_eV, self._cutoff_energy_bremsstrahlung_eV)

    def _create_penelope_body(self, old, materials_lookup):
        material = materials_lookup[old.material]
        return Body(material)

    def _create_penelope_layers(self, layers, materials_lookup):
        newlayers = []

        for layer in layers:
            material = materials_lookup[layer.material]

            # By default, the maximum step length in a layer is equal to 1/10 of 
            # the layer thickness
            maximum_step_length = layer.thickness_m / 10.0

            newlayers.append(Layer(material, layer.thickness_m, maximum_step_length))

        return newlayers

    def _convert_detectors(self, options):
        # Create PhotonSpectrumDetector for PhotonIntensityDetectors
        dets = options.detectors.findall(PhotonIntensityDetector)
        for key, det in dets.iteritems():
            newdet = PhotonSpectrumDetector(det.elevation_rad, det.azimuth_rad,
                                            (0.0, options.beam.energy_eV), 1000)
            options.detectors[key] = newdet

            message = "Replaced PhotonIntensityDetector (%s) with a PhotonSpectrumDetector" % key
            warnings.warn(message, ConversionWarning)

        # Superclass convert
        _Converter._convert_detectors(self, options)

        # Check that no photon detector have the same delimited limit
        dets = options.detectors.findall(PhotonSpectrumDetector)

        limits = {}
        for key, det in dets.iteritems():
            limit = det.elevation_rad + det.azimuth_rad

            for otherkey, otherlimit in limits.iteritems():
                if limit == otherlimit:
                    raise ConversionException, \
                        "Detector (%s) has the same opening as detector (%s)" % \
                            (key, otherkey)

            limits[key] = limit

    def _convert_limits(self, options):
        _Converter._convert_limits(self, options)

        if not options.limits:
            raise ConversionException, "At least one limit must be defined."

