""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.options import OptionsBuilder
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import SubstrateSample
from pymontecarlo.options.analyses.base import Analysis
from pymontecarlo.options.analyses.photonintensity import PhotonIntensityAnalysis
from pymontecarlo.util.cbook import are_mapping_equal

# Globals and constants variables.

class KRatioAnalysis(Analysis):

    DEFAULT_NONPURE_STANDARD_MATERIALS = \
        {7: Material.from_formula('BN', 2.1e3),
         8: Material.from_formula('Al2O3', 3.95e3),
         9: Material.from_formula('BaF2', 4.89e3),
         17: Material.from_formula('KCl', 1.98e3),
         36: Material.from_formula('KBr', 2.75e3),
         80: Material.from_formula('HgTe', 8.1e3)}

    def __init__(self):
        self.standard_materials = {}

    def __eq__(self, other):
        return super().__eq__(other) and \
            are_mapping_equal(self.standard_materials, other.standard_materials)

    def add_standard_material(self, z, material):
        self.standard_materials[z] = material

    def get_standard_material(self, z):
        if z in self.standard_materials:
            return self.standard_materials[z]

        if z in self.DEFAULT_NONPURE_STANDARD_MATERIALS:
            return self.DEFAULT_NONPURE_STANDARD_MATERIALS[z]

        return Material.pure(z)

    def apply(self, options):
        # Construct standard options
        builder = OptionsBuilder()

        builder.add_program(options.program)

        beam = GaussianBeam(energy_eV=options.beam.energy_eV,
                            diameter_m=0.0,
                            particle=options.beam.particle)
        builder.add_beam(beam)

        for material in options.sample.materials:
            for z in material.composition:
                standard = self.get_standard_material(z)
                builder.add_sample(SubstrateSample(standard))

        for detector in options.detectors:
            builder.add_detector(detector)

        for limit in options.limits:
            builder.add_limit(options.program, limit)

        for model in options.models:
            builder.add_model(model)

        analysis = PhotonIntensityAnalysis()
        builder.add_analysis(analysis)

        return super().apply(options) + builder.build()

    def calculate(self, simulations):
        pass

