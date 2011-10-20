"""
================================================================================
:mod:`options` -- Main class containing all options of a simulation
================================================================================

.. module:: options
   :synopsis: Main class containing all options of a simulation

.. inheritance-diagram:: pymontecarlo.input.options

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from xml.etree.ElementTree import Element

# Third party modules.

# Local modules.
from pymontecarlo.util.xmlobj import XMLObject, from_xml_choices
from pymontecarlo.input.beam import GaussianBeam, PencilBeam
from pymontecarlo.input.material import pure
from pymontecarlo.input.geometry import \
    Substrate, MultiLayers, GrainBoundaries, Inclusion
from pymontecarlo.input.limit import TimeLimit, ShowersLimit, UncertaintyLimit
from pymontecarlo.input.detector import \
    (BackscatteredElectronAzimuthalAngularDetector,
     BackscatteredElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector,
     EnergyDepositedSpatialDetector,
     PhiRhoZDetector,
     PhotonAzimuthalAngularDetector,
     PhotonIntensityDetector,
     PhotonPolarAngularDetector,
     PhotonSpectrumDetector,
     TransmittedElectronAzimuthalAngularDetector,
     TransmittedElectronEnergyDetector,
     TransmittedElectronPolarAngularDetector)

# Globals and constants variables.

class Options(XMLObject):
    BEAMS = [GaussianBeam, PencilBeam]
    GEOMETRIES = [Substrate, MultiLayers, GrainBoundaries, Inclusion]
    DETECTORS = [BackscatteredElectronAzimuthalAngularDetector,
                 BackscatteredElectronEnergyDetector,
                 BackscatteredElectronPolarAngularDetector,
                 EnergyDepositedSpatialDetector,
                 PhiRhoZDetector,
                 PhotonAzimuthalAngularDetector,
                 PhotonIntensityDetector,
                 PhotonPolarAngularDetector,
                 PhotonSpectrumDetector,
                 TransmittedElectronAzimuthalAngularDetector,
                 TransmittedElectronEnergyDetector,
                 TransmittedElectronPolarAngularDetector]
    LIMITS = [TimeLimit, ShowersLimit, UncertaintyLimit]

    def __init__(self, name='Untitled'):
        """
        
        """
        XMLObject.__init__(self)

        self.name = name
        self.beam = GaussianBeam(1e3, 1e-8) # 1 keV, 10 nm
        self.geometry = Substrate(pure(79)) # Au substrate
        self._detectors = {}
        self._limits = []

    @classmethod
    def from_xml(cls, element):
        name = element.get('name')

        child = list(element.find("beam"))[0]
        beam = from_xml_choices(child, cls.BEAMS)

        child = list(element.find("geometry"))[0]
        geometry = from_xml_choices(child, cls.GEOMETRIES)

        children = list(element.find("detectors"))
        detectors = {}
        for child in children:
            key = child.get('_key')
            obj = from_xml_choices(child, cls.DETECTORS)
            detectors[key] = obj

        children = list(element.find("limits"))
        limits = []
        for child in children:
            limits.append(from_xml_choices(child, cls.LIMITS))

        options = cls(name)
        options.beam = beam
        options.geometry = geometry
        options.detectors.update(detectors)
        options.limits.extend(limits)

        return options

    def __repr__(self):
        return '<Options(name=%s)>' % self.name

    def __str__(self):
        return self.name

    @property
    def beam(self):
        return self._beam

    @beam.setter
    def beam(self, beam):
        self._beam = beam

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, geometry):
        self._geometry = geometry

    @property
    def detectors(self):
        return self._detectors

    @property
    def limits(self):
        return self._limits

    def to_xml(self):
        element = XMLObject.to_xml(self)

        element.set('name', self.name)

        child = Element('beam')
        child.append(self.beam.to_xml())
        element.append(child)

        child = Element('geometry')
        child.append(self.geometry.to_xml())
        element.append(child)

        child = Element('detectors')
        for key, detector in self.detectors.iteritems():
            grandchild = detector.to_xml()
            grandchild.set('_key', key)
            child.append(grandchild)
        element.append(child)

        child = Element('limits')
        for limit in self.limits:
            child.append(limit.to_xml())
        element.append(child)

        return element

