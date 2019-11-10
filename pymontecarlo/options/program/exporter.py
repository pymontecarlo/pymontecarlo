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
from pymontecarlo.options.base import apply_lazy

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

    def _validate_program(self, program, options, erracc):
        pass

    def _validate_model(self, model, valid_models, erracc):
        if model not in valid_models:
            exc = ValueError("Model ({0}) is not supported.".format(model))
            erracc.add_exception(exc)

    def _export_beam(self, beam, options, erracc, *args, **kwargs):
        beam_class = beam.__class__
        if beam_class not in self.beam_export_methods:
            exc = ValueError("Beam ({0}) is not supported.".format(beam_class.__name__))
            erracc.add_exception(exc)
            return

        method = self.beam_export_methods[beam_class]
        method(beam, options, erracc, *args, **kwargs)

    def _validate_beam(self, beam, options, erracc):
        # Energy
        energy_eV = apply_lazy(beam.energy_eV, beam, options)

        if energy_eV <= 0.0:
            exc = ValueError(
                "Energy ({0:g} eV) must be greater than 0.0.".format(energy_eV)
            )
            erracc.add_exception(exc)

        # Particle
        particle = apply_lazy(beam.particle, beam, options)

        if not isinstance(particle, Particle):
            exc = ValueError("Unknown particle: {0}.".format(particle))
            erracc.add_exception(exc)

    def _validate_beam_pencil(self, beam, options, erracc):
        self._validate_beam(beam, options, erracc)

        # Position
        x0_m = apply_lazy(beam.x0_m, beam, options)

        if not math.isfinite(x0_m):
            exc = ValueError("Initial x position must be a finite number.")
            erracc.add_exception(exc)

        y0_m = apply_lazy(beam.y0_m, beam, options)

        if not math.isfinite(y0_m):
            exc = ValueError("Initial y position must be a finite number.")
            erracc.add_exception(exc)

    def _validate_beam_cylindrical(self, beam, options, erracc):
        self._validate_beam_pencil(beam, options, erracc)

        # Diameter
        diameter_m = apply_lazy(beam.diameter_m, beam, options)

        if diameter_m < 0.0:
            exc = ValueError(
                "Diameter ({0:g} m) must be greater or equal to 0.0.".format(diameter_m)
            )
            erracc.add_exception(exc)

    def _validate_beam_gaussian(self, beam, options, erracc):
        self._validate_beam_cylindrical(beam, options, erracc)

    def _validate_material(self, material, options, erracc):
        if material is VACUUM:
            return

        # Name
        name = apply_lazy(material.name, material, options).strip()

        if not name:
            exc = ValueError(
                "Name ({0:s}) must be at least one character.".format(name)
            )
            erracc.add_exception(exc)

        # Composition
        composition = apply_lazy(material.composition, material, options)

        for z, wf in composition.items():
            try:
                pyxray.descriptor.Element(z)
            except (ValueError, TypeError) as exc:
                erracc.add_exception(exc)

            if wf <= 0.0 or wf > 1.0:
                exc = ValueError("Weight fraction ({0:g}) must be between ]0.0, 1.0]")
                erracc.add_exception(exc)

        total = sum(composition.values())
        if not math.isclose(total, 1.0, abs_tol=Material.WEIGHT_FRACTION_TOLERANCE):
            exc = ValueError(
                "Total weight fraction ({0:g}) does not equal 1.0.".format(total)
            )
            erracc.add_exception(exc)

        # Density
        density_kg_per_m3 = apply_lazy(material.density_kg_per_m3, material, options)

        if density_kg_per_m3 <= 0:
            exc = ValueError(
                "Density ({0:g}kg/m3) must be greater or equal to 0.".format(
                    density_kg_per_m3
                )
            )
            erracc.add_exception(exc)

        # Color
        color = apply_lazy(material.color, material, options)

        if not matplotlib.colors.is_color_like(color):
            exc = ValueError("Color ({}) is not a valid color.".format(color))
            erracc.add_exception(exc)

    def _validate_layer(self, layer, options, erracc):
        # Material
        material = apply_lazy(layer.material, layer, options)

        self._validate_material(material, options, erracc)

        # Thickness
        thickness_m = apply_lazy(layer.thickness_m, layer, options)

        if thickness_m <= 0:
            exc = ValueError(
                "Thickness ({0:g} m) must be greater than 0.".format(thickness_m)
            )
            erracc.add_exception(exc)

    def _export_sample(self, sample, options, erracc, *args, **kwargs):
        sample_class = sample.__class__
        if sample_class not in self.sample_export_methods:
            exc = ValueError(
                "Sample ({0}) is not supported.".format(sample_class.__name__)
            )
            erracc.add_exception(exc)
            return

        method = self.sample_export_methods[sample_class]
        method(sample, options, erracc, *args, **kwargs)

    def _validate_sample(self, sample, options, erracc):
        # Tilt
        tilt_rad = apply_lazy(sample.tilt_rad, sample, options)

        if not math.isfinite(tilt_rad):
            exc = ValueError("Sample tilt must be a finite number.")
            erracc.add_exception(exc)

        # Azimuth
        azimuth_rad = apply_lazy(sample.azimuth_rad, sample, options)

        if not math.isfinite(azimuth_rad):
            exc = ValueError("Sample azimuth must be a finite number.")
            erracc.add_exception(exc)

    def _validate_sample_substrate(self, sample, options, erracc):
        self._validate_sample(sample, options, erracc)

        # Material
        material = apply_lazy(sample.material, sample, options)

        if material is VACUUM:
            exc = ValueError("Material cannot be VACUUM.")
            erracc.add_exception(exc)

        self._validate_material(material, options, erracc)

    def _validate_sample_inclusion(self, sample, options, erracc):
        self._validate_sample(sample, options, erracc)

        # Substrate material
        substrate_material = apply_lazy(sample.substrate_material, sample, options)

        if substrate_material is VACUUM:
            exc = ValueError("Substrate material cannot be VACUUM.")
            erracc.add_exception(exc)

        self._validate_material(substrate_material, options, erracc)

        # Inclusion material
        inclusion_material = apply_lazy(sample.inclusion_material, sample, options)

        if inclusion_material is VACUUM:
            exc = ValueError("Substrate material cannot be VACUUM.")
            erracc.add_exception(exc)

        self._validate_material(inclusion_material, options, erracc)

        # Inclusion diameter
        inclusion_diameter_m = apply_lazy(sample.inclusion_diameter_m, sample, options)

        if inclusion_diameter_m <= 0:
            exc = ValueError(
                "Diameter ({0:g} m) must be greater than 0.".format(
                    inclusion_diameter_m
                )
            )
            erracc.add_exception(exc)

    def _validate_sample_horizontallayers(self, sample, options, erracc):
        self._validate_sample(sample, options, erracc)

        # Layers
        layers = apply_lazy(sample.layers, sample, options)

        for layer in layers:
            self._validate_layer(layer, options, erracc)

        # Substrate material
        substrate_material = apply_lazy(sample.substrate_material, sample, options)

        self._validate_material(substrate_material, options, erracc)

    def _validate_sample_verticallayers(self, sample, options, erracc):
        self._validate_sample(sample, options, erracc)

        # Left material
        left_material = apply_lazy(sample.left_material, sample, options)

        if left_material is VACUUM:
            exc = ValueError("Left material cannot be VACUUM.")
            erracc.add_exception(exc)

        self._validate_material(left_material, options, erracc)

        # Layers
        layers = apply_lazy(sample.layers, sample, options)

        for layer in layers:
            self._validate_layer(layer, options, erracc)

        # Right material
        right_material = apply_lazy(sample.right_material, sample, options)

        if right_material is VACUUM:
            exc = ValueError("Right material cannot be VACUUM.")
            erracc.add_exception(exc)

        self._validate_material(right_material, options, erracc)

    def _validate_sample_sphere(self, sample, options, erracc):
        self._validate_sample(sample, options, erracc)

        # Material
        material = apply_lazy(sample.material, sample, options)

        if material is VACUUM:
            exc = ValueError("Material cannot be VACUUM.")
            erracc.add_exception(exc)

        self._validate_material(material, options, erracc)

        # Diameter
        diameter_m = apply_lazy(sample.diameter_m, sample, options)

        if diameter_m <= 0:
            exc = ValueError(
                "Diameter ({0:g} m) must be greater than 0.".format(diameter_m)
            )
            erracc.add_exception(exc)

    def _export_detectors(self, detectors, options, erracc, *args, **kwargs):
        for detector in detectors:
            self._export_detector(detector, options, erracc, *args, **kwargs)

    def _export_detector(self, detector, options, erracc, *args, **kwargs):
        detector_class = detector.__class__
        if detector_class not in self.detector_export_methods:
            exc = ValueError(
                "Detector ({0}) is not supported.".format(detector_class.__name__)
            )
            erracc.add_exception(exc)
            return

        method = self.detector_export_methods[detector_class]
        method(detector, options, erracc, *args, **kwargs)

    def _validate_detector(self, detector, options, erracc):
        # Name
        name = apply_lazy(detector.name, detector, options).strip()

        if not name:
            exc = ValueError(
                "Detector name ({0:s}) must be at least one character.".format(name)
            )
            erracc.add_exception(exc)

    def _validate_detector_photon(self, detector, options, erracc):
        self._validate_detector(detector, options, erracc)

        # Elevation
        elevation_rad = apply_lazy(detector.elevation_rad, detector, options)

        if elevation_rad < -math.pi / 2 or elevation_rad > math.pi / 2:
            exc = ValueError(
                "Elevation ({0:g} rad) must be between [-pi/2,pi/2].".format(
                    elevation_rad
                )
            )
            erracc.add_exception(exc)

        # Azimuth
        azimuth_rad = apply_lazy(detector.azimuth_rad, detector, options)

        if azimuth_rad < 0 or azimuth_rad >= 2 * math.pi:
            exc = ValueError(
                "Azimuth ({0:g} rad) must be between [0, 2pi[.".format(azimuth_rad)
            )
            erracc.add_exception(exc)

    def _export_analyses(self, analyses, options, erracc, *args, **kwargs):
        for analysis in analyses:
            self._export_analysis(analysis, options, erracc, *args, **kwargs)

    def _export_analysis(self, analysis, options, erracc, *args, **kwargs):
        analysis_class = analysis.__class__
        if analysis_class not in self.analysis_export_methods:
            exc = ValueError(
                "Analysis ({0}) is not supported.".format(analysis_class.__name__)
            )
            erracc.add_exception(exc)
            return

        method = self.analysis_export_methods[analysis_class]
        method(analysis, options, erracc, *args, **kwargs)

    def _validate_analysis_photonintensity(self, analysis, options, erracc):
        pass

    def _validate_analysis_kratio(self, analysis, options, erracc):
        standard_materials = apply_lazy(analysis.standard_materials, analysis, options)

        for z, material in standard_materials.items():
            self._validate_material(material, options, erracc)

            if z not in material.composition:
                exc = ValueError(
                    "Standard for element {0} does not have this element in its composition".format(
                        pyxray.element_symbol(z)
                    )
                )
                erracc.add_exception(exc)
