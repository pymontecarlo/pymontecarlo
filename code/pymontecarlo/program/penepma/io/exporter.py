#!/usr/bin/env python
"""
================================================================================
:mod:`exporter` -- Exporter to PENEPMA files
================================================================================

.. module:: exporter
   :synopsis: Exporter to PENEPMA files

.. inheritance-diagram:: pymontecarlo.program.penepma.io.exporter

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

# Third party modules.

# Local modules.
from pymontecarlo import get_settings
from pymontecarlo.input.detector import PhotonSpectrumDetector
from pymontecarlo.input.limit import ShowersLimit, TimeLimit, UncertaintyLimit
from pymontecarlo.program.penelope.io.exporter import Exporter as _Exporter, Keyword

# Globals and constants variables.

class Exporter(_Exporter):
    _KEYWORD_TITLE = Keyword("TITLE")

    _KEYWORD_SENERG = Keyword("SENERG", "Energy of the electron beam, in eV")
    _KEYWORD_SPOSIT = Keyword("SPOSIT", "Coordinates of the electron source")
    _KEYWORD_SDIREC = Keyword("SDIREC", "Direction angles of the beam axis, in deg")
    _KEYWORD_SAPERT = Keyword("SAPERT", "Beam aperture, in deg")
    _KEYWORD_SDIAM = Keyword('SDIAM', "Beam diameter, in cm")

    _KEYWORD_MFNAME = Keyword("MFNAME", "Material file, up to 20 chars")
    _KEYWORD_MSIMPA = Keyword("MSIMPA", "EABS(1:3),C1,C2,WCC,WCR")

    _KEYWORD_GEOMFN = Keyword("GEOMFN", "Geometry definition file, 20 chars")
    _KEYWORD_DSMAX = Keyword("DSMAX", "IB, maximum step length (cm) in body IB")

    _KEYWORD_IFORCE = Keyword("IFORCE", "KB,KPAR,ICOL,FORCER,WLOW,WHIG")

    _KEYWORD_NBE = Keyword("NBE", "E-interval and no. of energy bins")
    _KEYWORD_NBTH = Keyword("NBTH", "No. of bins for the polar angle THETA")
    _KEYWORD_NBPH = Keyword("NBPH", "No. of bins for the azimuthal angle PHI")

    _KEYWORD_PDANGL = Keyword("PDANGL", "Angular window, in deg, IPSF")
    _KEYWORD_PDENER = Keyword("PDENER", "Energy window, no. of channels")
    _KEYWORD_XRORIG = Keyword("XRORIG", "Map of emission sites of detected x-rays")

    _KEYWORD_GRIDX = Keyword("GRIDX", "X coordinates of the box vertices")
    _KEYWORD_GRIDY = Keyword("GRIDY", "Y coordinates of the box vertices")
    _KEYWORD_GRIDZ = Keyword("GRIDZ", "Z coordinates of the box vertices")
    _KEYWORD_GRIDBN = Keyword("GRIDBN", "Numbers of bins")
    _KEYWORD_XRAYE = Keyword("XRAYE", "Energy interval where x-rays are tallied")

    _KEYWORD_PRZ = Keyword("PRZ", "prz for transition IZ,IS1,IS of detector IPD")

    _KEYWORD_RESUME = Keyword("RESUME", "Resume from this dump file, 20 chars")
    _KEYWORD_DUMPTO = Keyword("DUMPTO", "Generate this dump file, 20 chars")
    _KEYWORD_DUMPP = Keyword("DUMPP", "Dumping period, in sec")

    _KEYWORD_NSIMSH = Keyword("NSIMSH", "Desired number of simulated showers")
    _KEYWORD_RSEED = Keyword("RSEED", "Seeds of the random - number generator")
    _KEYWORD_TIME = Keyword("TIME", "Allotted simulation time, in sec")
    _KEYWORD_XLIM = Keyword('XLIM', "Uncertainty limit")

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
        Creates a exporter to PENEPMA.
        """
        _Exporter.__init__(self)

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
        #
        # NOTE: Detectors are alphabetically sorted with their key. This is 
        #       important for the importer as this is the only way to know 
        #       the index of the detector.
        detectors = options.detectors.findall(PhotonSpectrumDetector)
        for key in sorted(detectors.keys()):
            detector = detectors[key]

            #FIXME: Elevation must be inverted
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

        text = getattr(get_settings().penelope, 'dumpp', 60.0)
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
