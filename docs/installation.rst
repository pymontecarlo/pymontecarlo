.. highlight:: shell

============
Installation
============

Stable release
--------------

There are two ways to install **pyMonteCarlo**.
The simplest one is the :ref:`stand-alone version <installation-standalone>`,
which comes as a *zip* file containing an application executable under Windows.
The more advanced one is to install **pyMonteCarlo** as a
:ref:`Python package <installation-python-package>` from the
`Python Package Index (PyPI) <pypi.org>`_.
Instructions for both methods are given below as well as how to
install **pyMonteCarlo** for :ref:`developers <installation-development>`.

.. _installation-standalone:

Stand-alone, graphical user interface
`````````````````````````````````````

.. note::

   Stand-alone version for MacOS and Linux are under development.
   Users of these operating systems can install **pyMonteCarlo** as a Python package.
   See instructions below.

Windows
'''''''

For Windows, **pyMonteCarlo** is packaged as a stand-alone distribution.
It can be downloaded `here <https://www.dropbox.com/s/8n4x8t5eidtpt7r/pymontecarlo-1.0.0%2B14.ga2a4121.zip?dl=0>`_.
To install, simply extract the content of the *zip* file and run *pymontecarlo.exe*.
This distribution is bundled with all :ref:`supported Monte Carlo programs <supported-monte-carlo-programs>`.

.. _installation-python-package:

Python package
``````````````

**pyMonteCarlo** only supports Python 3.7+.
It is recommended to install the latest Python version.
You can download Python from the `official release <https://www.python.org/downloads/>`_.
Using other Python distribution like Anaconda, minconda, etc. should also work.

To install **pyMonteCarlo**, run this command in your command prompt/terminal:

.. code-block:: console

    $ pip install pymontecarlo pymontecarlo-gui

This is the preferred method to install **pyMonteCarlo**, as it will always
install the most recent stable release.

**pyMonteCarlo** package provides the core, common functionalities.
In other words, it does not contain the interface to Monte Carlo programs.
Each interface has its own package.
The supported Monte Carlo programs are listed
:ref:`here <supported-monte-carlo-programs>`.

As a starting point, it is recommended to install *pymontecarlo-casino2*.
Most of the examples in this documentation are based on *pymontecarlo-casino2*.
This Monte Carlo program works on Windows and after installation *Wine* on MacOS
and Linux.
Installation instructions are :ref:`below <installation-wine>`.

.. code-block:: console

    $ pip install pymontecarlo-casino2

If your `PYTHONPATH` is properly configured, you should be able to run
**pyMonteCarlo** graphical user interface by simply typing **pyMonteCarlo** in
a command prompt/terminal:

.. code-block:: console

    $ pymontecarlo

If not, another way to start **pyMonteCarlo** is the following:

.. code-block:: console

    $ python -m pymontecarlo_gui

.. _installation-development:

Development
-----------

.. warning::

   Many projects in the **pyMonteCarlo** organization uses `Git LFS <https://git-lfs.github.com/>`_.
   Please make sure it is installed before cloning any repository.

Clone the **pyMonteCarlo** Github repository, either directly or after forking:

.. code-block:: console

    $ git clone git://github.com/pymontecarlo/pymontecarlo

Install the project in editable mode:

.. code-block:: console

    $ cd pymontecarlo
    $ pip install -e .[dev]

Run the unit tests to make sure everything works properly:

.. code-block:: console

    $ pytest

Repeat the same procedure for any other **pyMonteCarlo** projects in the Github
**pyMonteCarlo** `organization <https://github.com/pymontecarlo>`_.

.. _installation-wine:

Wine
----

`Wine <https://www.winehq.org>`_ is a Windows emulator for MacOS and Linux.
Since some Monte Carlo programs are only available on Windows, *Wine* is a way
to run them on other operating systems.
Please refer to the *Wine* `website <https://www.winehq.org>`_ to download
the latest version and the platform-specific installation instructions.
**pyMonteCarlo** assumes that *Wine* is properly installed and that the `wine`
executable is in the `PATH`.
