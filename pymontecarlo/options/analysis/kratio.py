""""""

# Standard library modules.
import logging
logger = logging.getLogger(__name__)

# Third party modules.

# Local modules.
from pymontecarlo.options.options import OptionsBuilder
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import SubstrateSample
from pymontecarlo.options.analysis.photon import PhotonAnalysis, PhotonAnalysisBuilder
from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysis
from pymontecarlo.results.photonintensity import EmittedPhotonIntensityResult
from pymontecarlo.results.kratio import KRatioResult, KRatioResultBuilder
from pymontecarlo.util.cbook import are_mapping_equal

# Globals and constants variables.

class KRatioAnalysis(PhotonAnalysis):

    DEFAULT_NONPURE_STANDARD_MATERIALS = \
        {7: Material.from_formula('BN', 2.1e3),
         8: Material.from_formula('Al2O3', 3.95e3),
         9: Material.from_formula('BaF2', 4.89e3),
         17: Material.from_formula('KCl', 1.98e3),
         36: Material.from_formula('KBr', 2.75e3),
         80: Material.from_formula('HgTe', 8.1e3)}

    def __init__(self, photon_detector, standard_materials=None):
        super().__init__(photon_detector)

        if standard_materials is None:
            standard_materials = {}
        self.standard_materials = standard_materials

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

    def _create_standard_options(self, options):
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

        for limit in options.limits:
            builder.add_limit(options.program, limit)

        for model in options.models:
            builder.add_model(options.program, model)

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
        stdoptions = self._create_standard_options(simulation.options)
        stdsimulations = [s for s in simulations if s.options in stdoptions]

        newresult = super().calculate(simulation, simulations)

        for unkresult in simulation.find_result(EmittedPhotonIntensityResult):
            if unkresult.analysis.photon_detector != self.photon_detector:
                continue

            # Check if KRatioResult already exists
            kratioresult = next((r for r in simulation.find_result(KRatioResult)
                                if r.analysis == self), None)
            if kratioresult is not None:
                if kratioresult.keys() == unkresult.keys():
                    logger.debug('KRatioResult already calculated')
                    continue

                simulation.results.remove(kratioresult)

            # Build cache of standard result
            stdresult_cache = {}
            for xrayline in unkresult:
                z = xrayline.atomic_number

                if z in stdresult_cache:
                    continue

                stdmaterial = self.get_standard_material(z)
                stdsimulation = \
                    next((s for s in stdsimulations
                          if s.options.sample.material == stdmaterial), None)
                if stdsimulation is None:
                    logger.debug('No standard simulation found for Z={}'.format(z))
                    stdresult_cache[z] = None
                    continue

                stdresult = \
                    next((r for r in stdsimulation.find_result(EmittedPhotonIntensityResult)
                         if r.analysis.photon_detector == self.photon_detector), None)
                if stdresult is None:
                    logger.debug('No standard result found for Z={}'.format(z))
                    stdresult_cache[z] = None
                    continue

                stdresult_cache[z] = stdresult

            # Calculate k-ratios
            builder = KRatioResultBuilder(unkresult.analysis)

            for xrayline, unkintensity in unkresult.items():
                z = xrayline.atomic_number

                stdresult = stdresult_cache.get(z)
                if stdresult is None:
                    continue

                stdintensity = stdresult.get(xrayline, None)
                if stdintensity is None:
                    logger.debug('No standard intensity for {}'.format(xrayline))
                    continue

                builder.add_kratio(xrayline, unkintensity, stdintensity)

            if builder.data:
                simulation.results.append(builder.build())
                newresult = True

        return newresult

class KRatioAnalysisBuilder(PhotonAnalysisBuilder):

    def build(self):
        return [KRatioAnalysis(d) for d in self.photon_detectors]






