"""
Base class for exporters
"""

# Standard library modules.
import abc
import math

# Third party modules.
import pyxray
import matplotlib.colors

# Local modules.
from pymontecarlo.exceptions import ExportError, ExportWarning
from pymontecarlo.util.error import ErrorAccumulator
from pymontecarlo.options import Material, VACUUM, Particle
from pymontecarlo.options.composition import calculate_density_kg_per_m3

# Globals and constants variables.

class ExporterBase(metaclass=abc.ABCMeta):
    """
    Base class for all exporters.
    """

    def __init__(self):
        self.beam_export_methods = {}
        self.sample_export_methods = {}
        self.detector_export_methods = {}
        self.analysis_export_methods = {}

    async def export(self, options, dirpath, dry_run=False):
        """
        Exports options to the specified output directory.
        
        Args:
            options (Options): options to export
            dirpath (str): full path to output directory
            dry_run: if true no file is written on disk
        """
        with ErrorAccumulator(ExportWarning, ExportError) as erracc:
            await self._export(options, dirpath, erracc, dry_run)

    @abc.abstractmethod
    async def _export(self, options, dirpath, erracc, dry_run=False):
        """
        Performs the actual export.
        
        :arg options: options to export
        :arg dirpath: full path to output directory
        :arg erracc: error accumulator
        """
        raise NotImplementedError

    def _run_exporters(self, options, erracc, *args, **kwargs):
        """
        Internal command to call the register export functions. 
        All optional arguments passed to this method are transferred to the
        export methods.
        """
        self._export_program(options.program, options, erracc, *args, **kwargs)
        self._export_beam(options.beam, options, erracc, *args, **kwargs)
        self._export_sample(options.sample, options, erracc, *args, **kwargs)
        self._export_detectors(options.detectors, options, erracc, *args, **kwargs)
        self._export_analyses(options.analyses, options, erracc, *args, **kwargs)

    @abc.abstractmethod
    def _export_program(self, program, options, erracc, *args, **kwargs):
        raise NotImplementedError

    def _export_model(self, model, valid_models, erracc, *args, **kwargs):
        if model not in valid_models:
            exc = ValueError('Model ({0}) is not supported.'.format(model))
            erracc.add_exception(exc)

    def _export_beam(self, beam, options, erracc, *args, **kwargs):
        beam_class = beam.__class__
        if beam_class not in self.beam_export_methods:
            exc = ValueError('Beam ({0}) is not supported.'
                             .format(beam_class.__name__))
            erracc.add_exception(exc)
            return

        method = self.beam_export_methods[beam_class]
        method(beam, options, erracc, *args, **kwargs)

    def _export_beam_cylindrical(self, beam, options, erracc, *args, **kwargs):
        # Energy
        energy_eV = beam.energy_eV

        if energy_eV <= 0.0:
            exc = ValueError('Energy ({0:g} eV) must be greater than 0.0.'
                             .format(energy_eV))
            erracc.add_exception(exc)

        # Particle
        particle = beam.particle
        if not isinstance(particle, Particle):
            exc = ValueError('Unknown particle: {0}.'.format(particle))
            erracc.add_exception(exc)

        # Diameter
        diameter_m = beam.diameter_m

        if diameter_m < 0.0:
            exc = ValueError('Diameter ({0:g} m) must be greater or equal to 0.0.'
                             .format(diameter_m))
            erracc.add_exception(exc)

        # Position
        if not math.isfinite(beam.x0_m):
            exc = ValueError('Initial x position must be a finite number.')
            erracc.add_exception(exc)

        if not math.isfinite(beam.y0_m):
            exc = ValueError('Initial y position must be a finite number.')
            erracc.add_exception(exc)

    def _export_beam_gaussian(self, beam, options, erracc, *args, **kwargs):
        # Energy
        energy_eV = beam.energy_eV

        if energy_eV <= 0.0:
            exc = ValueError('Energy ({0:g} eV) must be greater than 0.0.'
                             .format(energy_eV))
            erracc.add_exception(exc)

        # Particle
        particle = beam.particle
        if not isinstance(particle, Particle):
            exc = ValueError('Unknown particle: {0}.'.format(particle))
            erracc.add_exception(exc)

        # Diameter
        diameter_m = beam.diameter_m

        if diameter_m < 0.0:
            exc = ValueError('Diameter ({0:g} m) must be greater or equal to 0.0.'
                             .format(diameter_m))
            erracc.add_exception(exc)

        # Position
        if not math.isfinite(beam.x0_m):
            exc = ValueError('Initial x position must be a finite number.')
            erracc.add_exception(exc)

        if not math.isfinite(beam.y0_m):
            exc = ValueError('Initial y position must be a finite number.')
            erracc.add_exception(exc)

    def _export_material(self, material, options, erracc, *args, **kwargs):
        if material is VACUUM:
            return

        # Name
        name = material.name.strip()
        if not name:
            exc = ValueError('Name ({0:s}) must be at least one character.'
                             .format(name))
            erracc.add_exception(exc)

        # Composition
        for z, wf in material.composition.items():
            try:
                pyxray.descriptor.Element.validate(z)
            except (ValueError, TypeError) as exc:
                erracc.add_exception(exc)

            if wf <= 0.0 or wf > 1.0:
                exc = ValueError('Weight fraction ({0:g}) must be between ]0.0, 1.0]')
                erracc.add_exception(exc)

        total = sum(material.composition.values())
        if not math.isclose(total, 1.0, abs_tol=Material.WEIGHT_FRACTION_TOLERANCE):
            exc = ValueError('Total weight fraction ({0:g}) does not equal 1.0.'
                             .format(total))
            erracc.add_exception(exc)

        # Density
        if material.density_kg_per_m3 is None:
            material.density_kg_per_m3 = calculate_density_kg_per_m3(material.composition)
            warning = RuntimeWarning('Density for {} was calculated as {:g}kg/m3'
                                     .format(material.name, material.density_kg_per_m3))
            erracc.add_warning(warning)

        if material.density_kg_per_m3 <= 0:
            exc = ValueError('Density ({0:g}kg/m3) must be greater or equal to 0.'
                             .format(material.density_kg_per_m3))
            erracc.add_exception(exc)

        # Color
        if not matplotlib.colors.is_color_like(material.color):
            exc = ValueError('Color ({}) is not a valid color.'
                             .format(material.color))
            erracc.add_exception(exc)

    def _export_layer(self, layer, options, erracc, *args, **kwargs):
        self._export_material(layer.material, options, erracc, *args, **kwargs)

        if layer.thickness_m <= 0:
            exc = ValueError('Thickness ({0:g} m) must be greater than 0.'
                             .format(layer.thickness_m))
            erracc.add_exception(exc)

    def _export_sample(self, sample, options, erracc, *args, **kwargs):
        sample_class = sample.__class__
        if sample_class not in self.sample_export_methods:
            exc = ValueError('Sample ({0}) is not supported.'
                             .format(sample_class.__name__))
            erracc.add_exception(exc)
            return

        if not math.isfinite(sample.tilt_rad):
            exc = ValueError('Sample tilt must be a finite number.')
            erracc.add_exception(exc)

        if not math.isfinite(sample.azimuth_rad):
            exc = ValueError('Sample azimuth must be a finite number.')
            erracc.add_exception(exc)

        method = self.sample_export_methods[sample_class]
        method(sample, options, erracc, *args, **kwargs)

    def _export_sample_substrate(self, sample, options, erracc, *args, **kwargs):
        if sample.material is VACUUM:
            exc = ValueError('Material cannot be VACUUM.')
            erracc.add_exception(exc)

    def _export_sample_inclusion(self, sample, options, erracc, *args, **kwargs):
        if sample.substrate_material is VACUUM:
            exc = ValueError('Substrate material cannot be VACUUM.')
            erracc.add_exception(exc)

        if sample.inclusion_material is VACUUM:
            exc = ValueError('Substrate material cannot be VACUUM.')
            erracc.add_exception(exc)

        if sample.inclusion_diameter_m <= 0:
            exc = ValueError('Diameter ({0:g} m) must be greater than 0.'
                             .format(sample.inclusion_diameter_m))
            erracc.add_exception(exc)

    def _export_sample_horizontallayers(self, sample, options, erracc, *args, **kwargs):
        pass

    def _export_sample_verticallayers(self, sample, options, erracc, *args, **kwargs):
        if sample.left_material is VACUUM:
            exc = ValueError('Left material cannot be VACUUM.')
            erracc.add_exception(exc)

        if sample.right_material is VACUUM:
            exc = ValueError('Right material cannot be VACUUM.')
            erracc.add_exception(exc)

    def _export_sample_sphere(self, sample, options, erracc, *args, **kwargs):
        if sample.material is VACUUM:
            exc = ValueError('Material cannot be VACUUM.')
            erracc.add_exception(exc)

        if sample.diameter_m <= 0:
            exc = ValueError('Diameter ({0:g} m) must be greater than 0.'
                             .format(sample.diameter_m))
            erracc.add_exception(exc)

    def _export_detectors(self, detectors, options, erracc, *args, **kwargs):
        for detector in detectors:
            self._export_detector(detector, options, erracc, *args, **kwargs)

    def _export_detector(self, detector, options, erracc, *args, **kwargs):
        detector_class = detector.__class__
        if detector_class not in self.detector_export_methods:
            exc = ValueError('Detector ({0}) is not supported.'
                             .format(detector_class.__name__))
            erracc.add_exception(exc)
            return

        name = detector.name.strip()
        if not name:
            exc = ValueError('Detector name ({0:s}) must be at least one character.'
                             .format(name))
            erracc.add_exception(exc)

        method = self.detector_export_methods[detector_class]
        method(detector, options, erracc, *args, **kwargs)

    def _export_detector_photon(self, detector, options, erracc, *args, **kwargs):
        # Elevation
        elevation_rad = detector.elevation_rad

        if elevation_rad < -math.pi / 2 or elevation_rad > math.pi / 2:
            exc = ValueError('Elevation ({0:g} rad) must be between [-pi/2,pi/2].'
                             .format(elevation_rad))
            erracc.add_exception(exc)

        # Azimuth
        azimuth_rad = detector.azimuth_rad

        if azimuth_rad < 0 or azimuth_rad >= 2 * math.pi:
            exc = ValueError('Azimuth ({0:g} rad) must be between [0, 2pi[.'
                             .format(azimuth_rad))
            erracc.add_exception(exc)

    def _export_analyses(self, analyses, options, erracc, *args, **kwargs):
        for analysis in analyses:
            self._export_analysis(analysis, options, erracc, *args, **kwargs)

    def _export_analysis(self, analysis, options, erracc, *args, **kwargs):
        analysis_class = analysis.__class__
        if analysis_class not in self.analysis_export_methods:
            exc = ValueError('Analysis ({0}) is not supported.'
                             .format(analysis_class.__name__))
            erracc.add_exception(exc)
            return

        method = self.analysis_export_methods[analysis_class]
        method(analysis, options, erracc, *args, **kwargs)

    def _export_analysis_photonintensity(self, analysis, options, erracc, *args, **kwargs):
        pass

    def _export_analysis_kratio(self, analysis, options, erracc, *args, **kwargs):
        for z, material in analysis.standard_materials.items():
            if z not in material.composition:
                exc = ValueError('Standard for element {0} does not have this element in its composition'
                                 .format(pyxray.element_symbol(z)))
                erracc.add_exception(exc)
