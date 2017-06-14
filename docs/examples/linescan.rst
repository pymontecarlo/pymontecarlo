Line scan across a Fe-Ni couple
###############################

This examples shows how to setup a :ref:`grainboundaries` geometry, perform
a line scan across the interface and extract x-ray intensities 
(:ref:`detector <photonintensitydetector>` and 
:ref:`result <photonintensityresult>`) from the simulations. 
The simulation will be run using :ref:`nistmonte` with the fluorescence 
algorithm activated.
The last part of the script plots the Fe and Ni intensities using the library
matplotlib. 

.. literalinclude:: linescan.py

