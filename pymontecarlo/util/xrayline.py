""""""

# Standard library modules.

# Third party modules.
import pyxray

# Local modules.

# Globals and constants variables.

KNOWN_XRAYTRANSITIONS = [pyxray.xray_transition('Ka1'),
                         pyxray.xray_transition('Kb1'),
                         pyxray.xray_transition('La1'),
                         pyxray.xray_transition('Lb1'),
                         pyxray.xray_transition('Ll'),
                         pyxray.xray_transition('Ma1'),
                         pyxray.xray_transition('M4-N2') # Mz
                         ]

def convert_xrayline(xrayline):
    if isinstance(xrayline, pyxray.XrayLine):
        return xrayline

    try:
        return pyxray.xray_line(*xrayline)
    except:
        raise ValueError('"{}" is not an XrayLine'.format(xrayline))

def find_lowest_energy_known_xrayline(zs, minimum_energy_eV=0.0):
    lowest_energy_eV = float('inf')
    lowest_xrayline = None

    for z in zs:
        for xraytransition in pyxray.element_xray_transitions(z):
            if xraytransition not in KNOWN_XRAYTRANSITIONS:
                continue

            energy_eV = pyxray.xray_transition_energy_eV(z, xraytransition)
            if energy_eV < lowest_energy_eV and energy_eV >= minimum_energy_eV:
                lowest_xrayline = pyxray.xray_line(z, xraytransition)
                lowest_energy_eV = energy_eV

    return lowest_xrayline

def find_reference_xrayline(options):
    zs = set()
    for material in options.sample.materials:
        zs |= set(material.composition.keys())

    return find_lowest_energy_known_xrayline(zs, minimum_energy_eV=100.0)