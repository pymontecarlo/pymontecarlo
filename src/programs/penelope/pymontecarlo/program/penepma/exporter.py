#!/usr/bin/env python
"""
================================================================================
:mod:`exporter` -- Exporter to PENEPMA files
================================================================================

.. module:: exporter
   :synopsis: Exporter to PENEPMA files

.. inheritance-diagram:: pymontecarlo.program.penepma.options.exporter

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
import logging
import warnings
from operator import attrgetter, mul

# Third party modules.
from pyxray.transition import get_transitions

# Local modules.
from pymontecarlo.settings import get_settings

from pymontecarlo.options.particle import ELECTRON, PHOTON, POSITRON
from pymontecarlo.options.collision import \
    (DELTA, HARD_ELASTIC, HARD_INELASTIC, HARD_BREMSSTRAHLUNG_EMISSION,
     INNERSHELL_IMPACT_IONISATION, COHERENT_RAYLEIGH_SCATTERING,
     INCOHERENT_COMPTON_SCATTERING, PHOTOELECTRIC_ABSORPTION,
     ELECTRON_POSITRON_PAIR_PRODUCTION, ANNIHILATION)
from pymontecarlo.options.material import VACUUM
from pymontecarlo.options.detector import \
    (_PhotonDelimitedDetector, PhotonSpectrumDetector, PhotonDepthDetector,
     BackscatteredElectronEnergyDetector)
from pymontecarlo.options.limit import ShowersLimit, TimeLimit, UncertaintyLimit

from pymontecarlo.program._penelope.exporter import \
    Exporter as _Exporter, Keyword, Comment, ExporterException, ExporterWarning
from pymontecarlo.program.penepma.options.detector import index_delimited_detectors

from penelopelib.material import MaterialInfo

# Globals and constants variables.
MAX_PHOTON_DETECTORS = 25 # Set in penepma.f
MAX_PRZ = 20 # Set in penepma.f
MAX_PHOTON_DETECTOR_CHANNEL = 1000

_PARTICLES_REF = {ELECTRON: 1, PHOTON: 2, POSITRON: 3}
_COLLISIONS_REF = {ELECTRON: {HARD_ELASTIC: 2,
                              HARD_INELASTIC: 3,
                              HARD_BREMSSTRAHLUNG_EMISSION: 4,
                              INNERSHELL_IMPACT_IONISATION: 5,
                              DELTA: 7},
                   PHOTON: {COHERENT_RAYLEIGH_SCATTERING: 1,
                            INCOHERENT_COMPTON_SCATTERING: 2,
                            PHOTOELECTRIC_ABSORPTION: 3,
                            ELECTRON_POSITRON_PAIR_PRODUCTION: 4,
                            DELTA: 7},
                   POSITRON: {HARD_ELASTIC: 2,
                              HARD_INELASTIC: 3,
                              HARD_BREMSSTRAHLUNG_EMISSION: 4,
                              INNERSHELL_IMPACT_IONISATION: 5,
                              ANNIHILATION: 6,
                              DELTA: 7}}

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
    _KEYWORD_XLMTR = Keyword('XLMTR', "Transition(s) for uncertainty limit")
    _KEYWORD_XLMPD = Keyword('XLMPD', "Photon detector for uncertainty limit")
    _KEYWORD_XLMUNC = Keyword('XLMUNC', "Uncertainty limit on intensity")

    _COMMENT_SKIP = Comment('.')
    _COMMENT_ELECTROBEAM = Comment('>>>>>>>> Electron beam definition.')
    _COMMENT_MATERIALDATA = Comment(">>>>>>>> Material data and simulation parameters.")
    _COMMENT_GEOMETRY = Comment(">>>>>>>> Geometry of the sample.")
    _COMMENT_INTERACTION = Comment(">>>>>>>> Interaction forcing.")
    _COMMENT_EMERGINGDIST = Comment(">>>>>>>> Emerging particles. Energy and angular distributions.")
    _COMMENT_DETECTORS = Comment(">>>>>>>> Photon detectors.")
    _COMMENT_SPATIALDIST = Comment(">>>>>>>> Spatial distribution of events.")
    _COMMENT_PHIRHOZ = Comment(">>>>>>>> Phi rho z distributions.")
    _COMMENT_JOBPROP = Comment(">>>>>>>> Job properties.")

    _KEYWORD_END = Keyword("END")

    def __init__(self):
        """
        Creates a exporter to PENEPMA.
        """
        _Exporter.__init__(self, get_settings().penepma.pendbase)

    def _create_input_file(self, options, outputdir, geoinfo, matinfos, *args):
        """
        Creates .in file for the specific PENELOPE main program and returns
        its location.

        :arg options: options to be exported
        :arg outputdir: directory where all the simulation files are saved
        :arg geoinfo: class:`tuple` containing :class:`PenelopeGeometry`
            object used to create the *geo* file and the full path of this
            *geo* file.
        :arg matinfos: :class:`list` of :class:`tuple` where each :class:`tuple`
            contains :class:`PenelopeMaterial` object and its associated *mat*
            filepath. The order of the materials is the same as they appear in
            the geometry file.

        :return: path to the .in file
        """
        # Find index for each delimited detector
        # The same method (index_delimited_detectors) is called when importing
        # the result. It ensures that the same index is used for all detectors
        dets = dict(options.detectors.iterclass(_PhotonDelimitedDetector))
        phdets_key_index, phdets_index_keys = index_delimited_detectors(dets)

        # Create lines
        lines = []
        args = (lines, options, geoinfo, matinfos,
                phdets_key_index, phdets_index_keys) + args

        self._append_title(*args)
        self._append_electron_beam(*args)
        self._append_material_data(*args)
        self._append_geometry(*args)
        self._append_interaction_forcing(*args)
        self._append_emerging_particles_distribution(*args)
        self._append_photon_detectors(*args)
        self._append_spatial_distribution(*args)
        self._append_phirhoz_distribution(*args)
        self._append_job_properties(*args)

        lines.append(self._KEYWORD_END())

        # Create .in file
        filepath = os.path.join(outputdir, options.name + '.in')
        with open(filepath, 'w') as fp:
            for line in lines:
                fp.write(line + os.linesep)

        return filepath

    def _append_title(self, lines, options, geoinfo, matinfos, *args):
        text = options.name
        line = self._KEYWORD_TITLE(text)
        lines.append(line)

        lines.append(self._COMMENT_SKIP())

    def _append_electron_beam(self, lines, options, geoinfo, matinfos, *args):
        lines.append(self._COMMENT_ELECTROBEAM())

        text = options.beam.energy_eV
        line = self._KEYWORD_SENERG(text)
        lines.append(line)

        text = list(map(mul, [1e2] * 3, options.beam.origin_m)) # to cm
        line = self._KEYWORD_SPOSIT(text)
        lines.append(line)

        text = list(map(math.degrees, [options.beam.direction_polar_rad,
                                       options.beam.direction_azimuth_rad]))
        line = self._KEYWORD_SDIREC(text)
        lines.append(line)

        text = 0.0
        line = self._KEYWORD_SAPERT(text)
        lines.append(line)

        text = options.beam.diameter_m * 1e2 # to cm
        line = self._KEYWORD_SDIAM(text)
        lines.append(line)

        lines.append(self._COMMENT_SKIP())

    def _append_interaction_forcing(self, lines, options, geoinfo, matinfos, *args):
        lines.append(self._COMMENT_INTERACTION())

        matinfos = dict(matinfos)
        bodies = sorted(geoinfo[0].get_bodies(), key=attrgetter('_index'))
        for body in bodies:
            if body.material is VACUUM:
                continue

            for intforce in body.material.interaction_forcings:
                kpar = _PARTICLES_REF[intforce.particle]
                icol = _COLLISIONS_REF[intforce.particle][intforce.collision]
                forcer = intforce.forcer
                wlow = intforce.weight[0]
                whigh = intforce.weight[1]

                # Recalculate forcer
                # NOTE: We override PENEPMA calculations of negative forcers,
                # since PENEPMA uses the absorption energy of electron and
                # photons to evaluate the mean free path. This skews the
                # interaction forcings when the absorption energies are not
                # equal to 50.0 eV.
                if forcer < 0:
                    logging.debug('Recalculation of forcer (%s)', forcer)

                    matfilepath = matinfos[body.material]
                    matinfo = MaterialInfo(matfilepath)

                    e0 = options.beam.energy_eV
                    plt = matinfo.range_m(e0, kpar)
                    rmfp = matinfo.meanfreepath_m(e0, kpar, icol)
                    forcer = abs(forcer) * rmfp / plt

                    logging.debug('New forcer value: %s', forcer)

                text = [body._index + 1, kpar, icol, forcer, wlow, whigh]
                line = self._KEYWORD_IFORCE(text)
                lines.append(line)

        lines.append(self._COMMENT_SKIP())

    def _append_emerging_particles_distribution(self, lines, options,
                                                geoinfo, matinfos, *args):
        lines.append(self._COMMENT_EMERGINGDIST())

        #FIXME: Add emerging particle detectors

        detectors = list(options.detectors.iterclass(BackscatteredElectronEnergyDetector))
        if not detectors:
            lines.append(self._COMMENT_SKIP())
            return

        detector = detectors[0][1]
        text = detector.limits_eV[0], detector.limits_eV[1], detector.channels
        line = self._KEYWORD_NBE(text)
        lines.append(line)

        lines.append(self._COMMENT_SKIP())

    def _append_photon_detectors(self, lines, options, geoinfo, matinfos,
                                 phdets_key_index, phdets_index_keys, *args):
        lines.append(self._COMMENT_DETECTORS())

        # Check number of detectors
        if len(phdets_index_keys) > MAX_PHOTON_DETECTORS:
            raise ExporterException('PENEPMA can only have %i detectors. %i are defined.' % \
                                    (MAX_PHOTON_DETECTORS, len(phdets_index_keys)))

        # Add detector in correct order
        for index in sorted(phdets_index_keys.keys()):
            keys = phdets_index_keys[index]
            detectors = list(map(options.detectors.get, keys))

            # Find if any of the detector is a PhotonSpectrumDetector
            spectrum_detectors = \
                list(filter(lambda x: isinstance(x, PhotonSpectrumDetector), detectors))
            if not spectrum_detectors: # Create fake detector
                detector = PhotonSpectrumDetector(detectors[0].elevation_rad,
                                                  detectors[0].azimuth_rad,
                                                  1000,
                                                  (0.0, options.beam.energy_eV))
            else:
                detector = spectrum_detectors[0]

            logging.debug('For index=%i, using %s', index + 1, detector)

            # Invert elevation angle as PENELOPE elevation is defined from the
            # position z axis instead of from the x-y plane
            elevation_deg = detector.elevation_deg

            low = 90.0 - elevation_deg[0]
            high = 90.0 - elevation_deg[1]
            elevation_deg = min(low, high), max(low, high)

            # Check number of channels
            channels = detector.channels
            if channels > MAX_PHOTON_DETECTOR_CHANNEL:
                channels = MAX_PHOTON_DETECTOR_CHANNEL

                message = "Number of channel of photon detector (%i) exceeds PENEPMA limit (%i). The limit is enforced." % \
                    (channels, MAX_PHOTON_DETECTOR_CHANNEL)
                warnings.warn(message, ExporterWarning)

            # Add lines
            comment = Comment('Detector %i used by %s' % (index + 1, ', '.join(keys)))
            lines.append(comment())

            text = elevation_deg + tuple(detector.azimuth_deg) + (0,)
            line = self._KEYWORD_PDANGL(text)
            lines.append(line)

            text = tuple(detector.limits_eV) + (channels,)
            line = self._KEYWORD_PDENER(text)
            lines.append(line)

            lines.append(self._COMMENT_SKIP())

    def _append_spatial_distribution(self, lines, options, geoinfo, matinfos, *args):
        lines.append(self._COMMENT_SPATIALDIST())

        #FIXME: Add spatial distribution

        lines.append(self._COMMENT_SKIP())

    def _append_phirhoz_distribution(self, lines, options, geoinfo, matinfos,
                                     phdets_key_index, phdets_index_keys, *args):
        lines.append(self._COMMENT_PHIRHOZ())

        detectors = dict(options.detectors.iterclass(PhotonDepthDetector))
        if not detectors:
            lines.append(self._COMMENT_SKIP())
            return

        # Check number of prz
        if len(detectors) > MAX_PRZ:
            raise ExporterException('PENEPMA can only have %i phi-rho-z. %i are defined.' % \
                                    (MAX_PRZ, len(detectors)))

        # Retrieve all elements inside the geometry
        materials = options.geometry.get_materials()

        zs = set()
        for material in materials:
            zs |= set(material.composition.keys())

        # Retrieve all transitions above a certain probability
        energylow = min(mat.absorption_energy_eV[ELECTRON] for mat in materials)
        energyhigh = options.beam.energy_eV

        transitions = []
        for z in zs:
            transitions += filter(lambda t: t.probability > 1e-2,
                                  get_transitions(z, energylow, energyhigh))

        transitions.sort(key=attrgetter('probability'), reverse=True)

        if not transitions:
            message = "No transition found for PRZ distribution with high enough probability"
            warnings.warn(message, ExporterWarning)

        # Restrain number of transitions to maximum number of PRZ
        if len(detectors) * len(transitions) > MAX_PRZ:
            message = 'Too many transitions (%i) for the number of detectors (%i). Only the most probable is/are kept.' % \
                          (len(transitions), len(detectors))
            warnings.warn(message, ExporterWarning)

            n = int(MAX_PRZ / len(detectors)) # >= 1
            transitions = transitions[:n]

        logging.debug('PRZ of the following transitions: %s',
                      ', '.join(map(str, transitions)))

        # Create lines
        for key in detectors.keys():
            index = phdets_key_index[key] + 1

            for transition in transitions:
                text = (transition.z, transition.dest.index,
                        transition.src.index, index)
                lines.append(self._KEYWORD_PRZ(text))

            message = "PENEPMA does not support a specific number of slices for the PRZ"
            warnings.warn(message, ExporterWarning)

        lines.append(self._COMMENT_SKIP())

    def _append_job_properties(self, lines, options, geoinfo, matinfos, *args):
        lines.append(self._COMMENT_JOBPROP())

        text = 'dump.dat'
        line = self._KEYWORD_RESUME(text)
        lines.append(line)

        text = 'dump.dat'
        line = self._KEYWORD_DUMPTO(text)
        lines.append(line)

        text = getattr(get_settings().penepma, 'dumpp', 60.0)
        line = self._KEYWORD_DUMPP(text)
        lines.append(line)

        lines.append(self._COMMENT_SKIP())

        limits = list(options.limits.iterclass(ShowersLimit))
        showers = limits[0].showers if limits else 1e38
        text = '%e' % showers
        line = self._KEYWORD_NSIMSH(text)
        lines.append(line)

        #NOTE: No random number. PENEPMA will select them.

        limits = list(options.limits.iterclass(TimeLimit))
        time_s = limits[0].time_s if limits else 1e38
        text = '%e' % time_s
        line = self._KEYWORD_TIME(text)
        lines.append(line)

        limits = list(options.limits.iterclass(UncertaintyLimit))
        if limits:
            for transition in limits[0].transitions:
                text = [transition.z, transition.dest.index, transition.src.index]
                line = self._KEYWORD_XLMTR(text)
                lines.append(line)

            text = [-1] # FIXME: Specify detector for uncertainty
            line = self._KEYWORD_XLMPD(text)
            lines.append(line)

            text = [limits[0].uncertainty, 0.0]
            line = self._KEYWORD_XLMUNC(text)
            lines.append(line)

        lines.append(self._COMMENT_SKIP())
