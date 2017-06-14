Developper guide
================

Install the package in development mode::

   py -3 -m pip install -e .

See the list of installed packages in development mode::

   py -3 -m pip list -e.

Create a pip wheel file using setup.py::

   py -2 setup.py bdist_wheel -d dist
   py -3 setup.py bdist_wheel -d dist

For example if the projects are in the pymontecarlo folder and the command line in that folder::

   D:\work\codings> cd pyMonteCarlo

   D:\work\codings\pymontecarlo> dir
    Volume in drive D is Data2
    Volume Serial Number is EEC6-53A1

    Directory of D:\work\codings\pymontecarlo

   2015-08-26  18:30    <DIR>          .
   2015-08-26  18:30    <DIR>          ..
   2015-08-26  18:19    <DIR>          dtsa
   2014-12-18  10:32    <DIR>          monsel
   2014-12-18  11:28    <DIR>          penelope
   2014-12-18  10:48    <DIR>          penepma
   2014-12-18  10:32    <DIR>          penshower
   2014-12-19  17:22    <DIR>          pymontecarlo
   2014-12-09  15:19    <DIR>          pymontecarlo-casino2
   2014-12-09  15:18    <DIR>          pymontecarlo-casino3
   2014-12-19  17:27    <DIR>          pymontecarlo-cli
   2014-10-13  14:47    <DIR>          pymontecarlo-dtsa
   2014-12-18  10:12    <DIR>          pymontecarlo-dtsa2
   2014-12-19  17:44    <DIR>          pymontecarlo-dtsa2-java
   2014-12-19  17:48    <DIR>          pymontecarlo-gui
   2014-12-09  15:18    <DIR>          pymontecarlo-mcxray
   2014-12-09  15:17    <DIR>          pymontecarlo-monaco
   2014-12-09  15:16    <DIR>          pymontecarlo-penelope
   2014-12-18  11:25    <DIR>          pymontecarlo-penelope-fortran
   2014-12-09  15:19    <DIR>          pymontecarlo-pouchou
   2014-12-18  10:30    <DIR>          pymontecarlo-reconstruction
   2014-12-19  17:33    <DIR>          pymontecarlo-winxray
   2015-02-10  12:01    <DIR>          pymontecarlo.bitbucket.org
   2014-12-18  11:17    <DIR>          pypenelopelib
                  1 File(s)          1,980 bytes
                 24 Dir(s)  118,604,918,784 bytes free

These commands will install the projects in developer mode::

   py -3 -m pip install -e pymontecarlo
   py -3 -m pip install -e pymontecarlo-casino2
   py -3 -m pip install -e pymontecarlo-casino3
   py -3 -m pip install -e pymontecarlo-cli
   py -3 -m pip install -e pymontecarlo-dtsa2
   py -3 -m pip install -e pymontecarlo-gui
   py -3 -m pip install -e pymontecarlo-mcxray
   py -3 -m pip install -e pymontecarlo-monaco
   py -3 -m pip install -e pymontecarlo-penelope
   py -3 -m pip install -e pymontecarlo-pouchou
   py -3 -m pip install -e pymontecarlo-reconstruction
   py -3 -m pip install -e pymontecarlo-winxray
   py -3 -m pip install -e pypenelopelib

Build the doc
-------------

To build the doc you will need the pybtex package::

   py -3 -m pip install -U pybtex

Go into the doc folder::

   pymontecarlo/doc

Run::

   sphinx-build -b html www build

To build the code documentation, run::

   sphinx-apidoc -o www/code ../pymontecarlo
