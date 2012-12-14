Appendix: Running pymontecarlo on Aachen HPC
============================================

Running simulations using *pymontecarlo* on the Aachen HPC requires a few setup
steps and to know a few commands.

Setup
-----

1. Make sure the module for Python 2.7 and GCC are loaded::

      module load python/2.7.1
      module load GCC/4.6

   .. note::

      It is advisable to add this two commands to the user-specific init file
      (e.g. .bashrc)

2. Some third-party Python libraries are required to run *pymontecarlo* and
   compile *PENELOPE*. First create the directory *lib/python2.7/site-packages*
   inside the home directory::
   
      mkdir -p ~/lib/python2.7/site-packages
      
   This path must be added to the *PYTHONPATH*. This is done by editing 
   user-specific init file (e.g. .bashrc) as follows::
   
      export PYTHONPATH=$PYTHONPATH:$HOME/lib/python2.7/site-packages
   
   A quick way to install Python libraries is using the *distribute* tool. 
   First download the *distribute* tarball from this address and extract the 
   tarball::
   
      wget http://pypi.python.org/packages/source/d/distribute/distribute-0.6.32.tar.gz#md5=acb7a2da81e3612bfb1608abe4f0e568
      tar -xvzf distribute-0.6.32.tar.gz
      cd distribute-0.6.32
   
   Run the setup.py to install the package::
   
      python setup.py install --prefix=$HOME
   
   The argument ``--prefix=$HOME`` is important as it tells Python to install
   this package in the *~/lib/python2.7/site-packages*. After the installation,
   the tarball and *distribute-0.6.32* directory can be deleted.
   
   Now the following libraries should be installed:
   
      * pyparsing
      * h5py
      * hgtools
      * lxml
      * matplotlib
      
   .. note::
   
      *pymontecarlo* also requires *numpy* but this should already be installed
      on the HPC.
      
   Here is how to install each library::
   
      easy_install --prefix=$HOME pyparsing
      easy_install --prefix=$HOME h5py
      easy_install --prefix=$HOME hgtools
      easy_install --prefix=$HOME lxml
      easy_install --prefix=$HOME matplotlib
   
   To test that all packages are well installed, start a python prompt and 
   execute the following Python command::
   
      import pyparsing
      import h5py
      import hgtools
      import lxml
      import matplotlib
   
   If no ``ImportError`` is returned, then the installation is complete.

3. The next step is clone the *pymontecarlo*, *penelope* and *penepma-dev*
   repositories from bitbucket. It is advisable to clone these projects in a
   directory called *workspace* in the user's home directory::
   
      mkdir -p ~/workspace
      hg clone ssh://hg@bitbucket.org/pymontecarlo/pymontecarlo
      hg clone ssh://hg@bitbucket.org/pymontecarlo/penelope
      hg clone ssh://hg@bitbucket.org/pymontecarlo/penepma-dev
   
   .. warning::
   
      You will need to setup a SSH key on the HPC to access bitbucket 
      repository. Use the command: *ssh-keygen*.

4. These libraries must be added to the *PYTHONPATH*. Please modify the
   user-specific init file (e.g. .bashrc) as follows::

      export PYTHONPATH=$PYTHONPATH:$HOME/lib/python2.7/site-packages
      export PYTHONPATH=$PYTHONPATH:$HOME/workspace/pymontecarlo/code
      export PYTHONPATH=$PYTHONPATH:$HOME/workspace/penelope/src/pysource

5. Here is how to compile *PENELOPE* and its Python library *penelopelib*:: 

      cd ~/workspace/penelope
      python setup.py build_ext --inplace

   .. note::
   
      *PENELOPE* must be recompiled every time a new revision is pulled from 
      the repository.
      
   To test if the compilation worked, open a python prompt and type::
      
      import penelopelib.material

6. Here is how to compile *PENEPMA*::
   
      cd ~/workspace/penepma-dev/src
      gfortran -O2 -g -Wall -c penepma.f penelope.f rita.f pengeom.f penvared.f timer.f
      gfortran -static-libgcc -static-libgfortran *.o -o ../bin/penepma
   
   .. note::
   
      *PENEPMA* must be recompiled every time a new revision is pulled from 
      the repository.

7. *pymontecarlo* must be configured to specify where the *PENEPMA* executable
   is.
   This is done by running the configuration command line interface of
   *pymontecarlo*::
   
      python ~/workspace/pymontecarlo/code/pymontecarlo/ui/cli/configure.py
   
   At the moment, you only need to configure the program *penepma*.

