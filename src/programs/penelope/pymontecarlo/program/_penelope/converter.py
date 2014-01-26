#!/usr/bin/env python
"""
================================================================================
:mod:`converter` -- Base options conversion for all PENELOPE main programs
================================================================================

.. module:: converter
   :synopsis: Base options conversion for all PENELOPE main programs

.. inheritance-diagram:: pymontecarlo.program._penelope.options.converter

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
from pymontecarlo.program.converter import Converter as _Converter
from pymontecarlo.options.geometry import \
    Substrate, HorizontalLayers, VerticalLayers, Inclusion, Sphere #, Cuboids2D
from pymontecarlo.options.model import \
    (ELASTIC_CROSS_SECTION, INELASTIC_CROSS_SECTION, IONIZATION_CROSS_SECTION,
     BREMSSTRAHLUNG_EMISSION, PHOTON_SCATTERING_CROSS_SECTION,
     MASS_ABSORPTION_COEFFICIENT)
from pymontecarlo.options.helper import replace_material

from pymontecarlo.program._penelope.options.material import Material

# Globals and constants variables.

class Converter(_Converter):
    GEOMETRIES = [Substrate, HorizontalLayers, VerticalLayers, Inclusion, Sphere] #, Cuboids2D]
    MODELS = {ELASTIC_CROSS_SECTION: [ELASTIC_CROSS_SECTION.elsepa2005],
              INELASTIC_CROSS_SECTION: [INELASTIC_CROSS_SECTION.sternheimer_liljequist1952],
              IONIZATION_CROSS_SECTION: [IONIZATION_CROSS_SECTION.bote_salvat2008],
              BREMSSTRAHLUNG_EMISSION: [BREMSSTRAHLUNG_EMISSION.seltzer_berger1985],
              PHOTON_SCATTERING_CROSS_SECTION: [PHOTON_SCATTERING_CROSS_SECTION.brusa1996],
              MASS_ABSORPTION_COEFFICIENT: [MASS_ABSORPTION_COEFFICIENT.llnl1989]}
    DEFAULT_MODELS = {ELASTIC_CROSS_SECTION: ELASTIC_CROSS_SECTION.elsepa2005,
                      INELASTIC_CROSS_SECTION: INELASTIC_CROSS_SECTION.sternheimer_liljequist1952,
                      IONIZATION_CROSS_SECTION: IONIZATION_CROSS_SECTION.bote_salvat2008,
                      BREMSSTRAHLUNG_EMISSION: BREMSSTRAHLUNG_EMISSION.seltzer_berger1985,
                      PHOTON_SCATTERING_CROSS_SECTION: PHOTON_SCATTERING_CROSS_SECTION.brusa1996,
                      MASS_ABSORPTION_COEFFICIENT: MASS_ABSORPTION_COEFFICIENT.llnl1989}


    def __init__(self, elastic_scattering=(0.0, 0.0),
                 cutoff_energy_inelastic=50.0,
                 cutoff_energy_bremsstrahlung=50.0,
                 interaction_forcings=None,
                 maximum_step_length_m=1e20):
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
        self._interaction_forcings = interaction_forcings or []
        self._maximum_step_length_m = maximum_step_length_m

    def _convert_geometry(self, options):
        if not _Converter._convert_geometry(self, options):
            return False

        # Replace material with PENLOPE material
        for old_material in options.geometry.get_materials():
            new_material = self._create_penelope_material(old_material)
            replace_material(options, old_material, new_material)

        return True

    def _create_penelope_material(self, old):
        # Do not convert PENELOPE material
        if isinstance(old, Material):
            return old

        mat = Material(old.composition, old.name, old.density_kg_m3, old.absorption_energy_eV,
                       self._elastic_scattering,
                       self._cutoff_energy_inelastic_eV,
                       self._cutoff_energy_bremsstrahlung_eV,
                       self._interaction_forcings, self._maximum_step_length_m)

        return mat

