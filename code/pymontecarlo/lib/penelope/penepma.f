      INCLUDE 'penelope.f'  ! Files included to simplify compilation.
      INCLUDE 'rita.f'
      INCLUDE 'pengeom.f'
      INCLUDE 'penvared.f'
      INCLUDE 'timer.f'

CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C                                                                      C
C        PPPPP   EEEEEE  N    N  EEEEEE  PPPPP   M    M    AA          C
C        P    P  E       NN   N  E       P    P  MM  MM   A  A         C
C        P    P  E       N N  N  E       P    P  M MM M  A    A        C
C        PPPPP   EEEE    N  N N  EEEE    PPPPP   M    M  AAAAAA        C
C        P       E       N   NN  E       P       M    M  A    A        C
C        P       EEEEEE  N    N  EEEEEE  P       M    M  A    A        C
C                                                                      C
C                                                   (version 2011).    C
C                                                                      C
C  This program performs Monte Carlo simulation of electron-probe      C
C  microanalysis (EPMA) measurements, that is, of x-ray emission from  C
C  targets irradiated by electron beams. The geometry of the sample    C
C  is described by means of the quadric geometry package 'PENGEOM.F'.  C
C                                                                      C
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C                                                                      C
C  PENELOPE/PENGEOM (version 2011)                                     C
C  Copyright (c) 2001-2011                                             C
C  Universitat de Barcelona                                            C
C                                                                      C
C  Permission to use, copy, modify, distribute and sell this software  C
C  and its documentation for any purpose is hereby granted without     C
C  fee, provided that the above copyright notice appears in all        C
C  copies and that both that copyright notice and this permission      C
C  notice appear in all supporting documentation. The Universitat de   C
C  Barcelona makes no representations about the suitability of this    C
C  software for any purpose. It is provided 'as is' without express    C
C  or implied warranty.                                                C
C                                                                      C
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C
C  >>>>>>>> NOTE: All energies and lengths are given in eV and cm,
C                 respectively.
C
C
C  ************  Structure of the input data file.
C
C  Each line in the input data file consists of a 6-character keyword
C  (columns 1-6) followed either by numerical data (in free format) or
C  by a character string, which start at the 8th column. Keywords are
C  explicitly used/verified by the program (which is case sensitive!).
C  Notice also that the order of the data lines is important. The
C  keyword '______' (6 blanks) indicates comment lines, these can be
C  placed anywhere in the input file. The program ignores any text
C  following the first blank after the last numerical datum, or after
C  the character string, in each line (thus, in the table given below,
C  the comments in square brackets are ignored by the program). Lines
C  with some keywords (e.g., 'PDANGL', 'PDENER') can appear an arbitrary
C  number of times, limited only by the allocated amount of memory.
C
C  The program assigns default values to many input variables; lines
C  that declare default values may be eliminated from the input file.
C
C
C  The structure of the input file is the following,
C
C  ....+....1....+....2....+....3....+....4....+....5....+....6....+....
C  TITLE  Title of the job, up to 120 characters.
C         . (the dot prevents editors from removing trailing blanks)
C         >>>>>>>> Electron beam definition.
C  SENERG SE0                              [Energy of the electron beam]
C  SPOSIT SX0,SY0,SZ0               [Coordinates of the electron source]
C  SDIREC STHETA,SPHI        [Direction angles of the beam axis, in deg]
C  SAPERT SALPHA                                 [Beam aperture, in deg]
C  SDIAM  SDIAM                                   [Beam diameter, in cm]
C         .
C         >>>>>>>> Material data and simulation parameters.
C                  Up to 10 materials; 2 lines for each material.
C  MFNAME mat-filename.ext               [Material file, up to 20 chars]
C  MSIMPA EABS(1:3),C1,C2,WCC,WCR              [EABS(1:3),C1,C2,WCC,WCR]
C         .
C         >>>>>>>> Geometry of the sample.
C  GEOMFN geo-filename.ext          [Geometry definition file, 20 chars]
C  DSMAX  IBODY,DSMAX(IBODY)   [IB, maximum step length (cm) in body IB]
C         .
C         >>>>>>>> Interaction forcing.
C  IFORCE KB,KPAR,ICOL,FORCER,WLOW,WHIG  [KB,KPAR,ICOL,FORCER,WLOW,WHIG]
C         .
C         >>>>>>>> Emerging particles. Energy and angular distributions.
C  NBE    EMIN,EMAX,NBE              [E-interval and no. of energy bins]
C  NBTH   NBTH                   [No. of bins for the polar angle THETA]
C  NBPH   NBPH                 [No. of bins for the azimuthal angle PHI]
C         .
C         >>>>>>>> Photon detectors (up to 25 different detectors).
C         IPSF=0, the psf is not created.
C         IPSF=1, a psf is created.
C         IPSF>1, a psf is created, but contains only state variables
C                 of detected photons that have ILB(4)=IPSF (used for
C                 studying angular distributions of x rays).
C  PDANGL THETA1,THETA2,PHI1,PHI2,IPSF    [Angular window, in deg, IPSF]
C  PDENER EDEL,EDEU,NCHE                [Energy window, no. of channels]
C  XRORIG xorigID.dat         [Map of emission sites of detected x-rays]
C         .
C         >>>>>>>> Spatial distribution of events.
C  GRIDX  XL,XU                      [X coordinates of the box vertices]
C  GRIDY  YL,YU                      [Y coordinates of the box vertices]
C  GRIDZ  ZL,ZU                      [Z coordinates of the box vertices]
C  GRIDBN NX,NY,NZ                                     [Numbers of bins]
C  XRAYE  EMIN,EMAX           [Energy interval where x-rays are tallied]
C         .
C         >>>>>>>> Phi rho z distributions.
C  PRZ    IZ,IS1,IS2,IPD  [prz for transition IZ,IS1,IS of detector IPD]
C         .
C         >>>>>>>> Job properties.
C  RESUME dumpfile1.dat           [Resume from this dump file, 20 chars]
C  DUMPTO dumpfile2.dat              [Generate this dump file, 20 chars]
C  DUMPP  DUMPP                                 [Dumping period, in sec]
C         .
C  NSIMSH DSHN                     [Desired number of simulated showers]
C  RSEED  ISEED1,ISEED2           [Seeds of the random-number generator]
C  TIME   TIMEA                       [Allotted simulation time, in sec]
C  XLIM   IZ,IS1,IS2,IPD,UNC,UNCF       [Uncertainty limit on intensity]
C  ....+....1....+....2....+....3....+....4....+....5....+....6....+....
C
C
C  The following listing describes the function of each of the keywords,
C  the accompanying data and their default values. For clarity, blanks
C  in keywords are indicated as '_'.
C
C  TITLE_ : Title of the job (up to 120 characters).
C             DEFAULT: none (the input file must start with this line)
C
C           The TITLE string is used to mark dump files. To prevent the
C           improper use of wrong resuming files, change the title each
C           time you modify basic parameters of your problem. The code
C           will then be able to identify the inconsistency and to print
C           an error message before stopping.
C
C  >>>>>>>> Electron beam definition.
C
C  SENERG : Initial energy of the electron beam.
C             DEFAULT: SE0=1.0E5
C
C  SPOSIT : Coordinates of the electron source.
C             DEFAULT: SX0=SY0=0.0, SZ0=10.0E0
C  SDIREC : Polar and azimuthal angles of the electron beam axis direc-
C           tion, in deg.
C             DEFAULTS: STHETA=180.0, SPHI=0.0
C  SAPERT : Angular aperture of the electron beam, in deg.
C             DEFAULT: SALPHA=0.0
C
C           --> Notice that the default beam is a pencil beam that
C           moves downwards along the Z-axis.
C  SDIAM  : Diameter of the electron beam, in cm.
C             DEFAULT: SDIAM=10.0E-7 ! 10 nm
C
C  >>>>>>>> Material data and simulation parameters.
C
C  Each material is defined by introducing the following _two_ lines;
C
C  MFNAME : Name of a PENELOPE input material data file (up to 20
C           characters). This file must be generated in advance by
C           running the program MATERIAL.
C             DEFAULT: none
C
C  MSIMPA : Set of simulation parameters for this material; absorption
C           energies, EABS(1:3,M), elastic scattering parameters, C1(M)
C           and C2(M), and cutoff energy losses for inelastic collisions
C           and bremsstrahlung emission, WCC(M) and WCR(M).
C             DEFAULTS: EABS(1,M)=EABS(3,M)=0.01*EPMAX,
C                       EABS(2,M)=0.001*EPMAX
C                       C1(M)=C2(M)=0.1, WCC=EABS(1,M), WCR=EABS(2,M)
C             EPMAX is the upper limit of the energy interval covered
C             by the simulation lookup tables.
C
C  Note that we must declare a separate material data file name and a
C  set of simulation parameters for each material. The label (material
C  number) asigned by PENELOPE to each material is determined by the
C  ordering of the material data files in the PENMAIN input file. That
C  is, the first, second, ... materials are assigned the labels 1, 2,
C  ... These labels are also used in the geometry definition file.
C
C  The original programs in the distribution package allow up to 10
C  materials. This number can be increased by changing the value of the
C  parameter MAXMAT in the original source files.
C
C  >>>>>>>> Geometry of the sample.
C
C  GEOMFN : PENGEOM geometry definition file name (a string of up to
C           20 characters). It is assumed that the sample is located at
C           the origin of coordinates, with its surface at the z=0
C           plane.
C             DEFAULT: none.
C
C           --> The geometry definition file can be debugged/visualised
C           with the viewers GVIEW2D and GVIEW3D (operable only under
C           Windows).
C
C  DSMAX_ : Maximum step length DSMAX(IB) of electrons and positrons in
C           body IB. This parameter is important only for thin bodies;
C           it should be given a value of the order of one tenth of the
C           body thickness or less.
C             DEFAULT: DSMAX=1.0E20 (no step length control)
C
C  >>>>>>>> Interaction forcing.
C
C  IFORCE : Activates forcing of interactions of type ICOL of particles
C           KPAR in body KB. FORCER is the forcing factor, which must
C           be larger than unity. WLOW and WHIG are the lower and upper
C           limits of the weight window where interaction forcing is
C           applied.
C             DEFAULT: no interaction forcing
C
C           If the mean free path for real interactions of type ICOL is
C           MFP, the program will simulate interactions of this type
C           (real or forced) with an effective mean free path equal to
C           MFP/FORCER.
C
C           TRICK: a negative input value of FORCER, -FN, is  assumed to
C           mean that each particle should interact, on average and
C           approximately, +FN times in a path length equal to the range
C           of that kind of particle with E=EPMAX. This is very useful
C           to generate x-ray spectra from bulk samples.
C
C  The real effect of interaction forcing on the efficiency is not easy
C  to predict. Please, do tentative runs with different FORCER values
C  and check the efficiency gain (or loss!).
C
C  >>>>>>>> Energy and angular distributions of emerging particles.
C
C  NBE___ : Limits EMIN and EMAX of the interval where energy
C           distributions of emerging particles are tallied. Number of
C           energy bins.
C             DEFAULT: EMIN=0.0, EMAX=EPMAX, NBE=500
C
C  NBTH__ : Number of bins for the polar angle THETA.
C             DEFAULT: NBTH=90
C
C           WARNING: In the output files, the terms 'transmitted' and
C           'backscattered' are used to denote particles that leave the
C           sample moving upwards (THETA>0) and downwards (THETA<0),
C           respectively.
C
C  NBPH__ : Number of bins for the azimuthal angle PHI.
C             DEFAULT: NBPH=60
C
C  >>>>>>>> Photon detectors.
C
C  Each detector collects photons that leave the sample with directions
C  within a 'rectangle' on the unit sphere, limited by the 'parallels'
C  THETA1 and THETA2 and the 'meridians' PHI1 and PHI2. The output
C  spectrum is the energy distribution of photons that emerge within the
C  acceptance solid angle of the detector with energies in the interval
C  from EDEL to EDEU, recorded using NCHE channels. Notice that the
C  spectrum is given in absolute units (per incident electron, per eV
C  and per unit solid angle).
C
C  PDANGL : Starts the definition of a new detector. Up to 25 different
C           detectors can be defined. THETA1,THETA2 and PHI1,PHI2 are
C           the limits of the angular intervals covered by the detector,
C           in degrees.
C
C           The integer flag IPSF serves to activate the creation of a
C           phase-space file (psf), which contains the state variables
C           and weigths of particles that enter the detector. Use this
C           option with care, because psf's may grow very fast.
C           IPSF=0, the psf is not created.
C           IPSF=1, a psf is created.
C           IPSF>1, a psf is created, but contains only state variables
C                   of detected photons that have ILB(4)=IPSF (used for
C                   studying angular distributions of x rays).
C           Generating the psf is useful for tuning interaction forcing,
C           which requires knowing the weights of detected particles.
C
C             DEFAULTS: THETA1=35, THETA2=45, PHI1=0, PHI2=360, IPSF=0
C
C           NOTE: PHI1 and PHI2 must be both either in the interval
C           (0,360) or in the interval (-180,180).
C
C  PDENER : EDEL and EDEU are the lower and upper limits of the energy
C           window covered by the detector.
C           NCHE is the number of energy channels in the output spectrum
C           (.LE. 1000).
C             DEFAULT: EDEL=0.0, EDU=E0, NCHE=1000
C
C  XRORIG : This line in the input file activates the generation of a
C           file with the position coordinates of the emission sites of
C           the photons that reach the detector. The file name must be
C           explicitly defined. Notice that the file may grow very fast,
C           so use this option only in short runs. The output file is
C           overwritten when a simulation is resumed.
C             DEFAULT: NONE
C
C  >>>>>>>> Spatial distribution of x-ray emission.
C
C  The program can generate the space distribution of x-ray emission
C  inside a parallelepiped (the scoring box) whose edges are parallel to
C  the axes of the laboratory frame. This box is defined by giving the
C  coordinates of its vertices. The distribution of x-ray generation
C  events is tallied using a uniform orthogonal grid with NX, NY and NZ
C  (.LE. 100) bins along the directions of the coordinate axes.
C
C  GRIDX_ : X-coordinates of the vertices of the scoring box.
C             DEFAULT: None
C  GRIDY_ : Y-coordinates of the vertices of the scoring box.
C             DEFAULT: None
C  GRIDZ_ : Z-coordinates of the vertices of the scoring box.
C             DEFAULT: None
C  GRIDBN : Numbers of bins NX, NY, and NZ in the X, Y and Z directions,
C           respectively.
C             DEFAULTS: NX=50, NY=50, NZ=50
C  XRAYE_ : Limits EMIN and EMAX of the energy interval where x rays are
C           scored.
C             DEFAULTS: none
C
C  >>>>>>>> Job properties.
C
C  RESUME : The program will read the dump file named `dumpfile-1.dat'
C           (20 characters) and resume the simulation from the point
C           where it was left. Use this option very, _VERY_ carefully.
C           Make sure that the input data file is fully consistent with
C           the one used to generate the dump file.
C             DEFAULT: off
C
C  DUMPTO : Generate a dump file named 'dumpfile-2.ext' (20 characters)
C           after completing the simulation run. This allows resuming
C           the simulation later on to improve statistics.
C             DEFAULT: off
C
C           NOTE: If the file 'dumpfile-2.ext' already exists, it is
C           overwritten.
C
C  DUMPP_ : When the DUMPTO option is activated, simulation results are
C           written in the output files every DUMPP seconds. This option
C           is useful to check the progress of long simulations. It also
C           allows running the program with a long execution time and
C           stopping it when the required statistical uncertainty has
C           been reached.
C             DEFAULT: DUMPP=1.0E15
C
C  NSIMSH : Desired number of simulated showers.
C             DEFAULT: DSHN=2.0E9
C
C  RSEED_ : Seeds of the random-number generator.
C             DEFAULT: ISEED1=1, ISEED2=2
C
C  TIME__ : Allotted simulation time, in sec.
C             DEFAULT: TIMEA=100.0E0
C  XLIM__ : Uncertainty limit on the intensity of a characteristic
C           x-ray line. The simulation stops when the relative
C           uncertainty on the total intensity and/or the total
C           fluorescence intensity of the specified characteristic
C           line is below the specified limits. This check is performed
C           on all detectors or only a particular one.

C             IZ: atomic number of the characteristic x-ray line
C            IS1: label of the destination atomic electron shell
C            IS2: label of the source atomic electron shell
C            IPD: id of the detector from which the intensities are
C                 used to evalute the simulation uncertainties
C                 IPD=0, the simulation stops when the uncertainty is
C                        below the limit for all detectors
C                 IPD<0, the simulation stops when the uncertainty is
C                        below the limit of any detector
C                 IPD>0, the simulation stops when the uncertainty is
C                        below the limit of the specified detector
C            UNC: relative uncertainty limit on the total intensity.
C                 A fraction between 0.0 and 1.0.
C           UNCF: relative uncertainty limit on the total fluorescence
C                 intensity. A fraction between 0.0 and 1.0.
C
C           DEFAULT: Uncertainty limit is deactivated, equivalent to
C                    setting UNC=UNCF=0.0
C
C  The program is aborted when an incorrect input datum is found. The
C  conflicting quantity usually appears in the last line of the output
C  file. If the trouble is with arrays having dimensions smaller than
C  required, the program indicates how the problem can be solved (this
C  usually requires editing the source file, be careful).
C
C  The clock subroutine (TIMER) may have to be adapted to your specific
C  computer-compiler configuration; standard FORTRAN 77 does not provide
C  timing tools. However, the routines in module TIMER.F do work for
C  many FORTRAN compilers.
C
C  ************  Generating the executable PENEPMA and running it.
C
C  To generate the executable binary file PENEPMA.EXE, compile and link
C  the FORTRAN 77 source files PENEPMA.F, PENELOPE.F, PENGEOM.F,
C  PENVARED.F and TIMER.F. For example, if you are using the g77
C  compiler under Windows, place these five files in the same directory,
C  open a DOS window and from that directory enter the command
C    `g77 -Wall -O PENEPMA.F -o PENEPMA.EXE'
C  (The same, with file names in lowercase, should work under Linux).
C
C  To run PENEPMA, you have to generate an input data file, let's call
C  it PENEPMA.IN, and the corresponding geometry definition and material
C  data files. Place these three files and the binary file PEMEPMA.EXE
c  in the same directory and, from there, issue the command
C    `PENEPMA.EXE < PENEPMA.IN'
C
C  The calculated distributions are written in separate files, whose
C  names start with 'pe-' (for PenEpma) and have the extension '.dat'.
C  These files are in a format suited for direct visualisation with
C  GNUPLOT (version 4.0).
C
C  *********************************************************************
C                       MAIN PROGRAM
C  *********************************************************************
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER LIT*2,LCH10*10,DATE23*23
      CHARACTER*20 PMFILE,PFILE,SPCDIO,PFILED,PFILER,PSFDIO,PORIG
      CHARACTER*120 TITLE,TITLE2,BUFFER,BUF2,BUF3,BUF4,BUF5
      CHARACTER*200 PSFREC
      CHARACTER CS2(30)*2
      DATA CS2 /' K','L1','L2','L3','M1','M2','M3','M4','M5','N1','N2',
     1     'N3','N4','N5','N6','N7','O1','O2','O3','O4','O5','O6','O7',
     2     'P1','P2','P3','P4','P5','Q1',' X'/
C
      CHARACTER*6 KWORD,
     1  KWTITL,KWSENE,KWSPOS,KWSDIR,  KWSAPE,KWSDIA,KWMATF,KWSIMP,
     1  KWGEOM,KWSMAX,KWIFOR,KWNBE ,  KWNBTH,KWNBPH,KWDANG,KWDENE,
     1  KWORIG,KGRDXX,KGRDYY,KGRDZZ,  KGRDBN,KEVENT,
     1  KWRESU,KWDUMP,KWDMPP,KWNSIM,  KWRSEE,KWTIME,KWXLIM,KWPRZ ,
     1  KWCOMM
      PARAMETER(
     1  KWTITL='TITLE ',KWSENE='SENERG',KWSPOS='SPOSIT',KWSDIR='SDIREC',
     1  KWSAPE='SAPERT',KWSDIA='SDIAM ',KWMATF='MFNAME',KWSIMP='MSIMPA',
     1  KWGEOM='GEOMFN',KWSMAX='DSMAX ',KWIFOR='IFORCE',KWNBE ='NBE   ',
     1  KWNBTH='NBTH  ',KWNBPH='NBPH  ',KWDANG='PDANGL',KWDENE='PDENER',
     1  KWORIG='XRORIG',KGRDXX='GRIDX ',KGRDYY='GRIDY ',KGRDZZ='GRIDZ ',
     1  KGRDBN='GRIDBN',KEVENT='XRAYE ',
     1  KWRESU='RESUME',KWDUMP='DUMPTO',KWDMPP='DUMPP ',KWNSIM='NSIMSH',
     1  KWRSEE='RSEED ',KWTIME='TIME  ',KWXLIM='XLIM  ',KWPRZ ='PRZ   ',
     1  KWCOMM='      ')
C
      PARAMETER (PI=3.1415926535897932D0, TWOPI=2.0D0*PI,
     1  RA2DE=180.0D0/PI, DE2RA=PI/180.0D0)
C
C  ****  Main-PENELOPE commons.
C
      PARAMETER(MAXMAT=10)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,MAT,ILB(5)
      COMMON/RSEED/ISEED1,ISEED2
      DIMENSION PMFILE(MAXMAT)
C  ****  Composition data.
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****  Geometry.
      PARAMETER (NS=10000,NB=5000,NX=250)
      COMMON/QTREE/NBODY,MATER(NB),KMOTH(NB),KDGHT(NB,NX),
     1    KSURF(NB,NX),KFLAG(NB,NX),KALIAS(NS),NWARN
      COMMON/QKDET/KDET(NB)
      DIMENSION PARINP(20)
      DIMENSION DSMAX(NB)
C  ****  Interaction forcing parameters.
      DIMENSION IFORCE(NB,3),WLOW(NB,3),WHIG(NB,3)
      COMMON/CFORCE/FORCE(NB,3,8)
C
C  ************  Discrete counters.
C
      DIMENSION
     1  PRIM(3),PRIM2(3),DPRIM(3),     ! Numbers of IEXIT particles.
     1  SEC(3,3),SEC2(3,3),DSEC(3,3)   ! Generated secondary particles.
      DATA PRIM,PRIM2,SEC,SEC2/24*0.0D0/
      DIMENSION WSEC(3,3),WSEC2(3,3)
C  ----  Deposited energies in various bodies.
      DIMENSION TDEBO(NB),TDEBO2(NB),DEBO(NB)
C
C  ************  Continuous distributions.
C
C  ----  Energy distributions of emerging particles.
      PARAMETER (NBEM=1000)
      DIMENSION BSE(3)
      DIMENSION PDE(3,2,NBEM),PDE2(3,2,NBEM),PDEP(3,2,NBEM),
     1          LPDE(3,2,NBEM)
C
C  ----  Angular distributions of emerging particles.
      PARAMETER (NBTHM=90,NBPHM=60)
      DIMENSION PDA(3,NBTHM,NBPHM),PDA2(3,NBTHM,NBPHM),
     1          PDAP(3,NBTHM,NBPHM),LPDA(3,NBTHM,NBPHM)
C
      DIMENSION PDAT(3,NBTHM),PDAT2(3,NBTHM),PDATP(3,NBTHM),
     1  LPDAT(3,NBTHM)
C
C  ----  Photon detectors (up to NEDM different detectors).
      PARAMETER (NEDM=50,NEDCM=1000)
      DIMENSION IORIG(NEDM)
      DIMENSION DET(NEDM,NEDCM),DET2(NEDM,NEDCM),DETP(NEDM,NEDCM),
     1  LDET(NEDM,NEDCM),TDED(NEDM),TDED2(NEDM),DEDE(NEDM)
      DIMENSION EDEL(NEDM),EDEU(NEDM),BDEE(NEDM),NDECH(NEDM)
      DIMENSION THETA1(NEDM),THETA2(NEDM),PHI1(NEDM),PHI2(NEDM)
C
      DIMENSION DoT(NEDM,NEDCM),DoT2(NEDM,NEDCM),DoTP(NEDM,NEDCM),
     1  LDoT(NEDM,NEDCM)
C
      DIMENSION DoF(NEDM,NEDCM),DoF2(NEDM,NEDCM),DoFP(NEDM,NEDCM),
     1  LDoF(NEDM,NEDCM)
C
      DIMENSION RLAST(NEDM),RWRITE(NEDM),PSFDIO(NEDM),IPSF(NEDM)
C
C  ----  Event map (up to NDXM bins along each coord. axis).
      PARAMETER (NDXM=100,NDYM=100,NDZM=100)
      DIMENSION DOEV(NDXM,NDYM,NDZM),DOEV2(NDXM,NDYM,NDZM),
     1          DOEVP(NDXM,NDYM,NDZM),LDOEV(NDXM,NDYM,NDZM)
      DIMENSION DXL(3),DXU(3),BDOEV(3),BDOEVR(3),NDB(3)
C
C  ----  Intensities of characteristic photons at the detectors.
      PARAMETER (NTRANS=1000,NIZ=99,NIS=30)
      PARAMETER (NILB5=3)
      DIMENSION IZS(NTRANS),IS1S(NTRANS),IS2S(NTRANS),ENERGS(NTRANS)
      DIMENSION PTIoT(NEDM,NIZ,NIS,NIS),PTIoT2(NEDM,NIZ,NIS,NIS),
     1  PTIoTP(NEDM,NIZ,NIS,NIS),LPTIoT(NEDM,NIZ,NIS,NIS)
      DIMENSION PTIoF(NEDM,NIZ,NIS,NIS,NILB5),
     1  PTIoF2(NEDM,NIZ,NIS,NIS,NILB5),PTIoFP(NEDM,NIZ,NIS,NIS,NILB5),
     1  LPTIoF(NEDM,NIZ,NIS,NIS,NILB5)
C
C  ----  Probability of emission of characteristic photons.
      DIMENSION PTIGT(NIZ,NIS,NIS),PTIGT2(NIZ,NIS,NIS),
     1  PTIGTP(NIZ,NIS,NIS),LPTIGT(NIZ,NIS,NIS)
      DIMENSION PTIoG(NIZ,NIS,NIS,NILB5),PTIoG2(NIZ,NIS,NIS,NILB5),
     1  PTIoGP(NIZ,NIS,NIS,NILB5),LPTIoG(NIZ,NIS,NIS,NILB5)
C
C  ----  Probability of emission of bremsstrahlung photons.
      DIMENSION PDEBR(NBEM),PDEBR2(NBEM),PDEBRP(NBEM),LPDEBR(NBEM)
C
C  ----  Phi rho z distribution for characteristic x rays.
      PARAMETER (NPRZM=10,NPRZSL=250)
      DIMENSION IPRZZ(NPRZM),IPRZS1(NPRZM),IPRZS2(NPRZM),IPRZPD(NPRZM)
      DIMENSION PRZT(NPRZM,NPRZSL),PRZT2(NPRZM,NPRZSL),
     1  PRZTP(NPRZM,NPRZSL),LPRZT(NPRZM,NPRZSL)
      DIMENSION PRZF(NPRZM,NILB5,NPRZSL),PRZF2(NPRZM,NILB5,NPRZSL),
     1  PRZFP(NPRZM,NILB5,NPRZSL),LPRZF(NPRZM,NILB5,NPRZSL)
      DIMENSION PRZGT(NPRZM,NPRZSL),PRZGT2(NPRZM,NPRZSL),
     1  PRZGTP(NPRZM,NPRZSL),LPRZGT(NPRZM,NPRZSL)
      DIMENSION PRZG(NPRZM,NILB5,NPRZSL),PRZG2(NPRZM,NILB5,NPRZSL),
     1  PRZGP(NPRZM,NILB5,NPRZSL),LPRZG(NPRZM,NILB5,NPRZSL)
C
C  ****  Time counter initiation.
C
      WRITE(6,*) 'Start memory allocation'
      CALL TIME0
C
      DO I=1,NB
        TDEBO(I)=0.0D0
        TDEBO2(I)=0.0D0
      ENDDO
C
      DO I=1,3
        DO J=1,2
          DO K=1,NBEM
            PDE(I,J,K)=0.0D0
            PDE2(I,J,K)=0.0D0
            PDEP(I,J,K)=0.0D0
            LPDE(I,J,K)=0
          ENDDO
        ENDDO
      ENDDO
C
      DO I=1,3
        DO J=1,NBTHM
          DO K=1,NBPHM
            PDA(I,J,K)=0.0D0
            PDA2(I,J,K)=0.0D0
            PDAP(I,J,K)=0.0D0
            LPDA(I,J,K)=0
          ENDDO
        ENDDO
      ENDDO
C
      DO I=1,3
        DO J=1,NBTHM
          PDAT(I,J)=0.0D0
          PDAT2(I,J)=0.0D0
          PDATP(I,J)=0.0D0
          LPDAT(I,J)=0
        ENDDO
      ENDDO
C
      DO I=1,NEDM
        DO J=1,NEDCM
          DET(I,J)=0.0D0
          DET2(I,J)=0.0D0
          DETP(I,J)=0.0D0
          LDET(I,J)=0
        ENDDO
        TDED(I)=0.0D0
        TDED2(I)=0.0D0
      ENDDO
C
      DO I=1,NEDM
        DO J=1,NEDCM
          DoT(I,J)=0.0D0
          DoT2(I,J)=0.0D0
          DoTP(I,J)=0.0D0
          LDoT(I,J)=0
          DoF(I,J)=0.0D0
          DoF2(I,J)=0.0D0
          DoFP(I,J)=0.0D0
          LDoF(I,J)=0
        ENDDO
      ENDDO
C
      DO I=1,NDXM
        DO J=1,NDYM
          DO K=1,NDZM
            DOEV(I,J,K)=0.0D0
            DOEV2(I,J,K)=0.0D0
            DOEVP(I,J,K)=0.0D0
            LDOEV(I,J,K)=0
          ENDDO
        ENDDO
      ENDDO
C
      DO I=1,NEDM
        DO J=1,NIZ
          DO K=1,NIS
            DO L=1,NIS
              PTIoT(I,J,K,L)=0.0D0
              PTIoT2(I,J,K,L)=0.0D0
              PTIoTP(I,J,K,L)=0.0D0
              LPTIoT(I,J,K,L)=0
              DO M=1,NILB5
                PTIoF(I,J,K,L,M)=0.0D0
                PTIoF2(I,J,K,L,M)=0.0D0
                PTIoFP(I,J,K,L,M)=0.0D0
                LPTIoF(I,J,K,L,M)=0
              ENDDO
            ENDDO
          ENDDO
        ENDDO
      ENDDO
C
      DO J=1,NIZ
        DO K=1,NIS
          DO L=1,NIS
            PTIGT(J,K,L)=0.0D0
            PTIGT2(J,K,L)=0.0D0
            PTIGTP(J,K,L)=0.0D0
            LPTIGT(J,K,L)=0
            DO M=1,NILB5
              PTIoG(J,K,L,M)=0.0D0
              PTIoG2(J,K,L,M)=0.0D0
              PTIoGP(J,K,L,M)=0.0D0
              LPTIoG(J,K,L,M)=0
            ENDDO
          ENDDO
        ENDDO
      ENDDO
C
      DO I=1,NBEM
        PDEBR(I)=0.0D0
        PDEBR2(I)=0.0D0
        PDEBRP(I)=0.0D0
        LPDEBR(I)=0
      ENDDO
C
      DO I=1,NPRZM
        DO J=1,NPRZSL
          PRZT(I,J)=0.0D0
          PRZT2(I,J)=0.0D0
          PRZTP(I,J)=0.0D0
          LPRZT(I,J)=0
          PRZGT(I,J)=0.0D0
          PRZGT2(I,J)=0.0D0
          PRZGTP(I,J)=0.0D0
          LPRZGT(I,J)=0
        ENDDO
      ENDDO
      DO I=1,NPRZM
        DO J=1,NILB5
          DO K=1,NPRZSL
            PRZF(I,J,K)=0.0D0
            PRZF2(I,J,K)=0.0D0
            PRZFP(I,J,K)=0.0D0
            LPRZF(I,J,K)=0
            PRZG(I,J,K)=0.0D0
            PRZG2(I,J,K)=0.0D0
            PRZGP(I,J,K)=0.0D0
            LPRZG(I,J,K)=0
          ENDDO
        ENDDO
      ENDDO
C
C  ------------------------  Read input data file.
C
      WRITE(6,*) 'Reading input data'
C
      OPEN(26,FILE='penepma.dat')
      WRITE(26,1000)
 1000 FORMAT(//3X,61('*'),/3X,'**   Program PENEPMA. ',
     1 ' Input data and run-time messages.   **',/3X,61('*'))
C
      CALL PDATET(DATE23)
      WRITE(26,1001) DATE23
 1001 FORMAT(/3X,'Date and time: ',A23)
C
C  ****  Title.
C
      READ(5,'(A6,1X,A120)') KWORD,TITLE
      WRITE(26,'(/3X,A120)') TITLE
C
C  ************  Electron beam.
C
   11 CONTINUE
      READ(5,'(A6,1X,A120)') KWORD,BUFFER
      IF(KWORD.EQ.KWCOMM) GO TO 11
C
      WRITE(26,1100)
 1100 FORMAT(//3X,72('-'),/3X,'>>>>>>  Electron beam.')
C
      KPARP=1
      WRITE(26,1110)
 1110 FORMAT(3X,'Primary particles: electrons')
C
C  ****  Initial energy of primary particles.
C
      IF(KWORD.EQ.KWSENE) THEN
        READ(BUFFER,*) E0
        WRITE(26,1120) E0
 1120   FORMAT(3X,'Initial energy = ',1P,E13.6,' eV')
   13   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 13
      ELSE
        E0=1.0D5
        WRITE(26,1120) E0
      ENDIF
      IF(E0.LT.100.0D0) THEN
        WRITE(26,*) 'The initial energy E0 is too small.'
        STOP 'The initial energy E0 is too small.'
      ENDIF
      EPMAX=E0
C
      IF(KWORD.EQ.KWSPOS) THEN
        READ(BUFFER,*) SX0,SY0,SZ0
   16   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 16
      ELSE
        SX0=0.0D0
        SY0=0.0D0
        SZ0=10.0D0
      ENDIF
      WRITE(26,1132) SX0,SY0,SZ0
 1132 FORMAT(3X,'Coordinates of source:     SX0 = ',1P,E13.6,
     1  ' cm',/30X,'SY0 = ',E13.6,' cm',/30X,'SZ0 = ',E13.6,' cm')
C
      IF(KWORD.EQ.KWSDIR) THEN
        READ(BUFFER,*) STHETA,SPHI
   17   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 17
      ELSE
        STHETA=180.0D0
        SPHI=0.0D0
      ENDIF
      WRITE(26,1133) STHETA,SPHI
 1133 FORMAT(3X,'Beam direction angles:   THETA = ',1P,E13.6,' deg',
     1  /30X,'PHI = ',E13.6,' deg')
C
      IF(KWORD.EQ.KWSAPE) THEN
        READ(BUFFER,*) SALPHA
   18   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 18
      ELSE
        SALPHA=0.0D0
      ENDIF
      WRITE(26,1134) SALPHA
 1134 FORMAT(3X,'Beam aperture:',11X,'ALPHA = ',1P,E13.6,' deg')
      CALL GCONE0(STHETA*DE2RA,SPHI*DE2RA,SALPHA*DE2RA)
C
      IF(KWORD.EQ.KWSDIA) THEN
        READ(BUFFER,*) SDIAM
   19   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 19
      ELSE
        SDIAM=10.0E-7 ! 10 nm
      ENDIF
      WRITE(26,1135) SDIAM
 1135 FORMAT(3X,'Beam diameter:',13X,'DIA = ',1P,E13.6,' cm')
C
C  ************  Material data and simulation parameters.
C
      WRITE(26,1300)
 1300 FORMAT(//3X,72('-'),/
     1  3X,'>>>>>>  Material data and simulation parameters.')
C
C  ****  Simulation parameters.
C
      DO M=1,MAXMAT
        EABS(1,M)=0.010D0*EPMAX
        EABS(2,M)=0.001D0*EPMAX
        EABS(3,M)=0.010D0*EPMAX
        C1(M)=0.10D0
        C2(M)=0.10D0
        WCC(M)=EABS(1,M)
        WCR(M)=EABS(2,M)
      ENDDO
      DO IB=1,NB
        DSMAX(IB)=1.0D20
      ENDDO
      WGHT0=1.0D0   ! Primary particle weight.
      INTFOR=0      ! No interaction forcing as default.
C
      NMAT=0
   31 CONTINUE
      IF(KWORD.EQ.KWMATF) THEN
        NMAT=NMAT+1
        READ(BUFFER,'(A20)') PMFILE(NMAT)
   32   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 32
        IF(KWORD.EQ.KWMATF) GO TO 31
      ENDIF
C
      IF(KWORD.EQ.KWSIMP) THEN
        READ(BUFFER,*) EABS(1,NMAT),EABS(2,NMAT),EABS(3,NMAT),
     1    C1(NMAT),C2(NMAT),WCC(NMAT),WCR(NMAT)
   33   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 33
        IF(KWORD.EQ.KWMATF) GO TO 31
      ENDIF
C
      IF(NMAT.EQ.0) THEN
        WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
        WRITE(26,*) 'You have to specify a material file (line MFNAME).'
        STOP 'You have to specify a material file (line MFNAME).'
      ENDIF
      IF(NMAT.GT.MAXMAT) THEN
        WRITE(26,*) 'Wrong number of materials.'
        WRITE(26,'(''NMAT ='',I4,'' is larger than MAXMAT ='',I4)')
     1    NMAT,MAXMAT
        STOP 'Wrong number of materials.'
      ENDIF
C
      DO M=1,NMAT
        IF(M.EQ.1) LIT='st'
        IF(M.EQ.2) LIT='nd'
        IF(M.EQ.3) LIT='rd'
        IF(M.GT.3) LIT='th'
        WRITE(26,1320) M,LIT
 1320   FORMAT(/3X,'**** ',I2,A2,' material')
        WRITE(26,1325) PMFILE(M)
 1325   FORMAT(3X,'Material data file: ',A)
        IF(EABS(1,M).LT.5.0D1) EABS(1,M)=5.0D1
        IF(EABS(2,M).LT.5.0D1) EABS(2,M)=5.0D1
        IF(EABS(3,M).LT.5.0D1) EABS(3,M)=5.0D1
        WRITE(26,1321) EABS(1,M)
 1321   FORMAT(3X,'Electron absorption energy = ',1P,E13.6,' eV')
        WRITE(26,1322) EABS(2,M)
 1322   FORMAT(3X,'  Photon absorption energy = ',1P,E13.6,' eV')
        WRITE(26,1323) EABS(3,M)
 1323   FORMAT(3X,'Positron absorption energy = ',1P,E13.6,' eV')
        WCR(M)=MIN(WCR(M),EABS(1,M))
        WRITE(26,1324) C1(M),C2(M),WCC(M),WCR(M)
 1324   FORMAT(3X,'Electron-positron simulation parameters:',
     1    /4X,'C1 =',1P,E13.6,',      C2 =',E13.6,/3X,'Wcc =',E13.6,
     1    ' eV,  Wcr =',E13.6,' eV')
      ENDDO
C
C  ****  Initialisation of PENELOPE.
C
      WRITE(6,*) ' Initialising PENELOPE ...'
      IWR=16
      OPEN(IWR,FILE='pe-material.dat')
        INFO=1
        CALL PEINIT(EPMAX,NMAT,IWR,INFO,PMFILE)
      CLOSE(IWR)
C
C  ************  Set the sorted list of radiative transitions.
C
      IS3=0
      NPTRAN=0 ! Number of radiative transitions.
      DO M=1,NMAT
        DO IEL=1,NELEM(M)
          IZZ=IZ(M,IEL)
          DO IS1=1,NIS
            DO IS2=1,NIS
              CALL RELAXE(IZZ,IS1,IS2,IS3,ENERGY,TRPROB)
              IF(ENERGY.LT.1.0D34) THEN
                NPTRAN=NPTRAN+1
                IZS(NPTRAN)=IZZ
                IS1S(NPTRAN)=IS1
                IS2S(NPTRAN)=IS2
                ENERGS(NPTRAN)=ENERGY
              ENDIF
            ENDDO
          ENDDO
        ENDDO
      ENDDO
C
C  ---- Sort the transitions by increasing energies.
      IF(NPTRAN.GT.1) THEN
        DO I=1,NPTRAN-1
          DO J=I+1,NPTRAN
            IF(ENERGS(I).GT.ENERGS(J)) THEN
              ISAVE=IZS(I)
              IZS(I)=IZS(J)
              IZS(J)=ISAVE
              ISAVE=IS1S(I)
              IS1S(I)=IS1S(J)
              IS1S(J)=ISAVE
              ISAVE=IS2S(I)
              IS2S(I)=IS2S(J)
              IS2S(J)=ISAVE
              SAVE=ENERGS(I)
              ENERGS(I)=ENERGS(J)
              ENERGS(J)=SAVE
            ENDIF
          ENDDO
        ENDDO
      ENDIF
C
C  ************  Geometry definition.
C
C  Define here the geometry parameters that are to be altered, if any.
C     PARINP(1)=
C     PARINP(2)=  ...
      NPINP=0
C
      IF(KWORD.EQ.KWGEOM) THEN
        READ(BUFFER,'(A20)') PFILE
        WRITE(26,1340) PFILE
 1340   FORMAT(/3X,'PENGEOM''s geometry definition file: ',A20)
        OPEN(15,FILE=PFILE,IOSTAT=KODE)
        IF(KODE.NE.0) THEN
          WRITE(26,'(''File '',A20,'' could not be opened.'')') PFILE
          STOP
        ENDIF
        OPEN(16,FILE='pe-geometry.rep')
        CALL GEOMIN(PARINP,NPINP,NMATG,NBODY,15,16)
        CLOSE(UNIT=15)
        CLOSE(UNIT=16)
        IF(NMATG.LT.1) THEN
          WRITE(26,*) 'NMATG must be greater than 0.'
          STOP 'NMATG must be greater than 0.'
        ENDIF
C
        IF(NBODY.GT.NB) THEN
          WRITE(26,'(/6X,''Too many bodies.'')')
          STOP 'Too many bodies.'
        ENDIF
C
        IF(NMATG.GT.NMAT) THEN
          WRITE(26,'(/6X,''Too many different materials.'')')
          STOP 'Too many different materials.'
        ENDIF
C
   34   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 34
      ELSE
        WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
        WRITE(26,*) 'You have to specify a geometry file.'
        STOP 'You have to specify a geometry file.'
      ENDIF
C
C  ****  Maximum step lengths of electrons and positrons.
C
      IF(KWORD.EQ.KWSMAX) THEN
        READ(BUFFER,*) IB
        IF(IB.LT.1.OR.IB.GT.NBODY) THEN
          WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
          WRITE(26,*) 'Incorrect body number.'
          STOP 'Incorrect body number.'
        ENDIF
        READ(BUFFER,*) IB,DSMAX(IB)
        IF(DSMAX(IB).LT.1.0D-7) DSMAX(IB)=1.0D20
   35   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 35
        IF(KWORD.EQ.KWSMAX) THEN
          READ(BUFFER,*) IB
          IF(IB.LT.1.OR.IB.GT.NBODY) THEN
            WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
            WRITE(26,*) 'Incorrect body number.'
            STOP 'Incorrect body number.'
          ENDIF
          READ(BUFFER,*) IB,DSMAX(IB)
          IF(DSMAX(IB).LT.1.0D-7) DSMAX(IB)=1.0D20
          GO TO 35
        ENDIF
      ENDIF
C
      WRITE(26,1350)
 1350 FORMAT(//3X,72('-'),/3X,'>>>>>>  Maximum allowed step lengths of',
     1  ' electrons and positrons.')
      DO IB=1,NBODY
        WRITE(26,1351) IB,DSMAX(IB)
 1351   FORMAT(3X,'* Body =',I4,',   DSMAX = ',1P,E13.6,' cm')
      ENDDO
C
C  ************  Variance reduction (only interaction forcing).
C
      DO KB=1,NB
        DO ICOL=1,8
          DO KPAR=1,3
            FORCE(KB,KPAR,ICOL)=1.0D0
          ENDDO
        ENDDO
        DO KPAR=1,3
          IFORCE(KB,KPAR)=0
          WLOW(KB,KPAR)=0.0D0
          WHIG(KB,KPAR)=1.0D6
        ENDDO
      ENDDO
C
      IF(KWORD.EQ.KWIFOR) THEN
        WRITE(26,1400)
 1400   FORMAT(//3X,72('-'),/
     1    3X,'>>>>>>  Interaction forcing: FORCE(IBODY,KPAR,ICOL)')
   41   CONTINUE
        READ(BUFFER,*) KB,KPAR,ICOL,FORCER,WWLOW,WWHIG
C  ****  Negative FORCER values are re-interpreted, as described in the
C        heading comments above.
        IF(FORCER.LT.-1.0D-6) THEN
          MM=MATER(KB)
          EVENTS=MAX(ABS(FORCER),1.0D0)
          PLT=PRANGE(E0,KPAR,MM)
          RMFP=PHMFP(E0,KPAR,MM,ICOL)
          FORCER=EVENTS*RMFP/PLT
        ENDIF
        IF(WWLOW.LT.1.0D-6) WWLOW=1.0D-6
        IF(WWHIG.GT.1.0D6) WWHIG=1.0D6
        IF(KB.LT.1.OR.KB.GT.NBODY) THEN
          WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
          WRITE(26,*) 'Inconsistent KB value.'
          STOP 'Inconsistent KB value.'
        ENDIF
        IF(KPAR.LT.1.OR.KPAR.GT.3) THEN
          WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
          WRITE(26,*) 'Incorrect value of KPAR.'
          STOP 'Incorrect value of KPAR.'
        ENDIF
        IF(ICOL.LT.1.OR.ICOL.GT.8) THEN
          WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
          WRITE(26,*) 'Incorrect value of ICOL.'
          STOP 'Incorrect value of ICOL.'
        ENDIF
        WLOW(KB,KPAR)=MAX(WLOW(KB,KPAR),WWLOW)
        WHIG(KB,KPAR)=MIN(WHIG(KB,KPAR),WWHIG)
        IF(WLOW(KB,KPAR).GT.WHIG(KB,KPAR)) THEN
          WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
          WRITE(26,*) 'Incorrect weight window limits.'
          STOP 'Incorrect weight window limits.'
        ENDIF
        IF(FORCER.LT.1.0D0) STOP 'FORCER must be greater than unity.'
        IFORCE(KB,KPAR)=1
        FORCE(KB,KPAR,ICOL)=FORCER
        WRITE(26,1410) KB,KPAR,ICOL,FORCER,WLOW(KB,KPAR),WHIG(KB,KPAR)
 1410   FORMAT(3X,'FORCE(',I4,',',I1,',',I1,') =',1P,E13.6,
     1    ',  weight window = (',E9.2,',',E9.2,')')
   42   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 42
        IF(KWORD.EQ.KWIFOR) GO TO 41
      ENDIF
C
C  ************  Energy and angular distributions of emerging
C                particles.
C
      WRITE(26,1500)
 1500 FORMAT(//3X,72('-'),/
     1  3X,'>>>>>>  Energy and angular distributions of emerging',
     1  ' particles.')
C
      IF(KWORD.EQ.KWNBE) THEN
        READ(BUFFER,*) EMIN,EMAX,NBE
   51   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 51
      ELSE
        EMIN=0.0D0
        EMAX=EPMAX
        NBE=NBEM
      ENDIF
      EMIN=MAX(EMIN,0.0D0)
      EMAX=MAX(EMAX,EPMAX)
      NBE=MIN(MAX(NBE,10),NBEM)
      WRITE(26,1510) NBE,EMIN,EMAX
 1510 FORMAT(3X,'E:       NBE = ',I3,
     1  ',  EMIN =',1P,E13.6,' eV,  EMAX =',E13.6,' eV')
      IF(EMIN.GT.EMAX) THEN
        WRITE(26,*) 'Energy interval is too narrow.'
        STOP 'Energy interval is too narrow.'
      ENDIF
C
      IF(KWORD.EQ.KWNBTH) THEN
        READ(BUFFER,*) NBTH
   52   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 52
      ELSE
        NBTH=NBTHM
      ENDIF
      WRITE(26,1520) NBTH
 1520 FORMAT(3X,'Theta:  NBTH = ',I3)
      IF(NBTH.LT.1) THEN
        WRITE(26,*) 'Wrong number of THETA bins.'
        STOP 'Wrong number of THETA bins.'
      ELSE IF (NBTH.GT.NBTHM) THEN
        WRITE(26,*) 'NBTH is too large.'
        WRITE(26,*) 'Set the parameter NBTHM equal to ',NBTH
        STOP 'NBTH is too large.'
      ENDIF
C
      IF(KWORD.EQ.KWNBPH) THEN
        READ(BUFFER,*) NBPH
   53   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 53
      ELSE
        NBPH=NBPHM
      ENDIF
      WRITE(26,1530) NBPH
 1530 FORMAT(3X,'Phi:    NBPH = ',I3)
      IF(NBTH.LT.1) THEN
        WRITE(26,*) 'Wrong number of PHI bins.'
        STOP 'Wrong number of PHI bins.'
      ELSE IF (NBPH.GT.NBPHM) THEN
        WRITE(26,*) 'NBPH is too large.'
        WRITE(26,*) 'Set the parameter NBPHM equal to ',NBPH
        STOP 'NBPH is too large.'
      ENDIF
C
C  ****  Bin sizes.
C
C  ----  The factor 1.0000001 serves to ensure that the upper limit of
C  the tallied interval is within the last channel (otherwise, the array
C  dimensions could be exceeded).
      BSE(1)=1.0000001D0*(EMAX-EMIN)/DBLE(NBE)
      BSE(2)=1.0000001D0*(EMAX-EMIN)/DBLE(NBE)
      BSE(3)=1.0000001D0*(EMAX-EMIN)/DBLE(NBE)
      BSTH=1.0000001D0*180.0D0/DBLE(NBTH)
      BSPH=1.0000001D0*360.0D0/DBLE(NBPH)
C
C  ************  Photon detectors.
C
      NDEDEF=0
      DO I=1,NEDM
        IORIG(I)=0
      ENDDO
   43 CONTINUE
      IF(KWORD.EQ.KWDANG) THEN
        NDEDEF=NDEDEF+1
        IF(NDEDEF.GT.NEDM) THEN
          WRITE(26,'(3X,''NDEDEF = '',I4)') NDEDEF
          WRITE(26,*) 'Too many energy-deposition detectors.'
          STOP 'Too many energy-deposition detectors.'
        ENDIF
        WRITE(26,1650) NDEDEF
 1650   FORMAT(//3X,72('-'),/
     1    3X,'>>>>>>  Photon detector #', I2)
        READ(BUFFER,*) THETA1(NDEDEF),THETA2(NDEDEF),
     1    PHI1(NDEDEF),PHI2(NDEDEF),IPSF(NDEDEF)
        IF(THETA1(NDEDEF).GE.THETA2(NDEDEF)) THEN
          WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
          WRITE(26,*) 'THETA1 must be less than THETA2.'
          STOP 'THETA1 must be less than THETA2.'
        ENDIF
        IF(THETA1(NDEDEF).LT.0.0D0.OR.THETA1(NDEDEF).GT.180.0D0) THEN
          WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
          WRITE(26,*) 'THETA1 must be must be in the interval (0,180).'
          STOP 'THETA1 must be must be in the interval (0,180).'
        ENDIF
        IF(THETA2(NDEDEF).LT.0.0D0.OR.THETA2(NDEDEF).GT.180.0D0) THEN
          WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
          WRITE(26,*) 'THETA2 must be must be in the interval (0,180).'
          STOP 'THETA2 must be must be in the interval (0,180).'
        ENDIF
        IF(PHI1(NDEDEF).GE.PHI2(NDEDEF)) THEN
          WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
          WRITE(26,*) 'PHI1 must be less than PHI2.'
          STOP 'PHI1 must be less than PHI2.'
        ENDIF
        IF(PHI1(NDEDEF).LT.0.0D0) THEN
          IF(PHI1(NDEDEF).LT.-180.0001D0) THEN
            WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
            WRITE(26,*) 'PHI1 must be must be larger than -180.'
            STOP 'PHI1 must be must be larger than -180.'
          ENDIF
          IF(PHI2(NDEDEF).GT.180.0001D0) THEN
            WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
            WRITE(26,*) 'PHI2 must be must be less than 180.'
            STOP 'PHI2 must be must be less than 180.'
          ENDIF
        ELSE
          IF(PHI1(NDEDEF).GT.360.0001D0) THEN
            WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
            WRITE(26,*) 'PHI1 must be must be less than 360.'
            STOP 'PHI1 must be must be less than 360.'
          ENDIF
          IF(PHI2(NDEDEF).GT.360.0001D0) THEN
            WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
            WRITE(26,*) 'PHI2 must be must be less than 360.'
            STOP 'PHI2 must be must be less than 360.'
          ENDIF
        ENDIF
C
        WRITE(26,1611) THETA1(NDEDEF),THETA2(NDEDEF),
     1    PHI1(NDEDEF),PHI2(NDEDEF)
 1611   FORMAT(3X,'Angular intervals : theta_1 =',1P,E11.4,
     1    ' deg,  theta_2 =',E11.4,' deg',/25X,'phi_1 =',E11.4,
     2    ' deg,    phi_2 =',E11.4,' deg')
        THETA1(NDEDEF)=THETA1(NDEDEF)*DE2RA
        THETA2(NDEDEF)=THETA2(NDEDEF)*DE2RA
        PHI1(NDEDEF)=PHI1(NDEDEF)*DE2RA
        PHI2(NDEDEF)=PHI2(NDEDEF)*DE2RA
C
   44   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 44
        IF(KWORD.EQ.KWDENE) THEN
          READ(BUFFER,*) EDEL(NDEDEF),EDEU(NDEDEF),NDECH(NDEDEF)
          EDEL(NDEDEF)=MAX(EDEL(NDEDEF),0.0D0)
          EDEU(NDEDEF)=MIN(EDEU(NDEDEF),E0)
          IF(EDEU(NDEDEF).LT.EDEL(NDEDEF)) THEN
            WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
            WRITE(26,*) 'Incorrect energy limits. Modified.'
            WRITE(26,'(A,1P,E13.6)') 'EDEL =',EDEL(NDEDEF)
            WRITE(26,'(A,1P,E13.6)') 'EDEU =',EDEU(NDEDEF)
            STOP 'Incorrect energy limits.'
          ENDIF
          NDECH(NDEDEF)=MIN(MAX(NDECH(NDEDEF),10),NEDCM)
C
          WRITE(26,1610) EDEL(NDEDEF),EDEU(NDEDEF),NDECH(NDEDEF)
          BDEE(NDEDEF)=1.0000001D0*(EDEU(NDEDEF)-EDEL(NDEDEF))
     1      /DBLE(NDECH(NDEDEF))
          WRITE(26,1612) BDEE(NDEDEF)
   55     CONTINUE
          READ(5,'(A6,1X,A120)') KWORD,BUFFER
          IF(KWORD.EQ.KWCOMM) GO TO 55
          GO TO 56
        ELSE
          EDEL(NDEDEF)=0.0D0
          EDEU(NDEDEF)=E0
          NDECH(NDEDEF)=1000
          WRITE(26,1610) EDEL(NDEDEF),EDEU(NDEDEF),NDECH(NDEDEF)
          BDEE(NDEDEF)=1.0000001D0*(EDEU(NDEDEF)-EDEL(NDEDEF))
     1      /DBLE(NDECH(NDEDEF))
          WRITE(26,1612) BDEE(NDEDEF)
          IF(KWORD.EQ.KWDANG) GO TO 43
        ENDIF
 1610   FORMAT(3X,'Energy window = (',1P,E12.5,',',E12.5,') eV, no.',
     1    ' of channels = ',I4)
 1612   FORMAT(3X,'Channel width =',1P,E13.6,' eV')
C
   56   CONTINUE
        IF(IPSF(NDEDEF).GT.0) THEN
          WRITE(BUF2,'(I5)') 1000+NDEDEF
          SPCDIO='pe-psf-'//BUF2(4:5)//'.dat'
          PSFDIO(NDEDEF)=SPCDIO
          WRITE(26,1613) PSFDIO(NDEDEF)
 1613     FORMAT(3X,'Output phase-space file: ',A20)
        ENDIF
        IF(KWORD.EQ.KWDANG) GO TO 43
C
        IF(KWORD.EQ.KWORIG) THEN
          IORIG(NDEDEF)=1
          READ(BUFFER,'(A20)') PORIG
          OPEN(60+NDEDEF,FILE=PORIG)
          WRITE(26,1623) PORIG
 1623     FORMAT(3X,'Output x-ray emission sites file: ',A20)
   45     CONTINUE
          READ(5,'(A6,1X,A120)') KWORD,BUFFER
          IF(KWORD.EQ.KWCOMM) GO TO 45
          IF(KWORD.EQ.KWDANG) GO TO 43
        ENDIF
      ENDIF
      IF(NDEDEF.EQ.0) THEN
        WRITE(26,*) 'No photon detectors were defined.'
        WRITE(26,*) 'You must define at least one photon detector.'
        STOP 'No photon detectors were defined.'
      ENDIF
C
C  ************  Space distribution of x-ray emission.
C
      IDOEV=0
      IF(KWORD.EQ.KGRDXX) THEN
        IDOEV=1
        WRITE(26,1700)
 1700   FORMAT(//3X,72('-'),/3X,'>>>>>>  Space distribution of x-ray ',
     1    'emission.')
        READ(BUFFER,*) DXL(1),DXU(1)
        IF(DXL(1).GT.DXU(1)) THEN
          SAVE=DXL(1)
          DXL(1)=DXU(1)
          DXU(1)=SAVE
        ENDIF
        IF(DXU(1).LT.DXL(1)+1.0D-6) THEN
          WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
          WRITE(26,*) 'XU must be greater than XL+1.0E-6.'
          STOP 'XU must be greater than XL+1.0E-6.'
        ENDIF
        WRITE(26,1710) DXL(1),DXU(1)
 1710   FORMAT(3X,'Scoring box:  XL = ',1P,E13.6,' cm,  XU = ',
     1    E13.6,' cm')
   71   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 71
        IF(KWORD.EQ.KGRDYY) THEN
          READ(BUFFER,*) DXL(2),DXU(2)
          IF(DXL(2).GT.DXU(2)) THEN
            SAVE=DXL(2)
            DXL(2)=DXU(2)
            DXU(2)=SAVE
          ENDIF
          IF(DXU(2).LT.DXL(2)+1.0D-6) THEN
            WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
            WRITE(26,*) 'YU must be greater than YL+1.0E-6.'
            STOP 'YU must be greater than YL+1.0E-6.'
          ENDIF
          WRITE(26,1711) DXL(2),DXU(2)
 1711     FORMAT(17X,'YL = ',1P,E13.6,' cm,  YU = ',E13.6,' cm')
        ELSE
          WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
          WRITE(26,*) 'Unrecognized keyword.'
          STOP 'Unrecognized keyword.'
        ENDIF
   72   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 72
        IF(KWORD.EQ.KGRDZZ) THEN
          READ(BUFFER,*) DXL(3),DXU(3)
          IF(DXL(3).GT.DXU(3)) THEN
            SAVE=DXL(3)
            DXL(3)=DXU(3)
            DXU(3)=SAVE
          ENDIF
          IF(DXU(3).LT.DXL(3)+1.0D-6) THEN
            WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
            WRITE(26,*) 'ZU must be greater than ZL+1.0E-6.'
            STOP 'ZU must be greater than ZL+1.0E-6.'
          ENDIF
          WRITE(26,1712) DXL(3),DXU(3)
 1712     FORMAT(17X,'ZL = ',1P,E13.6,' cm,  ZU = ',E13.6,' cm')
        ELSE
          WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
          WRITE(26,*) 'Unrecognized keyword.'
          STOP 'Unrecognized keyword.'
        ENDIF
   73   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 73
        IF(KWORD.EQ.KGRDBN) THEN
          READ(BUFFER,*) NDB(1),NDB(2),NDB(3)
          IF(NDB(1).LT.0.OR.NDB(1).GT.NDXM) THEN
            WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
            WRITE(26,'(''NDB(1) must be .GT.0. and .LT.'',I4)') NDXM
            WRITE(26,*) 'Increase the value of the parameter NDXM.'
            STOP 'NDB(1) must be .GT.0. and .LE.NDXM'
          ENDIF
          IF(NDB(2).LT.0.OR.NDB(2).GT.NDYM) THEN
            WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
            WRITE(26,'(''NDB(2) must be .GT.0. and .LT.'',I4)') NDYM
            WRITE(26,*) 'Increase the value of the parameter NDYM.'
            STOP 'NDB(2) must be .GT.0. and .LE.NDYM'
          ENDIF
          IF(NDB(3).LT.0.OR.NDB(3).GT.NDZM) THEN
            WRITE(26,'(A6,1X,A120)') KWORD,BUFFER
            WRITE(26,'(''NDB(3) must be .GT.0. and .LT.'',I4)') NDZM
            WRITE(26,*) 'Increase the value of the parameter NDZM.'
            STOP 'NDB(3) must be .GT.0. and .LE.NDZM'
          ENDIF
          WRITE(26,1713) NDB(1),NDB(2),NDB(3)
 1713     FORMAT(3X,'Numbers of bins:     NBX =',I4,', NBY =',I4,
     1      ', NBZ =',I4)
        ELSE
          NDB(1)=50
          NDB(2)=50
          NDB(3)=50
          WRITE(26,1713) NDB(1),NDB(2),NDB(3)
        ENDIF
        DO I=1,3
          BDOEV(I)=1.0000001D0*(DXU(I)-DXL(I))/DBLE(NDB(I))
          BDOEVR(I)=1.0D0/BDOEV(I)
        ENDDO
   74   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 74
        IF(KWORD.EQ.KEVENT) THEN
          READ(BUFFER,*) XEMIN,XEMAX
          WRITE(26,1714) XEMIN,XEMAX
 1714     FORMAT(3X,'X-ray energy interval:  from',1P,E13.6,' keV to',
     1      E13.6,' keV')
          IDOEV=1
   75     CONTINUE
          READ(5,'(A6,1X,A120)') KWORD,BUFFER
          IF(KWORD.EQ.KWCOMM) GO TO 75
        ENDIF
      ENDIF
C
C  ************  Phi rho z distributions.
C
      NPRZ=0
      RANGE=0.0D0
      WRITE(26,1760)
 1760 FORMAT(//3X,72('-'),/3X,'>>>>>>  Phi rho z distribution.')
   76 CONTINUE
      IF(KWORD.EQ.KWPRZ) THEN
        NPRZ=NPRZ+1
        IF(NPRZ.GT.NPRZM) THEN
          WRITE(26,'(3X,''NPRZ = '',I4)') NPRZ
          WRITE(26,*) 'Too many phi rho z distributions.'
          STOP 'Too many phi rho z distributions.'
        ENDIF
        READ(BUFFER,*) IZZ,IS1,IS2,IPD
C
        DO I=1,NPTRAN
          IF (IZS(I).EQ.IZZ.AND.IS1S(I).EQ.IS1.AND.
     1          IS2S(I).EQ.IS2) GO TO 771
        ENDDO
        STOP 'PRZ transition does not exist for simulation materials'
  771   CONTINUE
        IF (IPD.LT.0.OR.IPD.GT.NDEDEF) THEN
          STOP 'PRZ detector is not defined'
        ENDIF
C
        IPRZZ(NPRZ)=IZZ
        IPRZS1(NPRZ)=IS1
        IPRZS2(NPRZ)=IS2
        IPRZPD(NPRZ)=IPD
        DO M=1,NMAT
          RANGE=MAX(RANGE,PHRANG(E0,M,IZZ,IS1,IS2))
        ENDDO
C
        WRITE(26,1770) IZZ,IS1,IS2,IPD
 1770   FORMAT(3X,'Z = ',I2,', S1 = ',I2,', S2 = ',I2,
     1    ', photon detector # ',I2)
C
   77   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 77
        IF(KWORD.EQ.KWPRZ) GO TO 76
      ENDIF
      PRZSL=RANGE*1.5D0/NPRZSL
      PRZSLF=RANGE*30.0D0/NPRZSL
      WRITE(26,1771) PRZSL
 1771 FORMAT(3X,'delta Z = ',E13.6,' cm')
C
C  ************  Job characteristics.
C
      WRITE(26,1800)
 1800 FORMAT(//3X,72('-'),/
     1  3X,'>>>>>>  Job characteristics.')
C
      IRESUM=0
      IF(KWORD.EQ.KWRESU) THEN
        READ(BUFFER,'(A20)') PFILER
        WRITE(26,1810) PFILER
 1810   FORMAT(3X,'Resume simulation from previous dump file: ',A20)
        IRESUM=1
   81   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 81
      ENDIF
C
      IDUMP=0
      DUMPP=1.0D15
      IF(KWORD.EQ.KWDUMP) THEN
        READ(BUFFER,'(A20)') PFILED
        WRITE(26,1820) PFILED
 1820   FORMAT(3X,'Write final counter values on the dump file: ',A20)
        IDUMP=1
   82   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 82
      ENDIF
C
      IF(KWORD.EQ.KWDMPP) THEN
        READ(BUFFER,*) DUMPP
        IF(IDUMP.EQ.1) THEN
          IF(DUMPP.LT.15.0D0) DUMPP=15.0D0
          IF(DUMPP.GT.86400.0D0) DUMPP=86400.0D0
          WRITE(26,1830) DUMPP
 1830     FORMAT(3X,'Dumping period: DUMPP =',1P,E13.6)
        ENDIF
   83   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 83
      ENDIF
C
      IF(KWORD.EQ.KWNSIM) THEN
        READ(BUFFER,*) DSHN
        IF(DSHN.LT.1.0D0) DSHN=2.0D9
   84   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 84
      ELSE
        DSHN=2.0D9
      ENDIF
      WRITE(26,1840) DSHN
 1840 FORMAT(/3X,'Number of showers to be simulated =',1P,E13.6)
C
      IF(KWORD.EQ.KWRSEE) THEN
        READ(BUFFER,*) ISEED1,ISEED2
        WRITE(26,1850) ISEED1,ISEED2
 1850   FORMAT(3X,'Random-number generator seeds = ',I10,', ',I10)
   85   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 85
      ELSE
        ISEED1=12345
        ISEED2=54321
      ENDIF
C
      IF(KWORD.EQ.KWTIME) THEN
        READ(BUFFER,*) TIMEA
   86   CONTINUE
        READ(5,'(A6,1X,A120)') KWORD,BUFFER
        IF(KWORD.EQ.KWCOMM) GO TO 86
      ELSE
        TIMEA=100.0D0
      ENDIF
      IF(TIMEA.LT.1.0D0) TIMEA=100.0D0
      WRITE(26,1860) TIMEA
 1860 FORMAT(3X,'Computation time available = ',1P,E13.6,' sec')
C
C  ---- Uncertainty limit based on characteristic x rays intensity
C       Variables:   IXLZ = atomic number of x ray transition
C                           (0 if no uncertaintly limit is defined)
C                   IXLS1 = first shell of x ray transition
C                   IXLS2 = second shell of x ray transition
C                   IXLPD = id of the detector
C                           (-1 = any, 0 = all, >0 = specific detector)
C                   XLUNC = Rel. uncertainty of total intensity
C                  XLUNCF = Rel. uncertainty of fluorescence intensity
      IF(KWORD.EQ.KWXLIM) THEN
        READ(BUFFER,*) IXLZ, IXLS1, IXLS2, IXLPD, XLUNC, XLUNCF
        DO I=1,NPTRAN
          IF (IZS(I).EQ.IXLZ.AND.IS1S(I).EQ.IXLS1.AND.
     1          IS2S(I).EQ.IXLS2) GO TO 871
        ENDDO
        STOP 'Transition does not exist for simulation materials'
  871   CONTINUE
        IF (IXLPD.GT.NDEDEF) THEN
          STOP 'The detector specified is not defined'
        ENDIF
        IF(XLUNC.LT.0.0D0.OR.XLUNC.GT.1.0D0) THEN
          STOP 'Rel. un. on total intensity outside [0.0, 1.0]'
        ENDIF
        IF(XLUNCF.LT.0.0D0.OR.XLUNCF.GT.1.0D0) THEN
          STOP 'Rel. unc. on fluorescence intensity outside [0.0, 1.0]'
        ENDIF
C
        WRITE(26,1874) IXLS2,IXLS1,IXLZ
        IF(IXLPD.EQ.0) WRITE(26,1875)
        IF(IXLPD.LT.0) WRITE(26,1876)
        IF(IXLPD.GT.0) WRITE(26,1877) IXLPD
        IF(XLUNC.GT.0.0D0) WRITE(26,1878) XLUNC*100.0D0
        IF(XLUNCF.GT.0.0D0) WRITE(26,1879) XLUNCF*100.0D0
 1874   FORMAT(
     1        /3X,'Uncertainty limit:',
     1        /3X,'               transition = ',I2,'->',I2,
     1        /3X,'                        Z = ',I2)
 1875   FORMAT(3X,'                 detector = all')
 1876   FORMAT(3X,'                 detector = any')
 1877   FORMAT(3X,'                 detector = ',I2)
 1878   FORMAT(3X,'       on total intensity = ',F13.6,'%')
 1879   FORMAT(3X,'on fluorescence intensity = ',F13.6,'%')
      ELSE
        IXLZ=0
        IXLS1=0
        IXLS2=0
        XLUNC=0.0D0
        XLUNCF=0.0D0
        WRITE(26,1880)
 1880   FORMAT(/3X,'No simulation limit is defined')
      ENDIF
C
      CALL TIMER(TSECIN)
      TSECA=TIMEA+TSECIN
      TSECAD=TSECIN
      WRITE(26,1890)
 1890 FORMAT(//3X,72('-'))
C
C  ************  If 'RESUME' is active, read previously generated
C                counters...
C
      SHNA=0.0D0
      CPUTA=0.0D0
      IRETRN=0
      N=0
C
      DO ID=1,NDEDEF
        RLAST(ID)=0.0D0
        RWRITE(ID)=0.0D0
      ENDDO
C
      IF(IRESUM.EQ.1) THEN
        WRITE(6,*) ' Reading the DUMP file ...'
        OPEN(9,FILE=PFILER)
        READ (9,*,ERR=91,END=91) SHNA,CPUTA
        READ (9,'(A120)') TITLE2
        IF(TITLE2.NE.TITLE) THEN
          WRITE(26,*)
     1      'The dump file is corrupted (the TITLE does not match).'
          STOP 'The dump file is corrupted (the TITLE does not match).'
        ENDIF
        READ (9,*,ERR=90) ISEED1,ISEED2
        READ (9,*,ERR=90) (PRIM(I),I=1,3),(PRIM2(I),I=1,3)
        READ (9,*,ERR=90)
     1    ((SEC(K,I),I=1,3),K=1,3),((SEC2(K,I),I=1,3),K=1,3)
        READ (9,*,ERR=90) (TDEBO(I),I=1,NBODY), (TDEBO2(I),I=1,NBODY)
        READ (9,*,ERR=90) (((PDE(I,J,K),K=1,NBE),J=1,2),I=1,3),
     1             (((PDE2(I,J,K),K=1,NBE),J=1,2),I=1,3)
        READ (9,*,ERR=90) (((PDA(I,J,K),K=1,NBPH),J=1,NBTH),I=1,3),
     1             (((PDA2(I,J,K),K=1,NBPH),J=1,NBTH),I=1,3)
        READ (9,*,ERR=90) ((PDAT(I,J),J=1,NBTH),I=1,3),
     1             ((PDAT2(I,J),J=1,NBTH),I=1,3)
        READ (9,*,ERR=90) (TDED(I),I=1,NDEDEF), (TDED2(I),I=1,NDEDEF)
        READ (9,*,ERR=90) (RLAST(ID),ID=1,NDEDEF)
        READ (9,*,ERR=90) (RWRITE(ID),ID=1,NDEDEF)
        DO ID=1,NDEDEF
          READ (9,*,ERR=90) (DET(ID,J),J=1,NDECH(ID))
          READ (9,*,ERR=90) (DET2(ID,J),J=1,NDECH(ID))
          READ (9,*,ERR=90) (DoT(ID,J),J=1,NDECH(ID))
          READ (9,*,ERR=90) (DoT2(ID,J),J=1,NDECH(ID))
          READ (9,*,ERR=90) (DoF(ID,J),J=1,NDECH(ID))
          READ (9,*,ERR=90) (DoF2(ID,J),J=1,NDECH(ID))
        ENDDO
        IF(IDOEV.NE.0) THEN
          READ (9,*,ERR=90)
     1      (((DOEV(I1,I2,I3),I3=1,NDB(3)),I2=1,NDB(2)),I1=1,NDB(1)),
     1      (((DOEV2(I1,I2,I3),I3=1,NDB(3)),I2=1,NDB(2)),I1=1,NDB(1))
        ENDIF
        DO ID=1,NDEDEF
          DO I=1,NPTRAN
            IZZ=IZS(I)
            IS1=IS1S(I)
            IS2=IS2S(I)
            READ(9,*,ERR=90)
     1        PTIoT(ID,IZZ,IS1,IS2),PTIoT2(ID,IZZ,IS1,IS2)
            READ(9,*,ERR=90)
     1        (PTIoF(ID,IZZ,IS1,IS2,L),L=1,NILB5),
     1        (PTIoF2(ID,IZZ,IS1,IS2,L),L=1,NILB5)
          ENDDO
        ENDDO
        DO I=1,NPTRAN
          IZZ=IZS(I)
          IS1=IS1S(I)
          IS2=IS2S(I)
          READ(9,*,ERR=90)
     1      PTIGT(IZZ,IS1,IS2),PTIGT2(IZZ,IS1,IS2)
          READ(9,*,ERR=90)
     1      (PTIoG(IZZ,IS1,IS2,L),L=1,NILB5),
     1      (PTIoG2(IZZ,IS1,IS2,L),L=1,NILB5)
        ENDDO
        READ(9,*,ERR=90) (PDEBR(I),I=1,NBE),(PDEBR2(I),I=1,NBE)
        DO I=1,NPRZ
          READ(9,*,ERR=90)
     1      (PRZT(I,J),J=1,NPRZSL),(PRZT2(I,J),J=1,NPRZSL)
          DO J=1,NILB5
            READ(9,*,ERR=90)
     1        (PRZF(I,J,K),K=1,NPRZSL),(PRZF2(I,J,K),K=1,NPRZSL)
          ENDDO
        ENDDO
        DO I=1,NPRZ
          READ(9,*,ERR=90)
     1      (PRZGT(I,J),J=1,NPRZSL),(PRZGT2(I,J),J=1,NPRZSL)
          DO J=1,NILB5
            READ(9,*,ERR=90)
     1        (PRZG(I,J,K),K=1,NPRZSL),(PRZG2(I,J,K),K=1,NPRZSL)
          ENDDO
        ENDDO
        CLOSE(9)
        WRITE(26,1900) PFILER
 1900   FORMAT(3X,'Simulation has been resumed from dump file: ',A20)
        GO TO 92
   90   CONTINUE
        WRITE(26,*) 'The dump file is empty or corrupted.'
        STOP 'The dump file is empty or corrupted.'
   91   CONTINUE
        WRITE(26,1911)
 1911   FORMAT(3X,'WARNING: Could not resume from dump file...')
        CLOSE(90)
        IRESUM=0
      ENDIF
   92 CONTINUE
C
      IF(NDEDEF.GT.0) THEN
        DO ID=1,NDEDEF
          IF(IPSF(ID).NE.0) THEN
            IPSFU=20+ID
            OPEN(IPSFU,FILE=PSFDIO(ID),IOSTAT=KODE)
            IF(KODE.NE.0) THEN
              WRITE(26,'(''File '',A20,'' could not be opened.'')')
     1          PSFDIO(ID)
              STOP 'File could not be opened.'
            ENDIF
            RWR=0.0D0
            IF(RWRITE(ID).GT.0) THEN
   93         CONTINUE
              CALL RDPSF(IPSFU,PSFREC,KODE)
              IF(KODE.NE.0) THEN
                GO TO 94
              ELSE
                RWR=RWR+1.0D0
                IF(RWR.LT.RWRITE(ID)-0.5D0) GO TO 93
                GO TO 94
              ENDIF
            ENDIF
   94       CONTINUE
            IF(RWR.LT.0.5D0) THEN
              WRITE(IPSFU,1941) ID
 1941         FORMAT(1X,'#  Results from PENEPMA. Phase-space fi',
     1          'le of detector no.',I3,/1X,'#')
              WRITE(IPSFU,1942)
 1942         FORMAT(1X,'#/KPAR',2X,'E',12X,'X',12X,'Y',12X,'Z',12X,
     1          'U',12X,'V',12X,'W',11X,'WGHT',5X,'ILB(1:4)',7X,'NSHI',
     1          /1X,'#',125('-'))
            ENDIF
          ENDIF
        ENDDO
      ENDIF
C
      WRITE(26,'(//3X,''***  END  ***'')')
      CLOSE(26) ! Done writing in penepma.dat
C
C  ************  Create comma separated value output.
C
C     Write header of output file
C
C     SIM_TIME: Simulation time
C     SIM_SPEED: Simulation speed
C     N_ELECTRON: Number of electrons simulated
C
C     PE_BSE: Primary electrons backscattered
C     PE_TRANS: Primary electrons transmitted
C     PE_ABS Primary electrons absorbed
C
C     SE_BSE: Secondary electrons backscattered
C     SE_BSE_E: Absolute error on secondary electrons backscattered
C     SE_TRANS: Secondary electrons transmitted
C     SE_TRANS_E: Absolute error on secondary electrons transmitted
C     SE_ABS: Secondary electrons absorbed
C     SE_ABS_E: Absolute error on secondary electrons absorbed
C
C     X_BSE: X-rays backscattered
C     X_BSE_E: Absolute error on X-rays backscattered
C     X_TRANS: X-rays transmitted
C     X_TRANS_E: Absolute error on X-rays transmitted
C     X_ABS: X-rays absorbed
C     X_ABS_E: Absolute error on X-rays absorbed
C
C     F_BSE: Fraction (coefficient) of electron backscattered
C     F_TRANS: Fraction (coefficient) of electron transmitted
C     F_ABS: X-raysFraction (coefficient) of electron absorbed
C
C     BE_XXXX_AV: Average deposited energies in body XXXX
C     BE_XXXX_ER: Absolute error on average deposited energies in body XXXX
C     BE_XXXX_EF: Efficiency of average deposited energies in body XXXX
C
C     DE_XXXX_AV: Average photon energy at the detector XXXX
C     DE_XXXX_ER: Absolute error on average photon energy at the detector XXXX
C     DE_XXXX_EF: Efficiency of average photon energy at the detector XXXX
C
      IF(IRESUM.EQ.0) THEN ! Only write header on fresh start
        OPEN(99, FILE='penepma.csv')
        WRITE(99,9901) 'SIM_TIME  ','SIM_SPEED ','N_ELECTRON',
     1    'PE_BSE    ','PE_TRANS  ','PE_ABS    ',
     1    'SE_BSE    ','SE_BSE_E  ','SE_TRANS  ','SE_TRANS_E',
     1    'SE_ABS    ','SE_ABS_E  ',
     1    'X_BSE     ','X_BSE_E   ','X_TRANS   ','X_TRANS_E ',
     1    'X_ABS     ','X_ABS_E   ',
     1    'F_BSE     ','F_BSE_E   ','F_TRANS   ','F_TRANS_E ',
     1    'F_ABS     ','F_ABS_E   '
        DO I=1, NBODY
          IF(MATER(I).NE.0) THEN
            WRITE(99,9902) 'BE_',I,'_AV'
            WRITE(99,9902) 'BE_',I,'_ER'
            WRITE(99,9902) 'BE_',I,'_EF'
          ENDIF
        ENDDO
        DO I=1, NDEDEF
          WRITE(99,9902) 'DE_',I,'_AV'
          WRITE(99,9902) 'DE_',I,'_ER'
          WRITE(99,9902) 'DE_',I,'_EF'
        ENDDO
        WRITE(99,9903) 'SEED1     ','SEED2     '
        WRITE(99,*) ! Line carriage return
 9901   FORMAT(24(A10,','),$)
 9902   FORMAT(A,I4.4,A,',',$)
 9903   FORMAT(A,',',A,',',$)
        CLOSE(99)
      ENDIF
C
C  ************  Initialise constants.
C
      SDIAMG=SDIAM/4.0D0 ! For the gaussian beam distribution calculation
      SHN=SHNA          ! Shower counter, including the dump file.
      DSHN=DSHN+SHNA
      N=MOD(SHN,2.0D9)+0.5D0
      TSIM=CPUTA
      CPUT0=CPUTIM()
      IF(SHN.GE.DSHN) GO TO 105
      WRITE(6,*) ' The simulation is started ...'
C
C
C
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C  ------------------------  Shower simulation starts here.
C
  101 CONTINUE
C
C  ************  Primary particle counters.
C
      DO I=1,3
        DPRIM(I)=0.0D0
        DO K=1,3
          DSEC(K,I)=0.0D0
        ENDDO
      ENDDO
      DO ID=1,NDEDEF
        DEDE(ID)=0.0D0
      ENDDO
      DO KB=1,NBODY
        DEBO(KB)=0.0D0  ! Energies deposited in the various bodies KB.
      ENDDO
      IEXIT=0
C
      CALL CLEANS          ! Cleans the secondary stack.
C
C  **********  Set the initial state of the primary particle.
C
C  ****  Point source.
      SHN=SHN+1.0D0
      N=N+1
      IF(N.GT.2000000000) N=N-2000000000
      KPAR=KPARP
      WGHT=WGHT0
C  ----  Initial position with gaussian beam distribution ...
      X=SX0+SDIAMG*RNDG3()
      Y=SY0+SDIAMG*RNDG3()
      Z=SZ0
C  ----  Initial direction ...
      CALL GCONE(U,V,W)
C  ----  initial energy ...
      E=E0
      ILB(1)=1  ! Identifies primary particles.
      ILB(2)=0
      ILB(3)=0
      ILB(4)=0
      ILB(5)=1 ! Used to track the origin of photons (1: primary,
               ! 2: characteristic, 3: bremsstrahlung).
C
C  ****  Check if the trajectory intersects the material system.
C
      CALL LOCATE
C
      IF(MAT.EQ.0) THEN
        CALL STEP(1.0D30,DSEF,NCROSS)
        IF(MAT.EQ.0) THEN  ! The particle does not enter the system.
          IF(W.GT.0) THEN
            IEXIT=1        ! Labels emerging 'transmitted' particles.
          ELSE
            IEXIT=2        ! Labels emerging 'backscattered' particles.
          ENDIF
          GO TO 104        ! Exit.
        ENDIF
      ENDIF
C  ---------------------------------------------------------------------
C  ------------------------  Track simulation begins here.
C
      XORIG=X
      YORIG=Y
      ZORIG=Z
  102 CONTINUE
      CALL START           ! Starts simulation in current medium.
C
  103 CONTINUE

c<    write(6,'(''n,kpar,gen,x,y,z,w,e,ibody='',3i3,1p,5e11.3,i3)')
c<   1    mod(n,100),kpar,ilb(1),x,y,z,w,e,ibody

C
      IF((IFORCE(IBODY,KPAR).EQ.1).AND.((WGHT.GE.WLOW(IBODY,KPAR)).AND.
     1  (WGHT.LE.WHIG(IBODY,KPAR)))) THEN
        CALL JUMPF(DSMAX(IBODY),DS)  ! Interaction forcing.
        INTFOR=1
      ELSE
        CALL JUMP(DSMAX(IBODY),DS)   ! Analogue simulation.
        INTFOR=0
      ENDIF
      CALL STEP(DS,DSEF,NCROSS)      ! Determines step end position.
C  ----  Check whether the particle is outside the enclosure.
      IF(MAT.EQ.0) THEN
        IF(W.GT.0) THEN
          IEXIT=1        ! Labels emerging 'transmitted' particles.
        ELSE
          IEXIT=2        ! Labels emerging 'backscattered' particles.
        ENDIF
        GO TO 104        ! Exit.
      ENDIF
C  ----  If the particle has crossed an interface, restart the track in
C        the new material.
      IF(NCROSS.GT.0) GO TO 102    ! The particle crossed an interface.
C  ----  Simulate next event.
      IF(INTFOR.EQ.0) THEN
        CALL KNOCK(DE,ICOL)        ! Analogue simulation.
      ELSE
        CALL KNOCKF(DE,ICOL)       ! Interaction forcing is active.
      ENDIF
      DEP=DE*WGHT
      DEBO(IBODY)=DEBO(IBODY)+DEP
C
      IF(E.LT.EABS(KPAR,MAT)) THEN  ! The particle has been absorbed.
        DEBO(IBODY)=DEBO(IBODY)+E*WGHT
        IEXIT=3                     ! Labels absorbed particles.
        GO TO 104                   ! Exit.
      ENDIF
C
      GO TO 103
C  ------------------------  The simulation of the track ends here.
C  ---------------------------------------------------------------------
  104 CONTINUE
C
C  ************  Increment particle counters.
C
      IF(ILB(1).EQ.1) THEN
        DPRIM(IEXIT)=DPRIM(IEXIT)+WGHT
      ELSE
        DSEC(KPAR,IEXIT)=DSEC(KPAR,IEXIT)+WGHT
      ENDIF
C
      IF(IEXIT.LT.3) THEN
C  ****  Energy distribution of emerging particles.
        K=1.0D0+(E-EMIN)/BSE(KPAR)
        IF(K.GT.0.AND.K.LE.NBE) THEN
          IF(N.NE.LPDE(KPAR,IEXIT,K)) THEN
            PDE(KPAR,IEXIT,K)=PDE(KPAR,IEXIT,K)+PDEP(KPAR,IEXIT,K)
            PDE2(KPAR,IEXIT,K)=PDE2(KPAR,IEXIT,K)+PDEP(KPAR,IEXIT,K)**2
            PDEP(KPAR,IEXIT,K)=WGHT
            LPDE(KPAR,IEXIT,K)=N
          ELSE
            PDEP(KPAR,IEXIT,K)=PDEP(KPAR,IEXIT,K)+WGHT
          ENDIF
        ENDIF
C  ****  Angular distribution of emerging particles.
        THETA=ACOS(W)
        KTH=1.0D0+THETA*RA2DE/BSTH
        IF(ABS(U).GT.1.0D-16) THEN  !  Azimuthal bin number corrected.
           PHI=ATAN2(V,U)
        ELSE IF(ABS(V).GT.1.0D-16) THEN
           PHI=ATAN2(V,U)
        ELSE
           PHI=0.0D0
        ENDIF
        IF(PHI.LT.0.0D0) PHI=PHI+TWOPI
        KPH=1.0D0+PHI*RA2DE/BSPH
        IF(N.NE.LPDA(KPAR,KTH,KPH)) THEN
          PDA(KPAR,KTH,KPH)=PDA(KPAR,KTH,KPH)+PDAP(KPAR,KTH,KPH)
          PDA2(KPAR,KTH,KPH)=PDA2(KPAR,KTH,KPH)+PDAP(KPAR,KTH,KPH)**2
          PDAP(KPAR,KTH,KPH)=WGHT
          LPDA(KPAR,KTH,KPH)=N
        ELSE
          PDAP(KPAR,KTH,KPH)=PDAP(KPAR,KTH,KPH)+WGHT
        ENDIF
C
        IF(N.NE.LPDAT(KPAR,KTH)) THEN
          PDAT(KPAR,KTH)=PDAT(KPAR,KTH)+PDATP(KPAR,KTH)
          PDAT2(KPAR,KTH)=PDAT2(KPAR,KTH)+PDATP(KPAR,KTH)**2
          PDATP(KPAR,KTH)=WGHT
          LPDAT(KPAR,KTH)=N
        ELSE
          PDATP(KPAR,KTH)=PDATP(KPAR,KTH)+WGHT
        ENDIF
C  ****  Spectra of photon detectors.
        IF(KPAR.EQ.2) THEN
c<        write(6,*) 'theta,phi =',theta*ra2de,phi*ra2de
          DO ID=1,NDEDEF
            IF(PHI1(ID).LT.0.0D0) THEN
              IF(PHI.GT.PI) THEN
                PHID=PHI-TWOPI
              ELSE
                PHID=PHI
              ENDIF
            ELSE
              PHID=PHI
            ENDIF
            IF(PHID.GT.PHI1(ID).AND.PHID.LT.PHI2(ID).AND.
     1          THETA.GT.THETA1(ID).AND.THETA.LT.THETA2(ID)) THEN
              IF(E.GT.EDEL(ID).AND.E.LT.EDEU(ID)) THEN
                DEDE(ID)=DEDE(ID)+E*WGHT
                IE=1.0D0+(E-EDEL(ID))/BDEE(ID)
C  ****  All photons (full spectrum).
                IF(N.NE.LDET(ID,IE)) THEN
                  DET(ID,IE)=DET(ID,IE)+DETP(ID,IE)
                  DET2(ID,IE)=DET2(ID,IE)+DETP(ID,IE)**2
                  DETP(ID,IE)=WGHT
                  LDET(ID,IE)=N
                ELSE
                  DETP(ID,IE)=DETP(ID,IE)+WGHT
                ENDIF
C  ****  Characteristic x-rays (all except electron bremss).
                IF(.NOT.(ILB(2).EQ.1.AND.ILB(3).EQ.4)) THEN
                  IF(N.NE.LDoT(ID,IE)) THEN
                    DoT(ID,IE)=DoT(ID,IE)+DoTP(ID,IE)
                    DoT2(ID,IE)=DoT2(ID,IE)+DoTP(ID,IE)**2
                    DoTP(ID,IE)=WGHT
                    LDoT(ID,IE)=N
                  ELSE
                    DoTP(ID,IE)=DoTP(ID,IE)+WGHT
                  ENDIF
C  ****  Fluorescent x-rays (2nd and higher generations).
                  IF(ILB(1).GT.2) THEN
                    IF(N.NE.LDoF(ID,IE)) THEN
                      DoF(ID,IE)=DoF(ID,IE)+DoFP(ID,IE)
                      DoF2(ID,IE)=DoF2(ID,IE)+DoFP(ID,IE)**2
                      DoFP(ID,IE)=WGHT
                      LDoF(ID,IE)=N
                    ELSE
                      DoFP(ID,IE)=DoFP(ID,IE)+WGHT
                    ENDIF
                  ENDIF
                ENDIF
C
                IF(IORIG(ID).NE.0) THEN
                  WRITE(60+ID,'(1P,3E13.5)') XORIG,YORIG,ZORIG
                ENDIF
C
                IF(IPSF(ID).GT.0) THEN
                  IF(IPSF(ID).EQ.1) THEN
                    NSHJ=SHN-RLAST(ID)
                    CALL N2CH10(NSHJ,LCH10,NDIG)
                    WRITE(20+ID,'(I2,1P,8E13.5,I3,I2,I2,I9,1X,A)')
     1                KPAR,E,X,Y,Z,U,V,W,WGHT,
     2                ILB(1),ILB(2),ILB(3),ILB(4),LCH10(1:NDIG)
                    RWRITE(ID)=RWRITE(ID)+1.0D0
                    RLAST(ID)=SHN
                  ELSE IF(IPSF(ID).EQ.ILB(4)) THEN
                    NSHJ=SHN-RLAST(ID)
                    CALL N2CH10(NSHJ,LCH10,NDIG)
                    WRITE(20+ID,'(I2,1P,8E13.5,I3,I2,I2,I9,1X,A)')
     1                KPAR,E,X,Y,Z,U,V,W,WGHT,
     2                ILB(1),ILB(2),ILB(3),ILB(4),LCH10(1:NDIG)
                    RWRITE(ID)=RWRITE(ID)+1.0D0
                    RLAST(ID)=SHN
                  ENDIF
                ENDIF
              ENDIF
C
C  ****  Intensities of charact. lines (excluding electron bremss).
C
              IF(.NOT.(ILB(2).EQ.1.AND.ILB(3).EQ.4)) THEN
                CALL PEILB4(ILB(4),IZZ,IS1,IS2,IS3)
C  ----  All characteristic lines.
                IF(N.NE.LPTIoT(ID,IZZ,IS1,IS2)) THEN
                  PTIoT(ID,IZZ,IS1,IS2)=PTIoT(ID,IZZ,IS1,IS2)+
     1              PTIoTP(ID,IZZ,IS1,IS2)
                  PTIoT2(ID,IZZ,IS1,IS2)=PTIoT2(ID,IZZ,IS1,IS2)+
     1              PTIoTP(ID,IZZ,IS1,IS2)**2
                  PTIoTP(ID,IZZ,IS1,IS2)=WGHT
                  LPTIoT(ID,IZZ,IS1,IS2)=N
                ELSE
                  PTIoTP(ID,IZZ,IS1,IS2)=PTIoTP(ID,IZZ,IS1,IS2)+WGHT
                ENDIF
C  ----  Fluorescent x-rays (2nd and higher generations).
                ILB5=ILB(5)
                IF(ILB(1).EQ.2) ILB5=1  ! Primary x ray.
                IF(N.NE.LPTIoF(ID,IZZ,IS1,IS2,ILB5)) THEN
                  PTIoF(ID,IZZ,IS1,IS2,ILB5)=
     1              PTIoF(ID,IZZ,IS1,IS2,ILB5)+
     1              PTIoFP(ID,IZZ,IS1,IS2,ILB5)
                  PTIoF2(ID,IZZ,IS1,IS2,ILB5)=
     1              PTIoF2(ID,IZZ,IS1,IS2,ILB5)+
     1              PTIoFP(ID,IZZ,IS1,IS2,ILB5)**2
                  PTIoFP(ID,IZZ,IS1,IS2,ILB5)=WGHT
                  LPTIoF(ID,IZZ,IS1,IS2,ILB5)=N
                ELSE
                  PTIoFP(ID,IZZ,IS1,IS2,ILB5)=
     1              PTIoFP(ID,IZZ,IS1,IS2,ILB5)+WGHT
                ENDIF
C  ****  Phi rho z
                J=1.0D0+ABS(ZORIG)/PRZSL
                JF=1.0D0+ABS(ZORIG)/PRZSLF
                IF(J.GT.NPRZSL) J=NPRZSL
                IF(JF.GT.NPRZSL) JF=NPRZSL
                DO I=1,NPRZ
                  IF(IZZ.EQ.IPRZZ(I).AND.IS1.EQ.IPRZS1(I).AND.
     1                IS2.EQ.IPRZS2(I).AND.ID.EQ.IPRZPD(I)) THEN
C  ----  All characteristic lines.
                    IF(N.NE.LPRZT(I,J)) THEN
                      PRZT(I,J)=PRZT(I,J)+PRZTP(I,J)
                      PRZT2(I,J)=PRZT2(I,J)+PRZTP(I,J)**2
                      PRZTP(I,J)=WGHT
                      LPRZT(I,J)=N
                    ELSE
                      PRZTP(I,J)=PRZTP(I,J)+WGHT
                    ENDIF
C  ----  Fluorescent x-rays (2nd and higher generations).
                    IF(N.NE.LPRZF(I,ILB5,JF)) THEN
                      PRZF(I,ILB5,JF)=PRZF(I,ILB5,JF)+PRZFP(I,ILB5,JF)
                      PRZF2(I,ILB5,JF)=PRZF2(I,ILB5,JF)+
     1                  PRZFP(I,ILB5,JF)**2
                      PRZFP(I,ILB5,JF)=WGHT
                      LPRZF(I,ILB5,JF)=N
                    ELSE
                      PRZFP(I,ILB5,JF)=PRZFP(I,ILB5,JF)+WGHT
                    ENDIF
                  ENDIF
                ENDDO
              ENDIF
            ENDIF
          ENDDO
        ENDIF
      ENDIF
C
C  ************  Any secondary left?
C
  202 CONTINUE
      CALL SECPAR(LEFT)
      IF(LEFT.GT.0) THEN
C  ****  Simulate particles up to the 4th generation.
        IF(ILB(1).GT.4) GO TO 202
C
        IF(KPAR.EQ.2) THEN
C
C  ****  Energy distribution of emitted bremsstrahlung photons.
          IF(KPAR.EQ.2.AND.ILB(2).EQ.1.AND.ILB(3).EQ.4) THEN
            K=1.0D0+(E-EMIN)/BSE(KPAR)
            IF(K.GT.0.AND.K.LE.NBE) THEN
              IF(N.NE.LPDEBR(K)) THEN
                PDEBR(K)=PDEBR(K)+PDEBRP(K)
                PDEBR2(K)=PDEBR2(K)+PDEBRP(K)**2
                PDEBRP(K)=WGHT
                LPDEBR(K)=N
              ELSE
                PDEBRP(K)=PDEBRP(K)+WGHT
              ENDIF
            ENDIF
          ENDIF
C
C  ****  Set ILB(5) for 2nd-generation photons, to separate fluorescence
C        from characteritic x rays and from the bremss continuum.
          IF(ILB(5).EQ.1) THEN
            IF(ILB(3).EQ.5) THEN
              ILB(5)=2  ! Characteristic x-ray from a shell ionisation.
            ELSE IF(ILB(3).EQ.4) THEN
              ILB(5)=3  ! Bremsstrahlung photon.
            ENDIF
          ENDIF
C
C  *****  Store generated intensities of characteristic lines
          IF(.NOT.(ILB(2).EQ.1.AND.ILB(3).EQ.4)) THEN
            CALL PEILB4(ILB(4),IZZ,IS1,IS2,IS3)
C  ----  All characteristic lines.
            IF(N.NE.LPTIGT(IZZ,IS1,IS2)) THEN
              PTIGT(IZZ,IS1,IS2)=PTIGT(IZZ,IS1,IS2)+PTIGTP(IZZ,IS1,IS2)
              PTIGT2(IZZ,IS1,IS2)=PTIGT2(IZZ,IS1,IS2)+
     1              PTIGTP(IZZ,IS1,IS2)**2
              PTIGTP(IZZ,IS1,IS2)=WGHT
              LPTIGT(IZZ,IS1,IS2)=N
            ELSE
              PTIGTP(IZZ,IS1,IS2)=PTIGTP(IZZ,IS1,IS2)+WGHT
            ENDIF
C  ----  Fluorescent x-rays (2nd and higher generations).
            ILB5=ILB(5)
            IF(ILB(1).EQ.2) ILB5=1  ! Primary x ray.
            IF(N.NE.LPTIoG(IZZ,IS1,IS2,ILB5)) THEN
              PTIoG(IZZ,IS1,IS2,ILB5)=PTIoG(IZZ,IS1,IS2,ILB5)+
     1          PTIoGP(IZZ,IS1,IS2,ILB5)
              PTIoG2(IZZ,IS1,IS2,ILB5)=PTIoG2(IZZ,IS1,IS2,ILB5)+
     1          PTIoGP(IZZ,IS1,IS2,ILB5)**2
              PTIoGP(IZZ,IS1,IS2,ILB5)=WGHT
              LPTIoG(IZZ,IS1,IS2,ILB5)=N
            ELSE
              PTIoGP(IZZ,IS1,IS2,ILB5)=PTIoGP(IZZ,IS1,IS2,ILB5)+WGHT
            ENDIF
C  ****  Phi rho z generated
            J=1.0D0+ABS(Z)/PRZSL
            JF=1.0D0+ABS(Z)/PRZSLF
            IF(J.GT.NPRZSL) J=NPRZSL
            IF(JF.GT.NPRZSL) JF=NPRZSL
            DO I=1,NPRZ
              IF(IZZ.EQ.IPRZZ(I).AND.IS1.EQ.IPRZS1(I).AND.
     1            IS2.EQ.IPRZS2(I)) THEN
C  ----  All characteristic lines.
                IF(N.NE.LPRZGT(I,J)) THEN
                  PRZGT(I,J)=PRZGT(I,J)+PRZGTP(I,J)
                  PRZGT2(I,J)=PRZGT2(I,J)+PRZGTP(I,J)**2
                  PRZGTP(I,J)=WGHT
                  LPRZGT(I,J)=N
                ELSE
                  PRZGTP(I,J)=PRZGTP(I,J)+WGHT
                ENDIF
C  ----  Fluorescent x-rays (2nd and higher generations).
                IF(N.NE.LPRZG(I,ILB5,JF)) THEN
                  PRZG(I,ILB5,JF)=PRZG(I,ILB5,JF)+PRZGP(I,ILB5,JF)
                  PRZG2(I,ILB5,JF)=PRZG2(I,ILB5,JF)+PRZGP(I,ILB5,JF)**2
                  PRZGP(I,ILB5,JF)=WGHT
                  LPRZG(I,ILB5,JF)=N
                ELSE
                  PRZGP(I,ILB5,JF)=PRZGP(I,ILB5,JF)+WGHT
                ENDIF
              ENDIF
            ENDDO
          ENDIF
        ENDIF
C
C  ****  Spatial distribution of characteristic x-ray emission.
        IF(KPAR.EQ.2.AND.IDOEV.EQ.1) THEN
          IF(ILB(4).NE.0.AND.XEMIN.LT.E.AND.XEMAX.GT.E) THEN
            IF((X.GT.DXL(1).AND.X.LT.DXU(1)).AND.
     1         (Y.GT.DXL(2).AND.Y.LT.DXU(2)).AND.
     1         (Z.GT.DXL(3).AND.Z.LT.DXU(3))) THEN
              I1=1.0D0+(X-DXL(1))*BDOEVR(1)
              I2=1.0D0+(Y-DXL(2))*BDOEVR(2)
              I3=1.0D0+(Z-DXL(3))*BDOEVR(3)
              IF(N.NE.LDOEV(I1,I2,I3)) THEN
                DOEV(I1,I2,I3)=DOEV(I1,I2,I3)+DOEVP(I1,I2,I3)
                DOEV2(I1,I2,I3)=DOEV2(I1,I2,I3)+DOEVP(I1,I2,I3)**2
                DOEVP(I1,I2,I3)=WGHT
                LDOEV(I1,I2,I3)=N
              ELSE
                DOEVP(I1,I2,I3)=DOEVP(I1,I2,I3)+WGHT
              ENDIF
            ENDIF
          ENDIF
        ENDIF
c<    write(6,'(/''new secondary'')')
c<    write(6,'(''n,kpar,gen,x,y,z,w,e,ibody='',3i3,1p,5e11.3,i3)')
c<   1    mod(n,100),kpar,ilb(1),x,y,z,w,e,ibody
        DEBO(IBODY)=DEBO(IBODY)-E*WGHT  ! Energy is removed.
        XORIG=X
        YORIG=Y
        ZORIG=Z
        GO TO 102
      ENDIF
C
C  ------------------------  The simulation of the shower ends here.
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C
C
C
      DO I=1,3
        PRIM(I)=PRIM(I)+DPRIM(I)
        PRIM2(I)=PRIM2(I)+DPRIM(I)**2
        DO K=1,3
          SEC(K,I)=SEC(K,I)+DSEC(K,I)
          SEC2(K,I)=SEC2(K,I)+DSEC(K,I)**2
        ENDDO
      ENDDO
C
C  ****  Energies deposited in different bodies.
C
      DO KB=1,NBODY
        TDEBO(KB)=TDEBO(KB)+DEBO(KB)
        TDEBO2(KB)=TDEBO2(KB)+DEBO(KB)**2
      ENDDO
C
C  ****  Energies entering the photon detectors.
C
      DO KD=1,NDEDEF
        TDED(KD)=TDED(KD)+DEDE(KD)
        TDED2(KD)=TDED2(KD)+DEDE(KD)**2
      ENDDO
C
  105 CONTINUE
      CALL TIMER(TSEC)
C
C  ****  Calculate the uncertainty on the x-ray transition
C
      IF (IXLZ.GT.0) THEN
        TOTN=SHN*WGHT0
        DF=1.0D0/TOTN
        IF(IXLPD.LT.0) THEN ! any detector
          XSUNC=1.0D0
          XSUNCF=1.0D0
          ID0=1
          IDN=NDEDEF
        ELSE IF(IXLPD.EQ.0) THEN ! all detectors
          XSUNC=0.0D0
          XSUNCF=0.0D0
          ID0=1
          IDN=NDEDEF
        ELSE ! specific detector
          XSUNC=1.0D0
          XSUNCF=1.0D0
          ID0=IXLPD
          IDN=IXLPD
        ENDIF
C
        DO ID=ID0,IDN
          YERR=3.0D0*SQRT(ABS(PTIoT2(ID,IXLZ,IXLS1,IXLS2)-
     1      PTIoT(ID,IXLZ,IXLS1,IXLS2)**2*DF))
          YAV=PTIoT(ID,IXLZ,IXLS1,IXLS2)
          IF(YAV.NE.0) THEN
            XDUNC=MIN(YERR/YAV,1.0D0)
          ELSE
            XDUNC=1.0D0
          ENDIF
          IF(IXLPD.EQ.0) THEN ! all detectors
            XSUNC=MAX(XDUNC,XSUNC)
          ELSE ! first detector
            XSUNC=MIN(XDUNC,XSUNC)
          ENDIF
C
          YERRFC=3.0D0*SQRT(ABS(PTIoF2(ID,IXLZ,IXLS1,IXLS2,2)-
     1      PTIoF(ID,IXLZ,IXLS1,IXLS2,2)**2*DF))
          YAVFC=PTIoF(ID,IXLZ,IXLS1,IXLS2,2)
          YERRFB=3.0D0*SQRT(ABS(PTIoF2(ID,IXLZ,IXLS1,IXLS2,3)-
     1      PTIoF(ID,IXLZ,IXLS1,IXLS2,3)**2*DF))
          YAVFB=PTIoF(ID,IXLZ,IXLS1,IXLS2,3)
          YERRF=YERRFC+YERRFB
          YAVF=YAVFC+YAVFB
          IF(YAVF.NE.0) THEN
            XDUNCF=MIN(YERRF/YAVF,1.0D0)
          ELSE
            XDUNCF=1.0D0
          ENDIF
          IF(IXLPD.EQ.0) THEN ! all detectors
            XSUNCF=MAX(XDUNCF,XSUNCF)
          ELSE ! first detector
            XSUNCF=MIN(XDUNCF,XSUNCF)
          ENDIF
        ENDDO
      ELSE
        XSUNC=1.0D0
        XSUNCF=1.0D0
      ENDIF
C
C  ----  End the simulation after the allotted time or after completing
C        DSHN showers.
C
      IRETRN=0
      IF(TSEC.LT.TSECA.AND.SHN.LT.DSHN.AND.
     1    XSUNC.GT.XLUNC.AND.XSUNCF.GT.XLUNCF) THEN
C  ****  Write partial results after each dumping period.
        IF(TSEC-TSECAD.GT.DUMPP) THEN
          IF(IDUMP.EQ.1) THEN
            TSECAD=TSEC
            IRETRN=1
            GO TO 203
          ENDIF
        ENDIF
        GO TO 101
      ENDIF
  203 CONTINUE
      TSIM=TSIM+CPUTIM()-CPUT0
C
      OPEN(98,FILE='penepma.log')
      WRITE(98,*) TOTN,TSIM,XSUNC,XSUNCF
      CLOSE(98)
C
C  ************  Transfer partial counters to global counters.
C
      DO KPAR=1,3
      DO IEXIT=1,2
      DO IE=1,NBE
        PDE(KPAR,IEXIT,IE)=PDE(KPAR,IEXIT,IE)+PDEP(KPAR,IEXIT,IE)
        PDE2(KPAR,IEXIT,IE)=PDE2(KPAR,IEXIT,IE)+PDEP(KPAR,IEXIT,IE)**2
        PDEP(KPAR,IEXIT,IE)=0.0D0
        LPDE(KPAR,IEXIT,IE)=0
      ENDDO
      ENDDO
      ENDDO
C
      DO KPAR=1,3
      DO KTH=1,NBTH
        PDAT(KPAR,KTH)=PDAT(KPAR,KTH)+PDATP(KPAR,KTH)
        PDAT2(KPAR,KTH)=PDAT2(KPAR,KTH)+PDATP(KPAR,KTH)**2
        PDATP(KPAR,KTH)=0.0D0
        LPDAT(KPAR,KTH)=0
        DO KPH=1,NBPH
          PDA(KPAR,KTH,KPH)=PDA(KPAR,KTH,KPH)+PDAP(KPAR,KTH,KPH)
          PDA2(KPAR,KTH,KPH)=PDA2(KPAR,KTH,KPH)+PDAP(KPAR,KTH,KPH)**2
          PDAP(KPAR,KTH,KPH)=0.0D0
          LPDA(KPAR,KTH,KPH)=0
        ENDDO
      ENDDO
      ENDDO
C
      DO ID=1,NDEDEF
        DO J=1,NDECH(ID)
          DET(ID,J)=DET(ID,J)+DETP(ID,J)
          DET2(ID,J)=DET2(ID,J)+DETP(ID,J)**2
          DETP(ID,J)=0.0D0
          LDET(ID,J)=0
C
          DoT(ID,J)=DoT(ID,J)+DoTP(ID,J)
          DoT2(ID,J)=DoT2(ID,J)+DoTP(ID,J)**2
          DoTP(ID,J)=0.0D0
          LDoT(ID,J)=0
C
          DoF(ID,J)=DoF(ID,J)+DoFP(ID,J)
          DoF2(ID,J)=DoF2(ID,J)+DoFP(ID,J)**2
          DoFP(ID,J)=0.0D0
          LDoF(ID,J)=0
        ENDDO
      ENDDO
C
      IF(IDOEV.NE.0) THEN
        DO I3=1,NDB(3)
        DO I2=1,NDB(2)
        DO I1=1,NDB(1)
          DOEV(I1,I2,I3)=DOEV(I1,I2,I3)+DOEVP(I1,I2,I3)
          DOEV2(I1,I2,I3)=DOEV2(I1,I2,I3)+DOEVP(I1,I2,I3)**2
          DOEVP(I1,I2,I3)=0.0D0
          LDOEV(I1,I2,I3)=0
        ENDDO
        ENDDO
        ENDDO
      ENDIF
C
      DO ID=1,NDEDEF
        DO I=1,NPTRAN
          IZZ=IZS(I)
          IS1=IS1S(I)
          IS2=IS2S(I)
C
          PTIoT(ID,IZZ,IS1,IS2)=PTIoT(ID,IZZ,IS1,IS2)+
     1      PTIoTP(ID,IZZ,IS1,IS2)
          PTIoT2(ID,IZZ,IS1,IS2)=PTIoT2(ID,IZZ,IS1,IS2)+
     1      PTIoTP(ID,IZZ,IS1,IS2)**2
          PTIoTP(ID,IZZ,IS1,IS2)=0.0D0
          LPTIoT(ID,IZZ,IS1,IS2)=0
C
          DO J=1,NILB5
            PTIoF(ID,IZZ,IS1,IS2,J)=PTIoF(ID,IZZ,IS1,IS2,J)+
     1        PTIoFP(ID,IZZ,IS1,IS2,J)
            PTIoF2(ID,IZZ,IS1,IS2,J)=PTIoF2(ID,IZZ,IS1,IS2,J)+
     1        PTIoFP(ID,IZZ,IS1,IS2,J)**2
            PTIoFP(ID,IZZ,IS1,IS2,J)=0.0D0
            LPTIoF(ID,IZZ,IS1,IS2,J)=0
          ENDDO
        ENDDO
      ENDDO
C
      DO I=1,NPTRAN
        IZZ=IZS(I)
        IS1=IS1S(I)
        IS2=IS2S(I)
C
        PTIGT(IZZ,IS1,IS2)=PTIGT(IZZ,IS1,IS2)+PTIGTP(IZZ,IS1,IS2)
        PTIGT2(IZZ,IS1,IS2)=PTIGT2(IZZ,IS1,IS2)+PTIGTP(IZZ,IS1,IS2)**2
        PTIGTP(IZZ,IS1,IS2)=0.0D0
        LPTIGT(IZZ,IS1,IS2)=0
C
        DO J=1,NILB5
          PTIoG(IZZ,IS1,IS2,J)=PTIoG(IZZ,IS1,IS2,J)+
     1      PTIoGP(IZZ,IS1,IS2,J)
          PTIoG2(IZZ,IS1,IS2,J)=PTIoG2(IZZ,IS1,IS2,J)+
     1      PTIoGP(IZZ,IS1,IS2,J)**2
          PTIoGP(IZZ,IS1,IS2,J)=0.0D0
          LPTIoG(IZZ,IS1,IS2,J)=0
        ENDDO
      ENDDO
C
      DO K=1,NBE
        PDEBR(K)=PDEBR(K)+PDEBRP(K)
        PDEBR2(K)=PDEBR2(K)+PDEBRP(K)**2
        PDEBRP(K)=0.0D0
        LPDEBR(K)=0
      ENDDO
C
      DO I=1,NPRZ
        DO J=1,NPRZSL
          PRZT(I,J)=PRZT(I,J)+PRZTP(I,J)
          PRZT2(I,J)=PRZT2(I,J)+PRZTP(I,J)**2
          PRZTP(I,J)=0.0D0
          LPRZT(I,J)=0
          PRZGT(I,J)=PRZGT(I,J)+PRZGTP(I,J)
          PRZGT2(I,J)=PRZGT2(I,J)+PRZGTP(I,J)**2
          PRZGTP(I,J)=0.0D0
          LPRZGT(I,J)=0
        ENDDO
C
        DO J=1,NILB5
          DO K=1,NPRZSL
            PRZF(I,J,K)=PRZF(I,J,K)+PRZFP(I,J,K)
            PRZF2(I,J,K)=PRZF2(I,J,K)+PRZFP(I,J,K)**2
            PRZFP(I,J,K)=0.0D0
            LPRZF(I,J,K)=0
            PRZG(I,J,K)=PRZG(I,J,K)+PRZGP(I,J,K)
            PRZG2(I,J,K)=PRZG2(I,J,K)+PRZGP(I,J,K)**2
            PRZGP(I,J,K)=0.0D0
            LPRZG(I,J,K)=0
          ENDDO
        ENDDO
      ENDDO
C
C  ************  If 'DUMPTO' is active, write counters in a dump file.
C
      IF(IDUMP.EQ.1) THEN
        OPEN(9,FILE=PFILED)
        WRITE(9,*) SHN,TSIM
        WRITE(9,'(A120)') TITLE
        WRITE(9,*) ISEED1,ISEED2
        WRITE(9,*) (PRIM(I),I=1,3),(PRIM2(I),I=1,3)
        WRITE(9,*) ((SEC(K,I),I=1,3),K=1,3),((SEC2(K,I),I=1,3),K=1,3)
        WRITE(9,*) (TDEBO(I),I=1,NBODY), (TDEBO2(I),I=1,NBODY)
        WRITE(9,*) (((PDE(I,J,K),K=1,NBE),J=1,2),I=1,3),
     1             (((PDE2(I,J,K),K=1,NBE),J=1,2),I=1,3)
        WRITE(9,*) (((PDA(I,J,K),K=1,NBPH),J=1,NBTH),I=1,3),
     1             (((PDA2(I,J,K),K=1,NBPH),J=1,NBTH),I=1,3)
        WRITE(9,*) ((PDAT(I,J),J=1,NBTH),I=1,3),
     1             ((PDAT2(I,J),J=1,NBTH),I=1,3)
        WRITE(9,*) (TDED(I),I=1,NDEDEF), (TDED2(I),I=1,NDEDEF)
        WRITE(9,*) (RLAST(ID),ID=1,NDEDEF)
        WRITE(9,*) (RWRITE(ID),ID=1,NDEDEF)
        DO ID=1,NDEDEF
          WRITE(9,*) (DET(ID,J),J=1,NDECH(ID))
          WRITE(9,*) (DET2(ID,J),J=1,NDECH(ID))
          WRITE(9,*) (DoT(ID,J),J=1,NDECH(ID))
          WRITE(9,*) (DoT2(ID,J),J=1,NDECH(ID))
          WRITE(9,*) (DoF(ID,J),J=1,NDECH(ID))
          WRITE(9,*) (DoF2(ID,J),J=1,NDECH(ID))
        ENDDO
        IF(IDOEV.NE.0) THEN
          WRITE(9,*)
     1      (((DOEV(I1,I2,I3),I3=1,NDB(3)),I2=1,NDB(2)),I1=1,NDB(1)),
     1      (((DOEV2(I1,I2,I3),I3=1,NDB(3)),I2=1,NDB(2)),I1=1,NDB(1))
        ENDIF
        DO ID=1,NDEDEF
          DO I=1,NPTRAN
            IZZ=IZS(I)
            IS1=IS1S(I)
            IS2=IS2S(I)
            WRITE(9,*) PTIoT(ID,IZZ,IS1,IS2),PTIoT2(ID,IZZ,IS1,IS2)
            WRITE(9,*)
     1        (PTIoF(ID,IZZ,IS1,IS2,L),L=1,NILB5),
     1        (PTIoF2(ID,IZZ,IS1,IS2,L),L=1,NILB5)
          ENDDO
        ENDDO
        DO I=1,NPTRAN
          IZZ=IZS(I)
          IS1=IS1S(I)
          IS2=IS2S(I)
          WRITE(9,*) PTIGT(IZZ,IS1,IS2),PTIGT2(IZZ,IS1,IS2)
          WRITE(9,*)
     1      (PTIoG(IZZ,IS1,IS2,L),L=1,NILB5),
     1      (PTIoG2(IZZ,IS1,IS2,L),L=1,NILB5)
        ENDDO
        WRITE(9,*) (PDEBR(I),I=1,NBE),(PDEBR2(I),I=1,NBE)
        DO I=1,NPRZ
          WRITE(9,*) (PRZT(I,J),J=1,NPRZSL),(PRZT2(I,J),J=1,NPRZSL)
          DO J=1,NILB5
            WRITE(9,*)
     1        (PRZF(I,J,K),K=1,NPRZSL),(PRZF2(I,J,K),K=1,NPRZSL)
          ENDDO
        ENDDO
        DO I=1,NPRZ
          WRITE(9,*) (PRZGT(I,J),J=1,NPRZSL),(PRZGT2(I,J),J=1,NPRZSL)
          DO J=1,NILB5
            WRITE(9,*)
     1        (PRZG(I,J,K),K=1,NPRZSL),(PRZG2(I,J,K),K=1,NPRZSL)
          ENDDO
        ENDDO
        WRITE(9,'(/3X,''*** END ***'')')
        CLOSE(9)
      ENDIF
C
C  ------------------------  Print simulation results.
C
C     IEXIT: 1=transmitted, 2=backscattered, 3=absorbed.
C
      OPEN(99, FILE='penepma.csv', ACCESS='APPEND')
C
      TOTN=SHN*WGHT0
      TAVS=TOTN/TSIM
      FNT=1.0D0/TOTN
C
C  ****  Time, speed, number of electrons
C                    'SIM_TIME  ', 'SIM_SPEED ', 'N_ELECTRON'
      WRITE(99,9913)  TSIM       ,  TAVS       ,  TOTN
C
C  ****  Primary particles counters
C                    'PE_BSE    ', 'PE_TRANS  ', 'PE_ABS    '
      WRITE(99,9913)  PRIM(1)    ,  PRIM(2)    ,  PRIM(3)
C
C  ****  Secondary-particle generation probabilities WSEC(KPAR,IEXIT)
      DO K=1,3
        DO I=1,3
          WSEC2(K,I)=3.0D0*FNT*SQRT(ABS(SEC2(K,I)-SEC(K,I)**2*FNT))
          WSEC(K,I)=SEC(K,I)*FNT
        ENDDO
      ENDDO
C                   'SE_BSE    ', 'SE_BSE_E  '
      WRITE(99,9912) WSEC(1,1)  ,  WSEC2(1,1)
C                   'SE_TRANS  ', 'SE_TRANS_E',
      WRITE(99,9912) WSEC(1,2)  ,  WSEC2(1,2)
C                   'SE_ABS    ', 'SE_ABS_E  ',
      WRITE(99,9912) WSEC(1,3)  ,  WSEC2(1,3)
C                   'X_BSE     ', 'X_BSE_E   ',
      WRITE(99,9912) WSEC(2,1)  ,  WSEC2(2,1)
C                   'X_TRANS   ', 'X_TRANS_E ',
      WRITE(99,9912) WSEC(2,2)  ,  WSEC2(2,2)
C                   'X_ABS     ', 'X_ABS_E   '
      WRITE(99,9912) WSEC(2,3)  ,  WSEC2(2,3)
C
C  ****  Fractions (coefficients)
      FB=(PRIM(1)+SEC(KPARP,1))*FNT
      ERR1=3.0D0*FNT*SQRT(ABS(PRIM2(1)-PRIM(1)**2*FNT))
      ERR2=3.0D0*FNT*SQRT(ABS(SEC2(KPARP,1)-SEC(KPARP,1)**2*FNT))
      FBERR=ERR1+ERR2
C                   'F_BSE     ', 'F_BSE_E   '
      WRITE(99,9912) FB         ,  FBERR
C
      FT=(PRIM(2)+SEC(KPARP,2))*FNT
      ERR1=3.0D0*FNT*SQRT(ABS(PRIM2(2)-PRIM(2)**2*FNT))
      ERR2=3.0D0*FNT*SQRT(ABS(SEC2(KPARP,2)-SEC(KPARP,2)**2*FNT))
      FTERR=ERR1+ERR2
C                   'F_TRANS   ', 'F_TRANS_E '
      WRITE(99,9912) FT         ,  FTERR
C
      FA=PRIM(3)*FNT
      ERR=3.0D0*FNT*SQRT(ABS(PRIM2(3)-PRIM(3)**2*FNT))
C                   'F_ABS     ', 'F_ABS_E   '
      WRITE(99,9912) FA         ,  FAERR
C
C  ****  Average energies deposited in bodies..
      DF=1.0D0/TOTN
      DO KB=1,NBODY
        IF(MATER(KB).NE.0) THEN
          QER=3.0D0*DF*SQRT(ABS(TDEBO2(KB)-TDEBO(KB)**2*DF))
          QAV=TDEBO(KB)*DF
          IF(QER.GT.1.0D-10*ABS(QAV)) THEN
            EFFIC=QAV**2/((QER/3.0D0)**2*TSIM)
          ELSE
            EFFIC=0.0D0
          ENDIF
          WRITE(99,9913) QAV,QER,EFFIC
        ENDIF
      ENDDO
C
C  ****  Average energies entering the detectors.
      DO KD=1,NDEDEF
        QER=3.0D0*DF*SQRT(ABS(TDED2(KD)-TDED(KD)**2*DF))
        QAV=TDED(KD)*DF
        IF(QER.GT.1.0D-10*ABS(QAV)) THEN
          EFFIC=QAV**2/((QER/3.0D0)**2*TSIM)
        ELSE
          EFFIC=0.0D0
        ENDIF
        WRITE(99,9913) QAV,QER,EFFIC
      ENDDO
C
C  ****  Last random seeds.
      WRITE(99,9914) ISEED1,ISEED2
C
      WRITE(99,*) ! Line carriage return
      CLOSE(99)
C
 9912 FORMAT(2(E10.4,','),$) ! Two values
 9913 FORMAT(3(E10.4,','),$) ! Three values
 9914 FORMAT(2(I10,','),$) ! Two integers
C
C  ************  Energy distributions of emerging particles.
C
C  ****  Transmitted electrons.
      OPEN(9,FILE='pe-energy-el-trans.dat')
      WRITE(9,9110)
 9110 FORMAT(
     1  1X,'#  Results from PENEPMA.',
     1 /1X,'#  Energy distribution of transmitted electrons.',
     1 /1X,'#  1st column: E (eV).',
     1 /1X,'#  2nd and 3rd columns: probability density and STU',
     1         ' (1/(eV*particle)).',/)
      DO K=1,NBE
        XX=EMIN+(K-0.5D0)*BSE(1)
        YERR=3.0D0*SQRT(ABS(PDE2(1,2,K)-PDE(1,2,K)**2*DF))
        YAV=PDE(1,2,K)*DF/BSE(1)
        YERR=YERR*DF/BSE(1)
        WRITE(9,'(1X,1P,3E14.6)')
     1     XX,MAX(YAV,1.0D-35),MAX(YERR,1.0D-35)
      ENDDO
      CLOSE(9)
C  ****  Backscattered electrons.
      OPEN(9,FILE='pe-energy-el-back.dat')
      WRITE(9,9120)
 9120 FORMAT(
     1  1X,'#  Results from PENEPMA.',
     1 /1X,'#  Energy distribution of backscattered electrons.',
     1 /1X,'#  1st column: E (eV).',
     1 /1X,'#  2nd and 3rd columns: probability density and STU',
     1         ' (1/(eV*particle)).',/)
      DO K=1,NBE
        XX=EMIN+(K-0.5D0)*BSE(1)
        YERR=3.0D0*SQRT(ABS(PDE2(1,1,K)-PDE(1,1,K)**2*DF))
        YAV=PDE(1,1,K)*DF/BSE(1)
        YERR=YERR*DF/BSE(1)
        WRITE(9,'(1X,1P,3E14.6)')
     1     XX,MAX(YAV,1.0D-35),MAX(YERR,1.0D-35)
      ENDDO
      CLOSE(9)
C  ****  Transmitted photons.
      OPEN(9,FILE='pe-energy-ph-trans.dat')
      WRITE(9,9130)
 9130 FORMAT(
     1  1X,'#  Results from PENEPMA.',
     1 /1X,'#  Energy distribution of transmitted photons.',
     1 /1X,'#  1st column: E (eV).',
     1 /1X,'#  2nd and 3rd columns: probability density and STU',
     1         ' (1/(eV*particle)).',/)
      DO K=1,NBE
        XX=EMIN+(K-0.5D0)*BSE(2)
        YERR=3.0D0*SQRT(ABS(PDE2(2,2,K)-PDE(2,2,K)**2*DF))
        YAV=PDE(2,2,K)*DF/BSE(2)
        YERR=YERR*DF/BSE(2)
        WRITE(9,'(1X,1P,3E14.6)')
     1     XX,MAX(YAV,1.0D-35),MAX(YERR,1.0D-35)
      ENDDO
      CLOSE(9)
C  ****  Backscattered photons.
      OPEN(9,FILE='pe-energy-ph-back.dat')
      WRITE(9,9140)
 9140 FORMAT(
     1  1X,'#  Results from PENEPMA.',
     1 /1X,'#  Energy distribution of backscattered photons.',
     1 /1X,'#  1st column: E (eV).',
     1 /1X,'#  2nd and 3rd columns: probability density and STU',
     1         ' (1/(eV*particle)).',/)
      DO K=1,NBE
        XX=EMIN+(K-0.5D0)*BSE(2)
        YERR=3.0D0*SQRT(ABS(PDE2(2,1,K)-PDE(2,1,K)**2*DF))
        YAV=PDE(2,1,K)*DF/BSE(2)
        YERR=YERR*DF/BSE(2)
        WRITE(9,'(1X,1P,3E14.6)')
     1     XX,MAX(YAV,1.0D-35),MAX(YERR,1.0D-35)
      ENDDO
      CLOSE(9)
C
C  ************  Angular distributions of emerging particles.
C
      OPEN(9,FILE='pe-anel.dat')
      WRITE(9,9060)
 9060 FORMAT(
     1  1X,'#  Results from PENEPMA. ',
     1 /1X,'#  Angular distribution of emerging electrons.',
     1 /1X,'#  1st column: THETA (deg).',
     1 /1X,'#  2nd and 3rd columns: probability density and STU',
     1         ' (1/sr)',/)
      DO K=1,NBTH
        XX=(K-0.5D0)*BSTH
        XXR=(K-1.0D0)*BSTH*DE2RA
        DSANG=(COS(XXR)-COS(XXR+BSTH*DE2RA))*TWOPI
        YERR=3.0D0*SQRT(ABS(PDAT2(1,K)-PDAT(1,K)**2*DF))
        YAV=PDAT(1,K)*DF/DSANG
        YERR=YERR*DF/DSANG
        WRITE(9,'(1X,1P,6E14.6)')
     1       XX,MAX(YAV,1.0D-35),MAX(YERR,1.0D-35)
      ENDDO
      CLOSE(9)
C
      OPEN(9,FILE='pe-anga.dat')
      WRITE(9,9070)
 9070 FORMAT(
     1  1X,'#  Results from PENEPMA. ',
     1 /1X,'#  Angular distribution of emerging photons.',
     1 /1X,'#  1st column: THETA (deg).',
     1 /1X,'#  2nd and 3rd columns: probability density and STU',
     1         ' (1/sr)',/)
      DO K=1,NBTH
        XX=(K-0.5D0)*BSTH
        XXR=(K-1.0D0)*BSTH*DE2RA
        DSANG=(COS(XXR)-COS(XXR+BSTH*DE2RA))*TWOPI
        YERR=3.0D0*SQRT(ABS(PDAT2(2,K)-PDAT(2,K)**2*DF))
        YAV=PDAT(2,K)*DF/DSANG
        YERR=YERR*DF/DSANG
        WRITE(9,'(1X,1P,6E14.6)')
     1     XX,MAX(YAV,1.0D-35),MAX(YERR,1.0D-35)
      ENDDO
      CLOSE(9)
C
      OPEN(9,FILE='pe-angle-el.dat')
      WRITE(9,9210)
 9210 FORMAT(
     1  1X,'#  Results from PENEPMA.',
     1 /1X,'#  Angular distribution of emerging electrons.',
     1 /1X,'#  1st and 2nd columns: THETA and PHI (deg).',
     1 /1X,'#  3rd and 4th columns: probability density and STU',
     1         ' (1/sr)',/)
      DO K=1,NBTH
        XX=(K-0.5D0)*BSTH
        XXR=(K-1.0D0)*BSTH*DE2RA
        DSANG=(COS(XXR)-COS(XXR+BSTH*DE2RA))*(BSPH*DE2RA)
        DO L=1,NBPH
          YY=(L-0.5D0)*BSPH
          YERR=3.0D0*SQRT(ABS(PDA2(1,K,L)-PDA(1,K,L)**2*DF))
          YAV=PDA(1,K,L)*DF/DSANG
          YERR=YERR*DF/DSANG
          WRITE(9,'(1X,1P,6E14.6)')
     1       XX,YY,MAX(YAV,1.0D-35),MAX(YERR,1.0D-35)
        ENDDO
        WRITE(9,*) '   '
      ENDDO
      CLOSE(9)
C
      OPEN(9,FILE='pe-angle-ph.dat')
      WRITE(9,9220)
 9220 FORMAT(
     1  1X,'#  Results from PENEPMA.',
     1 /1X,'#  Angular distribution of emerging photons.',
     1 /1X,'#  1st and 2nd columns: THETA and PHI (deg).',
     1 /1X,'#  3rd and 4th columns: probability density and STU',
     1         ' (1/sr)',/)
      DO K=1,NBTH
        XX=(K-0.5D0)*BSTH
        XXR=(K-1.0D0)*BSTH*DE2RA
        DSANG=(COS(XXR)-COS(XXR+BSTH*DE2RA))*(BSPH*DE2RA)
        DO L=1,NBPH
          YY=(L-0.5D0)*BSPH
          YERR=3.0D0*SQRT(ABS(PDA2(2,K,L)-PDA(2,K,L)**2*DF))
          YAV=PDA(2,K,L)*DF/DSANG
          YERR=YERR*DF/DSANG
          WRITE(9,'(1X,1P,6E14.6)')
     1       XX,YY,MAX(YAV,1.0D-35),MAX(YERR,1.0D-35)
        ENDDO
        WRITE(9,*) '   '
      ENDDO
      CLOSE(9)
C
C  ************  Spectra from photon detectors.
C
      IF(NDEDEF.GT.0) THEN
        DO ID=1,NDEDEF
          WRITE(BUF2,'(I5)') 1000+ID
          SPCDIO='pe-spect-'//BUF2(4:5)//'.dat'
          OPEN(9,FILE=SPCDIO)
          WRITE(9,9310) ID
 9310 FORMAT(1X,'#  Results from PENEPMA. Output from photon ',
     1  'detector #',I3,/1X,'#')
          WRITE(9,9311) THETA1(ID)*RA2DE,THETA2(ID)*RA2DE,
     1      PHI1(ID)*RA2DE,PHI2(ID)*RA2DE
 9311 FORMAT(1X,'#  Angular intervals : theta_1 =',1P,E13.6,
     1  ',  theta_2 =',E13.6,/1X,'#',24X,'phi_1 =',E13.6,
     2  ',    phi_2 =',E13.6)
          WRITE(9,9312) EDEL(ID),EDEU(ID),NDECH(ID)
 9312 FORMAT(1X,'#  Energy window = (',1P,E12.5,',',E12.5,') eV, no.',
     1  ' of channels = ',I4)
          WRITE(9,9313) BDEE(ID)
 9313 FORMAT(1X,'#  Channel width =',1P,E13.6,' eV',/1X,'#')
          WRITE(9,9314)
 9314 FORMAT(
     1  1X,'#  Whole spectrum. Characteristic peaks and background.',
     1 /1X,'#  1st column: photon energy (eV).',
     1 /1X,'#  2nd column: probability density (1/(eV*sr*electron)).',
     1 /1X,'#  3rd column: statistical uncertainty (3 sigma).',/1X,'#')
          SANGLE=(PHI2(ID)-PHI1(ID))*(COS(THETA1(ID))-COS(THETA2(ID)))
          DO J=1,NDECH(ID)
            XX=EDEL(ID)+(J-0.5D0)*BDEE(ID)
            YERR=3.0D0*SQRT(ABS(DET2(ID,J)-DET(ID,J)**2*DF))
            YAV=DET(ID,J)*DF/(BDEE(ID)*SANGLE)
            YERR=YERR*DF/(BDEE(ID)*SANGLE)
            WRITE(9,'(1X,1P,3E14.6)')
     1        XX,MAX(YAV,1.0D-35),MAX(YERR,1.0D-35)
          ENDDO
          CLOSE(9)
C
          SPCDIO='pe-charact-'//BUF2(4:5)//'.dat'
          OPEN(9,FILE=SPCDIO)
          WRITE(9,9310) ID
          WRITE(9,9311) THETA1(ID)*RA2DE,THETA2(ID)*RA2DE,
     1      PHI1(ID)*RA2DE,PHI2(ID)*RA2DE
          WRITE(9,9312) EDEL(ID),EDEU(ID),NDECH(ID)
          WRITE(9,9313) BDEE(ID)
          WRITE(9,9315)
 9315 FORMAT(
     1  1X,'#  Only characteristic peaks.',
     1 /1X,'#  1st column: photon energy (eV).',
     1 /1X,'#  2nd column: total prob. density (1/(eV*sr*electron)).',
     1 /1X,'#  3rd column: statistical uncertainty (3 sigma).',
     1 /1X,'#  4th column: fluorescent prob. density ',
     1         '(1/(eV*sr*electron)).',
     1 /1X,'#  5th column: statistical uncertainty (3 sigma).',/1X,'#')
          DO J=1,NDECH(ID)
            XX=EDEL(ID)+(J-0.5D0)*BDEE(ID)
            YERR=3.0D0*SQRT(ABS(DoT2(ID,J)-DoT(ID,J)**2*DF))
            YAV=DoT(ID,J)*DF/(BDEE(ID)*SANGLE)
            YERR=YERR*DF/(BDEE(ID)*SANGLE)
            YERRF=3.0D0*SQRT(ABS(DoF2(ID,J)-DoF(ID,J)**2*DF))
            YAVF=DoF(ID,J)*DF/(BDEE(ID)*SANGLE)
            YERRF=YERRF*DF/(BDEE(ID)*SANGLE)
            WRITE(9,'(1X,1P,2E14.6,E10.2,E14.6,E10.2)')
     1        XX,MAX(YAV,1.0D-35),MAX(YERR,1.0D-35),
     1        MAX(YAVF,1.0D-35),MAX(YERRF,1.0D-35)
          ENDDO
          CLOSE(9)
        ENDDO
      ENDIF
C
C  ************  Space distribution of x-ray emission.
C
      IF(IDOEV.NE.0) THEN
C
C  ****  Depth distribution of x rays.
C
        OPEN(9,FILE='pe-depth-xrays.dat')
        WRITE(9,9410)
 9410   FORMAT(
     1     1X,'#  Results from PENEPMA. Depth distribution of x rays.',
     1    /1X,'#  1st column: z coordinate (cm).',
     1    /1X,'#  2nd column: density of x-ray emission (1/cm).',
     1    /1X,'#  3rd column: statistical uncertainty (3 sigma).',/)
        DO I3=1,NDB(3)
          ZZ=DXL(3)+(I3-0.5D0)*BDOEV(3)
          YAV=0.0D0
          YAV2=0.0D0
          DO I1=1,NDB(1)
            DO I2=1,NDB(2)
              YAV=YAV+DOEV(I1,I2,I3)
              YAV2=YAV2+DOEV2(I1,I2,I3)
            ENDDO
          ENDDO
          YERR=3.0D0*SQRT(ABS(YAV2-YAV**2*DF))
          YAV=YAV*DF/BDOEV(3)
          YERR=YERR*DF/BDOEV(3)
          WRITE(9,'(1X,1P,3E14.6)')
     1      ZZ,MAX(YAV,1.0D-35),MAX(YERR,1.0D-35)
        ENDDO
        CLOSE(9)
C
        VOXEL=BDOEV(1)*BDOEV(2)*BDOEV(3)
        OPEN(9,FILE='pe-3d-xrays.dat')
        WRITE(9,9420)
 9420   FORMAT(1X,'#  Results from PENEPMA. 3D distribution of x rays.')
        WRITE(9,9421) DXL(1),DXU(1)
 9421   FORMAT(1X,'#  X-ray map box:    XL = ',1P,E13.6,
     1    ' cm,  XU = ',E13.6,' cm')
        WRITE(9,9422) DXL(2),DXU(2)
 9422   FORMAT(1X,'#',20X,'YL = ',1P,E13.6,' cm,  YU = ',E13.6,' cm')
        WRITE(9,9423) DXL(3),DXU(3)
 9423   FORMAT(1X,'#',20X,'ZL = ',1P,E13.6,' cm,  ZU = ',E13.6,' cm')
        WRITE(9,9424) NDB(1),NDB(2),NDB(3)
 9424   FORMAT(1X,'#  Numbers of bins:  NBX =',I4,', NBY =',I4,
     1        ', NBZ =',I4)
        WRITE(9,9425) BDOEV(1),BDOEV(2),BDOEV(3)
 9425   FORMAT(1X,'#  Bin dimensions:   DX = ',1P,E13.6,' cm',
     1    /1X,'#',20X,'DY = ',E13.6,' cm',/1X,'#',20X,
     1    'DZ = ',E13.6,' cm',/1X,'#')
        WRITE(9,9426)
 9426   FORMAT(1X,'#  columns 1 to 3: coordinates (X,Y,Z) of the bin ',
     1    'vertex (cm)',
     1    /1X,'#  4th column: density of x-ray emission (1/cm**3).',
     1    /1X,'#  5th column: statistical uncertainty (3 sigma).',/)
        DO I3=NDB(3),1,-1
          ZZ=DXL(3)+(I3-1.0D0)*BDOEV(3)
          DO I1=1,NDB(1)
            XX=DXL(1)+(I1-1.0D0)*BDOEV(1)
            DO I2=1,NDB(2)
              YY=DXL(2)+(I2-1.0D0)*BDOEV(2)
              YAV=DOEV(I1,I2,I3)
              YAV2=DOEV2(I1,I2,I3)
              YERR=3.0D0*SQRT(ABS(YAV2-YAV**2*DF))
              YAV=YAV*DF/VOXEL
              YERR=YERR*DF/VOXEL
              WRITE(9,9427) XX,YY,ZZ,MAX(YAV,1.0D-35),MAX(YERR,1.0D-35)
            ENDDO
            WRITE(9,'(''  '')')
          ENDDO
          WRITE(9,'(''  '')')
        ENDDO
 9427   FORMAT(1X,1P,3E11.3,E14.6,E10.2)
        CLOSE(9)
C
C  ****  Spatial x-ray distributions at the central axes.
C
        IF(MOD(NDB(1),2).NE.0) THEN
          I1L=((NDB(1)+1)/2)-1
          I1U=((NDB(1)+1)/2)+1
        ELSE
          I1L=NDB(1)/2
          I1U=(NDB(1)/2)+1
        ENDIF
        IF(MOD(NDB(2),2).NE.0) THEN
          I2L=((NDB(2)+1)/2)-1
          I2U=((NDB(2)+1)/2)+1
        ELSE
          I2L=NDB(2)/2
          I2U=(NDB(2)/2)+1
        ENDIF
        IF(MOD(NDB(3),2).NE.0) THEN
          I3L=((NDB(3)+1)/2)-1
          I3U=((NDB(3)+1)/2)+1
        ELSE
          I3L=NDB(3)/2
          I3U=(NDB(3)/2)+1
        ENDIF
C
        OPEN(9,FILE='pe-x-xrays.dat')
          WRITE(9,9440)
 9440   FORMAT(
     1     1X,'#  Results from PENEPMA.',
     1    /1X,'#  Density of x rays along the central X axis',
     1    /1X,'#  1st column: x (cm).',
     1    /1X,'#  2nd column: density of x-ray emission (1/cm**3).',
     1    /1X,'#  3rd column: statistical uncertainty (3 sigma).',/)
        DO I1=1,NDB(1)
          XYZ=DXL(1)+(I1-0.5D0)*BDOEV(1)
          NV=0
          YAV=0.0D0
          YAV2=0.0D0
          DO I2=I2L,I2U
            DO I3=I3L,I3U
              NV=NV+1
              YAV=YAV+DOEV(I1,I2,I3)
              YAV2=YAV2+DOEV2(I1,I2,I3)
            ENDDO
          ENDDO
          YERR=3.0D0*SQRT(ABS(YAV2-YAV**2*DF))
          YAV=YAV*DF/(NV*VOXEL)
          YERR=YERR*DF/(NV*VOXEL)
          WRITE(9,'(1X,1P,3E14.6)')
     1      XYZ,MAX(YAV,1.0D-35),MAX(YERR,1.0D-35)
        ENDDO
        CLOSE(9)
C
        OPEN(9,FILE='pe-y-xrays.dat')
          WRITE(9,9450)
 9450   FORMAT(
     1     1X,'#  Results from PENEPMA.',
     1    /1X,'#  Density of x rays along the central Y axis',
     1    /1X,'#  1st column: y (cm).',
     1    /1X,'#  2nd column: density of x-ray emission (1/cm**3).',
     1    /1X,'#  3rd column: statistical uncertainty (3 sigma).',/)
        DO I2=1,NDB(2)
          XYZ=DXL(2)+(I2-0.5D0)*BDOEV(2)
          NV=0
          YAV=0.0D0
          YAV2=0.0D0
          DO I1=I1L,I1U
            DO I3=I3L,I3U
              NV=NV+1
              YAV=YAV+DOEV(I1,I2,I3)
              YAV2=YAV2+DOEV2(I1,I2,I3)
            ENDDO
          ENDDO
          YERR=3.0D0*SQRT(ABS(YAV2-YAV**2*DF))
          YAV=YAV*DF/(NV*VOXEL)
          YERR=YERR*DF/(NV*VOXEL)
          WRITE(9,'(1X,1P,3E14.6)')
     1      XYZ,MAX(YAV,1.0D-35),MAX(YERR,1.0D-35)
        ENDDO
        CLOSE(9)
C
        OPEN(9,FILE='pe-z-xrays.dat')
          WRITE(9,9460)
 9460   FORMAT(
     1     1X,'#  Results from PENEPMA.',
     1    /1X,'#  Density of x rays along the central Z axis',
     1    /1X,'#  1st column: z (cm).',
     1    /1X,'#  2nd column: density of x-ray emission (1/cm**3).',
     1    /1X,'#  3rd column: statistical uncertainty (3 sigma).',/)
        DO I3=1,NDB(3)
          XYZ=DXL(3)+(I3-0.5D0)*BDOEV(3)
          NV=0
          YAV=0.0D0
          YAV2=0.0D0
          DO I1=I1L,I1U
            DO I2=I2L,I2U
              NV=NV+1
              YAV=YAV+DOEV(I1,I2,I3)
              YAV2=YAV2+DOEV2(I1,I2,I3)
            ENDDO
          ENDDO
          YERR=3.0D0*SQRT(ABS(YAV2-YAV**2*DF))
          YAV=YAV*DF/(NV*VOXEL)
          YERR=YERR*DF/(NV*VOXEL)
          WRITE(9,'(1X,1P,3E14.6)')
     1      XYZ,MAX(YAV,1.0D-35),MAX(YERR,1.0D-35)
        ENDDO
        CLOSE(9)
C
        VOXEL=BDOEV(1)*BDOEV(3)
        OPEN(9,FILE='pe-xz-xrays.dat')
        WRITE(9,9470)
 9470   FORMAT(
     1     1X,'#  Results from PENEPMA.',
     1  /1X,'#  Density of x rays on the XZ plane (integrated over Y)',
     1    /1X,'#  1st column: x (cm).',
     1    /1X,'#  2nd column: z (cm).',
     1    /1X,'#  3rd column: density of x-ray emission (1/cm**2).',
     1    /1X,'#  4th column: statistical uncertainty (3 sigma).',/)
        DO I1=1,NDB(1)
          XX=DXL(1)+(I1-1.0D0)*BDOEV(1)
          DO I3=NDB(3),1,-1
            ZZ=DXL(3)+(I3-1.0D0)*BDOEV(3)
            YAV=0.0D0
            YAV2=0.0D0
            DO I2=1,NDB(2)
              YAV=YAV+DOEV(I1,I2,I3)
              YAV2=YAV2+DOEV2(I1,I2,I3)
            ENDDO
            YERR=3.0D0*SQRT(ABS(YAV2-YAV**2*DF))
            YAV=YAV*DF/VOXEL
            YERR=YERR*DF/VOXEL
            WRITE(9,'(1X,1P,2E11.3,E14.6,E10.2)')
     1        XX,ZZ,MAX(YAV,1.0D-35),MAX(YERR,1.0D-35)
          ENDDO
          WRITE(9,'(''  '')')
        ENDDO
        CLOSE(9)
C
        VOXEL=BDOEV(2)*BDOEV(3)
        OPEN(9,FILE='pe-yz-xrays.dat')
        WRITE(9,9480)
 9480   FORMAT(
     1     1X,'#  Results from PENEPMA.',
     1  /1X,'#  Density of x rays on the YZ plane (integrated over X)',
     1    /1X,'#  1st column: y (cm).',
     1    /1X,'#  2nd column: z (cm).',
     1    /1X,'#  3rd column: density of x-ray emission (1/cm**2).',
     1    /1X,'#  4th column: statistical uncertainty (3 sigma).',/)
        DO I2=1,NDB(2)
          YY=DXL(2)+(I2-1.0D0)*BDOEV(2)
          DO I3=NDB(3),1,-1
            ZZ=DXL(3)+(I3-1.0D0)*BDOEV(3)
            YAV=0.0D0
            YAV2=0.0D0
            DO I1=1,NDB(1)
              YAV=YAV+DOEV(I1,I2,I3)
              YAV2=YAV2+DOEV2(I1,I2,I3)
            ENDDO
            YERR=3.0D0*SQRT(ABS(YAV2-YAV**2*DF))
            YAV=YAV*DF/VOXEL
            YERR=YERR*DF/VOXEL
            WRITE(9,'(1X,1P,2E11.3,E14.6,E10.2)')
     1        YY,ZZ,MAX(YAV,1.0D-35),MAX(YERR,1.0D-35)
          ENDDO
          WRITE(9,'(''  '')')
        ENDDO
        CLOSE(9)
C
        VOXEL=BDOEV(1)*BDOEV(2)
        OPEN(9,FILE='pe-xy-xrays.dat')
        WRITE(9,9490)
 9490   FORMAT(
     1     1X,'#  Results from PENEPMA.',
     1  /1X,'#  Density of x rays on the XY plane (integrated over Z)',
     1    /1X,'#  1st column: x (cm).',
     1    /1X,'#  2nd column: y (cm).',
     1    /1X,'#  3rd column: density of x-ray emission (1/cm**2).',
     1    /1X,'#  4th column: statistical uncertainty (3 sigma).',/)
        DO I1=1,NDB(1)
          XX=DXL(1)+(I1-1.0D0)*BDOEV(1)
          DO I2=1,NDB(2)
            YY=DXL(2)+(I2-1.0D0)*BDOEV(2)
            YAV=0.0D0
            YAV2=0.0D0
            DO I3=1,NDB(3)
              YAV=YAV+DOEV(I1,I2,I3)
              YAV2=YAV2+DOEV2(I1,I2,I3)
            ENDDO
            YERR=3.0D0*SQRT(ABS(YAV2-YAV**2*DF))
            YAV=YAV*DF/VOXEL
            YERR=YERR*DF/VOXEL
            WRITE(9,'(1X,1P,2E11.3,E14.6,E10.2)')
     1        XX,YY,MAX(YAV,1.0D-35),MAX(YERR,1.0D-35)
          ENDDO
          WRITE(9,'(''  '')')
        ENDDO
        CLOSE(9)
      ENDIF
C
C  ************  Intensities of characteristic lines.
C
      IF(NPTRAN.GT.0) THEN
        DO ID=1,NDEDEF
          WRITE(BUF2,'(I5)') 1000+ID
          SPCDIO='pe-inten-'//BUF2(4:5)//'.dat'
          OPEN(9,FILE=SPCDIO)
          WRITE(9,9510) ID
 9510 FORMAT(1X,'#  Results from PENEPMA. Output from photon ',
     1  'detector #',I3,/1X,'#')
          WRITE(9,9511) THETA1(ID)*RA2DE,THETA2(ID)*RA2DE,
     1      PHI1(ID)*RA2DE,PHI2(ID)*RA2DE
 9511 FORMAT(1X,'#  Angular intervals : theta_1 =',1P,E13.6,
     1  ',  theta_2 =',E13.6,/1X,'#',24X,'phi_1 =',E13.6,
     2  ',    phi_2 =',E13.6)
          WRITE(9,9512)
 9512 FORMAT(1X,'#'
     1  /1X,'#  Intensities of characteristic lines. ',
     2        'All in 1/(sr*electron).',
     1  /1X,'#    P = primary photons (from electron interactions);',
     1  /1X,'#    C = flourescence from characteristic x rays;',
     1  /1X,'#    B = flourescence from bremsstrahlung quanta;',
     1  /1X,'#   TF = C+B, total fluorescence;',
     1  /1X,'#  unc = statistical uncertainty (3 sigma).',
     1  /1X,'#',/1X,'# IZ S0 S1  E (eV)',6X,'P',12X,'unc',7X,'C',12X,
     2  'unc',7X,'B',12X,'unc',7X,'TF',11X,'unc',7X,'T',12X,'unc')
C
          SANGLE=(PHI2(ID)-PHI1(ID))*(COS(THETA1(ID))-COS(THETA2(ID)))
          DO I=1,NPTRAN
            IZZ=IZS(I)
            IS1=IS1S(I)
            IS2=IS2S(I)
            ENERGY=ENERGS(I)
C
            YERRT=3.0D0*SQRT(ABS(PTIoT2(ID,IZZ,IS1,IS2)-
     1        PTIoT(ID,IZZ,IS1,IS2)**2*DF))*DF/SANGLE
            YAVT=PTIoT(ID,IZZ,IS1,IS2)*DF/SANGLE
C
            YERRP=3.0D0*SQRT(ABS(PTIoF2(ID,IZZ,IS1,IS2,1)-
     1        PTIoF(ID,IZZ,IS1,IS2,1)**2*DF))*DF/SANGLE
            YAVP=PTIoF(ID,IZZ,IS1,IS2,1)*DF/SANGLE
C
            YERRFC=3.0D0*SQRT(ABS(PTIoF2(ID,IZZ,IS1,IS2,2)-
     1        PTIoF(ID,IZZ,IS1,IS2,2)**2*DF))*DF/SANGLE
            YAVFC=PTIoF(ID,IZZ,IS1,IS2,2)*DF/SANGLE
C
            YERRFB=3.0D0*SQRT(ABS(PTIoF2(ID,IZZ,IS1,IS2,3)-
     1        PTIoF(ID,IZZ,IS1,IS2,3)**2*DF))*DF/SANGLE
            YAVFB=PTIoF(ID,IZZ,IS1,IS2,3)*DF/SANGLE
C
            YAVF=YAVFB+YAVFC
            YERRF=YERRFC+YERRFB
C
            IF(YAVT.GT.0.0D0) THEN
              WRITE(9,'(2X,3I3,1P,E12.4,5(E14.6,E9.2))')
     1          IZZ,IS1,IS2,ENERGY,YAVP,YERRP,YAVFC,YERRFC,
     1          YAVFB,YERRFB,YAVF,YERRF,YAVT,YERRT
            ENDIF
          ENDDO
          CLOSE(9)
        ENDDO
C
C  ----  Probability of emission of characteristic photons.
C
        OPEN(9,FILE='pe-gen-ph.dat')
        WRITE(9,9610)
 9610 FORMAT(1X,'#  Results from PENEPMA.',
     1  /1X,'#  Probability of emission of characteristic lines. ',
     2        'All in 1/(sr*electron).',
     1  /1X,'#    P = primary photons (from electron interactions);',
     1  /1X,'#    C = flourescence from characteristic x rays;',
     1  /1X,'#    B = flourescence from bremsstrahlung quanta;',
     1  /1X,'#   TF = C+B, total fluorescence;',
     1  /1X,'#    T = P+C+B, total intensity;',
     1  /1X,'#  unc = statistical uncertainty (3 sigma).',
     1  /1X,'#',/1X,'# IZ S0 S1  E (eV)',6X,'P',12X,'unc',7X,'C',12X,
     2  'unc',7X,'B',12X,'unc',7X,'TF',11X,'unc',7X,'T',12X,'unc')
C
        SANGLE=TWOPI*2.0D0
        DO I=1,NPTRAN
          IZZ=IZS(I)
          IS1=IS1S(I)
          IS2=IS2S(I)
          ENERGY=ENERGS(I)
C
          YERRT=3.0D0*SQRT(ABS(PTIGT2(IZZ,IS1,IS2)-
     1      PTIGT(IZZ,IS1,IS2)**2*DF))*DF/SANGLE
          YAVT=PTIGT(IZZ,IS1,IS2)*DF/SANGLE
C
          YERRP=3.0D0*SQRT(ABS(PTIoG2(IZZ,IS1,IS2,1)-
     1      PTIoG(IZZ,IS1,IS2,1)**2*DF))*DF/SANGLE
          YAVP=PTIoG(IZZ,IS1,IS2,1)*DF/SANGLE
C
          YERRFC=3.0D0*SQRT(ABS(PTIoG2(IZZ,IS1,IS2,2)-
     1      PTIoG(IZZ,IS1,IS2,2)**2*DF))*DF/SANGLE
          YAVFC=PTIoG(IZZ,IS1,IS2,2)*DF/SANGLE
C
          YERRFB=3.0D0*SQRT(ABS(PTIoG2(IZZ,IS1,IS2,3)-
     1      PTIoG(IZZ,IS1,IS2,3)**2*DF))*DF/SANGLE
          YAVFB=PTIoG(IZZ,IS1,IS2,3)*DF/SANGLE
C
          YAVF=YAVFB+YAVFC
          YERRF=YERRFC+YERRFB
C
          IF(YAVT.GT.0.0D0) THEN
            WRITE(9,'(2X,3I3,1P,E12.4,7(E14.6,E9.2))')
     1        IZZ,IS1,IS2,ENERGY,YAVP,YERRP,YAVFC,YERRFC,
     1        YAVFB,YERRFB,YAVF,YERRF,YAVT,YERRT
          ENDIF
        ENDDO
        CLOSE(9)
      ENDIF
C
C  ****  Probability of emission of bremsstrahlung photons.
C
      OPEN(9,FILE='pe-gen-bremss.dat')
      WRITE(9,9710)
 9710 FORMAT(
     1  1X,'#  Results from PENEPMA.',
     1 /1X,'#  Probability of emission of bremmstrahlung photons.',
     1 /1X,'#  1st column: E (eV).',
     1 /1X,'#  2nd and 3rd columns: probability density and STU',
     1         ' (1/(eV*sr*electron)).',/)
      SANGLE=TWOPI*2.0D0
      DO K=1,NBE
        XX=EMIN+(K-0.5D0)*BSE(2)
        YERR=3.0D0*SQRT(ABS(PDEBR2(K)-PDEBR(K)**2*DF))
        YAV=PDEBR(K)*DF/(BSE(2)*SANGLE)
        YERR=YERR*DF/(BSE(2)*SANGLE)
        IF(EABS(2,1).LT.EMIN+(K-1)*BSE(2)+1.0D0)
     1    WRITE(9,'(1X,1P,3E14.6)')
     1      XX,MAX(YAV,1.0D-35),MAX(YERR,1.0D-35)
      ENDDO
      CLOSE(9)
C
C  ----  phi rho z distributions.
C
      IF(NPRZ.GT.0) THEN
        DO I=1,NPRZ
          ID=IPRZPD(I)
          WRITE(BUF2,'(I5)') 1000+IPRZZ(I)
          WRITE(BUF3,'(I5)') 1000+IPRZS1(I)
          WRITE(BUF4,'(I5)') 1000+IPRZS2(I)
          WRITE(BUF5,'(I5)') 1000+ID
          SPCDIO='pe-prz-'//BUF2(4:5)//BUF3(4:5)//BUF4(4:5)//'-'//
     1      BUF5(4:5)//'.dat'
          OPEN(9,FILE=SPCDIO)
          WRITE(9,9810)
 9810     FORMAT(1X,'#  Results from PENEPMA. Phi rho z distribution.',
     1      /1X,'#')
          WRITE(9,9811) IPRZZ(I),IPRZS1(I),IPRZS2(I)
 9811     FORMAT(1X,'#  Z = ',I2,', S1 = ',I2,', S2 = ',I2,/1X,'#')
          WRITE(9,9311) THETA1(ID)*RA2DE,THETA2(ID)*RA2DE,
     1      PHI1(ID)*RA2DE,PHI2(ID)*RA2DE
          WRITE(9,9812)
 9812     FORMAT(1X,'#'
     1      /1X,'# Intensities of characteristic lines. ',
     2        'All in 1/(cm*sr*electron).',
     1  /1X,'#    P = primary photons (from electron interactions);',
     1  /1X,'#    C = flourescence from characteristic x rays;',
     1  /1X,'#    B = flourescence from bremsstrahlung quanta;',
     1  /1X,'#   TF = C+B, total fluorescence;',
     1  /1X,'#    T = P+C+B, total intensity;',
     1  /1X,'#    E = emitted; G = generated;',
     1  /1X,'#  unc = statistical uncertainty (3 sigma).',
     1  /1X,'#',
     1  /1X,'# D (cm)',5X,'DF (cm)',4X,'PE',12X,'unc',7X,
     2  'PG',12X,'unc',7X,
     3  'CE',12X,'unc',7X,'CG',12X,'unc',7X,'BE',12X,'unc',7X,
     4  'BG',12X,'unc',7X,'TFE',11X,'unc',7X,'TFG',11X,'unc',7X,
     5  'TE',12X,'unc',7X,'TG',12X,'unc',7X)
C
          ID=IPRZPD(I)
          SANGLE=(PHI2(ID)-PHI1(ID))*(COS(THETA1(ID))-COS(THETA2(ID)))
          SANGLG=TWOPI*2.0D0
          DO J=1,NPRZSL-1
            XX=(J-1)*PRZSL
            XXF=(J-1)*PRZSLF
C
            YERRP=3.0D0*SQRT(ABS(PRZF2(I,1,J)-PRZF(I,1,J)**2*DF))
            YERRP=YERRP*DF/(PRZSL*SANGLE)
            YAVP=PRZF(I,1,J)*DF/(PRZSLF*SANGLE)
            YERRPG=3.0D0*SQRT(ABS(PRZG2(I,1,J)-PRZG(I,1,J)**2*DF))
            YERRPG=YERRPG*DF/(PRZSLF*SANGLG)
            YAVPG=PRZG(I,1,J)*DF/(PRZSLF*SANGLG)
C
            YERRC=3.0D0*SQRT(ABS(PRZF2(I,2,J)-PRZF(I,2,J)**2*DF))
            YERRC=YERRC*DF/(PRZSLF*SANGLE)
            YAVC=PRZF(I,2,J)*DF/(PRZSLF*SANGLE)
            YERRCG=3.0D0*SQRT(ABS(PRZG2(I,2,J)-PRZG(I,2,J)**2*DF))
            YERRCG=YERRCG*DF/(PRZSLF*SANGLG)
            YAVCG=PRZG(I,2,J)*DF/(PRZSLF*SANGLG)
C
            YERRB=3.0D0*SQRT(ABS(PRZF2(I,3,J)-PRZF(I,3,J)**2*DF))
            YERRB=YERRB*DF/(PRZSLF*SANGLE)
            YAVB=PRZF(I,3,J)*DF/(PRZSLF*SANGLE)
            YERRBG=3.0D0*SQRT(ABS(PRZG2(I,3,J)-PRZG(I,3,J)**2*DF))
            YERRBG=YERRBG*DF/(PRZSLF*SANGLG)
            YAVBG=PRZG(I,3,J)*DF/(PRZSLF*SANGLG)
C
            YERRF=YERRC+YERRB
            YAVF=YAVC+YAVB
            YERRFG=YERRCG+YERRBG
            YAVFG=YAVCG+YAVBG
C
            YERRT=3.0D0*SQRT(ABS(PRZT2(I,J)-PRZT(I,J)**2*DF))
            YERRT=YERRT*DF/(PRZSL*SANGLE)
            YAVT=PRZT(I,J)*DF/(PRZSL*SANGLE)
            YERRGT=3.0D0*SQRT(ABS(PRZGT2(I,J)-PRZGT(I,J)**2*DF))
            YERRGT=YERRGT*DF/(PRZSL*SANGLG)
            YAVGT=PRZGT(I,J)*DF/(PRZSL*SANGLG)
C
            WRITE(9,'(1X,1P,2E11.3,10(E14.6,E10.2))')
     1        XX,XXF,YAVP,YERRP,YAVPG,YERRPG,YAVC,YERRC,YAVCG,YERRCG,
     1        YAVB,YERRB,YAVBG,YERRBG,YAVF,YERRF,YAVFG,YERRFG,
     1        YAVT,YERRT,YAVGT,YERRGT
          ENDDO
          CLOSE(9)
        ENDDO
      ENDIF
C
C  ****  Continue if the DUMPTO option is active and IRETRN=1.
C
      IF(IRETRN.EQ.1) THEN
        WRITE(6,'(2X,72(''-''))')
        WRITE(6,3040) SHN
 3040   FORMAT(2X,'Number of simulated showers      =',1P,E14.7)
        WRITE(6,3041) XSUNC*100.0D0
 3041   FORMAT(2X,'Total intensity rel. uncertainty =',1P,E14.7,'%')
        WRITE(6,3042) XSUNCF*100.0D0
 3042   FORMAT(2X,'Fluorescence intensity rel. unc. =',1P,E14.7,'%')
        CPUT0=CPUTIM()
        GO TO 101
      ENDIF
C
      STOP
      END


C  *********************************************************************
C                       SUBROUTINE GCONE
C  *********************************************************************
      SUBROUTINE GCONE(UF,VF,WF)
C
C  This subroutine samples a random direction uniformly within a cone
C  with central axis in the direction (THETA,PHI) and aperture ALPHA.
C  Parameters are initialised by calling subroutine GCONE0.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (PI=3.1415926535897932D0, TWOPI=2.0D0*PI)
C  ****  Parameters for sampling directions within a cone.
      COMMON/CGCONE/CPCT,CPST,SPCT,SPST,SPHI,CPHI,STHE,CTHE,CAPER
C
      EXTERNAL RAND
C  ****  Define a direction relative to the z-axis.
      WT=CAPER+(1.0D0-CAPER)*RAND(1.0D0)
      DF=TWOPI*RAND(2.0D0)
      SUV=SQRT(1.0D0-WT*WT)
      UT=SUV*COS(DF)
      VT=SUV*SIN(DF)
C  **** Rotate to the beam axis direction.
      UF=CPCT*UT-SPHI*VT+CPST*WT
      VF=SPCT*UT+CPHI*VT+SPST*WT
      WF=-STHE*UT+CTHE*WT
C  ****  Ensure normalisation.
      DXY=UF*UF+VF*VF
      DXYZ=DXY+WF*WF
      IF(ABS(DXYZ-1.0D0).GT.1.0D-14) THEN
        FNORM=1.0D0/SQRT(DXYZ)
        UF=FNORM*UF
        VF=FNORM*VF
        WF=FNORM*WF
       ENDIF
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE GCONE0
C  *********************************************************************
      SUBROUTINE GCONE0(THETA,PHI,ALPHA)
C
C  This subroutine defines the parameters for sampling random directions
C  uniformly within a cone with axis in the direction (THETA,PHI) and
C  aperture ALPHA (in rad).
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Parameters for sampling directions within a cone.
      COMMON/CGCONE/CPCT,CPST,SPCT,SPST,SPHI,CPHI,STHE,CTHE,CAPER
C
      CPCT=COS(PHI)*COS(THETA)
      CPST=COS(PHI)*SIN(THETA)
      SPCT=SIN(PHI)*COS(THETA)
      SPST=SIN(PHI)*SIN(THETA)
      SPHI=SIN(PHI)
      CPHI=COS(PHI)
      STHE=SIN(THETA)
      CTHE=COS(THETA)
      CAPER=COS(ALPHA)
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE N2CH10
C  *********************************************************************
      SUBROUTINE N2CH10(N,L,NDIG)
C
C  This subroutine writes a positive integer number N in a 10-character
C  string L. The number is written at the left, followed by unused blank
C  characters. NDIG is the number of decimal digits of N.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*10 L,LT
C
      ND=MAX(N,0)
      WRITE(LT,'(I10)') ND
      DO I=1,10
        IF(LT(I:I).NE.' ') THEN
          IT=I-1
          GO TO 1
        ENDIF
      ENDDO
      IT=9
    1 CONTINUE
      L=LT(IT+1:10)
      NDIG=10-IT
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE RDPSF
C  *********************************************************************
      SUBROUTINE RDPSF(IUNIT,PSFREC,KODE)
C
C  This subroutine reads the phase space file. When KODE=0, a valid
C  particle record has been read and copied into the character variable
C  PSFREC. KODE=-1 indicates that the program tried to read after the
C  end of the phase-space file. Blank lines and lines starting with the
C  pound sign (#) are considered as comments and ignored.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*200 PSFREC
C
      KODE=0
    1 CONTINUE
      READ(IUNIT,'(A200)',END=2,ERR=1) PSFREC
      READ(PSFREC,*,ERR=1,END=1) ITEST
      RETURN
    2 CONTINUE
      KODE=-1   ! End of file
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PEILB4
C  *********************************************************************
      SUBROUTINE PEILB4(ILB4,IZZ,IS1,IS2,IS3)
C
C  This subroutine parses the value of the label ILB(4) and returns the
C  atomic number (IZZ) and the active electron shells (IS1,IS2,IS3).
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C
      IZZ=ILB4/1000000
      ITMP=ILB4-IZZ*1000000
      IS1=ITMP/10000
      ITMP=ITMP-IS1*10000
      IS2=ITMP/100
      IS3=MOD(ILB4,100)
C
      RETURN
      END
C  *********************************************************************
C                       FUNCTION PHRANG
C  *********************************************************************
      FUNCTION PHRANG(E,M,JZ,JS1,JS2)
C
C  This function returns the generated photon range in material M at
C  incident electron energy E for a characteristic x ray line
C  (JZ,JS1,JS2).
C
C  Reference:
C    Hovington, P., Drouin, D., Gauvin, R. & Joy, D.C. (1997).
C      Parameterization of the range of electrons at low energy using
C      the CASINO Monte Carlo program. Microsc Microanal 3(suppl.2),
C      885–886.
C  Input arguments:
C    E   ... incident electron energy (in eV).
C    M   ... material.
C    JZ  ... atomic number of the characteristic x ray line.
C    JS1 ... final atomic electron shell of the x ray line.
C    JS2 ... intial atomic electron shell of the x ray line.
C  Output values:
C        ... photon range (in cm)
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER(MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C
      PHRANG=0.0D0
      DO IEL=1,NELEM(M)
        IF(IZ(M,IEL).EQ.JZ) GO TO 10
      ENDDO
      RETURN
   10 CONTINUE
      CALL RELAXE(JZ,JS1,JS2,0,EC,TRPROB)
      IF(EC.GT.E) RETURN
C
      RHOM=RHO(M)
      CK=43.04D0+1.5D0*JZ+5.4D-3*JZ**2
      CN=1.755D0-7.4D-3*JZ+3.0D-5*JZ**2
      E0=E/1000.0D0
      EC=EC/1000.0D0
C
      PHRANG=CK/RHOM*(E0**CN-EC**CN)*1.0D-7
      RETURN
      END
