#!/usr/bin/env python
"""
================================================================================
:mod:`exporter` -- Exporter to PENELOPE files
================================================================================

.. module:: exporter
   :synopsis: Exporter to PENELOPE files

.. inheritance-diagram:: pymontecarlo.input.penelope.exporter

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import math
from operator import attrgetter, mul
from itertools import tee, izip

# Third party modules.

# Local modules.
from pymontecarlo import settings
from pymontecarlo.input.base.geometry import \
    Substrate, Inclusion, MultiLayers, GrainBoundaries, Sphere
from pymontecarlo.input.penelope.geometry import \
    PenelopeGeometry, Module, xplane, zplane, cylinder, sphere
from pymontecarlo.input.base.detector import PhotonSpectrumDetector
from pymontecarlo.input.base.limit import ShowersLimit, TimeLimit, UncertaintyLimit
from pymontecarlo.io.base.exporter import Exporter as _Exporter, ExporterException
import pymontecarlo.lib.penelope.material as penmaterial
from pymontecarlo.input.base.material import VACUUM

# Globals and constants variables.

def _pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

class _Keyword(object):
    LINE_KEYWORDS_SIZE = 6
    LINE_SIZE = 80

    def __init__(self, name, comment=""):
        self._name = name
        self._comment = comment

    @property
    def name(self):
        return self._name

    @property
    def comment(self):
        return self._comment

    def create_line(self, text):
        """
        Creates an input line of this keyword from the specified text.
        The white space between the items is automatically adjusted to fit the
        line size.
        The keyword and the total length of the line is checked not to exceed 
        their respective maximum size.
        
        :arg keyword: 6-character keyword
        :arg text: value of the keyword
        :arg comment: comment associated with the line
        """
        keyword = self.name.ljust(self.LINE_KEYWORDS_SIZE)
        assert len(keyword) == self.LINE_KEYWORDS_SIZE

        # Convert list to a single string
        if isinstance(text, (tuple, list)):
            text = ' '.join(map(str, text))

        line = "%s %s" % (keyword.upper(), text)
        if len(self.comment) > 0:
            line = line.ljust(self.LINE_SIZE - (len(self.comment) + 2))
            line += '[%s]' % self.comment

        assert len(line) <= self.LINE_SIZE

        return line

class Exporter(_Exporter):
    _KEYWORD_TITLE = _Keyword("TITLE")

    _KEYWORD_SENERG = _Keyword("SENERG", "Energy of the electron beam, in eV")
    _KEYWORD_SPOSIT = _Keyword("SPOSIT", "Coordinates of the electron source")
    _KEYWORD_SDIREC = _Keyword("SDIREC", "Direction angles of the beam axis, in deg")
    _KEYWORD_SAPERT = _Keyword("SAPERT", "Beam aperture, in deg")
    _KEYWORD_SDIAM = _Keyword('SDIAM', "Beam diameter, in cm")

    _KEYWORD_MFNAME = _Keyword("MFNAME", "Material file, up to 20 chars")
    _KEYWORD_MSIMPA = _Keyword("MSIMPA", "EABS(1:3),C1,C2,WCC,WCR")

    _KEYWORD_GEOMFN = _Keyword("GEOMFN", "Geometry definition file, 20 chars")
    _KEYWORD_DSMAX = _Keyword("DSMAX", "IB, maximum step length (cm) in body IB")

    _KEYWORD_IFORCE = _Keyword("IFORCE", "KB,KPAR,ICOL,FORCER,WLOW,WHIG")

    _KEYWORD_NBE = _Keyword("NBE", "E-interval and no. of energy bins")
    _KEYWORD_NBTH = _Keyword("NBTH", "No. of bins for the polar angle THETA")
    _KEYWORD_NBPH = _Keyword("NBPH", "No. of bins for the azimuthal angle PHI")

    _KEYWORD_PDANGL = _Keyword("PDANGL", "Angular window, in deg, IPSF")
    _KEYWORD_PDENER = _Keyword("PDENER", "Energy window, no. of channels")
    _KEYWORD_XRORIG = _Keyword("XRORIG", "Map of emission sites of detected x-rays")

    _KEYWORD_GRIDX = _Keyword("GRIDX", "X coordinates of the box vertices")
    _KEYWORD_GRIDY = _Keyword("GRIDY", "Y coordinates of the box vertices")
    _KEYWORD_GRIDZ = _Keyword("GRIDZ", "Z coordinates of the box vertices")
    _KEYWORD_GRIDBN = _Keyword("GRIDBN", "Numbers of bins")
    _KEYWORD_XRAYE = _Keyword("XRAYE", "Energy interval where x-rays are tallied")

    _KEYWORD_PRZ = _Keyword("PRZ", "prz for transition IZ,IS1,IS of detector IPD")

    _KEYWORD_RESUME = _Keyword("RESUME", "Resume from this dump file, 20 chars")
    _KEYWORD_DUMPTO = _Keyword("DUMPTO", "Generate this dump file, 20 chars")
    _KEYWORD_DUMPP = _Keyword("DUMPP", "Dumping period, in sec")

    _KEYWORD_NSIMSH = _Keyword("NSIMSH", "Desired number of simulated showers")
    _KEYWORD_RSEED = _Keyword("RSEED", "Seeds of the random - number generator")
    _KEYWORD_TIME = _Keyword("TIME", "Allotted simulation time, in sec")
    _KEYWORD_XLIM = _Keyword('XLIM', "Uncertainty limit")

    _LINE_SKIP = "       ."
    _LINE_ELECTROBEAM = "       >>>>>>>> Electron beam definition."
    _LINE_MATERIALDATA = "       >>>>>>>> Material data and simulation parameters."
    _LINE_GEOMETRY = "       >>>>>>>> Geometry of the sample."
    _LINE_INTERACTION = "       >>>>>>>> Interaction forcing."
    _LINE_EMERGINGDIST = "       >>>>>>>> Emerging particles. Energy and angular distributions."
    _LINE_DETECTORS = "       >>>>>>>> Photon detectors."
    _LINE_SPATIALDIST = "       >>>>>>>> Spatial distribution of events."
    _LINE_PHIRHOZ = "       >>>>>>>> Phi rho z distributions."
    _LINE_JOBPROP = "       >>>>>>>> Job properties."
    _LINE_END = "END"

    def __init__(self):
        """
        Creates a exporter to PENELOPE.
        """
        _Exporter.__init__(self)

        self._geometry_exporters[Substrate] = self._export_geometry_substrate
        self._geometry_exporters[Inclusion] = self._export_geometry_inclusion
        self._geometry_exporters[MultiLayers] = self._export_geometry_multilayers
        self._geometry_exporters[GrainBoundaries] = self._export_geometry_grainboundaries
        self._geometry_exporters[Sphere] = self._export_geometry_sphere

        self._pendbase_dir = settings.penelope.pendbase

    def export(self, options, outputdir):
        # Export geometry
        geoinfo, matinfos = self.export_geometry(options.geometry, outputdir)

        # Create input file
        lines = self._create_input_file(options, geoinfo, matinfos)

        filepath = os.path.join(outputdir, options.name + '.in')
        with open(filepath, 'w') as fp:
            for line in lines:
                fp.write(line + os.linesep)

        return filepath

    def _create_input_file(self, options, geoinfo, matinfos):
        lines = []

        # Description
        text = options.name
        line = self._KEYWORD_TITLE.create_line(text)
        lines.append(line)

        lines.append(self._LINE_SKIP)

        # Electron beam definition.
        lines.append(self._LINE_ELECTROBEAM)

        text = options.beam.energy_eV
        line = self._KEYWORD_SENERG.create_line(text)
        lines.append(line)

        text = map(mul, [1e2] * 3, options.beam.origin_m) # to cm
        line = self._KEYWORD_SPOSIT.create_line(text)
        lines.append(line)

        text = map(math.degrees, [options.beam.direction_polar_rad,
                                  options.beam.direction_azimuth_rad])
        line = self._KEYWORD_SDIREC.create_line(text)
        lines.append(line)

        text = 0.0
        line = self._KEYWORD_SAPERT.create_line(text)
        lines.append(line)

        text = options.beam.diameter_m * 1e2 # to cm
        line = self._KEYWORD_SDIAM.create_line(text)
        lines.append(line)

        lines.append(self._LINE_SKIP)

        # Material data and simulation parameters
        lines.append(self._LINE_MATERIALDATA)

        for material, matfilepath in matinfos:
            text = os.path.basename(matfilepath)
            line = self._KEYWORD_MFNAME.create_line(text)
            lines.append(line)

            text = [material.absorption_energy_electron_eV,
                    material.absorption_energy_photon_eV,
                    options.beam.energy_eV, # No positron simulated
                    material.elastic_scattering[0],
                    material.elastic_scattering[1],
                    material.cutoff_energy_inelastic_eV,
                    material.cutoff_energy_bremsstrahlung_eV]
            line = self._KEYWORD_MSIMPA.create_line(text)
            lines.append(line)

        lines.append(self._LINE_SKIP)

        # Geometry
        lines.append(self._LINE_GEOMETRY)

        pengeom, geofilepath = geoinfo

        text = os.path.basename(geofilepath)
        line = self._KEYWORD_GEOMFN.create_line(text)
        lines.append(line)

        bodies = sorted(pengeom.get_bodies(), key=attrgetter('_index'))
        for body in bodies:
            if body.material.is_vacuum():
                continue
            text = [body._index + 1,
                    body.maximum_step_length_m * 1e2]
            line = self._KEYWORD_DSMAX.create_line(text)
            lines.append(line)

        lines.append(self._LINE_SKIP)

        # Interaction forcing
        lines.append(self._LINE_INTERACTION)

        for body in bodies:
            if body.material.is_vacuum():
                continue

            for intforce in sorted(body.interaction_forcings):
                text = [body._index + 1,
                        intforce.particle,
                        intforce.collision,
                        intforce.forcer,
                        intforce.weight[0],
                        intforce.weight[1]]
                line = self._KEYWORD_IFORCE.create_line(text)
                lines.append(line)

        lines.append(self._LINE_SKIP)

        # Emerging particles
        lines.append(self._LINE_EMERGINGDIST)

        #FIXME: Add emerging particle detectors

        lines.append(self._LINE_SKIP)

        # Photon detectors
        lines.append(self._LINE_DETECTORS)

        # NOTE: Only PhotonSpectrumDetector are considered (i.e.  
        #       PhotonIntensityDetector are neglected), as the PENELOPE 
        #       converter takes care of creating PhotonSpectrumDetector for all 
        #       PhotonIntensityDetector.
        detectors = options.detectors.findall(PhotonSpectrumDetector)
        for detector in detectors:
            text = map(math.degrees, detector.elevation_rad + detector.azimuth_rad) + [0]
            line = self._KEYWORD_PDANGL.create_line(text)
            lines.append(line)

            text = detector.limits_eV + (detector.channels,)
            line = self._KEYWORD_PDENER.create_line(text)
            lines.append(line)

        lines.append(self._LINE_SKIP)

        # Spatial distribution
        lines.append(self._LINE_SPATIALDIST)

        #FIXME: Add spatial distribution

        lines.append(self._LINE_SKIP)

        # Phi rho z distribution
        lines.append(self._LINE_PHIRHOZ)


        # FIXME: Add phi-rho-z distribution

        lines.append(self._LINE_SKIP)

        # Job properties
        text = 'dump.dat'
        line = self._KEYWORD_RESUME.create_line(text)
        lines.append(line)

        text = 'dump.dat'
        line = self._KEYWORD_DUMPTO.create_line(text)
        lines.append(line)

        text = getattr(settings.penelope, 'dumpp', 60.0)
        line = self._KEYWORD_DUMPP.create_line(text)
        lines.append(line)

        lines.append(self._LINE_SKIP)

        limit = options.limits.find(ShowersLimit, ShowersLimit(1e38))
        text = '%e' % limit.showers
        line = self._KEYWORD_NSIMSH.create_line(text)
        lines.append(line)

        #NOTE: No random number. PENEPMA will select them.

        limit = options.limits.find(TimeLimit, TimeLimit(1e38))
        text = '%e' % limit.time_s
        line = self._KEYWORD_TIME.create_line(text)
        lines.append(line)

        limit = options.limits.find(UncertaintyLimit)
        if limit:
            transition = limit.transition
            text = [transition.z,
                    transition.dest,
                    transition.src,
                    - 1, # FIXME: Specify detector for uncertainty
                    limit.uncertainty,
                    0.0]
            line = self._KEYWORD_XLIM.create_line(text)
            lines.append(line)

        lines.append(self._LINE_SKIP)

        # End
        lines.append(self._LINE_END)

        return lines

    def export_geometry(self, geometry, outputdir):
        """
        Exports geometry to a *geo* file and all materials to *mat* files.
        
        :arg geometry: :geometry object
        
        :arg outputdir: full path to a directory where the files will be saved.
            Note that any conflicting files will be overwritten without warnings.
            
        :return: a :class:`tuple` and a list of :class:`tuple`.
            The class:`tuple` contains 2 items: the :class:`PenelopeGeometry`
            object used to create the *geo* file and the full path of this
            *geo* file.
            Each :class:`tuple` in the list contains 2 items: the 
            :class:`PenelopeMaterial` object and its associated *mat* filepath.
            The order of the materials is the same as they appear in the 
            geometry file.
            In other words, the first material has an index of 1 in the 
            geometry file. 
        """
        # Save geometry
        title = geometry.__class__.__name__.lower()
        pengeom = PenelopeGeometry(title)
        pengeom._props.update(geometry._props) # tilt and rotation

        self._export_geometry(geometry, pengeom)

        lines = pengeom.to_geo()
        geofilepath = os.path.join(outputdir, title + ".geo")
        with open(geofilepath, 'w') as f:
            for line in lines:
                f.write(line + '\n')

        # Save materials
        cwd = os.getcwd()
        os.chdir(self._pendbase_dir)

        matinfos = []
        for material in pengeom.get_materials():
            index = material._index
            if index == 0: continue

            filepath = os.path.join(outputdir, 'mat%i.mat' % index)
            penmaterial.create(material, filepath)

            matinfos.append((material, filepath))

        os.chdir(cwd)

        return (pengeom, geofilepath), matinfos

    def _export_geometry(self, geometry, *args):
        clasz = geometry.__class__
        method = self._geometry_exporters.get(clasz)

        if method:
            method(geometry, *args)
        else:
            raise ExporterException, "Could not export geometry '%s'" % clasz.__name__

    def _export_geometry_substrate(self, geometry, pengeom):
        surface_cylinder = cylinder(0.1) # 10 cm radius
        surface_top = zplane(0.0) # z = 0
        surface_bottom = zplane(-0.1) # z = -10 cm

        module = Module.from_body(geometry.body)
        module.add_surface(surface_cylinder, -1)
        module.add_surface(surface_top, -1)
        module.add_surface(surface_bottom, 1)

        pengeom.modules.add(module)

    def _export_geometry_inclusion(self, geometry, pengeom):
        surface_cylinder = cylinder(0.1) # 10 cm radius
        surface_top = zplane(0.0) # z = 0
        surface_bottom = zplane(-0.1) # z = -10 cm
        surface_sphere = sphere(geometry.inclusion_diameter_m / 2.0)

        module_inclusion = Module.from_body(geometry.inclusion_body, 'Inclusion')
        module_inclusion.add_surface(surface_top, -1)
        module_inclusion.add_surface(surface_sphere, -1)

        module_substrate = Module.from_body(geometry.substrate_body, 'Substrate')
        module_substrate.add_surface(surface_cylinder, -1)
        module_substrate.add_surface(surface_top, -1)
        module_substrate.add_surface(surface_bottom, 1)
        module_substrate.add_module(module_inclusion)

        pengeom.modules.add(module_substrate)
        pengeom.modules.add(module_inclusion)

    def _export_geometry_multilayers(self, geometry, pengeom):
        # Surfaces
        surface_cylinder = cylinder(0.1) # 10 cm radius

        surface_layers = [zplane(0.0)]
        for layer in geometry.layers:
            dim = geometry.get_dimensions(layer)
            surface_layers.append(zplane(dim.zmin_m))

        # Modules
        tmpgrouping = []
        for i, surfaces in enumerate(_pairwise(surface_layers)):
            surface_top, surface_bottom = surfaces
            layer = geometry.layers[i]

            module = Module.from_body(layer, 'Layer %i' % (i + 1,))
            module.add_surface(surface_cylinder, -1)
            module.add_surface(surface_top, -1)
            module.add_surface(surface_bottom, 1)

            pengeom.modules.add(module)
            tmpgrouping.append((module, surface_bottom))

        if geometry.has_substrate():
            surface_top = surface_layers[-1]
            surface_bottom = zplane(surface_top.shift.z_m - 0.1) # 10 cm below last layer

            module = Module.from_body(geometry.substrate_body, 'Substrate')
            module.add_surface(surface_cylinder, -1)
            module.add_surface(surface_top, -1)
            module.add_surface(surface_bottom, 1)

            pengeom.modules.add(module)
            tmpgrouping.append((module, surface_bottom))

        # Grouping
        # G0: s0, s2, m0, m1
        # G1: s0, s3, m2, g0
        # G2: s0, s4, m3, g1
        # etc.

        if len(tmpgrouping) <= 2: # no grouping required if only 2 modules
            return

        module, surface_bottom = tmpgrouping[1]

        group = Module(VACUUM, 'grouping')
        group.add_surface(surface_cylinder, -1)
        group.add_surface(surface_layers[0], -1) # top z = 0.0
        group.add_surface(surface_bottom, 1)
        group.add_module(tmpgrouping[0][0]) # m0
        group.add_module(module) #m1

        pengeom.modules.add(group)

        for module, surface_bottom in tmpgrouping[2:]:
            oldgroup = group

            group = Module(VACUUM, 'grouping')
            group.add_surface(surface_cylinder, -1)
            group.add_surface(surface_layers[0], -1) # top z = 0.0
            group.add_surface(surface_bottom, 1)
            group.add_module(module)
            group.add_module(oldgroup)

            pengeom.modules.add(group)

    def _export_geometry_grainboundaries(self, geometry, pengeom):
        # Surfaces
        surface_top = zplane(0.0) # z = 0
        surface_bottom = zplane(-0.1) # z = -10 cm

        surface_layers = []
        for layer in geometry.layers:
            dim = geometry.get_dimensions(layer)
            surface_layers.append(xplane(dim.xmin_m))
        surface_layers.append(xplane(dim.xmax_m))

        diameter_m = sum(map(attrgetter('thickness_m'), geometry.layers))
        surface_cylinder = cylinder(0.1 + 3.0 * diameter_m) # 10 cm radius

        # Modules
        ## Left substrate
        module = Module.from_body(geometry.left_body, 'Left substrate')
        module.add_surface(surface_cylinder, -1)
        module.add_surface(surface_top, -1)
        module.add_surface(surface_bottom, 1)
        module.add_surface(surface_layers[0], -1)

        pengeom.modules.add(module)

        ## Layers
        for i, surfaces in enumerate(_pairwise(surface_layers)):
            surface_left, surface_right = surfaces
            layer = geometry.layers[i]

            module = Module.from_body(layer, 'Layer %i' % (i + 1,))
            module.add_surface(surface_cylinder, -1)
            module.add_surface(surface_top, -1)
            module.add_surface(surface_bottom, 1)
            module.add_surface(surface_left, 1)
            module.add_surface(surface_right, -1)

            pengeom.modules.add(module)

        ## Right substrate
        module = Module.from_body(geometry.right_body, 'Right substrate')
        module.add_surface(surface_cylinder, -1)
        module.add_surface(surface_top, -1)
        module.add_surface(surface_bottom, 1)
        module.add_surface(surface_layers[-1], 1)

        pengeom.modules.add(module)

    def _export_geometry_sphere(self, geometry, pengeom):
        surface_sphere = sphere(geometry.diameter_m / 2.0)

        module = Module.from_body(geometry.body, 'Sphere')
        module.add_surface(surface_sphere, -1)
        pengeom.modules.add(module)

