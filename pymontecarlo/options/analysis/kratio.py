""""""

__all__ = ["KRatioAnalysis", "KRatioAnalysisBuilder"]

# Standard library modules.
import logging
import copy

# Third party modules.
import h5py
import numpy as np
import pyxray
import more_itertools

# Local modules.
from pymontecarlo.options.options import OptionsBuilder
from pymontecarlo.options.beam import PencilBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import SubstrateSample
from pymontecarlo.options.analysis.photon import (
    PhotonAnalysisBase,
    PhotonAnalysisBuilderBase,
)
from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysis
from pymontecarlo.results.photonintensity import EmittedPhotonIntensityResult
from pymontecarlo.results.kratio import KRatioResult, KRatioResultBuilder
import pymontecarlo.options.base as base

# Globals and constants variables.
logger = logging.getLogger(__name__)

TAG_STANDARD = "standard"


class KRatioAnalysis(PhotonAnalysisBase):

    DEFAULT_NONPURE_STANDARD_MATERIALS = {
        7: Material.from_formula("BN", 2.1e3),
        8: Material.from_formula("Al2O3", 3.95e3),
        9: Material.from_formula("BaF2", 4.89e3),
        17: Material.from_formula("KCl", 1.98e3),
        36: Material.from_formula("KBr", 2.75e3),
        80: Material.from_formula("HgTe", 8.1e3),
    }

    def __init__(self, photon_detector, standard_materials=None):
        super().__init__(photon_detector)

        if standard_materials is None:
            standard_materials = {}
        self.standard_materials = standard_materials.copy()

    def __eq__(self, other):
        return super().__eq__(other) and base.are_mapping_equal(
            self.standard_materials, other.standard_materials
        )

    def add_standard_material(self, z, material):
        self.standard_materials[z] = material

    def get_standard_material(self, z):
        if z in self.standard_materials:
            return self.standard_materials[z]

        if z in self.DEFAULT_NONPURE_STANDARD_MATERIALS:
            return self.DEFAULT_NONPURE_STANDARD_MATERIALS[z]

        return Material.pure(z)

    def _create_standard_options(self, options):
        builder = OptionsBuilder(tags=[TAG_STANDARD])

        program = copy.copy(options.program)
        builder.add_program(program)

        beam = PencilBeam(
            energy_eV=options.beam.energy_eV, particle=options.beam.particle
        )
        builder.add_beam(beam)

        for material in options.sample.materials:
            for z in material.composition:
                standard = self.get_standard_material(z)
                builder.add_sample(SubstrateSample(standard))

        analysis = PhotonIntensityAnalysis(self.photon_detector)
        builder.add_analysis(analysis)

        return builder.build()

    def apply(self, options):
        analysis = PhotonIntensityAnalysis(self.photon_detector)

        # Add photon analysis to options if missing
        if analysis not in options.analyses:
            options.analyses.append(analysis)

        # Construct standard options
        standard_options = self._create_standard_options(options)

        return super().apply(options) + standard_options

    def calculate(self, simulation, simulations):
        # If k-ratio result exists, return False, no new result
        for kratioresult in simulation.find_result(KRatioResult):
            if kratioresult.analysis == self:
                logger.debug("KRatioResult already calculated")
                return False

        # Find emitted photon intensity result(s)
        it = (
            r
            for r in simulation.find_result(EmittedPhotonIntensityResult)
            if r.analysis.photon_detector == self.photon_detector
        )
        unkresult = more_itertools.first(it, None)

        # If no result, return False, no new result
        if unkresult is None:
            return False

        # Find standard simulations
        stdoptions = self._create_standard_options(simulation.options)
        stdsimulations = [s for s in simulations if s.options in stdoptions]

        # Build cache of standard result
        stdresult_cache = {}
        for xrayline in unkresult:
            z = xrayline.atomic_number

            if z in stdresult_cache:
                continue

            stdmaterial = self.get_standard_material(z)
            it = (s for s in stdsimulations if s.options.sample.material == stdmaterial)
            stdsimulation = more_itertools.first(it, None)
            if stdsimulation is None:
                logger.debug("No standard simulation found for Z={}".format(z))
                stdresult_cache[z] = None
                continue

            it = (
                r
                for r in stdsimulation.find_result(EmittedPhotonIntensityResult)
                if r.analysis.photon_detector == self.photon_detector
            )
            stdresult = more_itertools.first(it, None)
            if stdresult is None:
                logger.debug("No standard result found for Z={}".format(z))
                stdresult_cache[z] = None
                continue

            stdresult_cache[z] = stdresult

        # Calculate k-ratios
        builder = KRatioResultBuilder(self)

        for xrayline, unkintensity in unkresult.items():
            z = xrayline.atomic_number

            stdresult = stdresult_cache.get(z)
            if stdresult is None:
                continue

            stdintensity = stdresult.get(xrayline, None)
            if stdintensity is None:
                logger.debug("No standard intensity for {}".format(xrayline))
                continue

            builder.add_kratio(xrayline, unkintensity, stdintensity)

        # Create result
        newresult = super().calculate(simulation, simulations)

        if builder.data:
            simulation.results.append(builder.build())
            newresult = True

        return newresult

    # region HDF5

    DATASET_ATOMIC_NUMBER = "atomic number"
    DATASET_STANDARDS = "standards"

    @classmethod
    def parse_hdf5(cls, group):
        detector = cls._parse_hdf5(group, cls.ATTR_DETECTOR)
        standard_materials = cls._parse_hdf5_standard_materials(group)
        return cls(detector, standard_materials)

    @classmethod
    def _parse_hdf5_standard_materials(cls, group):
        ds_z = group[cls.DATASET_ATOMIC_NUMBER]
        ds_standard = group[cls.DATASET_STANDARDS]
        return dict(
            (z, cls._parse_hdf5_reference(group, reference))
            for z, reference in zip(ds_z, ds_standard)
        )

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5_standard_materials(group, self.standard_materials)

    def _convert_hdf5_standard_materials(self, group, standard_materials):
        shape = (len(standard_materials),)
        ref_dtype = h5py.special_dtype(ref=h5py.Reference)
        ds_z = group.create_dataset(
            self.DATASET_ATOMIC_NUMBER, shape=shape, dtype=np.byte
        )
        ds_standard = group.create_dataset(
            self.DATASET_STANDARDS, shape=shape, dtype=ref_dtype
        )

        ds_z.make_scale()
        ds_standard.dims[0].label = self.DATASET_ATOMIC_NUMBER
        ds_standard.dims[0].attach_scale(ds_z)

        for i, (z, material) in enumerate(standard_materials.items()):
            ds_z[i] = z
            ds_standard[i] = self._convert_hdf5_reference(group, material)

    # endregion

    # region Document

    TABLE_STANDARD = "standard"

    def convert_document(self, builder):
        super().convert_document(builder)

        # Standards
        section = builder.add_section()
        section.add_title("Standard(s)")

        if self.standard_materials:
            table = section.require_table(self.TABLE_STANDARD)

            table.add_column("Element")
            table.add_column("Material")

            for z, material in self.standard_materials.items():
                row = {"Element": pyxray.element_symbol(z), "Material": material.name}
                table.add_row(row)

            section = builder.add_section()
            section.add_title("Materials")

            for material in self.standard_materials.values():
                section.add_entity(material)

        else:
            section.add_text("No standard defined")


# endregion


class KRatioAnalysisBuilder(PhotonAnalysisBuilderBase):
    def build(self):
        return [KRatioAnalysis(d) for d in self.photon_detectors]
