#!/usr/bin/env python
"""
================================================================================
:mod:`convol` -- Convolution of a spectrum
================================================================================

.. module:: convol
   :synopsis: Convolution of a spectrum

Adapted from PENELOPE convol program (F. Salvat).
"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import logging
import math

# Third party modules.
from scipy.integrate import romberg

# Local modules.

# Globals and constants variables.
SQR2PI = math.sqrt(2 * math.pi)
D1 = 0.0498673470
D2 = 0.0211410061
D3 = 0.0032776263
D4 = 0.0000380036
D5 = 0.0000488906
D6 = 0.0000053830

def fwhm_sili(energy):
    return math.sqrt(7849.255 + 2.237253 * energy)

def fwhm_cdte(energy):
    return math.sqrt(64.5 * energy)

def fwhm_nai(energy):
    return 40.0 * math.sqrt(energy) + 0.028 * energy

def convol(energies, intensities, channel_width, fwhm=fwhm_sili):
    assert len(energies) == len(intensities)
    assert len(energies) > 2

    delta_energy = energies[1] - energies[0]
    energy_min = energies[0]
    energy_max = energies[-1]
    area = sum(intensities) * delta_energy

    logging.debug("Minimum energy: %f" % energy_min)
    logging.debug("Maximum energy: %f" % energy_max)
    logging.debug("Energy bin width: %f" % delta_energy)
    logging.debug("Number of energy bins: %i" % len(energies))

    nchannels = int((energy_max + 4.0 * fwhm(energy_max)) / channel_width)
    logging.debug("Number of channels: %i" % nchannels)

    convol_area = 0.0
    convol_energies = []
    convol_intensities = []

    data = zip(energies, intensities)

    for i in range(nchannels):
        vu = energy_min + i * channel_width
        vl = vu - channel_width
        vc = 0.5 * (vl + vu)

        gauss_width = 0.4246609 * fwhm(vc) * math.sqrt(-2.0 * math.log(0.001));
        low = int((vc - gauss_width) / delta_energy)
        high = int((vc + gauss_width) / delta_energy)

        sumt = 0.0

        for energy, intensity in data[low:high]:
            el = max(energy - 0.5 * delta_energy, 1e-3)
            eu = el + delta_energy

            tst = 1e20
            if eu < vl:
                tst = _pulses(eu, vl, fwhm)
            if el > vu:
                tst = _pulses(el, vu, fwhm)

            if tst > 1e-20:
                integral = romberg(_f1, el, eu, tol=1e-4, args=(vl, vu, fwhm))
                sumt += integral * intensity

        sumv = max(sumt / channel_width, 1e-25)
        convol_area += sumt

        convol_energies.append(vc)
        convol_intensities.append(sumv)

    logging.debug("Input spectrum area: %e" % area)
    logging.debug("Convoluted spectrum area: %e" % convol_area)

    return convol_energies, convol_intensities

def _pulses(energy, height, fwhm):
    """
    This function computes the pulse height spectrum that results from
    the detection of a photon with specified energy. 
    
    The output value is the probability of having a pulse of the specified height. 
    The detector response function is assumed to be Gaussian.
    
    :arg energy: deposited energy
    :arg height: output pulse height
    :arg fwhm: function to calculate the full with at half maximum
    
    :return: probability of having a pulse of the specified height
    """
    sigma = max(0.4246609 * fwhm(energy), 1.0e-6)
    tst = 0.5 * ((height - energy) / sigma) ** 2
    if tst < 80.0:
        return math.exp(-tst) / (SQR2PI * sigma)
    else:
        return 0.0

def _pacn(x):
    """
    Normal cumulative probability function. 
    Hastings' rational approximation.
    """
    if x > 25.0:
        return 1.0
    elif x > 0.0:
        return 1.0 - 0.5 / (1.0 + x * (D1 + x * (D2 + x * (D3 + x * (D4 + x * (D5 + x * D6)))))) ** 16
    elif x > -25.0:
        t = -x
        return 0.5 / (1.0 + t * (D1 + t * (D2 + t * (D3 + t * (D4 + t * (D5 + t * D6)))))) ** 16
    else:
        return 0.0

def _f1(energy, vl, vu, fwhm):
    sigma = 0.4246609 * fwhm(energy)
    xl = (vl - energy) / sigma
    xu = (vu - energy) / sigma

    return _pacn(xu) - _pacn(xl)

