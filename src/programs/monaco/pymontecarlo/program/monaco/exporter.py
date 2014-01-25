#!/usr/bin/env python
"""
================================================================================
:mod:`exporter` -- Exporter for Monaco program
================================================================================

.. module:: exporter
   :synopsis: Exporter for Monaco program

.. inheritance-diagram:: pymontecarlo.program.monaco.input.exporter

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
import math

# Third party modules.
import numpy as np

import pyxray.element_properties as ep

# Local modules.
from pymontecarlo.program.exporter import Exporter as _Exporter

from pymontecarlo.options.geometry import Substrate
from pymontecarlo.options.particle import ELECTRON
from pymontecarlo.options.limit import ShowersLimit

# Globals and constants variables.

class Exporter(_Exporter):

    def __init__(self):
        """
        Creates a exporter for Monaco program.
        """
        _Exporter.__init__(self)

        self._geometry_exporters[Substrate] = self._export_geometry_substrate

    def _export(self, options, outputdir, *args, **kwargs):
        simfilepath = self._create_sim_file(options, outputdir, *args, **kwargs)
        self._export_geometry(options, outputdir, *args, **kwargs)
        return simfilepath

    def _create_sim_file(self, options, outputdir, *args, **kwargs):
        filepath = os.path.join(outputdir, options.name + '.SIM')
        with open(filepath, 'wb') as fp:
            # Header
            # DELPHI:
            # s := 0;Sum := 0;
            # BlockWrite(Sf,VersionCheck,1,w);
            # BlockWrite(Sf,VERSION,SizeOf(VERSION),w);
            fp.write(struct.pack('c', b'v'))
            fp.write(struct.pack('d', 3.2))

            # User: bot
            # DELPHI:
            # TmpStrLen := Length(UserStr);
            # l := 1;   Inc(s,l);BlockWrite(Sf, TmpStrLen, l,w); Inc(Sum, w);
            # if TmpStrLen<>0 then begin
            #     l := SizeOf(UserStr); Inc(s,l);BlockWrite(Sf, UserStr, l, w);Inc(Sum, w);
            #end;
            fp.write(b'\x03\x03')
            fp.write(b'bot')

            # Comment: No comment
            # DELPHI:
            # TmpStrLen := Length(CommentStr);
            # l := 1;   Inc(s,l);BlockWrite(Sf, TmpStrLen, l,w); Inc(Sum, w);
            # if TmpStrLen<>0 then begin
            #     l := SizeOf(CommentStr); Inc(s,l);BlockWrite(Sf, CommentStr, l, w);Inc(Sum, w);
            # end;
            fp.write(b'\x00')

            # DELPHI: l:=2; Inc(s,l); BlockWrite(Sf,GenNECheck,l,w); Inc(Sum,w);
            fp.write(b'\x00\x00')

            # Number of electrons
            # DELPHI:   l:=4; Inc(s,l); BlockWrite(Sf,NE,l,w);    Inc(Sum,w);
            limit = list(options.limits.iterclass(ShowersLimit))[0]
            showers = limit.showers
            fp.write(struct.pack('i', showers))

            # Cutoff energy
            # DELPHI: l:=4; Inc(s,l); BlockWrite(Sf,EM,l,w);    Inc(Sum,w);


            abs_energy_keV = min(material.absorption_energy_eV[ELECTRON] \
                                 for material in options.geometry.get_materials())
            fp.write(struct.pack('f', abs_energy_keV / 1000.0))

            # Secondary electron
            # DELPHI:   l:=1; Inc(s,l); BlockWrite(Sf,SE,l,w);    Inc(Sum,w);
            fp.write(struct.pack('b', 1))

            # Strings of number of electrons
            # DELPHI: l:=1+Length(NEstr); Inc(s,l); Blockwrite(Sf,NEStr,l,w); Inc(Sum,w);
            showers_str = str(showers).encode('ascii')
            fp.write(struct.pack('b', len(showers_str)))
            fp.write(showers_str)

            # String of cutoff energy
            # DELPHI: l:=1+Length(EMstr); Inc(s,l); Blockwrite(Sf,EMStr,l,w); Inc(Sum,w);
            abs_energy_keV_str = str(abs_energy_keV).encode('ascii')
            fp.write(struct.pack('b', len(abs_energy_keV_str)))
            fp.write(abs_energy_keV_str)

            # String of secondary electron
            # DELPHI: l:=1+Length(SEstr); Inc(s,l); Blockwrite(Sf,SEStr,l,w); Inc(Sum,w);
            fp.write(struct.pack('b', 1))
            fp.write(b'Y')

            # N
            # DELPHI: l:=4; Inc(s,l); BlockWrite(Sf,N,l,w);    Inc(Sum,w);
            fp.write(struct.pack('i', 1))

            # Stat
            # DELPHI: l:=N+1; Inc(s,l); BlockWrite(Sf,Stat,l,w); Inc(Sum,w);
            fp.write(b'\x00\x03')

            # Beam energy
            # DELPHI: l:=4*(N+1); Inc(s,l); BlockWrite(Sf,E,l,w);    Inc(Sum,w);
            energy_keV = options.beam.energy_eV / 1000.0
            fp.write(struct.pack('f', 1.0))
            fp.write(struct.pack('f', energy_keV))

            # Tilt
            # DELPHI: l:=4*(N+1); Inc(s,l); BlockWrite(Sf,T,l,w);    Inc(Sum,w);
            a = np.array(options.beam.direction.tolist())
            b = np.array([0, 0, -1])
            angle = math.degrees(np.arccos(np.vdot(a, b) / np.linalg.norm(a)))
            fp.write(struct.pack('f', 1.0))
            fp.write(struct.pack('f', angle))

            # Sputtering
            # DELPHI: l:=4*(N+1); Inc(s,l); BlockWrite(Sf,Sp,l,w);    Inc(Sum,w);
            sputtering = 0.0
            fp.write(struct.pack('f', 1.0))
            fp.write(struct.pack('f', sputtering))

            # String of beam energy
            # DELPHI:
            # l:=1;Inc(s,l); TmpStrLen:=length(EStr); Blockwrite(Sf,TmpStrLen,l,w); Inc(Sum,w);
            # l:=length(Estr);Inc(s,l); Blockwrite(Sf,EStr[1],l,w); Inc(Sum,w);
            energy_keV_str = str(energy_keV).encode('ascii')
            fp.write(struct.pack('b', len(energy_keV_str)))
            fp.write(energy_keV_str)

            # String of tilt
            # DELPHI:
            # l:=1;Inc(s,l); TmpStrLen:=length(TStr); Blockwrite(Sf,TmpStrLen,l,w); Inc(Sum,w);
            # l:=length(Tstr);Inc(s,l); Blockwrite(Sf,TStr[1],l,w); Inc(Sum,w);
            angle_str = str(angle).encode('ascii')
            fp.write(struct.pack('b', len(angle_str)))
            fp.write(angle_str)

            # String of sputtering
            # DELPHI:
            # l:=1;Inc(s,l); TmpStrLen:=length(SpStr); Blockwrite(Sf,TmpStrLen,l,w); Inc(Sum,w);
            # l:=length(Spstr);Inc(s,l); Blockwrite(Sf,SpStr[1],l,w); Inc(Sum,w);
            sputtering_str = str(sputtering).encode('ascii')
            fp.write(struct.pack('b', len(sputtering_str)))
            fp.write(sputtering_str)

        return filepath

    def _export_geometry_substrate(self, options, geometry, outputdir, *args):
        material = geometry.body.material
        composition = sorted(material.composition.items(), key=itemgetter(0))
        density_g_cm3 = material.density_kg_m3 / 1000.0

        filepath = os.path.join(outputdir, options.name + '.MAT')
        with open(filepath, 'wb') as fp:
            # Header
            # DELPHI: s:=6;Blockwrite(Matfile,Typ,6,f);Inc(Sum,f);
            # 1st Byte: Type = 2 (homogenous bulk)
            # 2nd Byte: NC = <nr. of elements> (amount of occurring formulae (compounds or elements))
            # 3rd Byte: NZ = <nr. of elements>
            # 4th Byte: NP = 0 (nr. of layers)
            # 5th Byte: CU = 2 (1=at%, 2=wt%)
            # 6th Byte: MU = 1 (not important for bulk; this is the unit for the layer thickness)
            fp.write(struct.pack('b', 2))
            fp.write(struct.pack('b', len(composition)))
            fp.write(struct.pack('b', len(composition)))
            fp.write(struct.pack('b', 0))
            fp.write(struct.pack('b', 2))
            fp.write(struct.pack('b', 1))

            # Write length of element and element
            # DELPHI:
            # for i:=1 to Nc do begin
            #     l:=1+Length(Comp[i]);Inc(s,l);
            #     Blockwrite(Matfile,Comp[i,0],l,f);Inc(Sum,f);
            # end;
            for z, _wf in composition:
                symbol = ep.symbol(z).upper()
                fp.write(struct.pack('b', len(symbol)) + symbol.encode('ascii'))

            # Write molar mass
            # DELPHI: l:=4*Nc;Inc(s,l);Blockwrite(Matfile,AC[1],l,f);Inc(Sum,f);
            for z, _wf in composition:
                mass = ep.atomic_mass_kg_mol(z) * 1000.0
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
            fp.write(b'\x00\x00\x00\x00') # Skip 4 bytes
            for z, _wf in composition:
                mass = ep.atomic_mass_kg_mol(z) * 1000.0
                fp.write(struct.pack('f', mass))

            for i, item in enumerate(composition):
                z = item[0]
                mass = ep.atomic_mass_kg_mol(z) * 1000.0
                fp.write(struct.pack('f', mass))
                fp.write(b'\x00\x00\x00\x00' * i) # Skip 4 bytes
                fp.write(struct.pack('f', 1.0 / mass))
                fp.write(b'\x00\x00\x00\x00' * (len(composition) - i - 1)) # Skip 4 bytes

            # DELPHI: Inc(s,l);BlockWrite(Matfile,GM,l,f);Inc(Sum,f);
            gs = [wf / (ep.atomic_mass_kg_mol(z) * 1000.0) for z, wf in composition]
            g0 = 1.0 / sum(gs)
            fp.write(struct.pack('f', g0))
            for g in gs:
                fp.write(struct.pack('f', g))

            # DELPHI:
            # for i:=0 to NP do begin
            #     Inc(s,l);BlockWrite(Matfile,GS[i],l,f);Inc(Sum,f);
            # end;
            fp.write(b'\x00\x00\x00\x00' * (len(composition) + 1))

            # DELPHI:
            # l:=4*NP+4;Inc(s,l);Blockwrite(Matfile,ML[0],l,f);Inc(Sum,f);
            fp.write(b'\x00\x00\x00\x00')

            # DELPHI: Inc(s,l);Blockwrite(Matfile,rho[0],l,f);Inc(Sum,f);
            fp.write(struct.pack('f', density_g_cm3))

            # DELPHI:
            # l:=NC+1;
            # for i:=0 to NP do begin
            #     Inc(s,l);BlockWrite(Matfile,PC[i],l,f);Inc(Sum,f);
            # end;
            fp.write(struct.pack('b', len(composition)))
            fp.write(b'\x00' * len(composition))

            # DELPHI: Inc(s,l);BlockWrite(Matfile,PM,l,f);Inc(Sum,f);
            fp.write(struct.pack('b', len(composition)))
            for i in range(len(composition)):
                fp.write(struct.pack('b', i + 1))

        return filepath

if __name__ == '__main__':
    from pymontecarlo.options.options import Options
    from pymontecarlo.options.material import Material

    options = Options('test')
    options.geometry.body.material = Material({6: 0.4, 13: 0.1, 79: 0.5})
    options.limits.add(ShowersLimit(1000))

    Exporter().export(options, '/tmp')
