#!/usr/bin/env python
"""
================================================================================
:mod:`exporter` -- Exporter for Monaco program
================================================================================

.. module:: exporter
   :synopsis: Exporter for Monaco program

.. inheritance-diagram:: pymontecarlo.program.monaco.io.exporter

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import struct
from operator import itemgetter

# Third party modules.

# Local modules.
from pymontecarlo.io.exporter import Exporter as _Exporter

from pymontecarlo.input.geometry import Substrate

import pymontecarlo.util.element_properties as ep

# Globals and constants variables.

class Exporter(_Exporter):

    def __init__(self):
        """
        Creates a exporter for Monaco program.
        """
        _Exporter.__init__(self)

        self._geometry_exporters[Substrate] = self._export_geometry_substrate

    def export(self, options, outputdir):
        """
        Creates MAT and SIM files for Monaco program.
        
        :arg options: options to be exported
        :arg outputdir: directory where the simulation files should be saved
        """
        self._export(options, outputdir)

    def _export(self, options, outputdir, *args):
        self._export_geometry(options, outputdir, *args)

    def _export_geometry_substrate(self, options, geometry, outputdir, *args):
        composition = sorted(geometry.material.composition.items(), key=itemgetter(0))
        density_g_cm3 = geometry.material.density_kg_m3

        filepath = os.path.join(outputdir, options.name + '.MAT')
        with open(filepath, 'wb') as fp:
            # Header
            # DELPHI: s:=6;Blockwrite(Matfile,Typ,6,f);Inc(Sum,f);
            fp.write('\x02\x02\x02\x00\x02\x01')

            # Write length of element and element
            # DELPHI:
            # for i:=1 to Nc do begin
            #     l:=1+Length(Comp[i]);Inc(s,l);
            #     Blockwrite(Matfile,Comp[i,0],l,f);Inc(Sum,f);
            # end;
            for z, _wf in composition:
                symbol = ep.symbol(z).upper()
                fp.write(struct.pack('b', len(symbol)) + symbol)

            # Write molar mass
            # DELPHI: l:=4*Nc;Inc(s,l);Blockwrite(Matfile,AC[1],l,f);Inc(Sum,f);
            for z, _wf in composition:
                mass = ep.atomic_mass(z)
                fp.write(struct.pack('f', mass))

            # Write atomic number
            # DELPHI: Inc(s,NZ);Blockwrite(Matfile,Z[1],NZ,f);Inc(Sum,f);
            for z, _wf in composition:
                fp.write(struct.pack('b', z))

            # Write molar mass
            # DELPHI:
            # l:=4*Nc+4;
            # for i:=0 to NZ do begin
            #     Inc(s,l);BlockWrite(Matfile,GZ[i],l,f);Inc(Sum,f);
            # end;
            fp.write('\x00\x00\x00\x00') # Skip 4 bytes
            for z, _wf in composition:
                mass = ep.atomic_mass(z)
                fp.write(struct.pack('f', mass))

            for i, item in enumerate(composition):
                z = item[0]
                mass = ep.atomic_mass(z)
                fp.write(struct.pack('f', mass)) # FIXME: Error here
                fp.write('\x00\x00\x00\x00' * i) # Skip 4 bytes
                fp.write(struct.pack('f', 1.0 / mass))
                fp.write('\x00\x00\x00\x00' * (len(composition) - i - 1)) # Skip 4 bytes

            # DELPHI: Inc(s,l);BlockWrite(Matfile,GM,l,f);Inc(Sum,f);
            gs = [wf / ep.atomic_mass(z) for z, wf in composition]
            g0 = 1.0 / sum(gs)
            fp.write(struct.pack('f', g0))
            for g in gs:
                fp.write(struct.pack('f', g))

            # DELPHI:
            # for i:=0 to NP do begin
            #     Inc(s,l);BlockWrite(Matfile,GS[i],l,f);Inc(Sum,f);
            # end;
            fp.write('\x00\x00\x00\x00' * (len(composition) + 1))

            # DELPHI:
            # l:=4*NP+4;Inc(s,l);Blockwrite(Matfile,ML[0],l,f);Inc(Sum,f);
            fp.write('\x00\x00\x00\x00')

            # DELPHI: Inc(s,l);Blockwrite(Matfile,rho[0],l,f);Inc(Sum,f);
            fp.write(struct.pack('f', density_g_cm3))

            # DELPHI:
            # l:=NC+1;
            # for i:=0 to NP do begin
            #     Inc(s,l);BlockWrite(Matfile,PC[i],l,f);Inc(Sum,f);
            # end;
            fp.write(struct.pack('b', len(composition)))
            fp.write('\x00' * len(composition))

            # DELPHI: Inc(s,l);BlockWrite(Matfile,PM,l,f);Inc(Sum,f);
            fp.write(struct.pack('b', len(composition)))
            for i in range(len(composition)):
                fp.write(struct.pack('b', i + 1))

if __name__ == '__main__':
    from pymontecarlo.input.options import Options

    options = Options('test')
    options.geometry.material.composition = {6: 0.4, 13: 0.1, 79: 0.5}

    Exporter().export(options, '/tmp')