8. To run jobs on the HPC, some scripts are required. Please create the
   following files in the user's bin directory (*~/bin*).

   **lsfpymontecarlo.lsf**::
   
      #!/bin/bash
      #BSUB -J pymontecarlo
      #BSUB -o pymontecarlo_%J.out
      #BSUB -W 23:30
      #BSUB -M 1024
      #BSUB -u <ENTER EMAIL ADDRESS>
      ###BSUB -N
      
      source $HOME/.bashrc
      
      python $HOME/bin/lsfpymontecarlo.lsf.py
      
   Replace ``<ENTER EMAIL ADDRESS>`` by an email address.

   **lsfpymontecarlo.lsf.py**::
   
      #!/usr/bin/env python

      import os
      import sys
      
      print sys.path
      
      stdin = sys.stdin.read()
      program, inputfile = stdin.split(";")
      
      inputfile = os.path.abspath(inputfile)
      outputdir = os.path.dirname(inputfile)
      
      args = []
      args += ['python', '$HOME/workspace/pymontecarlo/code/pymontecarlo/ui/cli/main.py']
      args += ['-v'] # verbose
      args += ['-s'] # skip existing results
      args += ['-q'] # quiet
      args += ['-n', '1'] # one processor
      args += ['--' + program] # program
      args += ['-o', outputdir] # output dir
      args += [inputfile] # input file
      
      os.chdir(outputdir)
      
      cmd = ' '.join(args)
      print cmd
      os.system(cmd)
      
   **lsfpymontecarlo.py**::
   
      #!/usr/bin/env python

      import os
      import sys
      import optparse
      
      # parser
      parser = optparse.OptionParser()
      parser.add_option("-p", "--program", dest="program", action="store",
                        help="Alias of the program to use")
      parser.add_option('-q', '--quiet', dest='quiet', action='store_true',
                        help='Activate quiet mode')
      
      options, args = parser.parse_args()
      
      if not options.program:
           print 'Please specify a program'
           sys.exit(1)
      
      quiet = options.quiet
      
      if not args:
           print "Please specify a directory"
           sys.exit(1)
      elif len(args) != 1:
           print "Please specify only one directory"
           sys.exit(1)
      
      searchdir = os.path.abspath(args[0])
      print "Searching in %s" % searchdir
      
      count = 1
      for root, dirs, files in os.walk(searchdir):
          for file in files:
               base, ext = os.path.splitext(file)
               if ext == '.xml':
                    if os.path.exists(os.path.join(root, base + '.zip')):
                         if not quiet:
                              print 'Skipping: %s' % os.path.join(root, file)
                         continue
      
                    print 'Found: %s' % os.path.join(root, file)
                    with open('input.%i' % count, 'w') as f:
                        f.write('%s;%s' % (options.program, os.path.join(root, file)))
                    count += 1
            
Run job(s) on HPC
-----------------

Before running any job on the HPC, please ensure that you have the latest
version of *pymontecarlo*, *penelope* and *penepma-dev* respositories and that
*penelope* and *penepma-dev* have been compiled properly.
The HPC requires that all job files be located in the cluster work folder.
It is advisable to create a symbolic link to this folder in the user's home
directory::

   ln -s /rwthfs/rz/cluster/work/ab123456 ~/work

Running any simulation on the HPC requires three steps:

   1. Create input files specifying the Monte Carlo program and location of
      each option XML file.
   2. Editing the *lsfpymontecarlo.lsf* to adjust the maximum running time.
   3. Submitting a job array to the HPC.

After transfering the options files (``.xml``) in the work directory or
a sub-directory of the work directory, run the following command inside the
folder to create the input files::

   python ~/bin/lsfpymontecarlo.py -p PROGRAM .

Replace ``PROGRAM`` by the Monte Carlo program you want to use,
for example, ``penepma``.
This will create a ``input.X`` file for each XML file found inside the folder.

The *lsfpymontecarlo.lsf* file in the user's *bin* directory contains the flag
``#BSUB -W`` which specifies the maximum running time.
The running time cannot be longer than 24 hours and it should be adjusted to
match the simulation running time.
Jobs with a smaller running time have a higher chance of being run before longer
jobs.

To submit the jobs to the HPC, use the following command::

   bsub -J "NAME[1-NBSIM]" -i "input.%I" < /home/ab123456/bin/lsfpymontecarlo.lsf
   
Replace ``NAME`` with a name of the simulations you are about to run, ``NBSIM``
with the total number of simulations and ``ab123456`` with your TIM number.

.. warning::

   A maximum of 1000 jobs can be submitted at once (i.e. NBSIM <= 1000).
   However, multiple *bsub* can be executed one after another.
   
Finally, to see the status of the submitted job, use the command::

   bjobs -A

