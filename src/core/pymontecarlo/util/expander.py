#!/usr/bin/env python
"""
================================================================================
:mod:`expander` -- Expand a options to several options with single value
================================================================================

.. module:: expander
   :synopsis: Expand a options to several options with single value

.. inheritance-diagram:: expander

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import copy

# Third party modules.

# Local modules.
from pymontecarlo.options.options import Options
from pymontecarlo.options.detector import _DelimitedDetector

from pymontecarlo.util.parameter import Expander as _Expander

# Globals and constants variables.

class Expander(_Expander):
    """
    Special expander for the options to automatically generate a meaningful
    name for each options based on the varied parameter.
    """

    def expand(self, obj):
        if not isinstance(obj, Options):
            raise ValueError("Argument must be an Options")
        return _Expander.expand(self, obj)

    def _create_objects(self, baseobj, combinations, parameter_objs, parameters):
        opss = _Expander._create_objects(self, baseobj, combinations,
                                         parameter_objs, parameters)

        for options, combination in zip(opss, combinations):
            parts = [options.name]

            for parameter, value in zip(parameters, combination):
                parts.append('%s=%s' % (parameter.name, value[0]))

            name = '+'.join(parts)
            name = name.replace(',', '_')
            options._name = name

        return opss

class ExpanderSingleDetector(Expander):
    """
    Further expansion to to ensure that there is only one type of detector
    per options.
    """

    def __init__(self, detector_classes):
        """
        Special expander that expands the options to ensure that there is
        only one type of detector per options.

        :arg detector_classes: list of detector classes that should be unique
        """
        Expander.__init__(self)

        self._detector_classes = list(detector_classes) # copy

    def expand(self, obj):
        list_options = Expander.expand(self, obj)

        # Check detector duplicates
        for detector_class in self._detector_classes:
            for options in list(list_options):
                detectors = list(options.detectors.iterclass(detector_class))
                if len(detectors) <= 1:
                    continue

                # Remove all detectors
                baseoptions = copy.deepcopy(options)
                for key, _ in detectors:
                    del baseoptions.detectors[key]

                # Add only one detector per options
                for i, item in enumerate(detectors):
                    key, detector = item
                    newoptions = copy.deepcopy(baseoptions)
                    newoptions._name += '+%i' % i
                    newoptions.detectors[key] = detector
                    list_options.append(newoptions)

                # Remove original options
                list_options.remove(options)

        return list_options

    def is_expandable(self, obj):
        if Expander.is_expandable(self, obj):
            return True

        for detector_class in self._detector_classes:
            detectors = list(obj.detectors.iterclass(detector_class))
            if len(detectors) > 1:
                return True

        return False

class ExpanderSingleDetectorSameOpening(ExpanderSingleDetector):
    """
    Further expansion to to ensure that there is only one type of detector
    per options and that the delimited detectors have the same opening.
    """

    def __init__(self, detector_classes, precision=1e-6):
        """
        Special expander that expands the options to ensure that there is
        only one type of detector per options and that the delimited detectors
        have the same opening up to the specified precision.

        :arg detector_classes: list of detector classes that should be unique
        """
        ExpanderSingleDetector.__init__(self, detector_classes)

        self._precision = precision

    def expand(self, obj):
        list_options = ExpanderSingleDetector.expand(self, obj)

        for options in list(list_options):
            detectors = list(options.detectors.iterclass(_DelimitedDetector))
            if len(detectors) <= 1:
                continue

            openings = self._group_openings(detectors)
            if len(openings) == 1:
                continue

            # Remove all detectors
            baseoptions = copy.deepcopy(options)
            for key, _ in detectors:
                del baseoptions.detectors[key]

            # Add detector with same opening to a new options
            for i, items in enumerate(openings.values()):
                newoptions = copy.deepcopy(baseoptions)
                newoptions._name += '+opening%i' % i

                for key, detector in items:
                    newoptions.detectors[key] = detector

                list_options.append(newoptions)

            # Remove original options
            list_options.remove(options)

        return list_options

    def _group_openings(self, detectors):
        openings = {}

        comparator = lambda x, y: abs(x - y) < self._precision

        for key, detector in detectors:
            elevation = tuple(detector.elevation_rad)
            azimuth = tuple(detector.azimuth_rad)
            current_opening = elevation + azimuth

            has_similar = False
            for opening in openings.keys():
                if all(map(comparator, current_opening, opening)):
                    openings.setdefault(opening, []).append((key, detector))
                    has_similar = True
                    break

            if not has_similar:
                openings.setdefault(current_opening, []).append((key, detector))

        return openings

    def is_expandable(self, obj):
        if ExpanderSingleDetector.is_expandable(self, obj):
            return True

        detectors = list(obj.detectors.iterclass(_DelimitedDetector))
        if len(detectors) <= 1:
            return False

        openings = self._group_openings(detectors)
        if len(openings) > 1:
            return True

        return False
