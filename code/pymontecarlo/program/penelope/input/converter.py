#!/usr/bin/env python
"""
================================================================================
:mod:`converter` -- Base options conversion for all PENELOPE main programs
================================================================================

.. module:: converter
   :synopsis: Base options conversion for all PENELOPE main programs

.. inheritance-diagram:: pymontecarlo.program.penelope.input.converter

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.input.converter import \
    Converter as _Converter, ConversionException
from pymontecarlo.input.material import VACUUM
from pymontecarlo.input.geometry import \
    Substrate, MultiLayers, GrainBoundaries, Inclusion, Sphere, Cuboids2D
from pymontecarlo.input.model import \
    (ELASTIC_CROSS_SECTION, INELASTIC_CROSS_SECTION, IONIZATION_CROSS_SECTION,
     BREMSSTRAHLUNG_EMISSION, PHOTON_SCATTERING_CROSS_SECTION,
     MASS_ABSORPTION_COEFFICIENT)

from pymontecarlo.program.penelope.input.material import Material
from pymontecarlo.program.penelope.input.body import Body, Layer

# Globals and constants variables.

class Converter(_Converter):
    GEOMETRIES = [Substrate, MultiLayers, GrainBoundaries, Inclusion, Sphere, Cuboids2D]
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
        Converter from base options to PENEPMA options.
        
        During the conversion, the materials are converted to :class:`PenelopeMaterial`. 
        For this, the specified elastic scattering and cutoff energies are used
        as the default values in the conversion.
        """
        _Converter.__init__(self)

        self._elastic_scattering = elastic_scattering
        self._cutoff_energy_inelastic_eV = cutoff_energy_inelastic
        self._cutoff_energy_bremsstrahlung_eV = cutoff_energy_bremsstrahlung

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

        elif isinstance(geometry, Sphere):
            geometry._props['body'] = \
                self._create_penelope_body(geometry.body, materials_lookup)

        elif isinstance(geometry, Cuboids2D):
            for position, body in geometry._bodies.iteritems():
                geometry._bodies[position] = \
                    self._create_penelope_body(body, materials_lookup)

        else:
            raise ConversionException, "Cannot convert geometry"

    def _create_penelope_materials(self, oldmaterials):
        materials_lookup = {VACUUM: VACUUM}

        for oldmaterial in oldmaterials:
            materials_lookup[oldmaterial] = self._create_penelope_material(oldmaterial)

        return materials_lookup

    def _create_penelope_material(self, old):
        # Do not convert PENELOPE material
        if isinstance(old, Material):
            return old

        return Material(old.name, old.composition, old.density_kg_m3,
                        old.absorption_energy_electron_eV, old.absorption_energy_photon_eV,
                        self._elastic_scattering,
                        self._cutoff_energy_inelastic_eV, self._cutoff_energy_bremsstrahlung_eV)

    def _create_penelope_body(self, old, materials_lookup):
        # Do not convert PENELOPE body
        if isinstance(old, Body):
            return old

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
