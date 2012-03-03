CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C                                                                      C
C    PPPPP   EEEEEE  N    N  EEEEEE  L        OOOO   PPPPP   EEEEEE    C
C    P    P  E       NN   N  E       L       O    O  P    P  E         C
C    P    P  E       N N  N  E       L       O    O  P    P  E         C
C    PPPPP   EEEE    N  N N  EEEE    L       O    O  PPPPP   EEEE      C
C    P       E       N   NN  E       L       O    O  P       E         C
C    P       EEEEEE  N    N  EEEEEE  LLLLLL   OOOO   P       EEEEEE    C
C                                                                      C
C                                                   (version 2011).    C
C                                                                      C
C  Subroutine package for Monte Carlo simulation of coupled electron-  C
C  photon transport in homogeneous media.                              C
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
C  Barelona makes no representations about the suitability of this    C
C  software for any purpose. It is provided "as is" without express    C
C  or implied warranty.                                                C
C                                                                      C
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C
C  The convention used to name the interaction simulation subroutines is
C  the following:
C  - The first letter indicates the particle (E for electrons, P for
C    positrons, G for photons).
C  - The second and third letters denote the interaction mechanism
C    (EL for elastic, IN for inelastic, SI for inner-shell ionisation,
C    BR for bremsstrahlung, AN for annihilation, RA for Rayleigh, CO for
C    Compton, PH for photoelectric and PP for pair production).
C  - The fourth (lowercase) letter indicates the theoretical model
C    used to describe the interactions. This serves to distinguish the
C    default model (denoted by the letter 'a') from alternative models.
C  - The random sampling routines have four-letter names. Auxiliary
C    routines, which perform specific calculations, have longer names,
C    with the fifth and subsequent letters and/or numbers indicating
C    the kind of calculation (T for total x-section, D for differen-
C    tial x-section) or action (W for write data in a file, R for read
C    data from a file, I for initialisation of simulation algorithm).
C
C  The present subroutines may print warning and error messages in
C  the I/O unit 26. This is the default output unit in the example main
C  programs PENCYL and PENMAIN.
C
C  Subroutine PEMATW connects files to the I/O units 3 (input) and 7
C  (output). However, this does not conflict with the main program,
C  because PEMATW is not invoked during simulation. This subroutine is
C  used only by the program MATERIAL, to generate material data files.
C
C  Subroutine PEINIT connects material definition files to the input
C  unit 3; this unit is closed before returning to the main program.
C
C  *********************************************************************
C                       SUBROUTINE PEINIT
C  *********************************************************************
      SUBROUTINE PEINIT(EMAX,NMAT,IWR,INFO,PMFILE)
C
C  Input of material data and initialisation of simulation routines.
C
C  Each material is defined through an input file, which is created by
C  the program MATERIAL using information contained in the database.
C  This file can be modified by the user if more accurate interaction
C  data are available.
C
C  Input arguments:
C    EMAX ... maximum particle energy (kinetic energy for electrons and
C             positrons) used in the simulation. Note: Positrons with
C             energy E may produce photons with energy E+1.022E6.
C    NMAT ... number of materials in the geometry.
C    PMFILE .... array of MAXMAT 4096-character strings. The first NMAT
C             elements are the filenames of the material data files.
C             The file PMFILE(M) contains radiation interaction data
C             for material M (that is, the order is important!).
C    IWR .... output unit.
C    INFO ... determines the amount of information that is written on
C             the output file,
C               INFO=1, minimal (composition data only).
C               INFO=2, medium (same information as in the material
C                 definition data file, useful to check that the struc-
C                 ture of the latter is correct).
C               INFO=3 or larger, full information, including tables of
C                 interaction properties used in the simulation.
C
C  For the preliminary computations, PEINIT needs to know the absorption
C  energies EABS(KPAR,M) and the simulation parameters C1(M), C2(M),
C  WCC(M) and WCR(M). This information is introduced through the named
C  common block /CSIMPA/ that has to be loaded before invoking the
C  PEINIT subroutine.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*3 LIT
      CHARACTER*4096 PMFILE
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
      COMMON/STOKES/SP1,SP2,SP3,IPOL
C  ****  Simulation parameters.
      PARAMETER (MAXMAT=10)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
      COMMON/CECUTR/ECUTR(MAXMAT)
      DIMENSION PMFILE(MAXMAT),EABS0(3,MAXMAT)
C
      COMMON/CERSEC/IERSEC
      IERSEC=0
C
      DO M=1,NMAT
        EABS0(1,M)=EABS(1,M)
        EABS0(2,M)=EABS(2,M)
        EABS0(3,M)=EABS(3,M)
      ENDDO
C
C  ****  By default, photon polarisation is not considered.
C
      IPOL=0
      SP1=0.0D0
      SP2=0.0D0
      SP3=0.0D0
C
      WRITE(IWR,2000)
 2000 FORMAT(/1X,34('*'),/1X,'**   PENELOPE  (version 2011)   **',
     1  /1X,34('*'))
C
C  ****  Lower limit of the energy grid.
C
      EMIN=1.0D35
      DO M=1,NMAT
        IF(EABS(1,M).GE.EMAX) THEN
          EABS(1,M)=EMAX*0.9999D0
          WRITE(IWR,2100) 1,M
        ENDIF
        IF(EABS(2,M).GE.EMAX) THEN
          EABS(2,M)=EMAX*0.9999D0
          WRITE(IWR,2100) 2,M
        ENDIF
        IF(EABS(3,M).GE.EMAX) THEN
          EABS(3,M)=EMAX*0.9999D0
          WRITE(IWR,2100) 3,M
        ENDIF
        EMIN=MIN(EMIN,EABS(1,M),EABS(2,M),EABS(3,M))
      ENDDO
 2100 FORMAT(/1X,'WARNING: EABS(',I1,',',I2,') has been modified.')
      IF(EMIN.LT.50.0D0) EMIN=50.0D0
C
      WRITE(IWR,2001) EMIN,EMAX
 2001 FORMAT(/1X,'EMIN =',1P,E11.4,' eV,  EMAX =',E11.4,' eV')
      IF(EMAX.LT.EMIN+10.0D0) STOP 'The energy interval is too narrow.'
      IF(NMAT.GT.MAXMAT) THEN
        WRITE(IWR,2002) NMAT,MAXMAT,NMAT
 2002   FORMAT(/1X,'*** PENELOPE cannot handle ',I2,' different mater',
     1  'ials.'/5X,'Edit the source file and change the parameter ',
     2  'MAXMAT = ',I2,' to MAXMAT = ',I2)
        STOP 'PEINIT. Too many materials.'
      ENDIF
      IF(INFO.GT.2) WRITE(IWR,2102)
 2102 FORMAT(/1X,'NOTE: 1 mtu = 1 g/cm**2')
C
      CALL EGRID(EMIN,EMAX)  ! Defines the simulation energy grid.
      CALL ESIa0  ! Initialises electron impact ionisation routines.
      CALL PSIa0  ! Initialises positron impact ionisation routines.
      CALL GPHa0  ! Initialises photoelectric routines.
      CALL RELAX0  ! Initialises atomic relaxation routines.
      CALL RNDG30  ! Initialises the Gaussian sampling routine.
C
      IRD=3
      DO M=1,NMAT
        IF(M.EQ.1) LIT='st'
        IF(M.EQ.2) LIT='nd'
        IF(M.EQ.3) LIT='rd'
        IF(M.GT.3) LIT='th'
        WRITE(IWR,2003) M,LIT
 2003   FORMAT(//1X,22('*')/1X,'**  ',I2,A2,' material   **',
     1    /1X,22('*'))
        WRITE(IWR,2103) PMFILE(M)
 2103   FORMAT(/1X,'Material data file: ',A)
        OPEN(IRD,FILE=PMFILE(M),IOSTAT=KODE)
        IF(KODE.NE.0) THEN
          WRITE(26,'(''File '',A20,'' could not be opened.'')')
     1      PMFILE(M)
          STOP 'The material data file could not be opened'
        ENDIF
C
C  ****  Energy limits and thresholds.
C
        WRITE(IWR,2004)
 2004   FORMAT(/1X,'*** Simulation parameters:')
        IF(EABS(1,M).LT.50.0D0) THEN
          EABS(1,M)=50.0D0
          WRITE(IWR,2005)
 2005     FORMAT(1X,'*** Warning: electron absorption energy has ',
     1      'been set to 50 eV')
        ENDIF
        WRITE(IWR,2006) EABS(1,M)
 2006   FORMAT(5X,'Electron absorption energy =',1P,E11.4,' eV')
C
        IF(EABS(2,M).LT.50.0D0) THEN
          EABS(2,M)=50.0D0
          WRITE(IWR,2007)
 2007     FORMAT(1X,'*** Warning: photon absorption energy has ',
     1    'been set to 50 eV')
        ENDIF
        WRITE(IWR,2008) EABS(2,M)
 2008   FORMAT(7X,'Photon absorption energy =',1P,E11.4,' eV')
C
        IF(EABS(3,M).LT.50.0D0) THEN
          EABS(3,M)=50.0D0
          WRITE(IWR,2009)
 2009     FORMAT(1X,'*** Warning: positron absorption energy has ',
     1      'been set to 50 eV')
        ENDIF
        WRITE(IWR,2010) EABS(3,M)
 2010   FORMAT(5X,'Positron absorption energy =',1P,E11.4,' eV')
C
        C1(M)=MIN(0.2D0,ABS(C1(M)))
        C2(M)=MIN(0.2D0,ABS(C2(M)))
C
        WCC(M)=MIN(ABS(WCC(M)),EMAX)
        IF(WCC(M).GT.EABS(1,M)) WCC(M)=EABS(1,M)
C
        IF(WCR(M).GT.EABS(2,M)) WCR(M)=EABS(2,M)
        IF(WCR(M).LT.0.0D0) WRITE(IWR,2011)
 2011   FORMAT(1X,'*** Warning: soft radiative losses are switched off')
        WRITE(IWR,2012) C1(M),C2(M),WCC(M),MAX(WCR(M),10.0D0)
 2012   FORMAT(6X,'C1 =',1P,E11.4,',       C2 =',E11.4,/5X,'WCC =',
     2    E11.4,' eV,   WCR =',E11.4,' eV',/)
C
        ECUTR(M)=MIN(EABS(1,M),EABS(2,M))
        CALL PEMATR(M,IRD,IWR,INFO)
        CLOSE(IRD)
      ENDDO
C
C  ****  Restore the user values of EABS(.), to avoid inconsistencies
C        in the main program.
C
      DO M=1,NMAT
        EABS(1,M)=EABS0(1,M)
        EABS(2,M)=EABS0(2,M)
        EABS(3,M)=EABS0(3,M)
      ENDDO
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE EGRID
C  *********************************************************************
      SUBROUTINE EGRID(EMINu,EMAXu)
C
C  This subroutine sets the energy grid where transport functions are
C  tabulated. The grid is logarithmically spaced and we assume that it
C  is dense enough to permit accurate linear log-log interpolation of
C  the tabulated functions.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C
C  ****  Consistency of the interval end-points.
C
      IF(EMINu.LT.50.0D0) EMINu=50.0D0
      IF(EMINu.GT.EMAXu-1.0D0) THEN
        WRITE(26,2100) EMINu,EMAXu
 2100   FORMAT(/3X,'EMIN =',1P,E11.4,' eV,  EMAX =',E11.4,' eV')
        STOP 'EGRID. The energy interval is too narrow.'
      ENDIF
C
C  ****  Energy grid points.
C
      EMIN=EMINu
      EL=0.99999D0*EMINu
      EU=1.00001D0*EMAXu
      DLFC=LOG(EU/EL)/DBLE(NEGP-1)
      DLEMP1=LOG(EL)
      DLEMP(1)=DLEMP1
      ET(1)=EL
      DO I=2,NEGP
        DLEMP(I)=DLEMP(I-1)+DLFC
        ET(I)=EXP(DLEMP(I))
      ENDDO
      DLFC=1.0D0/DLFC
C
C  NOTE: To determine the interval KE where the energy E is located, we
C  do the following,
C     XEL=LOG(E)
C     XE=1.0D0+(XEL-DLEMP1)*DLFC
C     KE=XE
C     XEK=XE-KE  ! 'fractional' part of XE (used for interpolation).
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PEMATR
C  *********************************************************************
      SUBROUTINE PEMATR(M,IRD,IWR,INFO)
C
C  This subroutine reads the definition file of material M (unit IRD)
C  and initialises the simulation routines for this material. Informa-
C  tion is written on unit IWR, the amount of written information is
C  determined by the value of INFO.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*2 LASYMB
      CHARACTER*62 NAME,LNAME
      PARAMETER (A0B=5.291772108D-9)  ! Bohr radius (cm)
      PARAMETER (HREV=27.2113845D0)  ! Hartree energy (eV)
      PARAMETER (AVOG=6.0221415D23)  ! Avogadro's number
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (SL=137.03599911D0)  ! Speed of light (1/alpha)
      PARAMETER (PI=3.1415926535897932D0, FOURPI=4.0D0*PI)
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****  Element data.
      COMMON/CADATA/ATW(99),EPX(99),RSCR(99),ETA(99),EB(99,30),
     1  IFI(99,30),IKS(99,30),NSHT(99),LASYMB(99)
C  ****  Simulation parameters.
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
      COMMON/CECUTR/ECUTR(MAXMAT)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
      COMMON/CRANGE/RANGE(3,MAXMAT,NEGP),RANGEL(3,MAXMAT,NEGP)
C  ****  E/P inelastic collisions.
      PARAMETER (NO=128)
      COMMON/CEIN/EXPOT(MAXMAT),OP2(MAXMAT),F(MAXMAT,NO),UI(MAXMAT,NO),
     1  WRI(MAXMAT,NO),KZ(MAXMAT,NO),KS(MAXMAT,NO),NOSC(MAXMAT)
      COMMON/CEINAC/EINAC(MAXMAT,NEGP,NO),PINAC(MAXMAT,NEGP,NO)
      COMMON/CEINTF/T1EI(NEGP),T2EI(NEGP),T1PI(NEGP),T2PI(NEGP)
C  ****  Partial cross sections of individual shells/oscillators.
      COMMON/CEIN00/SXH0(NO),SXH1(NO),SXH2(NO),SXS0(NO),SXS1(NO),
     1              SXS2(NO),SXT0(NO),SXT1(NO),SXT2(NO)
      COMMON/CPIN00/SYH0(NO),SYH1(NO),SYH2(NO),SYS0(NO),SYS1(NO),
     1              SYS2(NO),SYT0(NO),SYT1(NO),SYT2(NO)
C  ****  Compton scattering.
      PARAMETER (NOCO=128)
      COMMON/CGCO/FCO(MAXMAT,NOCO),UICO(MAXMAT,NOCO),FJ0(MAXMAT,NOCO),
     2  KZCO(MAXMAT,NOCO),KSCO(MAXMAT,NOCO),NOSCCO(MAXMAT)
C  ****  Electron simulation tables.
      COMMON/CEIMFP/SEHEL(MAXMAT,NEGP),SEHIN(MAXMAT,NEGP),
     1  SEISI(MAXMAT,NEGP),SEHBR(MAXMAT,NEGP),SEAUX(MAXMAT,NEGP),
     2  SETOT(MAXMAT,NEGP),CSTPE(MAXMAT,NEGP),RSTPE(MAXMAT,NEGP),
     3  DEL(MAXMAT,NEGP),W1E(MAXMAT,NEGP),W2E(MAXMAT,NEGP),
     4  DW1EL(MAXMAT,NEGP),DW2EL(MAXMAT,NEGP),
     5  RNDCE(MAXMAT,NEGP),AE(MAXMAT,NEGP),BE(MAXMAT,NEGP),
     6  T1E(MAXMAT,NEGP),T2E(MAXMAT,NEGP)
C  ****  Positron simulation tables.
      COMMON/CPIMFP/SPHEL(MAXMAT,NEGP),SPHIN(MAXMAT,NEGP),
     1  SPISI(MAXMAT,NEGP),SPHBR(MAXMAT,NEGP),SPAN(MAXMAT,NEGP),
     2  SPAUX(MAXMAT,NEGP),SPTOT(MAXMAT,NEGP),CSTPP(MAXMAT,NEGP),
     3  RSTPP(MAXMAT,NEGP),W1P(MAXMAT,NEGP),W2P(MAXMAT,NEGP),
     4  DW1PL(MAXMAT,NEGP),DW2PL(MAXMAT,NEGP),
     5  RNDCP(MAXMAT,NEGP),AP(MAXMAT,NEGP),BP(MAXMAT,NEGP),
     6  T1P(MAXMAT,NEGP),T2P(MAXMAT,NEGP)
C  ****  Electron and positron radiative yields.
      COMMON/CBRYLD/EBRY(MAXMAT,NEGP),PBRY(MAXMAT,NEGP)
C  ****  Photon simulation tables.
      COMMON/CGIMFP/SGRA(MAXMAT,NEGP),SGCO(MAXMAT,NEGP),
     1  SGPH(MAXMAT,NEGP),SGPP(MAXMAT,NEGP),SGAUX(MAXMAT,NEGP)
      PARAMETER (NDIM=1500)
      COMMON/CGPH01/ER(NDIM),XSR(NDIM),NPHD
      COMMON/CGPP01/TRIP(MAXMAT,NEGP),PKSCO(MAXMAT,NOCO)
C  ****  Auxiliary arrays.
      DIMENSION EIT(NEGP),EITL(NEGP),FL(NEGP),F1(NEGP),F2(NEGP),
     1  F3(NEGP),F4(NEGP),A(NEGP),B(NEGP),C(NEGP),D(NEGP),RADY(NEGP),
     2  RADN(NEGP)
C  ****  Inner-shell ionisation by electron and positron impact.
      PARAMETER (NRP=8000)
      COMMON/CESI0/XESI(NRP,16),IESIF(99),IESIL(99),NSESI(99),NCURE
      COMMON/CPSI0/XPSI(NRP,16),IPSIF(99),IPSIL(99),NSPSI(99),NCURP
C
C  ****  Rescaling of calculated MFPs.
C  When ISCALE is set equal to 1, the program rescales the calculated
C  total cross sections and MFPs to reproduce the cross sections and
C  stopping powers read from the input material data file. To avoid this
C  rescaling, set ISCALE=0.
C
      ISCALE=1
C
C  ************  Material characteristics.
C
      IF(M.GT.MAXMAT) STOP 'PEMATR. Too many materials.'
C
      LNAME=' PENELOPE (v. 2011)  Material data file ...............'
      READ(IRD,'(A55)') NAME
      IF(NAME.NE.LNAME) THEN
        WRITE(IWR,'(/1X,''I/O error. Corrupt material data file.'')')
        WRITE(IWR,'(''     The first line is: '',A55)') NAME
        WRITE(IWR,'(''     ... and should be: '',A55)') LNAME
        WRITE(26,'(/1X,''I/O error. Corrupt material data file.'')')
        WRITE(26,'(''     The first line is: '',A55)') NAME
        WRITE(26,'(''     ... and should be: '',A55)') LNAME
        STOP 'PEMATR. Corrupt material data file.'
      ENDIF
      WRITE(IWR,'(A55)') NAME
C
      READ(IRD,5001) LNAME
 5001 FORMAT(11X,A62)
      WRITE(IWR,1001) LNAME
 1001 FORMAT(' Material: ',A62)
      READ(IRD,5002) RHO(M)
 5002 FORMAT(15X,E15.8)
      WRITE(IWR,1002) RHO(M)
 1002 FORMAT(' Mass density =',1P,E15.8,' g/cm**3')
      READ(IRD,5003) NELEM(M)
 5003 FORMAT(37X,I3)
      WRITE(IWR,1003) NELEM(M)
 1003 FORMAT(' Number of elements in the molecule = ',I2)
      IF(NELEM(M).GT.30) STOP 'PEMATR. Too many elements.'
      ZT(M)=0.0D0
      AT(M)=0.0D0
      DO I=1,NELEM(M)
        READ(IRD,5004) IZ(M,I),STF(M,I)
 5004   FORMAT(18X,I3,19X,E15.8)
        WRITE(IWR,1004) LASYMB(IZ(M,I)),IZ(M,I),STF(M,I)
 1004   FORMAT(3X,' Element: ',A2,' (Z=',I2,'), atoms/molecule =',1P,
     1    E15.8)
        ZT(M)=ZT(M)+STF(M,I)*IZ(M,I)
        IZZ=IZ(M,I)
        AT(M)=AT(M)+ATW(IZZ)*STF(M,I)
      ENDDO
      VMOL(M)=AVOG*RHO(M)/AT(M)
      IF(INFO.GE.2) WRITE(IWR,
     1  '(/1X,''Molecular density = '',1P,E15.8,'' 1/cm**3'')') VMOL(M)
      OP2(M)=FOURPI*ZT(M)*VMOL(M)*A0B**3*HREV**2
      OMEGA=SQRT(OP2(M))
C
      IF(INFO.GE.2) THEN
        WRITE(IWR,'(/1X,''*** Electron/positron inelastic'',
     1    '' scattering.'')')
        WRITE(IWR,
     1  '(1X,''Plasma energy = '',1P,E15.8,'' eV'')') OMEGA
      ENDIF
C
      READ(IRD,5005) EXPOT(M)
 5005 FORMAT(25X,E15.8)
      WRITE(IWR,1005) EXPOT(M)
 1005 FORMAT(' Mean excitation energy =',1P,E15.8,' eV')
C
C  ****  E/P inelastic collisions.
C
      READ(IRD,5006) NOSC(M)
 5006 FORMAT(24X,I3)
      IF(INFO.GE.2.OR.NOSC(M).GT.NO) WRITE(IWR,1006) NOSC(M)
 1006 FORMAT(' Number of oscillators =',I3)
      IF(NOSC(M).GT.NO) STOP 'PEMATR. Too many oscillators.'
      IF(INFO.GE.2) WRITE(IWR,5507)
 5507 FORMAT(/11X,'Fi',12X,'Ui (eV)',9X,'Wi (eV)',6X,
     1  'KZ  KS',/1X,60('-'))
      EXPT=0.0D0
      DO I=1,NOSC(M)
        READ(IRD,5007) F(M,I),UI(M,I),WRI(M,I),KZ(M,I),KS(M,I)
 5007   FORMAT(4X,1P,3E16.8,2I4)
        IF(UI(M,I).LT.1.0D-3) THEN
          UI(M,I)=0.0D0
        ENDIF
        IF(INFO.GE.2) WRITE(IWR,1007) I,F(M,I),UI(M,I),WRI(M,I),
     1   KZ(M,I),KS(M,I)
 1007   FORMAT(I4,1P,3E16.8,2I4)
        EXPT=EXPT+F(M,I)*LOG(WRI(M,I))
      ENDDO
      EXPT=EXP(EXPT/ZT(M))
C
      IF(ABS(EXPT-EXPOT(M)).GT.1.0D-8*EXPOT(M)) THEN
        WRITE(26,*) 'EXPT      =',EXPT
        WRITE(26,*) 'EXPOT (M) =',EXPOT(M)
        WRITE(26,*) 'Inconsistent oscillator data.'
        STOP 'PEMATR. Inconsistent oscillator data.'
      ENDIF
C
C  ****  Compton scattering.
C
      READ(IRD,5106) NOSCCO(M)
 5106 FORMAT(19X,I3)
      IF(INFO.GE.2.OR.NOSCCO(M).GT.NOCO) THEN
        WRITE(IWR,'(/1X,''*** Compton scattering '',
     1    ''(Impulse Approximation).'')')
        WRITE(IWR,1106) NOSCCO(M)
 1106   FORMAT(1X,'Number of shells =',I3)
        IF(NOSCCO(M).GT.NOCO) STOP 'PEMATR. Too many shells.'
      ENDIF
      IF(INFO.GE.2) WRITE(IWR,5607)
 5607 FORMAT(/11X,'Fi',12X,'Ui (eV)',9X,'Ji(0)',8X,'KZ  KS',
     1       /1X,60('-'))
      DO I=1,NOSCCO(M)
        READ(IRD,5107) FCO(M,I),UICO(M,I),FJ0(M,I),KZCO(M,I),KSCO(M,I)
 5107   FORMAT(4X,1P,3E16.8,2I4)
        IF(INFO.GE.2) WRITE(IWR,1207) I,FCO(M,I),UICO(M,I),FJ0(M,I),
     1    KZCO(M,I),KSCO(M,I)
 1207   FORMAT(I4,1P,3E16.8,2I4)
        FJ0(M,I)=FJ0(M,I)*SL
      ENDDO
C
C  ************  Atomic relaxation data.
C
      DO I=1,NELEM(M)
        CALL RELAXR(IRD,IWR,INFO)
      ENDDO
C
C  ****  Electron and positron interaction properties.
C
C  ****  Scaled bremss x-section.
      IF(WCR(M).GE.0.0D0) THEN
        WCR(M)=MAX(WCR(M),10.0D0)
        WCRM=WCR(M)
        IBREMS=1
      ELSE
        WCRM=10.0D0
        WCR(M)=10.0D0
        IBREMS=0
      ENDIF
      CALL EBRaR(WCRM,M,IRD,IWR,INFO)
C  ****  Bremss angular distribution.
      CALL BRaAR(M,IRD,IWR,INFO)
C
C  ****  Stopping powers.
C
      READ(IRD,5008) NDATA
 5008 FORMAT(58X,I4)
      IF(INFO.GE.2) WRITE(IWR,1008) NDATA
 1008 FORMAT(/1X,'*** Stopping powers for electrons and positrons',
     1  ',  NDATA =',I4)
      IF(NDATA.GT.NEGP) STOP 'PEMATR. Too many data points (1).'
      IF(INFO.GE.2) WRITE(IWR,1108)
 1108 FORMAT(/2X,'Energy',5X,'Scol,e-',5X,'Srad,e-',5X,'Scol,e+',
     1  5X,'Srad,e+',/3X,'(eV)',5X,'(MeV/mtu)',3X,'(MeV/mtu)',3X,
     2  '(MeV/mtu)',3X,'(MeV/mtu)',/1X,58('-'))
      DO I=1,NDATA
        READ(IRD,*) EIT(I),F1(I),F2(I),F3(I),F4(I)
        IF(INFO.GE.2) WRITE(IWR,'(1P,E10.3,5E12.5)')
     1    EIT(I),F1(I),F2(I),F3(I),F4(I)
        EITL(I)=LOG(EIT(I))
      ENDDO
C
C  ****  Inelastic x-section for electrons.
C
      WCCM=WCC(M)
      DIFMAX=0.0D0
      DO I=1,NDATA
        IF(EIT(I).GE.EL.AND.EIT(I).LE.EU) THEN
          STPI=F1(I)*RHO(M)*1.0D6  ! Collision stopping power.
          CALL EINaT(EIT(I),WCCM,XH0,XH1,XH2,XS0,XS1,XS2,XT1,XT2,
     1     DELTA,M)
          STPC=(XS1+XH1)*VMOL(M)
          DIFMAX=MAX(DIFMAX,ABS(STPC-STPI)/(0.01D0*STPI))
        ENDIF
      ENDDO
C
      IF(DIFMAX.GT.1.0D-3.AND.ISCALE.EQ.1) THEN
        ICOR=1
        DO I=1,NDATA
          FL(I)=LOG(F1(I)*RHO(M)*1.0D6)
        ENDDO
        CALL SPLINE(EITL,FL,A,B,C,D,0.0D0,0.0D0,NDATA)
      ELSE
        ICOR=0
      ENDIF
C
      DO I=1,NEGP
        CALL EINaT(ET(I),WCCM,XH0,XH1,XH2,XS0,XS1,XS2,XT1,XT2,DELTA,M)
        STPC=(XS1+XH1)*VMOL(M)
        IF(ICOR.EQ.1) THEN
          EC=DLEMP(I)
          CALL FINDI(EITL,EC,NDATA,J)
          STPI=EXP(A(J)+EC*(B(J)+EC*(C(J)+EC*D(J))))
          FACT=STPI/STPC
        ELSE
          FACT=1.0D0
        ENDIF
        CSTPE(M,I)=STPC*FACT
        SEHIN(M,I)=LOG(MAX(XH0*VMOL(M)*FACT,1.0D-35))
        W1E(M,I)=XS1*VMOL(M)*FACT
        W2E(M,I)=XS2*VMOL(M)*FACT
        T1EI(I)=XT1*VMOL(M)*FACT
        T2EI(I)=XT2*VMOL(M)*FACT
        DEL(M,I)=DELTA
C
        SXHT=0.0D0
        DO KO=1,NOSC(M)
          EINAC(M,I,KO)=SXHT
          SXHT=SXHT+SXH0(KO)
        ENDDO
        IF(SXHT.GT.1.0D-35) THEN
          FNORM=1.0D0/SXHT
          DO KO=1,NOSC(M)
            EINAC(M,I,KO)=EINAC(M,I,KO)*FNORM
          ENDDO
        ELSE
          DO KO=1,NOSC(M)
            EINAC(M,I,KO)=1.0D0
          ENDDO
        ENDIF
      ENDDO
C
C  ****  Bremss x-section for electrons.
C
      DIFMAX=0.0D0
      DO I=1,NDATA
        IF(EIT(I).GE.EL.AND.EIT(I).LT.EU) THEN
          STPI=F2(I)*RHO(M)*1.0D6  ! Radiative stopping power.
          CALL EBRaT(EIT(I),WCRM,XH0,XH1,XH2,XS1,XS2,M)
          STPR=(XS1+XH1)*VMOL(M)
          DIFMAX=MAX(DIFMAX,ABS(STPR-STPI)/(0.01D0*STPI))
        ENDIF
      ENDDO
C
      IF(DIFMAX.GT.1.0D-3.AND.ISCALE.EQ.1) THEN
        ICOR=1
        DO I=1,NDATA
          FL(I)=LOG(F2(I)*RHO(M)*1.0D6)
        ENDDO
        CALL SPLINE(EITL,FL,A,B,C,D,0.0D0,0.0D0,NDATA)
      ELSE
        ICOR=0
      ENDIF
C
      DO I=1,NEGP
        CALL EBRaT(ET(I),WCRM,XH0,XH1,XH2,XS1,XS2,M)
        STPR=(XS1+XH1)*VMOL(M)
        IF(ICOR.EQ.1) THEN
          EC=DLEMP(I)
          CALL FINDI(EITL,EC,NDATA,J)
          STPI=EXP(A(J)+EC*(B(J)+EC*(C(J)+EC*D(J))))
          FACT=STPI/STPR
        ELSE
          FACT=1.0D0
        ENDIF
        RSTPE(M,I)=STPR*FACT
        SEHBR(M,I)=LOG(MAX(XH0*VMOL(M)*FACT,1.0D-35))
        IF(IBREMS.EQ.1) THEN
          W1E(M,I)=W1E(M,I)+XS1*VMOL(M)*FACT
          W2E(M,I)=W2E(M,I)+XS2*VMOL(M)*FACT
        ENDIF
      ENDDO
C
C  ****  Electron range as a function of energy.
C
      DO I=1,NEGP
        F1(I)=1.0D0/(CSTPE(M,I)+RSTPE(M,I))
      ENDDO
      CALL SPLINE(ET,F1,A,B,C,D,0.0D0,0.0D0,NEGP)
      RANGE(1,M,1)=1.0D-8
      RANGEL(1,M,1)=LOG(RANGE(1,M,1))
      DO I=2,NEGP
        XL=ET(I-1)
        XU=ET(I)
        CALL SINTEG(ET,A,B,C,D,XL,XU,DR,NEGP)
        RANGE(1,M,I)=RANGE(1,M,I-1)+DR
        RANGEL(1,M,I)=LOG(RANGE(1,M,I))
      ENDDO
C
C  ****  Electron radiative yield as a function of energy.
C
      DO I=1,NEGP
        F1(I)=RSTPE(M,I)/(CSTPE(M,I)+RSTPE(M,I))
      ENDDO
      RADY(1)=1.0D-35
      EBRY(M,1)=LOG(RADY(1)/ET(1))
      DO I=2,NEGP
        XL=ET(I-1)
        XU=ET(I)
        RADY(I)=RADY(I-1)+RMOMX(ET,F1,XL,XU,NEGP,0)
        EBRY(M,I)=LOG(RADY(I)/ET(I))
      ENDDO
C
C  ****  Electron bremss. photon number yield as a function of energy.
C
      DO I=1,NEGP
        F1(I)=EXP(SEHBR(M,I))/(CSTPE(M,I)+RSTPE(M,I))
      ENDDO
      RADN(1)=0.0D0
      DO I=2,NEGP
        XL=ET(I-1)
        XU=ET(I)
        RADN(I)=RADN(I-1)+RMOMX(ET,F1,XL,XU,NEGP,0)
      ENDDO
C
C  ****  Print electron stopping power tables.
C
      IF(INFO.GE.3) THEN
        WRITE(IWR,1009)
 1009   FORMAT(/1X,'PENELOPE >>>  Stopping powers for electrons')
        WRITE(IWR,1010)
 1010   FORMAT(/3X,'Energy',8X,'Scol',9X,'Srad',9X,'range',5X,
     1    'Rad. Yield',3X,'PhotonYield',4X,'delta',/4X,'(eV)',7X,
     2    '(eV/mtu)',5X,'(eV/mtu)',7X,'(mtu)',20X,'(W>WCR)'/1X,90('-'))
        DO I=1,NEGP
          WRITE(IWR,'(1P,7(E12.5,1X))') ET(I),CSTPE(M,I)/RHO(M),
     1      RSTPE(M,I)/RHO(M),RANGE(1,M,I)*RHO(M),RADY(I)/ET(I),
     2      RADN(I),DEL(M,I)
        ENDDO
      ENDIF
C
C  ****  Inelastic x-section for positrons.
C
      DIFMAX=0.0D0
      DO I=1,NDATA
        IF(EIT(I).GE.EL.AND.EIT(I).LE.EU) THEN
          STPI=F3(I)*RHO(M)*1.0D6  ! Collision stopping power.
          CALL PINaT(EIT(I),WCCM,XH0,XH1,XH2,XS0,XS1,XS2,XT1,XT2,
     1      DELTA,M)
          STPC=(XS1+XH1)*VMOL(M)
          DIFMAX=MAX(DIFMAX,ABS(STPC-STPI)/(0.01D0*STPI))
        ENDIF
      ENDDO
C
      IF(DIFMAX.GT.1.0D-3.AND.ISCALE.EQ.1) THEN
        ICOR=1
        DO I=1,NDATA
          FL(I)=LOG(F3(I)*RHO(M)*1.0D6)
        ENDDO
        CALL SPLINE(EITL,FL,A,B,C,D,0.0D0,0.0D0,NDATA)
      ELSE
        ICOR=0
      ENDIF
C
      DO I=1,NEGP
        CALL PINaT(ET(I),WCCM,XH0,XH1,XH2,XS0,XS1,XS2,XT1,XT2,DELTA,M)
        STPC=(XS1+XH1)*VMOL(M)
        IF(ICOR.EQ.1) THEN
          EC=DLEMP(I)
          CALL FINDI(EITL,EC,NDATA,J)
          STPI=EXP(A(J)+EC*(B(J)+EC*(C(J)+EC*D(J))))
          FACT=STPI/STPC
        ELSE
          FACT=1.0D0
        ENDIF
        CSTPP(M,I)=STPC*FACT
        SPHIN(M,I)=LOG(MAX(XH0*VMOL(M)*FACT,1.0D-35))
        W1P(M,I)=XS1*VMOL(M)*FACT
        W2P(M,I)=XS2*VMOL(M)*FACT
        T1PI(I)=XT1*VMOL(M)*FACT
        T2PI(I)=XT2*VMOL(M)*FACT
C
        SXHT=0.0D0
        DO KO=1,NOSC(M)
          PINAC(M,I,KO)=SXHT
          SXHT=SXHT+SYH0(KO)
        ENDDO
        IF(SXHT.GT.1.0D-35) THEN
          FNORM=1.0D0/SXHT
          DO KO=1,NOSC(M)
            PINAC(M,I,KO)=PINAC(M,I,KO)*FNORM
          ENDDO
        ELSE
          DO KO=1,NOSC(M)
            PINAC(M,I,KO)=1.0D0
          ENDDO
        ENDIF
      ENDDO
C
C  ****  Bremss x-section for positrons.
C
      DIFMAX=0.0D0
      DO I=1,NDATA
        IF(EIT(I).GE.EL.AND.EIT(I).LT.EU) THEN
          STPI=F4(I)*RHO(M)*1.0D6  ! Radiative stopping power.
          CALL PBRaT(EIT(I),WCRM,XH0,XH1,XH2,XS1,XS2,M)
          STPR=(XS1+XH1)*VMOL(M)
          DIFMAX=MAX(DIFMAX,ABS(STPR-STPI)/(0.01D0*STPI))
        ENDIF
      ENDDO
C
      IF(DIFMAX.GT.1.0D-3.AND.ISCALE.EQ.1) THEN
        ICOR=1
        DO I=1,NDATA
          FL(I)=LOG(F4(I)*RHO(M)*1.0D6)
        ENDDO
        CALL SPLINE(EITL,FL,A,B,C,D,0.0D0,0.0D0,NDATA)
      ELSE
        ICOR=0
      ENDIF
C
      DO I=1,NEGP
        CALL PBRaT(ET(I),WCRM,XH0,XH1,XH2,XS1,XS2,M)
        STPR=(XS1+XH1)*VMOL(M)
        IF(ICOR.EQ.1) THEN
          EC=DLEMP(I)
          CALL FINDI(EITL,EC,NDATA,J)
          STPI=EXP(A(J)+EC*(B(J)+EC*(C(J)+EC*D(J))))
          FACT=STPI/STPR
        ELSE
          FACT=1.0D0
        ENDIF
        RSTPP(M,I)=STPR*FACT
        SPHBR(M,I)=LOG(MAX(XH0*VMOL(M)*FACT,1.0D-35))
        IF(IBREMS.EQ.1) THEN
          W1P(M,I)=W1P(M,I)+XS1*VMOL(M)*FACT
          W2P(M,I)=W2P(M,I)+XS2*VMOL(M)*FACT
        ENDIF
      ENDDO
C
C  ****  Positron annihilation.
C
      DO I=1,NEGP
        CALL PANaT(ET(I),TXAN)
        SPAN(M,I)=LOG(TXAN*ZT(M)*VMOL(M))
      ENDDO
C
C  ****  Positron range as a function of energy.
C
      DO I=1,NEGP
        F3(I)=1.0D0/(CSTPP(M,I)+RSTPP(M,I))
      ENDDO
      CALL SPLINE(ET,F3,A,B,C,D,0.0D0,0.0D0,NEGP)
      RANGE(3,M,1)=1.0D-8
      RANGEL(3,M,1)=LOG(RANGE(3,M,1))
      DO I=2,NEGP
        XL=ET(I-1)
        XU=ET(I)
        CALL SINTEG(ET,A,B,C,D,XL,XU,DR,NEGP)
        RANGE(3,M,I)=RANGE(3,M,I-1)+DR
        RANGEL(3,M,I)=LOG(RANGE(3,M,I))
      ENDDO
C
C  ****  Positron radiative yield as a function of energy.
C
      DO I=1,NEGP
        F3(I)=RSTPP(M,I)/(CSTPP(M,I)+RSTPP(M,I))
      ENDDO
      RADY(1)=1.0D-35
      PBRY(M,1)=LOG(RADY(1)/ET(1))
      DO I=2,NEGP
        XL=ET(I-1)
        XU=ET(I)
        RADY(I)=RADY(I-1)+RMOMX(ET,F3,XL,XU,NEGP,0)
        PBRY(M,I)=LOG(RADY(I)/ET(I))
      ENDDO
C
C  ****  Positron bremss. photon number yield as a function of energy.
C
      DO I=1,NEGP
        F3(I)=EXP(SPHBR(M,I))/(CSTPP(M,I)+RSTPP(M,I))
      ENDDO
      RADN(1)=0.0D0
      DO I=2,NEGP
        XL=ET(I-1)
        XU=ET(I)
        RADN(I)=RADN(I-1)+RMOMX(ET,F3,XL,XU,NEGP,0)
      ENDDO
C
C  ****  Print positron stopping power tables.
C
      IF(INFO.GE.3) THEN
        WRITE(IWR,1011)
 1011   FORMAT(/1X,'PENELOPE >>>  Stopping powers for positrons')
        WRITE(IWR,1012)
 1012   FORMAT(/3X,'Energy',8X,'Scol',9X,'Srad',9X,'range',5X,
     1    'Rad. Yield',3X,'PhotonYield',2X,'annih. mfp',/4X,'(eV)',7X,
     2    '(eV/mtu)',5X,'(eV/mtu)',7X,'(mtu)',20X,'(W>WCR)',6X,'(mtu)',
     3    /1X,90('-'))
        DO I=1,NEGP
          WRITE(IWR,'(1P,7(E12.5,1X))') ET(I),CSTPP(M,I)/RHO(M),
     1     RSTPP(M,I)/RHO(M),RANGE(3,M,I)*RHO(M),RADY(I)/ET(I),
     2     RADN(I),RHO(M)/EXP(SPAN(M,I))
        ENDDO
      ENDIF
C
      IF(INFO.GE.3) WRITE(IWR,'(/1X,''PENELOPE >>>  Soft stopping '',
     1  ''power and energy straggling'')')
      IF(INFO.GE.3) WRITE(IWR,1111)
 1111 FORMAT(/3X,'Energy',7X,'SStp,e-',6X,'SStr,e-',5X,'STP,e-',
     1  5X,'SStp,e+',6X,'SStr,e+',5X,'Stp,e+',/4X,'(eV)',7X,
     2  '(eV/mtu)',4X,'(eV**2/mtu)',2X,'soft/tot',3X,'(eV/mtu)',4X,
     3  '(eV**2/mtu)',2X,'soft/tot',/1X,84('-'))
      FMTU=1.0D0/RHO(M)
      DO I=1,NEGP
C  ****  Soft energy-loss events are switched off when W1 is too small.
        FSOFTE=W1E(M,I)/(CSTPE(M,I)+RSTPE(M,I))
        FSOFTP=W1P(M,I)/(CSTPP(M,I)+RSTPP(M,I))
        IF(W1E(M,I).GT.1.0D-5*(CSTPE(M,I)+RSTPE(M,I))) THEN
          W1EW=W1E(M,I)
          W2EW=W2E(M,I)
          W1E(M,I)=LOG(MAX(W1E(M,I),1.0D-35))
          W2E(M,I)=LOG(MAX(W2E(M,I),1.0D-35))
        ELSE
          W1EW=0.0D0
          W2EW=0.0D0
          W1E(M,I)=-100.0D0
          W2E(M,I)=-100.0D0
        ENDIF
        IF(W1P(M,I).GT.1.0D-5*(CSTPP(M,I)+RSTPP(M,I))) THEN
          W1PW=W1P(M,I)
          W2PW=W2P(M,I)
          W1P(M,I)=LOG(MAX(W1P(M,I),1.0D-35))
          W2P(M,I)=LOG(MAX(W2P(M,I),1.0D-35))
        ELSE
          W1PW=0.0D0
          W2PW=0.0D0
          W1P(M,I)=-100.0D0
          W2P(M,I)=-100.0D0
        ENDIF
        IF(INFO.GE.3) WRITE(IWR,'(1P,E12.5,2(2E13.5,E10.2))')
     1    ET(I),W1EW*FMTU,W2EW*FMTU,FSOFTE,W1PW*FMTU,W2PW*FMTU,FSOFTP
      ENDDO
C
C  ****  Elastic scattering of electrons and positrons.
C
      CALL EELaR(M,IRD,IWR,INFO)
      CALL EELdR(M,IRD,IWR,INFO)  ! Uses the ELSEPA database.
C
      IF(INFO.GE.3) THEN
        WRITE(IWR,'(/1X,''PENELOPE >>>  Soft angular transport coef'',
     1    ''ficients'')')
        WRITE(IWR,1113)
 1113   FORMAT(/3X,'Energy',6X,'SITMFP1,e-',3X,'SITMFP2,e-',3X,
     1    'SITMFP1,e+',3X,'SITMFP2,e+',/4X,'(eV)',8X,'(1/mtu)',6X,
     2    '(1/mtu)',6X,'(1/mtu)',6X,'(1/mtu)',/1X,64('-'))
        DO I=1,NEGP
          WRITE(IWR,'(1P,E12.5,4E13.5)')
     1    ET(I),EXP(T1E(M,I))*FMTU,EXP(T2E(M,I))*FMTU,
     2    EXP(T1P(M,I))*FMTU,EXP(T2P(M,I))*FMTU
        ENDDO
      ENDIF
C
C  ****  Inner-shell ionisation by electron and positron impact.
C
      CALL ESIaR(M,IRD,IWR,INFO)
      CALL PSIaR(M,IRD,IWR,INFO)
C
      DO I=1,NEGP
        SEIST=0.0D0
        DO J=1,NELEM(M)
          IZZ=IZ(M,J)
          INDC=IESIF(IZZ)-1
          DO ISH=1,NSESI(IZZ)
            WCUT=EB(IZZ,ISH)
            IF(WCUT.GT.ECUTR(M).AND.WCUT.LT.ET(I)) THEN
              PCSI=EXP(XESI(INDC+I,ISH))
              IF(PCSI.GT.1.1D-35) SEIST=SEIST+PCSI*STF(M,J)
            ENDIF
          ENDDO
        ENDDO
        SEISI(M,I)=LOG(MAX(SEIST*VMOL(M),1.0D-35))
      ENDDO
C
      DO I=1,NEGP
        SPIST=0.0D0
        DO J=1,NELEM(M)
          IZZ=IZ(M,J)
          INDC=IPSIF(IZZ)-1
          DO ISH=1,NSPSI(IZZ)
            WCUT=EB(IZZ,ISH)
            IF(WCUT.GT.ECUTR(M).AND.WCUT.LT.ET(I)) THEN
              PCSI=EXP(XPSI(INDC+I,ISH))
              IF(PCSI.GT.1.1D-35) SPIST=SPIST+PCSI*STF(M,J)
            ENDIF
          ENDDO
        ENDDO
        SPISI(M,I)=LOG(MAX(SPIST*VMOL(M),1.0D-35))
      ENDDO
C
C  ****  Print electron mean free path tables.
C
      IF(INFO.GE.3) THEN
        WRITE(IWR,1109)
 1109   FORMAT(/1X,'PENELOPE >>>  Electron mean free paths (hard',
     1    ' events)',/1X,'*** NOTE: The MFP for inner-shell ionisation',
     2    ' (isi) is listed only for',/11X,'completeness. The MFP ',
     3    'for inelastic collisions (in) has been',/11X,'calculated by',
     4    ' considering all inelastic events, including isi.')
        WRITE(IWR,1110)
 1110   FORMAT(/3X,'Energy',8X,'MFPel',8X,'MFPin',8X,'MFPbr',7X,
     1   'MFPtot',7X,'MFPisi',/4X,'(eV)',9X,'(mtu)',8X,'(mtu)',8X,
     2   '(mtu)',8X,'(mtu)',8X,'(mtu)',/1X,77('-'))
      ENDIF
      DO I=1,NEGP
        FPEL=EXP(SEHEL(M,I))
        FPIN=EXP(SEHIN(M,I))
        FPSI=EXP(SEISI(M,I))
        FPBR=EXP(SEHBR(M,I))
        FPTOT=FPEL+FPIN+FPBR
        IF(INFO.GE.3) WRITE(IWR,'(1P,6(E12.5,1X))') ET(I),RHO(M)/FPEL,
     1    RHO(M)/FPIN,RHO(M)/FPBR,RHO(M)/FPTOT,RHO(M)/FPSI
        SEAUX(M,I)=LOG(1.0D-35)
        SETOT(M,I)=LOG(FPTOT+FPSI)
      ENDDO
C
      DO I=2,NEGP-1
        IF(EXP(SETOT(M,I)).GT.1.005D0*EXP(SETOT(M,I-1)).AND.
     1     EXP(SETOT(M,I)).GT.1.005D0*EXP(SETOT(M,I+1)).AND.
     2     ET(I).GT.EABS(1,M).AND.ET(I).LT.1.0D6) THEN
          WRITE(IWR,1112) ET(I)
          WRITE(26,1112) ET(I)
 1112     FORMAT(/1X,'WARNING: The electron hard IMFP has a maximum',
     1      ' at E =',1P,E13.6,' eV')
        ENDIF
      ENDDO
C
C  ****  Print positron mean free path tables.
C
      IF(INFO.GE.3) THEN
        WRITE(IWR,1209)
 1209   FORMAT(/1X,'PENELOPE >>>  Positron mean free paths (hard',
     1    ' events)',/1X,'*** NOTE: The MFP for inner-shell ionisation',
     2    ' (isi) is listed only for',/11X,'completeness. The MFP ',
     3    'for inelastic collisions (in) has been',/11X,'calculated by',
     4    ' considering all inelastic events, including isi.')
        WRITE(IWR,1210)
 1210   FORMAT(/3X,'Energy',8X,'MFPel',8X,'MFPin',8X,'MFPbr',8X,
     1   'MFPan',7X,'MFPtot',7X,'MFPisi',/4X,'(eV)',9X,'(mtu)',8X,
     2   '(mtu)',8X,'(mtu)',8X,'(mtu)',8X,'(mtu)',8X,'(mtu)',
     3   /1X,90('-'))
      ENDIF
      DO I=1,NEGP
        FPEL=EXP(SPHEL(M,I))
        FPIN=EXP(SPHIN(M,I))
        FPSI=EXP(SPISI(M,I))
        FPBR=EXP(SPHBR(M,I))
        FPAN=EXP(SPAN(M,I))
        FPTOT=FPEL+FPIN+FPBR+FPAN
        IF(INFO.GE.3) WRITE(IWR,'(1P,7(E12.5,1X))') ET(I),RHO(M)/FPEL,
     1    RHO(M)/FPIN,RHO(M)/FPBR,RHO(M)/FPAN,RHO(M)/FPTOT,RHO(M)/FPSI
        SPAUX(M,I)=LOG(1.0D-35)
        SPTOT(M,I)=LOG(FPTOT+FPSI)
      ENDDO
C
      DO I=2,NEGP-1
        IF(EXP(SPTOT(M,I)).GT.1.005D0*EXP(SPTOT(M,I-1)).AND.
     1     EXP(SPTOT(M,I)).GT.1.005D0*EXP(SPTOT(M,I+1)).AND.
     2     ET(I).GT.EABS(3,M).AND.ET(I).LT.1.0D6) THEN
          WRITE(IWR,1212) ET(I)
          WRITE(26,1212) ET(I)
 1212     FORMAT(/1X,'WARNING: The positron hard IMFP has a maximum',
     1      ' at E =',1P,E13.6,' eV')
        ENDIF
      ENDDO
C
C  ****  Correction for the energy dependence of the stopping power and
C  the energy straggling parameter of soft interactions.
C
      DO I=1,NEGP-1
        DW1EL(M,I)=(W1E(M,I+1)-W1E(M,I))/(ET(I+1)-ET(I))
        DW2EL(M,I)=0.5D0*(W2E(M,I+1)-W2E(M,I))/(ET(I+1)-ET(I))
     1            +DW1EL(M,I)
        DW1EL(M,I)=0.5D0*DW1EL(M,I)
        DW1PL(M,I)=(W1P(M,I+1)-W1P(M,I))/(ET(I+1)-ET(I))
        DW2PL(M,I)=0.5D0*(W2P(M,I+1)-W2P(M,I))/(ET(I+1)-ET(I))
     1            +DW1PL(M,I)
        DW1PL(M,I)=0.5D0*DW1PL(M,I)
      ENDDO
      DW1EL(M,NEGP)=0.0D0
      DW2EL(M,NEGP)=0.0D0
      DW1PL(M,NEGP)=0.0D0
      DW2PL(M,NEGP)=0.0D0
C
C  ************  Photon interaction properties.
C
C  ****  Rayleigh scattering.
      CALL GRAaR(M,IRD,IWR,INFO)
C  ****  Compton scattering and pair production.
      READ(IRD,5009) NDATA
 5009 FORMAT(57X,I4)
      IF(INFO.GE.2) WRITE(IWR,1013) NDATA
 1013 FORMAT(/1X,'*** Compton and pair-production cross sections,  ',
     1  'NDATA =',I4)
      IF(NDATA.GT.NEGP) STOP 'PEMATR. Too many data points (2).'
      IF(INFO.GE.2) WRITE(IWR,1114)
 1114 FORMAT(/2X,'Energy',5X,'CS_Comp',5X,'CS_pair',3X,'CS_triplet',/3X,
     1  '(eV)',6X,'(cm**2)',5X,'(cm**2)',5X,'(cm**2)',/1X,46('-'))
      DO I=1,NDATA
        READ(IRD,*) EIT(I),F2(I),F3(I),F4(I)
        IF(INFO.GE.2) WRITE(IWR,'(1P,E10.3,5E12.5)')
     1    EIT(I),F2(I),F3(I),F4(I)
        EITL(I)=LOG(EIT(I))
      ENDDO
C
C  ****  Compton scattering.
C
      VMOLL=LOG(VMOL(M))
      DO I=1,NDATA
        FL(I)=LOG(MAX(F2(I),1.0D-35))
      ENDDO
      CALL SPLINE(EITL,FL,A,B,C,D,0.0D0,0.0D0,NDATA)
      DO I=1,NEGP
        EC=DLEMP(I)
        CALL FINDI(EITL,EC,NDATA,J)
        SGCO(M,I)=A(J)+EC*(B(J)+EC*(C(J)+EC*D(J)))+VMOLL
      ENDDO
C
C  ****  Electron-positron pair and triplet production.
C
      NP=0
      DO 1 I=1,NDATA
        IF(EIT(I).LT.1.023D6) GO TO 1
        NP=NP+1
        F1(NP)=EITL(I)
        FL(NP)=LOG(MAX(F3(I)+F4(I),1.0D-35))
    1 CONTINUE
      CALL SPLINE(F1,FL,A,B,C,D,0.0D0,0.0D0,NP)
      DO I=1,NEGP
        IF(ET(I).LT.1.023D6) THEN
          SGPP(M,I)=-80.6D0
        ELSE
          EC=DLEMP(I)
          CALL FINDI(F1,EC,NP,J)
          SGPP(M,I)=A(J)+EC*(B(J)+EC*(C(J)+EC*D(J)))+VMOLL
        ENDIF
      ENDDO
C
      NP=0
      DO 2 I=1,NDATA
        IF(EIT(I).LT.2.045D6) GO TO 2
        NP=NP+1
        F1(NP)=EITL(I)
        FL(NP)=LOG(MAX(F4(I),1.0D-35))
    2 CONTINUE
      CALL SPLINE(F1,FL,A,B,C,D,0.0D0,0.0D0,NP)
      DO I=1,NEGP
        IF(ET(I).LT.2.045D6) THEN
          TRIP(M,I)=-80.6D0
        ELSE
          EC=DLEMP(I)
          CALL FINDI(F1,EC,NP,J)
          TRIPL=A(J)+EC*(B(J)+EC*(C(J)+EC*D(J)))+VMOLL
          TRIP(M,I)=EXP(TRIPL)/EXP(SGPP(M,I))
        ENDIF
      ENDDO
C
      IF(NOSCCO(M).GT.1) THEN
        PKSCO(M,1)=FCO(M,1)
        DO I=2,NOSCCO(M)
          PKSCO(M,I)=PKSCO(M,I-1)+FCO(M,I)
        ENDDO
        DO I=1,NOSCCO(M)
          PKSCO(M,I)=PKSCO(M,I)/PKSCO(M,NOSCCO(M))
        ENDDO
      ELSE
        PKSCO(M,1)=1.0D0
      ENDIF
C
C  ****  Photoelectric absorption.
C
      CALL GPHaR(M,IRD,IWR,INFO)
C
C  ****  Photon 'range' (= mean free path, slightly underestimated).
C
      DO KE=1,NEGP
        CALL GRAaTI(ET(KE),ECS,M)
        PRA=ECS*VMOL(M)
        PCO=EXP(SGCO(M,KE))
        IF(ET(KE).LT.1.023D6) THEN
          PPP=1.0D-35
        ELSE
          PPP=EXP(SGPP(M,KE))
        ENDIF
        PPH=SGPH(M,KE)
        PT=(PRA+PCO+PPP+PPH)
        RANGE(2,M,KE)=1.0D0/PT
        RANGEL(2,M,KE)=LOG(RANGE(2,M,KE))
      ENDDO
C
      IF(INFO.GE.3) THEN
        WRITE(IWR,1014)
 1014   FORMAT(/1X,'PENELOPE >>>  Photon mass attenuation coefficients')
        WRITE(IWR,1015)
 1015   FORMAT(/3X,'Energy',6X,'Rayleigh',6X,'Compton',4X,'Photoelect.',
     1    5X,'Pair',9X,'Total',/4X,'(eV)',8X,'(1/mtu)',6X,'(1/mtu)',6X,
     2    '(1/mtu)',6X,'(1/mtu)',6X,'(1/mtu)',/1X,77('-'))
      ENDIF
      DO I=1,NPHD
        IF(ER(I).GE.EL.AND.ER(I).LE.EU) THEN
          XEL=LOG(ER(I))
          XE=1.0D0+(XEL-DLEMP1)*DLFC
          KE=XE
          XEK=XE-KE
          CALL GRAaTI(ER(I),ECS,M)
          PRA=ECS*VMOL(M)/RHO(M)
          PCO=EXP(SGCO(M,KE)+(SGCO(M,KE+1)-SGCO(M,KE))*XEK)/RHO(M)
          IF(ER(I).LT.1.022D6) THEN
            PPP=1.0D-35
          ELSE
            PPP=EXP(SGPP(M,KE)+(SGPP(M,KE+1)-SGPP(M,KE))*XEK)/RHO(M)
          ENDIF
          PPH=XSR(I)*VMOL(M)/RHO(M)
          PT=PRA+PCO+PPP+PPH
          IF(INFO.GE.3) THEN
            WRITE(IWR,'(1P,E12.5,5E13.5)') ER(I),PRA,PCO,PPH,PPP,PT
          ENDIF
        ENDIF
      ENDDO
C
C  ****  Pair production. Initialisation routine.
C
      CALL GPPa0(M)
C
      DO IE=1,NEGP
        SGAUX(M,IE)=LOG(1.0D-35)
      ENDDO
C
      LNAME=' PENELOPE (v. 2011)  End of material data file ........'
      READ(IRD,'(A55)') NAME
      IF(NAME.NE.LNAME) THEN
        WRITE(IWR,'(/1X,''I/O error. Corrupt material data file.'')')
        WRITE(IWR,'(''      The last line is: '',A55)') NAME
        WRITE(IWR,'(''     ... and should be: '',A55)') LNAME
        WRITE(26,'(/1X,''I/O error. Corrupt material data file.'')')
        WRITE(26,'(''      The last line is: '',A55)') NAME
        WRITE(26,'(''     ... and should be: '',A55)') LNAME
        STOP 'PEMATR. Corrupt material data file.'
      ENDIF
      WRITE(IWR,'(A55)') NAME
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PEMATW
C  *********************************************************************
      SUBROUTINE PEMATW
C
C  This subroutine generates the material definition file, a part of the
C  input data file of PENELOPE.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*2 LASYMB
      CHARACTER*5 CH5
      CHARACTER*80 PFILE
      CHARACTER*62 NAME
      PARAMETER (A0B=5.291772108D-9)  ! Bohr radius (cm)
      PARAMETER (HREV=27.2113845D0)  ! Hartree energy (eV)
      PARAMETER (AVOG=6.0221415D23)  ! Avogadro's number
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (SL=137.03599911D0)  ! Speed of light (1/alpha)
      PARAMETER (TREV=2.0D0*REV)
      PARAMETER (PI=3.1415926535897932D0, FOURPI=4.0D0*PI)
      COMMON/CMATFN/PFILE
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
      DIMENSION FBW(30)
C  ****  Element data.
      COMMON/CADATA/ATW(99),EPX(99),RSCR(99),ETA(99),EB(99,30),
     1  IFI(99,30),IKS(99,30),NSHT(99),LASYMB(99)
      DIMENSION CP(99,30),IFS(99,30)
C  ****  Simulation parameters.
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  E/P inelastic collisions.
      PARAMETER (NO=128)
      COMMON/CEIN/EXPOT(MAXMAT),OP2(MAXMAT),F(MAXMAT,NO),UI(MAXMAT,NO),
     1  WRI(MAXMAT,NO),KZ(MAXMAT,NO),KS(MAXMAT,NO),NOSC(MAXMAT)
C  ****  Compton scattering.
      PARAMETER (NOCO=128)
      COMMON/CGCO/FCO(MAXMAT,NOCO),UICO(MAXMAT,NOCO),FJ0(MAXMAT,NOCO),
     2  KZCO(MAXMAT,NOCO),KSCO(MAXMAT,NOCO),NOSCCO(MAXMAT)
      PARAMETER (NOM=400)
      DIMENSION FF(NOM),UUI(NOM),FFJ0(NOM),WWRI(NOM),KKZ(NOM),KKS(NOM)
      DIMENSION FFT(NOM),UIT(NOM),WRIT(NOM),KZT(NOM),KST(NOM)
      DIMENSION FC(NOM),UIC(NOM),FJ0C(NOM),KZC(NOM),KSC(NOM)
C  ****  Bremsstrahlung emission.
      PARAMETER (NBE=57, NBW=32)
      COMMON/CEBR/WB(NBW),PBCUT(MAXMAT,NEGP),WBCUT(MAXMAT,NEGP),
     1  PDFB(MAXMAT,NEGP,NBW),DPDFB(MAXMAT,NEGP,NBW),
     2  PACB(MAXMAT,NEGP,NBW),ZBR2(MAXMAT)
C
      DIMENSION EGRT(17)
      DATA EGRT/1.0D0,1.25D0,1.50D0,1.75D0,2.00D0,2.50D0,3.00D0,
     1  3.50D0,4.00D0,4.50D0,5.00D0,5.50D0,6.00D0,7.00D0,8.00D0,
     2  9.00D0,1.00D1/
C  ****  'Standard' energy grid.
      PARAMETER (NEGP1=1500)
      DIMENSION EIT(NEGP1),ES(NEGP1),ESS(NEGP1)
      DIMENSION XGP0(NEGP1),XGT0(NEGP1),PPE(NEGP1),PPT(NEGP1)
C
      M=1
C
      WRITE(6,*) '      '
      WRITE(6,*) ' Select one option (1 or 2):'
      WRITE(6,*) '   1: Enter composition data from the keyboard'
      WRITE(6,*) '   2: Read them from the file pdcompos.p08'
      READ(5,*) IREAD
      IF(IREAD.EQ.2) GO TO 901
C
C  ************  Data entered from keyboard.
C
      WRITE(6,*) ' Enter material name, for your information ',
     1  '(no more than 60 characters) ...'
      READ(5,'(A62)') NAME
      WRITE(6,'(1X,'' Material: '',A62)') NAME
C
      ZT(M)=0.0D0
      AT(M)=0.0D0
      EXPOT(M)=0.0D0
C  ****  Chemical formula or fractions by weight.
  800 CONTINUE
      WRITE(6,*) '      '
      WRITE(6,*) ' Chemical formula:'
      WRITE(6,*) ' Number of elements in the molecule...'
      READ(5,*) NELEM(M)
      IF(NELEM(M).LT.1.OR.NELEM(M).GT.30) THEN
        WRITE(6,*) ' NELEM must be positive and less than 31.'
        WRITE(6,*) ' Please, enter an allowed value.'
        GO TO 800
      ENDIF
      WRITE(6,'(1X,'' Number of elements = '',I2)') NELEM(M)
      WRITE(6,*) '      '
C
      IF(NELEM(1).EQ.1) THEN
  810   CONTINUE
        WRITE(6,230)
  230   FORMAT(/1X,' Enter atomic number of the element...')
        READ(5,*) IZZ
        IF(IZZ.LT.1.OR.IZZ.GT.99) THEN
          WRITE(6,*) ' The atomic number must be in the range 1-99.'
          WRITE(6,*) ' Please, enter an allowed value.'
          GO TO 810
        ENDIF
        IZ(M,1)=IZZ
        STF(M,1)=1.0D0
        WRITE(6,'(1X,'' Element: '',A2,'' (Z='',I2,''), atoms/'',
     1    ''molecule ='',1P,E12.5)') LASYMB(IZZ),IZZ,STF(M,1)
        ZT(M)=IZZ
        AT(M)=ATW(IZZ)
        EXPOT(M)=IZZ*LOG(EPX(IZZ))
      ELSE
C
        WRITE(6,*) ' Select one option (1 or 2):'
        WRITE(6,*) '   1: Enter chemical (stoichiometric) formula'
        WRITE(6,*) '   2: Enter fraction by weight of each element'
        READ(5,*) IREAD2
C
      IF(IREAD2.EQ.2) THEN
        WRITE(6,*) '      '
        WRITE(6,*) ' Weight fractions...'
        DO I=1,NELEM(M)
 801      CONTINUE
          IF(I.EQ.1) THEN
            WRITE(6,231)
 231        FORMAT(/1X,' Enter atomic number and fraction by weight',
     1        ' of the first element ...')
          ELSE IF(I.EQ.2) THEN
            WRITE(6,232)
 232        FORMAT(/1X,' Enter atomic number and fraction by weight',
     1        ' of the second element ...')
          ELSE IF(I.EQ.3) THEN
            WRITE(6,233)
 233        FORMAT(/1X,' Enter atomic number and fraction by weight',
     1        ' of the third element ...')
          ELSE
            WRITE(6,234) I
 234        FORMAT(/1X,' Enter atomic number and fraction by weight',
     1        ' of the',I3,'-th element ...')
          ENDIF
          READ(5,*) IZZ,FBW(I)
          IF(IZZ.LT.1.OR.IZZ.GT.99) THEN
            WRITE(6,*) ' The atomic number must be in the range 1-99.'
            WRITE(6,*) ' Please, enter an allowed value.'
            GO TO 801
          ENDIF
          IF(FBW(I).LE.0.0D0) THEN
            WRITE(6,*) ' The fraction by weight must be positive.'
            WRITE(6,*) ' Please, enter a positive value.'
            GO TO 801
          ENDIF
          WRITE(6,*) '      '
          IZ(M,I)=IZZ
          WRITE(6,'(1X,'' Element: '',A2,'' (Z='',I2,''), fraction '',
     1    ''by weight ='',1P,E12.5)') LASYMB(IZZ),IZZ,FBW(I)
          IF(I.GT.1) THEN
            DO K=1,I-1
              IF(IZZ.EQ.IZ(M,K))
     1          STOP 'This element has been declared twice.'
            ENDDO
          ENDIF
          STF(M,I)=FBW(I)/ATW(IZZ)
        ENDDO
C
        STFM=0.0D0
        DO I=1,NELEM(M)
          IF(STF(M,I).GT.STFM) THEN
            STFM=STF(M,I)
          ENDIF
        ENDDO
        IF(STFM.LT.1.0D-16) STOP 'Fractions by weight are too small.'
        DO I=1,NELEM(M)
          STF(M,I)=STF(M,I)/STFM
        ENDDO
C
        WRITE(6,*) '      '
        DO I=1,NELEM(M)
          IZZ=IZ(M,I)
          WRITE(6,'(1X,'' Element: '',A2,'' (Z='',I2,''), atoms/'',
     1      ''molecule ='',1P,E12.5)') LASYMB(IZZ),IZZ,STF(M,I)
          ZT(M)=ZT(M)+IZZ*STF(M,I)
          AT(M)=AT(M)+ATW(IZZ)*STF(M,I)
          EXPOT(M)=EXPOT(M)+IZZ*LOG(EPX(IZZ))*STF(M,I)
        ENDDO
      ELSE
C
        WRITE(6,*) '      '
        WRITE(6,*) ' Stoichiometric indices...'
        DO I=1,NELEM(M)
 802      CONTINUE
          IF(I.EQ.1) THEN
            WRITE(6,2001)
 2001     FORMAT(/1X,' Enter atomic number and number of atoms/molec',
     1      'ule of the first element ...')
          ELSE IF(I.EQ.2) THEN
            WRITE(6,2002)
 2002     FORMAT(/1X,' Enter atomic number and number of atoms/molec',
     1      'ule of the second element ...')
          ELSE IF(I.EQ.3) THEN
            WRITE(6,2003)
 2003     FORMAT(/1X,' Enter atomic number and number of atoms/molec',
     1      'ule of the third element ...')
          ELSE
            WRITE(6,2004) I
 2004     FORMAT(/1X,' Enter atomic number and number of atoms/molec',
     1      'ule of the',I3,'-th element ...')
          ENDIF
          READ(5,*) IZZ,STF(M,I)
          IF(IZZ.LT.1.OR.IZZ.GT.99) THEN
            WRITE(6,*) ' The atomic number must be in the range 1-99.'
            WRITE(6,*) ' Please, enter an allowed value.'
            GO TO 802
          ENDIF
          IF(STF(M,I).LE.0.0D0) THEN
            WRITE(6,*) ' The stoichiometric fraction must be positive.'
            WRITE(6,*) ' Please, enter a positive value.'
            GO TO 802
          ENDIF
          IZ(M,I)=IZZ
          WRITE(6,'(1X,'' Element: '',A2,'' (Z='',I2,''), atoms/'',
     1      ''molecule ='',1P,E12.5)') LASYMB(IZZ),IZZ,STF(M,I)
          IF(I.GT.1) THEN
            DO K=1,I-1
              IF(IZZ.EQ.IZ(M,K))
     1          STOP 'This element has been declared twice.'
            ENDDO
          ENDIF
          ZT(M)=ZT(M)+IZZ*STF(M,I)
          AT(M)=AT(M)+ATW(IZZ)*STF(M,I)
          EXPOT(M)=EXPOT(M)+IZZ*LOG(EPX(IZZ))*STF(M,I)
        ENDDO
      ENDIF
      ENDIF
C
      EXPOT(M)=EXP(EXPOT(M)/ZT(M))
      WRITE(6,*) '      '
      WRITE(6,'(1X,'' The calculated mean excitation energy I'',
     1  '' is '',1P,E12.5,'' eV'')') EXPOT(M)
      WRITE(6,*) ' Do you want to change it?   (1=yes,2=no)'
      READ(5,*) IYESNO
      IF(IYESNO.EQ.1) THEN
 803    CONTINUE
        WRITE(6,*) '      '
        WRITE(6,*) ' Enter mean excitation energy (eV) ...'
        READ(5,*) EXPOT(M)
        WRITE(6,'(1X,'' Mean excitation energy ='',1P,E12.5,
     1    '' eV'')') EXPOT(M)
        IF(EXPOT(M).LT.1.0D0) THEN
          WRITE(6,*) ' The mean exc. energy must be larger than 1 eV.'
          WRITE(6,*) ' Please, enter a valid value.'
          GO TO 803
        ENDIF
      ENDIF
C
 804  CONTINUE
      WRITE(6,*) '      '
      WRITE(6,*) ' Enter mass density (g/cm**3) ...'
      READ(5,*) RHO(M)
      WRITE(6,'(1X,'' Density = '',1P,E12.5,'' g/cm**3'')') RHO(M)
      IF(RHO(M).LE.0.0D0) THEN
        WRITE(6,*) ' The mass density must be positive.'
        WRITE(6,*) ' Please, enter a positive value.'
        GO TO 804
      ENDIF
      VMOL(M)=AVOG*RHO(M)/AT(M)
      GO TO 904
C
C  ************  Material data read from file 'compdata.p08'.
C
  901 CONTINUE
      WRITE(6,*) ' Enter material identification number ...'
      READ(5,*) IDNUM
      IF(IDNUM.LT.1.OR.IDNUM.GT.280)
     1  STOP 'The allowed material ID numbers are 1-280.'
C
      OPEN(3,FILE='./pdfiles/pdcompos.p08')
      DO I=1,15
        READ(3,'(A62)') NAME
      ENDDO
      DO K1=1,300
        READ(3,'(I3,2X,A62)',END=902) IORD,NAME
        READ(3,*) NELEM(M),HOLLOW,EXPOT(M),RHO(M)
        IF(NELEM(M).GT.30) STOP 'NELEM cannot be larger than 30.'
        IF(NELEM(M).LT.1) STOP 'NELEM must be positive.'
        DO I=1,NELEM(M)
          READ(3,*) IZ(M,I),HOLLOW,STF(M,I)
        ENDDO
        IF(IORD.EQ.IDNUM) GO TO 903
      ENDDO
  902 CONTINUE
      STOP 'Abnormal termination of file ''pdcompos.p08''.'
  903 CONTINUE
      CLOSE(UNIT=3)
      WRITE(6,'(/2X,I3,1X,A62)') IORD,NAME
C
      ZT(M)=0.0D0
      AT(M)=0.0D0
      DO I=1,NELEM(M)
        IZZ=IZ(M,I)
        IF(IZZ.LT.1.OR.IZZ.GT.99) THEN
          WRITE(6,'(1X,'' Element:    (Z='',I2,''), atoms/'',
     1    ''molecule ='',1P,E12.5)') LASYMB(IZZ),IZZ,STF(M,I)
          STOP 'Wrong atomic number.'
        ENDIF
        WRITE(6,'(1X,'' Element: '',A2,'' (Z='',I2,''), atoms/'',
     1    ''molecule ='',1P,E12.5)') LASYMB(IZZ),IZZ,STF(M,I)
        IF(STF(M,I).LE.0.0D0) STOP 'STF must be positive.'
        IF(I.GT.1) THEN
          DO K=1,I-1
            IF(IZZ.EQ.IZ(M,K)) STOP 'Element has been declared twice.'
          ENDDO
        ENDIF
        ZT(M)=ZT(M)+IZZ*STF(M,I)
        AT(M)=AT(M)+ATW(IZZ)*STF(M,I)
      ENDDO
      WRITE(6,'(/1X,'' Density = '',1P,E12.5,'' g/cm**3'')') RHO(M)
      WRITE(6,'(/1X,'' Number of electrons per molecule = '',
     1  1P,E12.5)') ZT(M)
      IF(RHO(M).LE.0.0D0) STOP 'The density must be positive.'
      WRITE(6,'(1X,'' Mean excitation energy ='',1P,E12.5,
     1  '' eV'')') EXPOT(M)
      VMOL(M)=AVOG*RHO(M)/AT(M)
  904 CONTINUE
C
C  ************  Atomic configuration.
C
      DO I=1,99
        NSHT(I)=0
        DO J=1,30
          EB(I,J)=0.0D0
          CP(I,J)=0.0D0
          IFI(I,J)=0
          IFS(I,J)=0
          IKS(I,J)=0
        ENDDO
      ENDDO
C
      DO I=1,NELEM(M)
        IZZ=IZ(M,I)
C  ****  Loads element data only once. NSHT(IZZ) is used as a status
C        indicator.
        IF(NSHT(IZZ).EQ.0) THEN
          OPEN(3,FILE='./pdfiles/pdatconf.p08')
          DO J=1,22
            READ(3,'(A5)') CH5
          ENDDO
          NS=0
          IZZT=0
          DO J=1,150000
            READ(3,2005,END=905) IIZ,IS,CH5,IIF,EIE,CCP
 2005       FORMAT(I3,I3,1X,A5,I3,E12.5,E9.2)
            IF(IIZ.EQ.IZZ) THEN
              NS=NS+1
              IF(NS.GT.30) THEN
                WRITE(6,'(/1X,''NS ='',I4)') NS
                STOP 'Too many shells.'
              ENDIF
              IF(IS.LT.1.OR.IS.GT.30) THEN
                WRITE(6,'(/1X,''IS ='',I4)') IS
                STOP 'Wrong shell number.'
              ENDIF
              IZZT=IZZT+ABS(IIF)
              EB(IZZ,IS)=EIE
              CP(IZZ,IS)=CCP
              IFI(IZZ,IS)=ABS(IIF)
              IFS(IZZ,IS)=IIF
              IKS(IZZ,NS)=IS
            ENDIF
          ENDDO
  905     CONTINUE
          NSHT(IZZ)=NS
          IF(IZZ.NE.IZZT) STOP 'Unbalanced charges (element).'
          CLOSE(3)
        ENDIF
      ENDDO
C
C  ************  E/P inelastic scattering model parameters.
C
C  ****  Set the oscillator table (analogous to ICRU37).
C
      DO I=1,NO
        F(M,I)=0.0D0
        UI(M,I)=0.0D0
        WRI(M,I)=0.0D0
        KZ(M,I)=0
        KS(M,I)=0
      ENDDO
C
      DO I=1,NOM
        FF(I)=0.0D0
        UUI(I)=0.0D0
        WWRI(I)=0.0D0
        FFJ0(I)=0.0D0
        KKZ(I)=0
        KKS(I)=0
      ENDDO
      FT=0.0D0
C  ****  The 1st oscillator corresponds to the conduction band, which is
C  tentatively assumed to consist of valence electrons (each atom con-
C  tributes a number of electrons equal to its lowest chemical valence).
      NOS=1
      FF(1)=0.0D0
      UUI(1)=0.0D0
      FFJ0(1)=0.0D0
      KKZ(1)=0
      KKS(1)=30
      DO I=1,NELEM(M)
        IZZ=IZ(M,I)
        DO K=1,30
          JS=IKS(IZZ,K)
          IF(JS.GT.0) THEN
            IF(ABS(IFS(IZZ,JS)).GT.0) THEN
              NOS=NOS+1
              IF(NOS.GT.NOM) STOP
     1    'Too many oscillators. The parameter NOM should be enlarged.'
              FF(NOS)=ABS(IFS(IZZ,JS))*STF(M,I)
              UUI(NOS)=EB(IZZ,JS)
              FFJ0(NOS)=CP(IZZ,JS)
              KKZ(NOS)=IZZ
              IF(IZZ.GT.6.AND.JS.LT.17) THEN
                KKS(NOS)=JS
              ELSE
                KKS(NOS)=30
              ENDIF
              FT=FT+FF(NOS)
              IF(IFS(IZZ,JS).LT.0)
     1          FF(1)=FF(1)+ABS(IFS(IZZ,JS))*STF(M,I)
            ENDIF
          ENDIF
        ENDDO
      ENDDO
C
      IF(ABS(FT-ZT(M)).GT.1.0D-10*ZT(M))
     1  STOP 'Unbalanced charges (compound).'
C  ****  Oscillators are sorted by increasing ionization energies.
      DO I=1,NOS-1
        DO J=I+1,NOS
          IF(UUI(I).GE.UUI(J)) THEN
            SAVE=UUI(I)
            UUI(I)=UUI(J)
            UUI(J)=SAVE
            SAVE=FF(I)
            FF(I)=FF(J)
            FF(J)=SAVE
            SAVE=FFJ0(I)
            FFJ0(I)=FFJ0(J)
            FFJ0(J)=SAVE
            ISAVE=KKZ(I)
            KKZ(I)=KKZ(J)
            KKZ(J)=ISAVE
            ISAVE=KKS(I)
            KKS(I)=KKS(J)
            KKS(J)=ISAVE
          ENDIF
        ENDDO
      ENDDO
C
C  ************  Plasma energy and conduction band excitations.
C
      OP2(M)=FOURPI*ZT(M)*VMOL(M)*A0B**3*HREV**2
      OMEGA=SQRT(OP2(M))
      EPP=OMEGA*SQRT(FF(1)/ZT(M))
      WRITE(6,'(/1X,'' Estimated oscillator strength and '',
     1  ''energy of the plasmon:''/2X,''Fcb ='',1P,E12.5,'',  Wcb ='',
     2  E12.5,'' eV'',/2X,''(for insulators, these quantiti'',
     1  ''es should be set equal to zero)'')') FF(1),EPP
C
      WRITE(6,'(/1X,'' Do you wish to change the Fcb and Wcb values? '',
     1  ''  (1=yes,2=no)''/2X,''(type 2 if you are not sure...)'')')
      READ(5,*) IPLOSP
C
      IF(IPLOSP.EQ.1) THEN
        WRITE(6,*) '      '
        WRITE(6,2007)
 2007   FORMAT(1X,' Enter the oscillator strength Fcb and ',
     1    'energy Wcb (in eV) of the plasmon ...')
        READ(5,*) FP,EP
        IF(FP.LT.0.5D0) THEN
          FP=0.0D0
          EP=0.0D0
          GO TO 975
        ENDIF
        IF(EP.LT.0.1D0) THEN
          EP=OMEGA*SQRT(FP/ZT(M))
        ENDIF
      ELSE
        EP=EPP
        FP=FF(1)
      ENDIF
  975 CONTINUE
      WRITE(6,'(/1X,'' Fcb ='',1P,E12.5,'',  Wcb ='',E12.5,'' eV'')')
     1   FP,EP
      IF(FP.GT.ZT(M)+1.0D-13) STOP 'FP is too large.'
      IF(EP.LT.1.0D0.OR.FP.LT.0.5D0) THEN
C  ****  Insulator. There is no conduction band.
        IFCB=0
        DO J=1,NOS-1
          FF(J)=FF(J+1)
          UUI(J)=UUI(J+1)
          FFJ0(J)=FFJ0(J+1)
          KKZ(J)=KKZ(J+1)
          KKS(J)=KKS(J+1)
        ENDDO
        NOS=NOS-1
      ELSE
C  ****  Conductor. Outer shells are 'moved' to the c.b.
        IFCB=1
        IDEAD=0
        FPP=FP
        I=1
  907   I=I+1
        IF(FF(I).LT.FPP) THEN
          FPP=FPP-FF(I)
          FF(I)=0.0D0
          IDEAD=IDEAD+1
          GO TO 907
        ELSE
          FF(I)=FF(I)-FPP
          IF(ABS(FF(I)).LT.1.0D-12) THEN
            FP=FP+FF(I)
            FF(I)=0.0D0
            IDEAD=IDEAD+1
          ENDIF
        ENDIF
        FF(1)=FP
        UUI(1)=0.0D0
        WWRI(1)=EP
        FFJ0(1)=0.75D0/SQRT(3.0D0*PI*PI*VMOL(M)*A0B**3*FP)
        KKZ(1)=0
        KKS(1)=30
        IF(IDEAD.GT.0) THEN
          DO J=2,NOS-IDEAD
            FF(J)=FF(J+IDEAD)
            UUI(J)=UUI(J+IDEAD)
            FFJ0(J)=FFJ0(J+IDEAD)
            KKZ(J)=KKZ(J+IDEAD)
            KKS(J)=KKS(J+IDEAD)
          ENDDO
          NOS=NOS-IDEAD
        ENDIF
      ENDIF
C  ****  Check f-sum rule.
      SUM=0.0D0
      DO J=1,NOS
        SUM=SUM+FF(J)
      ENDDO
      IF(ABS(SUM-ZT(M)).GT.1.0D-6*ZT(M))
     1  STOP 'Inconsistent oscillator strength data.'
      IF(ABS(SUM-ZT(M)).GT.1.0D-12*ZT(M)) THEN
        FACT=ZT(M)/SUM
        DO J=1,NOS
          FF(J)=FACT*FF(J)
        ENDDO
      ENDIF
C
C  ****  Initial parameters for Compton scattering (before grouping).
C
      NOSTC=NOS
      CSUMT=0.0D0
      DO I=1,NOSTC
        FC(I)=FF(I)
        UIC(I)=UUI(I)
        FJ0C(I)=FFJ0(I)
        KZC(I)=KKZ(I)
        KSC(I)=KKS(I)
        CSUMT=CSUMT+FC(I)*FJ0C(I)
      ENDDO
C
C  ************  Sternheimer's adjustment factor.
C
      IF(NOS.GT.1) THEN
        TST=ZT(M)*DLOG(EXPOT(M))
        AAL=0.5D0
        AAU=10.0D0
  908   AA=0.5D0*(AAL+AAU)
        SUM=0.0D0
        DO I=1,NOS
          IF(I.EQ.1.AND.IFCB.EQ.1) THEN
            SUM=SUM+FF(1)*DLOG(WWRI(1))
          ELSE
            WI2=(AA*UUI(I))**2
     1         +0.666666666666666D0*(FF(I)/ZT(M))*OMEGA**2
            WWRI(I)=DSQRT(WI2)
            SUM=SUM+FF(I)*DLOG(WWRI(I))
          ENDIF
        ENDDO
        IF(SUM.LT.TST) THEN
          AAL=AA
        ELSE
          AAU=AA
        ENDIF
        IF(AAU-AAL.GT.1.0D-14*AA) GO TO 908
      ELSE
        UUI(1)=DABS(UUI(1))
        WWRI(1)=EXPOT(M)
      ENDIF
      WRITE(6,'(1X,'' Sternheimer adjustment factor = '',1P,E12.5)') AA
C  ****  Verification.
      EXPT=FF(1)*LOG(WWRI(1))
      TST=FF(1)
      IF(NOS.GT.1) THEN
        DO I=2,NOS
          EXPT=EXPT+FF(I)*LOG(WWRI(I))
          TST=TST+FF(I)
        ENDDO
      ENDIF
C
      IF(ABS(TST-ZT(M)).GT.1.0D-8*ZT(M)) THEN
        WRITE(6,*) ' TST-ZT(M) =',TST-ZT(M)
        STOP 'Inconsistent oscillator-strength data.'
      ENDIF
      EXPT=EXP(EXPT/ZT(M))
      IF(ABS(EXPT-EXPOT(M)).GT.1.0D-8*EXPOT(M)) THEN
        WRITE(6,*) 'EXPT-EXPOT(M) =',EXPT-EXPOT(M)
        WRITE(6,*) 'Error in the calculation of the Sternheimer factor.'
        WRITE(6,*) '      '
        WRITE(6,'(1X,'' Number of oscillators  = '',I3)') NOS
        DO I=1,NOS
          WRITE(6,'(I4,1P,4E13.5,2I4)')
     1      I,FF(I),UUI(I),WWRI(I),FFJ0(I),KKZ(I),KKS(I)
        ENDDO
        STOP 'Inconsistent oscillator-strength data (2).'
      ENDIF
C
C  ****  Selection of the lowest ionisation energy for inner shells.
C  Only the K, L, M and N shells with ionisation energies less than that
C  of the O1 shell of the heaviest element in the material are consider-
C  ed as inner shells. As a result, the inner/outer character of an
C  atomic shell depends on the composition of the material.
C
      IZMAX=0
      DO I=1,NELEM(M)
        IZMAX=MAX(IZMAX,IZ(M,I))
      ENDDO
      WISCUT=MAX(50.0D0,EB(IZMAX,17))
C
      NOST=NOS
      DO I=1,NOST
        FFT(I)=FF(I)
        UIT(I)=UUI(I)
        WRIT(I)=WWRI(I)
        KZT(I)=KKZ(I)
        KST(I)=KKS(I)
      ENDDO
C  ****  Oscillators are sorted by increasing resonance energies.
      IF(NOST.GT.IFCB+1) THEN
        DO I=IFCB+1,NOST-1
          DO J=I+1,NOST
            IF(WRIT(I).GT.WRIT(J)) THEN
              SAVE=FFT(I)
              FFT(I)=FFT(J)
              FFT(J)=SAVE
              SAVE=UIT(I)
              UIT(I)=UIT(J)
              UIT(J)=SAVE
              SAVE=WRIT(I)
              WRIT(I)=WRIT(J)
              WRIT(J)=SAVE
              ISAVE=KZT(I)
              KZT(I)=KZT(J)
              KZT(J)=ISAVE
              ISAVE=KST(I)
              KST(I)=KST(J)
              KST(J)=ISAVE
            ENDIF
          ENDDO
        ENDDO
      ENDIF
C
C  ****  Oscillators of outer shells with resonance energies differing
C  by a factor less than RGROUP are grouped as a single oscillator.
C
      RGROUP=1.05D0
  910 CONTINUE
      IELIM=0
      IF(NOST.GT.IFCB+2) THEN
        DO 911 I=IFCB+1,NOST-1
        IF(KST(I+1).LT.17.AND.UIT(I+1).GT.WISCUT) GO TO 911
        IF(WRIT(I).LT.1.0D0.OR.WRIT(I+1).LT.1.0D0) GO TO 911
        IF(WRIT(I+1).GT.RGROUP*WRIT(I)) GO TO 911
        WRIT(I)=EXP((FFT(I)*LOG(WRIT(I))+FFT(I+1)*LOG(WRIT(I+1)))
     1         /(FFT(I)+FFT(I+1)))
        UIT(I)=(FFT(I)*UIT(I)+FFT(I+1)*UIT(I+1))/(FFT(I)+FFT(I+1))
        FFT(I)=FFT(I)+FFT(I+1)
        IF(KZT(I).NE.KZT(I+1)) KZT(I)=0
        IF(KST(I).LT.17.OR.KST(I+1).LT.17) THEN
          KST(I)=MIN(KST(I),KST(I+1))
        ELSE
          KST(I)=30
        ENDIF
        IF(I.LT.NOST-1) THEN
          DO J=I+1,NOST-1
            FFT(J)=FFT(J+1)
            UIT(J)=UIT(J+1)
            WRIT(J)=WRIT(J+1)
            KZT(J)=KZT(J+1)
            KST(J)=KST(J+1)
          ENDDO
        ENDIF
        IELIM=IELIM+1
        FFT(NOST)=0.0D0
        UIT(NOST)=0.0D0
        WRIT(NOST)=0.0D0
        KZT(NOST)=0
        KST(NOST)=0
  911   CONTINUE
      ENDIF
      IF(IELIM.GT.0) THEN
        NOST=NOST-IELIM
        GO TO 910
      ENDIF
C  ****  E/P inelastic model parameters transferred to the final
C        arrays.
      IF(NOST.LT.NO) THEN
        IF(RGROUP.LT.1.4142D0) THEN
          RGROUP=RGROUP**2
          GO TO 910
        ENDIF
        NOSC(M)=NOST
        DO I=1,NOSC(M)
          F(M,I)=FFT(I)
          UI(M,I)=UIT(I)
          WRI(M,I)=WRIT(I)
          IF(UI(M,I).LT.1.0D-3) THEN
            UI(M,I)=0.0D0
          ENDIF
          KZ(M,I)=KZT(I)
          KS(M,I)=KST(I)
        ENDDO
      ELSE
        RGROUP=RGROUP**2
        GO TO 910
      ENDIF
      WRITE(6,'(1X,'' E/P in. grouping factor = '',1P,E12.5)') RGROUP
C
C  ************  Compton (impulse approximation) parameters.
C
C
C  ****  Outer shells with ionisation energies differing by a factor
C  less than RGROUP are grouped as a single shell.
C
      RGROUP=1.50D0
C  ****  Shells are sorted by increasing ionisation energies.
      IF(NOSTC.GT.1) THEN
        DO I=1,NOSTC-1
          DO J=I+1,NOSTC
            IF(UIC(I).GT.UIC(J)) THEN
              SAVE=FC(I)
              FC(I)=FC(J)
              FC(J)=SAVE
              SAVE=UIC(I)
              UIC(I)=UIC(J)
              UIC(J)=SAVE
              SAVE=FJ0C(I)
              FJ0C(I)=FJ0C(J)
              FJ0C(J)=SAVE
              ISAVE=KZC(I)
              KZC(I)=KZC(J)
              KZC(J)=ISAVE
              ISAVE=KSC(I)
              KSC(I)=KSC(J)
              KSC(J)=ISAVE
            ENDIF
          ENDDO
        ENDDO
      ENDIF
C
  920 CONTINUE
      IELIM=0
      IF(NOSTC.GT.2) THEN
        DO 921 I=1,NOSTC-1
          IF(KSC(I+1).LT.17.AND.UIC(I+1).GT.WISCUT) GO TO 921
          IF(UIC(I).LT.1.0D0.OR.UIC(I+1).LT.1.0D0) GO TO 921
          IF(UIC(I+1).GT.RGROUP*UIC(I)) GO TO 921
          UIC(I)=(FC(I)*UIC(I)+FC(I+1)*UIC(I+1))/(FC(I)+FC(I+1))
          FJ0C(I)=(FC(I)*FJ0C(I)+FC(I+1)*FJ0C(I+1))/(FC(I)+FC(I+1))
          FC(I)=FC(I)+FC(I+1)
          IF(KZC(I).NE.KZC(I+1)) KZC(I)=0
          KSC(I)=30
          IF(I.LT.NOSTC-1) THEN
            DO J=I+1,NOSTC-1
              FC(J)=FC(J+1)
              UIC(J)=UIC(J+1)
              FJ0C(J)=FJ0C(J+1)
              KZC(J)=KZC(J+1)
              KSC(J)=KSC(J+1)
            ENDDO
          ENDIF
          IELIM=IELIM+1
          FC(NOSTC)=0.0D0
          UIC(NOSTC)=0.0D0
          FJ0C(NOSTC)=0.0D0
          KZC(NOSTC)=0
          KSC(NOSTC)=0
  921   CONTINUE
      ENDIF
      IF(IELIM.GT.0) THEN
        NOSTC=NOSTC-IELIM
        GO TO 920
      ENDIF
C  ****  Compton scattering model parameters transferred to the final
C        arrays.
      IF(NOSTC.LT.NOCO) THEN
        IF(RGROUP.LT.2.0D0) THEN
          RGROUP=RGROUP**2
          GO TO 920
        ENDIF
        NOSCCO(M)=NOSTC
        DO I=1,NOSCCO(M)
          FCO(M,I)=FC(I)
          UICO(M,I)=UIC(I)
          FJ0(M,I)=FJ0C(I)
          KZCO(M,I)=KZC(I)
          KSCO(M,I)=KSC(I)
          CSUMT=CSUMT-FCO(M,I)*FJ0(M,I)
        ENDDO
        IF(ABS(CSUMT).GT.1.0D-9) THEN
          WRITE(6,'(''  Residual sum ='',1p,e12.5)') ABS(CSUMT)
          STOP 'Error in grouping the Compton profiles.'
        ENDIF
      ELSE
        RGROUP=RGROUP**2
        GO TO 920
      ENDIF
      WRITE(6,'(1X,'' Compton grouping factor = '',1P,E12.5)') RGROUP
C
C  ************  PENELOPE's input file.
C
      WRITE(6,*) '      '
      WRITE(6,*) ' PENELOPE''s material data file is being created.'
      WRITE(6,*) ' Enter path+name for this file (up to 80 characte',
     1   'rs) ...'
      READ(5,'(A80)') PFILE
      OPEN(7,FILE=PFILE)
C
      WRITE(7,1000)
 1000 FORMAT(1X,
     1  'PENELOPE (v. 2011)  Material data file ...............')
      WRITE(7,1001) NAME
 1001 FORMAT(' Material: ',A62)
      WRITE(7,1002) RHO(M)
 1002 FORMAT(' Mass density =',1P,E15.8,' g/cm**3')
      WRITE(7,1003) NELEM(M)
 1003 FORMAT(' Number of elements in the molecule = ',I2)
      DO I=1,NELEM(M)
        WRITE(7,1004) IZ(M,I),STF(M,I)
 1004   FORMAT('   atomic number =',I3,',  atoms/molecule =',1P,E15.8)
      ENDDO
      WRITE(7,1005) EXPOT(M)
 1005 FORMAT(' Mean excitation energy =',1P,E15.8,' eV')
C
      WRITE(7,1006) NOSC(M)
 1006 FORMAT(' Number of oscillators =',I3,' (E/P inelastic model)')
      DO I=1,NOSC(M)
        WRITE(7,1007) I,F(M,I),UI(M,I),WRI(M,I),KZ(M,I),KS(M,I)
 1007   FORMAT(I4,1P,3E16.8,2I4)
      ENDDO
C
      WRITE(7,1106) NOSCCO(M)
 1106 FORMAT(' Number of shells =',I3,' (Compton IA model)')
      DO I=1,NOSCCO(M)
        WRITE(7,1107) I,FCO(M,I),UICO(M,I),FJ0(M,I),KZCO(M,I),
     1    KSCO(M,I)
 1107   FORMAT(I4,1P,3E16.8,2I4)
        FJ0(M,I)=FJ0(M,I)*SL
      ENDDO
C
C  ****  Atomic relaxation data.
C
      DO I=1,NELEM(M)
        IZZ=IZ(M,I)
        CALL RELAXW(IZZ,7)
      ENDDO
C
C  ****  Energy grid (standard).
C
      NES=0
      IGRID=0
      FGRID=1.0D0
  101 IGRID=IGRID+1
      EV=EGRT(IGRID)*FGRID
      IF(IGRID.EQ.17) THEN
        IGRID=1
        FGRID=10.0D0*FGRID
      ENDIF
      IF(EV.LT.49.0D0) GO TO 101
      NES=NES+1
      ES(NES)=EV
      IF(EV.LT.1.0D9) GO TO 101
C
      EMIN=50.0D0
      EMAX=1.0D9
      CALL EGRID(EMIN,EMAX)
C
      WCRM=10.0D0
      WCCM=0.0D0
C
C  ****  Bremsstrahlung emission,
C
      CALL EBRaW(M,7)
      ZEQ=SQRT(ZBR2(M))
      CALL BRaAW(ZEQ,7)
C
      WRITE(7,1008) NES
 1008 FORMAT(1X,'*** Stopping powers for electrons and positrons',
     1  ',  NDATA =',I4)
      DO IE=1,NES
        EE=ES(IE)
        CALL EINaT(EE,WCCM,XH0,XH1,XH2,XS0,XS1,XS2,XT1,XT2,DELTA,M)
        ESTP=(XS1+XH1)*VMOL(M)*1.0D-6/RHO(M)
        CALL EBRaT(EE,WCRM,XH0,XH1,XH2,XS1,XS2,M)
        ERSTP=(XS1+XH1)*VMOL(M)*1.0D-6/RHO(M)
        CALL PINaT(EE,WCCM,XH0,XH1,XH2,XS0,XS1,XS2,XT1,XT2,DELTA,M)
        PSTP=(XS1+XH1)*VMOL(M)*1.0D-6/RHO(M)
        CALL PBRaT(EE,WCRM,XH0,XH1,XH2,XS1,XS2,M)
        PRSTP=(XS1+XH1)*VMOL(M)*1.0D-6/RHO(M)
        WRITE(7,'(1P,E10.3,5E12.5)') EE,ESTP,ERSTP,PSTP,PRSTP
      ENDDO
C
C  **** Electron and positron elastic x-sections.
C
      CALL EELaW(M,7)
      CALL EELdW(M,7)  ! Uses the ELSEPA database.
C
C  **** Electron and positron inner-shell ionisation x-sections.
C
      CALL ESIaW(M,7)
      CALL PSIaW(M,7)
C
C  ****  Photon x-sections.
C
      CALL GRAaW(M,7)
C
      CALL GPPaW(EIT,XGP0,XGT0,NPTAB,M)
      DO I=1,NES
        PPE(I)=0.0D0
      ENDDO
      CALL MERGE2(ES,PPE,EIT,XGP0,ESS,PPT,NES,NPTAB,NESS)
      DO I=1,NESS
        XGP0(I)=PPT(I)
      ENDDO
      DO I=1,NES
        PPE(I)=0.0D0
      ENDDO
      CALL MERGE2(ES,PPE,EIT,XGT0,ESS,PPT,NES,NPTAB,NESS)
      DO I=1,NESS
        XGT0(I)=PPT(I)
      ENDDO
C
      WRITE(7,1009) NESS
 1009 FORMAT(1X,'*** Compton and pair-production cross',
     1  ' sections,  NDATA =',I4)
      DO IE=1,NESS
        EE=ESS(IE)
        CALL GCOaT(EE,CSC,M)
        IF(CSC.LT.1.0D-35) CSC=0.0D0
        IF(EE.LT.TREV+5.0D0) XGP0(IE)=0.0D0
        IF(EE.LT.2.0D0*TREV+10.0D0) XGT0(IE)=0.0D0
        WRITE(7,'(1P,E10.3,5E12.5)') EE,CSC,XGP0(IE),XGT0(IE)
      ENDDO
C
      CALL GPHaW(M,7)
C
      WRITE(7,1099)
 1099 FORMAT(1X,
     1  'PENELOPE (v. 2011)  End of material data file ........')
      CLOSE(7)
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PEMATS
C  *********************************************************************
      SUBROUTINE PEMATS(NELEMI,IZI,FBWI,RHOI,NAME,IWR)
C
C  This subroutine generates the material definition file, a part of the
C  input data file of PENELOPE. This subroutine is a modification of
C  PEMATW where all the information is passed in the arguments instead
C  of asking the user for these values.
C
C    NELEMM: Number of elements
C    IZI: Array of atomic numbers (length = 30)
C    FBWI: Array of weight fractions (0.0 to 1.0) (length = 30)
C    RHOI: Density in g/cm3
C    NAME: Name of material (max. 60 characters)
C    IWR: Output unit
C
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*2 LASYMB
      CHARACTER*5 CH5
      CHARACTER*62 NAME
      PARAMETER (A0B=5.291772108D-9)  ! Bohr radius (cm)
      PARAMETER (HREV=27.2113845D0)  ! Hartree energy (eV)
      PARAMETER (AVOG=6.0221415D23)  ! Avogadro's number
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (SL=137.03599911D0)  ! Speed of light (1/alpha)
      PARAMETER (TREV=2.0D0*REV)
      PARAMETER (PI=3.1415926535897932D0, FOURPI=4.0D0*PI)
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
      DIMENSION IZI(30)
      DIMENSION FBWI(30)
C  ****  Element data.
      COMMON/CADATA/ATW(99),EPX(99),RSCR(99),ETA(99),EB(99,30),
     1  IFI(99,30),IKS(99,30),NSHT(99),LASYMB(99)
      DIMENSION CP(99,30),IFS(99,30)
C  ****  Simulation parameters.
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  E/P inelastic collisions.
      PARAMETER (NO=128)
      COMMON/CEIN/EXPOT(MAXMAT),OP2(MAXMAT),F(MAXMAT,NO),UI(MAXMAT,NO),
     1  WRI(MAXMAT,NO),KZ(MAXMAT,NO),KS(MAXMAT,NO),NOSC(MAXMAT)
C  ****  Compton scattering.
      PARAMETER (NOCO=128)
      COMMON/CGCO/FCO(MAXMAT,NOCO),UICO(MAXMAT,NOCO),FJ0(MAXMAT,NOCO),
     2  KZCO(MAXMAT,NOCO),KSCO(MAXMAT,NOCO),NOSCCO(MAXMAT)
      PARAMETER (NOM=400)
      DIMENSION FF(NOM),UUI(NOM),FFJ0(NOM),WWRI(NOM),KKZ(NOM),KKS(NOM)
      DIMENSION FFT(NOM),UIT(NOM),WRIT(NOM),KZT(NOM),KST(NOM)
      DIMENSION FC(NOM),UIC(NOM),FJ0C(NOM),KZC(NOM),KSC(NOM)
C  ****  Bremsstrahlung emission.
      PARAMETER (NBE=57, NBW=32)
      COMMON/CEBR/WB(NBW),PBCUT(MAXMAT,NEGP),WBCUT(MAXMAT,NEGP),
     1  PDFB(MAXMAT,NEGP,NBW),DPDFB(MAXMAT,NEGP,NBW),
     2  PACB(MAXMAT,NEGP,NBW),ZBR2(MAXMAT)
C
      DIMENSION EGRT(17)
      DATA EGRT/1.0D0,1.25D0,1.50D0,1.75D0,2.00D0,2.50D0,3.00D0,
     1  3.50D0,4.00D0,4.50D0,5.00D0,5.50D0,6.00D0,7.00D0,8.00D0,
     2  9.00D0,1.00D1/
C  ****  'Standard' energy grid.
      PARAMETER (NEGP1=1500)
      DIMENSION EIT(NEGP1),ES(NEGP1),ESS(NEGP1)
      DIMENSION XGP0(NEGP1),XGT0(NEGP1),PPE(NEGP1),PPT(NEGP1)
C
      M=1
C
      NELEM(M)=NELEMI
      ZT(M)=0.0D0
      AT(M)=0.0D0
      EXPOT(M)=0.0D0
C
      DO I=1,NELEM(M)
        IZZ=IZI(I)
        FBW=FBWI(I)
        IF(IZZ.LT.1.OR.IZZ.GT.99) THEN
          STOP 'The atomic number must be in the range 1-99.'
        ENDIF
        IF(FBW.LE.0.0D0) THEN
          STOP 'The fraction by weight must be positive.'
        ENDIF
        IZ(M,I)=IZZ
        IF(I.GT.1) THEN
          DO K=1,I-1
            IF(IZZ.EQ.IZ(M,K))
     1        STOP 'This element has been declared twice.'
          ENDDO
        ENDIF
        STF(M,I)=FBW/ATW(IZZ)
      ENDDO
C
      STFM=0.0D0
      DO I=1,NELEM(M)
        IF(STF(M,I).GT.STFM) THEN
          STFM=STF(M,I)
        ENDIF
      ENDDO
      IF(STFM.LT.1.0D-16) STOP 'Fractions by weight are too small.'
      DO I=1,NELEM(M)
        STF(M,I)=STF(M,I)/STFM
      ENDDO
C
      DO I=1,NELEM(M)
        IZZ=IZ(M,I)
        ZT(M)=ZT(M)+IZZ*STF(M,I)
        AT(M)=AT(M)+ATW(IZZ)*STF(M,I)
        EXPOT(M)=EXPOT(M)+IZZ*LOG(EPX(IZZ))*STF(M,I)
      ENDDO
C
      EXPOT(M)=EXP(EXPOT(M)/ZT(M))
C
      RHO(M)=RHOI
      IF(RHO(M).LE.0.0D0) THEN
        STOP 'The mass density must be positive.'
      ENDIF
      VMOL(M)=AVOG*RHO(M)/AT(M)
C
C  ************  Atomic configuration.
C
      DO I=1,99
        NSHT(I)=0
        DO J=1,30
          EB(I,J)=0.0D0
          CP(I,J)=0.0D0
          IFI(I,J)=0
          IFS(I,J)=0
          IKS(I,J)=0
        ENDDO
      ENDDO
C
      DO I=1,NELEM(M)
        IZZ=IZ(M,I)
C  ****  Loads element data only once. NSHT(IZZ) is used as a status
C        indicator.
        IF(NSHT(IZZ).EQ.0) THEN
          OPEN(3,FILE='./pdfiles/pdatconf.p08')
          DO J=1,22
            READ(3,'(A5)') CH5
          ENDDO
          NS=0
          IZZT=0
          DO J=1,150000
            READ(3,2005,END=905) IIZ,IS,CH5,IIF,EIE,CCP
 2005       FORMAT(I3,I3,1X,A5,I3,E12.5,E9.2)
            IF(IIZ.EQ.IZZ) THEN
              NS=NS+1
              IF(NS.GT.30) THEN
                STOP 'Too many shells.'
              ENDIF
              IF(IS.LT.1.OR.IS.GT.30) THEN
                STOP 'Wrong shell number.'
              ENDIF
              IZZT=IZZT+ABS(IIF)
              EB(IZZ,IS)=EIE
              CP(IZZ,IS)=CCP
              IFI(IZZ,IS)=ABS(IIF)
              IFS(IZZ,IS)=IIF
              IKS(IZZ,NS)=IS
            ENDIF
          ENDDO
  905     CONTINUE
          NSHT(IZZ)=NS
          IF(IZZ.NE.IZZT) STOP 'Unbalanced charges (element).'
          CLOSE(3)
        ENDIF
      ENDDO
C
C  ************  E/P inelastic scattering model parameters.
C
C  ****  Set the oscillator table (analogous to ICRU37).
C
      DO I=1,NO
        F(M,I)=0.0D0
        UI(M,I)=0.0D0
        WRI(M,I)=0.0D0
        KZ(M,I)=0
        KS(M,I)=0
      ENDDO
C
      DO I=1,NOM
        FF(I)=0.0D0
        UUI(I)=0.0D0
        WWRI(I)=0.0D0
        FFJ0(I)=0.0D0
        KKZ(I)=0
        KKS(I)=0
      ENDDO
      FT=0.0D0
C  ****  The 1st oscillator corresponds to the conduction band, which is
C  tentatively assumed to consist of valence electrons (each atom con-
C  tributes a number of electrons equal to its lowest chemical valence).
      NOS=1
      FF(1)=0.0D0
      UUI(1)=0.0D0
      FFJ0(1)=0.0D0
      KKZ(1)=0
      KKS(1)=30
      DO I=1,NELEM(M)
        IZZ=IZ(M,I)
        DO K=1,30
          JS=IKS(IZZ,K)
          IF(JS.GT.0) THEN
            IF(ABS(IFS(IZZ,JS)).GT.0) THEN
              NOS=NOS+1
              IF(NOS.GT.NOM) STOP
     1    'Too many oscillators. The parameter NOM should be enlarged.'
              FF(NOS)=ABS(IFS(IZZ,JS))*STF(M,I)
              UUI(NOS)=EB(IZZ,JS)
              FFJ0(NOS)=CP(IZZ,JS)
              KKZ(NOS)=IZZ
              IF(IZZ.GT.6.AND.JS.LT.17) THEN
                KKS(NOS)=JS
              ELSE
                KKS(NOS)=30
              ENDIF
              FT=FT+FF(NOS)
              IF(IFS(IZZ,JS).LT.0)
     1          FF(1)=FF(1)+ABS(IFS(IZZ,JS))*STF(M,I)
            ENDIF
          ENDIF
        ENDDO
      ENDDO
C
      IF(ABS(FT-ZT(M)).GT.1.0D-10*ZT(M))
     1  STOP 'Unbalanced charges (compound).'
C  ****  Oscillators are sorted by increasing ionization energies.
      DO I=1,NOS-1
        DO J=I+1,NOS
          IF(UUI(I).GE.UUI(J)) THEN
            SAVE=UUI(I)
            UUI(I)=UUI(J)
            UUI(J)=SAVE
            SAVE=FF(I)
            FF(I)=FF(J)
            FF(J)=SAVE
            SAVE=FFJ0(I)
            FFJ0(I)=FFJ0(J)
            FFJ0(J)=SAVE
            ISAVE=KKZ(I)
            KKZ(I)=KKZ(J)
            KKZ(J)=ISAVE
            ISAVE=KKS(I)
            KKS(I)=KKS(J)
            KKS(J)=ISAVE
          ENDIF
        ENDDO
      ENDDO
C
C  ************  Plasma energy and conduction band excitations.
C
      OP2(M)=FOURPI*ZT(M)*VMOL(M)*A0B**3*HREV**2
      OMEGA=SQRT(OP2(M))
      EPP=OMEGA*SQRT(FF(1)/ZT(M))
      EP=EPP
      FP=FF(1)
      IF(FP.GT.ZT(M)+1.0D-13) STOP 'FP is too large.'
      IF(EP.LT.1.0D0.OR.FP.LT.0.5D0) THEN
C  ****  Insulator. There is no conduction band.
        IFCB=0
        DO J=1,NOS-1
          FF(J)=FF(J+1)
          UUI(J)=UUI(J+1)
          FFJ0(J)=FFJ0(J+1)
          KKZ(J)=KKZ(J+1)
          KKS(J)=KKS(J+1)
        ENDDO
        NOS=NOS-1
      ELSE
C  ****  Conductor. Outer shells are 'moved' to the c.b.
        IFCB=1
        IDEAD=0
        FPP=FP
        I=1
  907   I=I+1
        IF(FF(I).LT.FPP) THEN
          FPP=FPP-FF(I)
          FF(I)=0.0D0
          IDEAD=IDEAD+1
          GO TO 907
        ELSE
          FF(I)=FF(I)-FPP
          IF(ABS(FF(I)).LT.1.0D-12) THEN
            FP=FP+FF(I)
            FF(I)=0.0D0
            IDEAD=IDEAD+1
          ENDIF
        ENDIF
        FF(1)=FP
        UUI(1)=0.0D0
        WWRI(1)=EP
        FFJ0(1)=0.75D0/SQRT(3.0D0*PI*PI*VMOL(M)*A0B**3*FP)
        KKZ(1)=0
        KKS(1)=30
        IF(IDEAD.GT.0) THEN
          DO J=2,NOS-IDEAD
            FF(J)=FF(J+IDEAD)
            UUI(J)=UUI(J+IDEAD)
            FFJ0(J)=FFJ0(J+IDEAD)
            KKZ(J)=KKZ(J+IDEAD)
            KKS(J)=KKS(J+IDEAD)
          ENDDO
          NOS=NOS-IDEAD
        ENDIF
      ENDIF
C  ****  Check f-sum rule.
      SUM=0.0D0
      DO J=1,NOS
        SUM=SUM+FF(J)
      ENDDO
      IF(ABS(SUM-ZT(M)).GT.1.0D-6*ZT(M))
     1  STOP 'Inconsistent oscillator strength data.'
      IF(ABS(SUM-ZT(M)).GT.1.0D-12*ZT(M)) THEN
        FACT=ZT(M)/SUM
        DO J=1,NOS
          FF(J)=FACT*FF(J)
        ENDDO
      ENDIF
C
C  ****  Initial parameters for Compton scattering (before grouping).
C
      NOSTC=NOS
      CSUMT=0.0D0
      DO I=1,NOSTC
        FC(I)=FF(I)
        UIC(I)=UUI(I)
        FJ0C(I)=FFJ0(I)
        KZC(I)=KKZ(I)
        KSC(I)=KKS(I)
        CSUMT=CSUMT+FC(I)*FJ0C(I)
      ENDDO
C
C  ************  Sternheimer's adjustment factor.
C
      IF(NOS.GT.1) THEN
        TST=ZT(M)*DLOG(EXPOT(M))
        AAL=0.5D0
        AAU=10.0D0
  908   AA=0.5D0*(AAL+AAU)
        SUM=0.0D0
        DO I=1,NOS
          IF(I.EQ.1.AND.IFCB.EQ.1) THEN
            SUM=SUM+FF(1)*DLOG(WWRI(1))
          ELSE
            WI2=(AA*UUI(I))**2
     1         +0.666666666666666D0*(FF(I)/ZT(M))*OMEGA**2
            WWRI(I)=DSQRT(WI2)
            SUM=SUM+FF(I)*DLOG(WWRI(I))
          ENDIF
        ENDDO
        IF(SUM.LT.TST) THEN
          AAL=AA
        ELSE
          AAU=AA
        ENDIF
        IF(AAU-AAL.GT.1.0D-14*AA) GO TO 908
      ELSE
        UUI(1)=DABS(UUI(1))
        WWRI(1)=EXPOT(M)
      ENDIF
C  ****  Verification.
      EXPT=FF(1)*LOG(WWRI(1))
      TST=FF(1)
      IF(NOS.GT.1) THEN
        DO I=2,NOS
          EXPT=EXPT+FF(I)*LOG(WWRI(I))
          TST=TST+FF(I)
        ENDDO
      ENDIF
C
      IF(ABS(TST-ZT(M)).GT.1.0D-8*ZT(M)) THEN
        STOP 'Inconsistent oscillator-strength data.'
      ENDIF
      EXPT=EXP(EXPT/ZT(M))
      IF(ABS(EXPT-EXPOT(M)).GT.1.0D-8*EXPOT(M)) THEN
        STOP 'Inconsistent oscillator-strength data (2).'
      ENDIF
C
C  ****  Selection of the lowest ionisation energy for inner shells.
C  Only the K, L, M and N shells with ionisation energies less than that
C  of the O1 shell of the heaviest element in the material are consider-
C  ed as inner shells. As a result, the inner/outer character of an
C  atomic shell depends on the composition of the material.
C
      IZMAX=0
      DO I=1,NELEM(M)
        IZMAX=MAX(IZMAX,IZ(M,I))
      ENDDO
      WISCUT=MAX(50.0D0,EB(IZMAX,17))
C
      NOST=NOS
      DO I=1,NOST
        FFT(I)=FF(I)
        UIT(I)=UUI(I)
        WRIT(I)=WWRI(I)
        KZT(I)=KKZ(I)
        KST(I)=KKS(I)
      ENDDO
C  ****  Oscillators are sorted by increasing resonance energies.
      IF(NOST.GT.IFCB+1) THEN
        DO I=IFCB+1,NOST-1
          DO J=I+1,NOST
            IF(WRIT(I).GT.WRIT(J)) THEN
              SAVE=FFT(I)
              FFT(I)=FFT(J)
              FFT(J)=SAVE
              SAVE=UIT(I)
              UIT(I)=UIT(J)
              UIT(J)=SAVE
              SAVE=WRIT(I)
              WRIT(I)=WRIT(J)
              WRIT(J)=SAVE
              ISAVE=KZT(I)
              KZT(I)=KZT(J)
              KZT(J)=ISAVE
              ISAVE=KST(I)
              KST(I)=KST(J)
              KST(J)=ISAVE
            ENDIF
          ENDDO
        ENDDO
      ENDIF
C
C  ****  Oscillators of outer shells with resonance energies differing
C  by a factor less than RGROUP are grouped as a single oscillator.
C
      RGROUP=1.05D0
  910 CONTINUE
      IELIM=0
      IF(NOST.GT.IFCB+2) THEN
        DO 911 I=IFCB+1,NOST-1
        IF(KST(I+1).LT.17.AND.UIT(I+1).GT.WISCUT) GO TO 911
        IF(WRIT(I).LT.1.0D0.OR.WRIT(I+1).LT.1.0D0) GO TO 911
        IF(WRIT(I+1).GT.RGROUP*WRIT(I)) GO TO 911
        WRIT(I)=EXP((FFT(I)*LOG(WRIT(I))+FFT(I+1)*LOG(WRIT(I+1)))
     1         /(FFT(I)+FFT(I+1)))
        UIT(I)=(FFT(I)*UIT(I)+FFT(I+1)*UIT(I+1))/(FFT(I)+FFT(I+1))
        FFT(I)=FFT(I)+FFT(I+1)
        IF(KZT(I).NE.KZT(I+1)) KZT(I)=0
        IF(KST(I).LT.17.OR.KST(I+1).LT.17) THEN
          KST(I)=MIN(KST(I),KST(I+1))
        ELSE
          KST(I)=30
        ENDIF
        IF(I.LT.NOST-1) THEN
          DO J=I+1,NOST-1
            FFT(J)=FFT(J+1)
            UIT(J)=UIT(J+1)
            WRIT(J)=WRIT(J+1)
            KZT(J)=KZT(J+1)
            KST(J)=KST(J+1)
          ENDDO
        ENDIF
        IELIM=IELIM+1
        FFT(NOST)=0.0D0
        UIT(NOST)=0.0D0
        WRIT(NOST)=0.0D0
        KZT(NOST)=0
        KST(NOST)=0
  911   CONTINUE
      ENDIF
      IF(IELIM.GT.0) THEN
        NOST=NOST-IELIM
        GO TO 910
      ENDIF
C  ****  E/P inelastic model parameters transferred to the final
C        arrays.
      IF(NOST.LT.NO) THEN
        IF(RGROUP.LT.1.4142D0) THEN
          RGROUP=RGROUP**2
          GO TO 910
        ENDIF
        NOSC(M)=NOST
        DO I=1,NOSC(M)
          F(M,I)=FFT(I)
          UI(M,I)=UIT(I)
          WRI(M,I)=WRIT(I)
          IF(UI(M,I).LT.1.0D-3) THEN
            UI(M,I)=0.0D0
          ENDIF
          KZ(M,I)=KZT(I)
          KS(M,I)=KST(I)
        ENDDO
      ELSE
        RGROUP=RGROUP**2
        GO TO 910
      ENDIF
C
C  ************  Compton (impulse approximation) parameters.
C
C
C  ****  Outer shells with ionisation energies differing by a factor
C  less than RGROUP are grouped as a single shell.
C
      RGROUP=1.50D0
C  ****  Shells are sorted by increasing ionisation energies.
      IF(NOSTC.GT.1) THEN
        DO I=1,NOSTC-1
          DO J=I+1,NOSTC
            IF(UIC(I).GT.UIC(J)) THEN
              SAVE=FC(I)
              FC(I)=FC(J)
              FC(J)=SAVE
              SAVE=UIC(I)
              UIC(I)=UIC(J)
              UIC(J)=SAVE
              SAVE=FJ0C(I)
              FJ0C(I)=FJ0C(J)
              FJ0C(J)=SAVE
              ISAVE=KZC(I)
              KZC(I)=KZC(J)
              KZC(J)=ISAVE
              ISAVE=KSC(I)
              KSC(I)=KSC(J)
              KSC(J)=ISAVE
            ENDIF
          ENDDO
        ENDDO
      ENDIF
C
  920 CONTINUE
      IELIM=0
      IF(NOSTC.GT.2) THEN
        DO 921 I=1,NOSTC-1
          IF(KSC(I+1).LT.17.AND.UIC(I+1).GT.WISCUT) GO TO 921
          IF(UIC(I).LT.1.0D0.OR.UIC(I+1).LT.1.0D0) GO TO 921
          IF(UIC(I+1).GT.RGROUP*UIC(I)) GO TO 921
          UIC(I)=(FC(I)*UIC(I)+FC(I+1)*UIC(I+1))/(FC(I)+FC(I+1))
          FJ0C(I)=(FC(I)*FJ0C(I)+FC(I+1)*FJ0C(I+1))/(FC(I)+FC(I+1))
          FC(I)=FC(I)+FC(I+1)
          IF(KZC(I).NE.KZC(I+1)) KZC(I)=0
          KSC(I)=30
          IF(I.LT.NOSTC-1) THEN
            DO J=I+1,NOSTC-1
              FC(J)=FC(J+1)
              UIC(J)=UIC(J+1)
              FJ0C(J)=FJ0C(J+1)
              KZC(J)=KZC(J+1)
              KSC(J)=KSC(J+1)
            ENDDO
          ENDIF
          IELIM=IELIM+1
          FC(NOSTC)=0.0D0
          UIC(NOSTC)=0.0D0
          FJ0C(NOSTC)=0.0D0
          KZC(NOSTC)=0
          KSC(NOSTC)=0
  921   CONTINUE
      ENDIF
      IF(IELIM.GT.0) THEN
        NOSTC=NOSTC-IELIM
        GO TO 920
      ENDIF
C  ****  Compton scattering model parameters transferred to the final
C        arrays.
      IF(NOSTC.LT.NOCO) THEN
        IF(RGROUP.LT.2.0D0) THEN
          RGROUP=RGROUP**2
          GO TO 920
        ENDIF
        NOSCCO(M)=NOSTC
        DO I=1,NOSCCO(M)
          FCO(M,I)=FC(I)
          UICO(M,I)=UIC(I)
          FJ0(M,I)=FJ0C(I)
          KZCO(M,I)=KZC(I)
          KSCO(M,I)=KSC(I)
          CSUMT=CSUMT-FCO(M,I)*FJ0(M,I)
        ENDDO
        IF(ABS(CSUMT).GT.1.0D-9) THEN
          STOP 'Error in grouping the Compton profiles.'
        ENDIF
      ELSE
        RGROUP=RGROUP**2
        GO TO 920
      ENDIF
C
C  ************  PENELOPE's input file.
C
      WRITE(IWR,1000)
 1000 FORMAT(1X,
     1  'PENELOPE (v. 2011)  Material data file ...............')
      WRITE(IWR,1001) NAME
 1001 FORMAT(' Material: ',A62)
      WRITE(IWR,1002) RHO(M)
 1002 FORMAT(' Mass density =',1P,E15.8,' g/cm**3')
      WRITE(IWR,1003) NELEM(M)
 1003 FORMAT(' Number of elements in the molecule = ',I2)
      DO I=1,NELEM(M)
        WRITE(IWR,1004) IZ(M,I),STF(M,I)
 1004   FORMAT('   atomic number =',I3,',  atoms/molecule =',1P,E15.8)
      ENDDO
      WRITE(IWR,1005) EXPOT(M)
 1005 FORMAT(' Mean excitation energy =',1P,E15.8,' eV')
C
      WRITE(IWR,1006) NOSC(M)
 1006 FORMAT(' Number of oscillators =',I3,' (E/P inelastic model)')
      DO I=1,NOSC(M)
        WRITE(IWR,1007) I,F(M,I),UI(M,I),WRI(M,I),KZ(M,I),KS(M,I)
 1007   FORMAT(I4,1P,3E16.8,2I4)
      ENDDO
C
      WRITE(IWR,1106) NOSCCO(M)
 1106 FORMAT(' Number of shells =',I3,' (Compton IA model)')
      DO I=1,NOSCCO(M)
        WRITE(IWR,1107) I,FCO(M,I),UICO(M,I),FJ0(M,I),KZCO(M,I),
     1    KSCO(M,I)
 1107   FORMAT(I4,1P,3E16.8,2I4)
        FJ0(M,I)=FJ0(M,I)*SL
      ENDDO
C
C  ****  Atomic relaxation data.
C
      DO I=1,NELEM(M)
        IZZ=IZ(M,I)
        CALL RELAXW(IZZ,IWR)
      ENDDO
C
C  ****  Energy grid (standard).
C
      NES=0
      IGRID=0
      FGRID=1.0D0
  101 IGRID=IGRID+1
      EV=EGRT(IGRID)*FGRID
      IF(IGRID.EQ.17) THEN
        IGRID=1
        FGRID=10.0D0*FGRID
      ENDIF
      IF(EV.LT.49.0D0) GO TO 101
      NES=NES+1
      ES(NES)=EV
      IF(EV.LT.1.0D9) GO TO 101
C
      EMIN=50.0D0
      EMAX=1.0D9
      CALL EGRID(EMIN,EMAX)
C
      WCRM=10.0D0
      WCCM=0.0D0
C
C  ****  Bremsstrahlung emission,
C
      CALL EBRaW(M,IWR)
      ZEQ=SQRT(ZBR2(M))
      CALL BRaAW(ZEQ,IWR)
C
      WRITE(IWR,1008) NES
 1008 FORMAT(1X,'*** Stopping powers for electrons and positrons',
     1  ',  NDATA =',I4)
      DO IE=1,NES
        EE=ES(IE)
        CALL EINaT(EE,WCCM,XH0,XH1,XH2,XS0,XS1,XS2,XT1,XT2,DELTA,M)
        ESTP=(XS1+XH1)*VMOL(M)*1.0D-6/RHO(M)
        CALL EBRaT(EE,WCRM,XH0,XH1,XH2,XS1,XS2,M)
        ERSTP=(XS1+XH1)*VMOL(M)*1.0D-6/RHO(M)
        CALL PINaT(EE,WCCM,XH0,XH1,XH2,XS0,XS1,XS2,XT1,XT2,DELTA,M)
        PSTP=(XS1+XH1)*VMOL(M)*1.0D-6/RHO(M)
        CALL PBRaT(EE,WCRM,XH0,XH1,XH2,XS1,XS2,M)
        PRSTP=(XS1+XH1)*VMOL(M)*1.0D-6/RHO(M)
        WRITE(IWR,'(1P,E10.3,5E12.5)') EE,ESTP,ERSTP,PSTP,PRSTP
      ENDDO
C
C  **** Electron and positron elastic x-sections.
C
      CALL EELaW(M,IWR)
      CALL EELdW(M,IWR)  ! Uses the ELSEPA database.
C
C  **** Electron and positron inner-shell ionisation x-sections.
C
      CALL ESIaW(M,IWR)
      CALL PSIaW(M,IWR)
C
C  ****  Photon x-sections.
C
      CALL GRAaW(M,IWR)
C
      CALL GPPaW(EIT,XGP0,XGT0,NPTAB,M)
      DO I=1,NES
        PPE(I)=0.0D0
      ENDDO
      CALL MERGE2(ES,PPE,EIT,XGP0,ESS,PPT,NES,NPTAB,NESS)
      DO I=1,NESS
        XGP0(I)=PPT(I)
      ENDDO
      DO I=1,NES
        PPE(I)=0.0D0
      ENDDO
      CALL MERGE2(ES,PPE,EIT,XGT0,ESS,PPT,NES,NPTAB,NESS)
      DO I=1,NESS
        XGT0(I)=PPT(I)
      ENDDO
C
      WRITE(IWR,1009) NESS
 1009 FORMAT(1X,'*** Compton and pair-production cross',
     1  ' sections,  NDATA =',I4)
      DO IE=1,NESS
        EE=ESS(IE)
        CALL GCOaT(EE,CSC,M)
        IF(CSC.LT.1.0D-35) CSC=0.0D0
        IF(EE.LT.TREV+5.0D0) XGP0(IE)=0.0D0
        IF(EE.LT.2.0D0*TREV+10.0D0) XGT0(IE)=0.0D0
        WRITE(IWR,'(1P,E10.3,5E12.5)') EE,CSC,XGP0(IE),XGT0(IE)
      ENDDO
C
      CALL GPHaW(M,IWR)
C
      WRITE(IWR,1099)
 1099 FORMAT(1X,
     1  'PENELOPE (v. 2011)  End of material data file ........')
      CLOSE(IWR)
      RETURN
      END
C  *********************************************************************
C                  FUNCTION PRANGE
C  *********************************************************************
      FUNCTION PRANGE(E,KPAR,M)
C
C  This function computes the range (in cm) of particles of type KPAR
C  and energy E in material M. For electrons and positrons, the output
C  is the CSDA range. For photons, the delivered value is the mean free
C  path (=inverse attenuation coefficient).
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
      COMMON/CRANGE/RANGE(3,MAXMAT,NEGP),RANGEL(3,MAXMAT,NEGP)
C  ****  Photon simulation tables.
      COMMON/CGIMFP/SGRA(MAXMAT,NEGP),SGCO(MAXMAT,NEGP),
     1  SGPH(MAXMAT,NEGP),SGPP(MAXMAT,NEGP),SGAUX(MAXMAT,NEGP)
C  ****  Rayleigh scattering.
      PARAMETER (NQ=250,NEX=1024)
      COMMON/CGRA01/FF(MAXMAT,NQ),ERA(NEX),XSRA(MAXMAT,NEX),
     1    IED(NEGP),IEU(NEGP),NE
C  ****  Photoelectric cross sections.
      PARAMETER (NTP=8000)
      COMMON/CGPH00/EPH(NTP),XPH(NTP,17),IPHF(99),IPHL(99),NPHS(99),NCUR
C
      IF(E.LT.EL) THEN
        EE=EL
      ELSE IF (E.GT.EU) THEN
        EE=EU
      ELSE
        EE=E
      ENDIF
      XEL=LOG(EE)
      XE=1.0D0+(XEL-DLEMP1)*DLFC
      KE=XE
      IF(KE.LT.1) KE=1
      IF(KE.GE.NEGP) KE=NEGP-1
      XEK=XE-KE
C
C  ************  Electrons and positrons.
C
      IF(KPAR.NE.2) THEN
        PRANGE=EXP(RANGEL(KPAR,M,KE)
     1        +(RANGEL(KPAR,M,KE+1)-RANGEL(KPAR,M,KE))*XEK)
        RETURN
      ENDIF
C
C  ************  Photons.
C
C  ****  Rayleigh scattering.
      II=IED(KE)
      IU=IEU(KE)
    1 IT=(II+IU)/2
      IF(XEL.GT.ERA(IT)) THEN
        II=IT
      ELSE
        IU=IT
      ENDIF
      IF(IU-II.GT.1) GO TO 1
      HMF1=EXP(XSRA(M,II)+(XSRA(M,II+1)-XSRA(M,II))*(XEL-ERA(II))
     1    /(ERA(II+1)-ERA(II)))
C  ****  Compton scattering.
      HMF2=EXP(SGCO(M,KE)+(SGCO(M,KE+1)-SGCO(M,KE))*XEK)
C  ****  Photoelectric absorption.
      PTOT=0.0D0
      DO IEL=1,NELEM(M)
        IZZ=IZ(M,IEL)
        I=IPHF(IZZ)
        IU=IPHL(IZZ)
    2   IT=(I+IU)/2
        IF(XEL.GT.EPH(IT)) THEN
          I=IT
        ELSE
          IU=IT
        ENDIF
        IF(IU-I.GT.1) GO TO 2
C
        DEE=EPH(I+1)-EPH(I)
        IF(DEE.GT.1.0D-15) THEN
          PCSL=XPH(I,1)+(XPH(I+1,1)-XPH(I,1))*(XEL-EPH(I))/DEE
        ELSE
          PCSL=XPH(I,1)
        ENDIF
        PTOT=PTOT+STF(M,IEL)*EXP(PCSL)
      ENDDO
      HMF3=PTOT*VMOL(M)
C  ****  Pair production.
      IF(E.GT.1.022D6) THEN
        HMF4=EXP(SGPP(M,KE)+(SGPP(M,KE+1)-SGPP(M,KE))*XEK)
      ELSE
        HMF4=0.0D0
      ENDIF
      PRANGE=1.0D0/MAX(HMF1+HMF2+HMF3+HMF4,1.0D-35)
      RETURN
      END
C  *********************************************************************
C                  FUNCTION PHMFP
C  *********************************************************************
      FUNCTION PHMFP(E,KPAR,M,ICOL)
C
C  This function computes the mean free path (in cm) of particles of
C  type KPAR and energy E between hard interactions of kind ICOL in
C  material M. If ICOL does not correspond to a hard interaction type,
C  the result is set equal to 1.0D35.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****  Electron simulation tables.
      COMMON/CEIMFP/SEHEL(MAXMAT,NEGP),SEHIN(MAXMAT,NEGP),
     1  SEISI(MAXMAT,NEGP),SEHBR(MAXMAT,NEGP),SEAUX(MAXMAT,NEGP),
     2  SETOT(MAXMAT,NEGP),CSTPE(MAXMAT,NEGP),RSTPE(MAXMAT,NEGP),
     3  DEL(MAXMAT,NEGP),W1E(MAXMAT,NEGP),W2E(MAXMAT,NEGP),
     4  DW1EL(MAXMAT,NEGP),DW2EL(MAXMAT,NEGP),
     5  RNDCE(MAXMAT,NEGP),AE(MAXMAT,NEGP),BE(MAXMAT,NEGP),
     6  T1E(MAXMAT,NEGP),T2E(MAXMAT,NEGP)
C  ****  Positron simulation tables.
      COMMON/CPIMFP/SPHEL(MAXMAT,NEGP),SPHIN(MAXMAT,NEGP),
     1  SPISI(MAXMAT,NEGP),SPHBR(MAXMAT,NEGP),SPAN(MAXMAT,NEGP),
     2  SPAUX(MAXMAT,NEGP),SPTOT(MAXMAT,NEGP),CSTPP(MAXMAT,NEGP),
     3  RSTPP(MAXMAT,NEGP),W1P(MAXMAT,NEGP),W2P(MAXMAT,NEGP),
     4  DW1PL(MAXMAT,NEGP),DW2PL(MAXMAT,NEGP),
     5  RNDCP(MAXMAT,NEGP),AP(MAXMAT,NEGP),BP(MAXMAT,NEGP),
     6  T1P(MAXMAT,NEGP),T2P(MAXMAT,NEGP)
C  ****  Photon simulation tables.
      COMMON/CGIMFP/SGRA(MAXMAT,NEGP),SGCO(MAXMAT,NEGP),
     1  SGPH(MAXMAT,NEGP),SGPP(MAXMAT,NEGP),SGAUX(MAXMAT,NEGP)
C  ****  Rayleigh scattering.
      PARAMETER (NQ=250,NEX=1024)
      COMMON/CGRA01/FF(MAXMAT,NQ),ERA(NEX),XSRA(MAXMAT,NEX),
     1    IED(NEGP),IEU(NEGP),NE
C  ****  Photoelectric cross sections.
      PARAMETER (NTP=8000)
      COMMON/CGPH00/EPH(NTP),XPH(NTP,17),IPHF(99),IPHL(99),NPHS(99),NCUR
C
      IF(E.LE.EL.OR.E.GE.EU) THEN
        PHMFP=1.0D50
        RETURN
      ENDIF
      XEL=LOG(E)
      XE=1.0D0+(XEL-DLEMP1)*DLFC
      KE=XE
      IF(KE.LT.1) KE=1
      IF(KE.GE.NEGP) KE=NEGP-1
      XEK=XE-KE
C
      HMFP=1.0D-35
      IF(KPAR.EQ.1) THEN
        IF(ICOL.EQ.2) THEN
          HMFP=EXP(SEHEL(M,KE)+(SEHEL(M,KE+1)-SEHEL(M,KE))*XEK)
        ELSE IF(ICOL.EQ.3) THEN
          HMFP=EXP(SEHIN(M,KE)+(SEHIN(M,KE+1)-SEHIN(M,KE))*XEK)
        ELSE IF(ICOL.EQ.4) THEN
          HMFP=EXP(SEHBR(M,KE)+(SEHBR(M,KE+1)-SEHBR(M,KE))*XEK)
        ELSE IF(ICOL.EQ.5) THEN
          HMFP=EXP(SEISI(M,KE)+(SEISI(M,KE+1)-SEISI(M,KE))*XEK)
        ELSE IF(ICOL.EQ.8) THEN
          HMFP=EXP(SEAUX(M,KE)+(SEAUX(M,KE+1)-SEAUX(M,KE))*XEK)
        ENDIF
      ELSE IF(KPAR.EQ.2) THEN
        IF(ICOL.EQ.1) THEN
C  ****  Binary search.
          I=IED(KE)
          IU=IEU(KE)
    1     IT=(I+IU)/2
          IF(XEL.GT.ERA(IT)) THEN
            I=IT
          ELSE
            IU=IT
          ENDIF
          IF(IU-I.GT.1) GO TO 1
          HMFP=EXP(XSRA(M,I)+(XSRA(M,I+1)-XSRA(M,I))*(XEL-ERA(I))
     1        /(ERA(I+1)-ERA(I)))
        ELSE IF(ICOL.EQ.2) THEN
          HMFP=EXP(SGCO(M,KE)+(SGCO(M,KE+1)-SGCO(M,KE))*XEK)
        ELSE IF(ICOL.EQ.3) THEN
          PTOT=0.0D0
          DO IEL=1,NELEM(M)
            IZZ=IZ(M,IEL)
C  ****  Binary search.
            I=IPHF(IZZ)
            IU=IPHL(IZZ)
    2       IT=(I+IU)/2
            IF(XEL.GT.EPH(IT)) THEN
              I=IT
            ELSE
              IU=IT
            ENDIF
            IF(IU-I.GT.1) GO TO 2
C
            DEE=EPH(I+1)-EPH(I)
            IF(DEE.GT.1.0D-15) THEN
              PCSL=XPH(I,1)+(XPH(I+1,1)-XPH(I,1))*(XEL-EPH(I))/DEE
            ELSE
              PCSL=XPH(I,1)
            ENDIF
            PTOT=PTOT+STF(M,IEL)*EXP(PCSL)
          ENDDO
          HMFP=PTOT*VMOL(M)
        ELSE IF(ICOL.EQ.4.AND.E.GT.1.022D6) THEN
          HMFP=EXP(SGPP(M,KE)+(SGPP(M,KE+1)-SGPP(M,KE))*XEK)
        ELSE IF(ICOL.EQ.6) THEN
          HMFP=EXP(SGAUX(M,KE)+(SGAUX(M,KE+1)-SGAUX(M,KE))*XEK)
        ENDIF
      ELSE IF(KPAR.EQ.3) THEN
        IF(ICOL.EQ.2) THEN
          HMFP=EXP(SPHEL(M,KE)+(SPHEL(M,KE+1)-SPHEL(M,KE))*XEK)
        ELSE IF(ICOL.EQ.3) THEN
          HMFP=EXP(SPHIN(M,KE)+(SPHIN(M,KE+1)-SPHIN(M,KE))*XEK)
        ELSE IF(ICOL.EQ.4) THEN
          HMFP=EXP(SPHBR(M,KE)+(SPHBR(M,KE+1)-SPHBR(M,KE))*XEK)
        ELSE IF(ICOL.EQ.5) THEN
          HMFP=EXP(SPISI(M,KE)+(SPISI(M,KE+1)-SPISI(M,KE))*XEK)
        ELSE IF(ICOL.EQ.6) THEN
          HMFP=EXP(SPAN(M,KE)+(SPAN(M,KE+1)-SPAN(M,KE))*XEK)
        ELSE IF(ICOL.EQ.8) THEN
          HMFP=EXP(SPAUX(M,KE)+(SPAUX(M,KE+1)-SPAUX(M,KE))*XEK)
        ENDIF
      ENDIF
C
      PHMFP=1.0D0/MAX(HMFP,1.0D-35)
      RETURN
      END
C  *********************************************************************
C                  FUNCTION RYIELD
C  *********************************************************************
      FUNCTION RYIELD(E,KPAR,M)
C
C  This function calculates the radiative (bremsstrahlung) yields of
C  electrons and positrons.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Electron and positron radiative yields.
      COMMON/CBRYLD/EBRY(MAXMAT,NEGP),PBRY(MAXMAT,NEGP)
C
      IF(KPAR.EQ.2) THEN
        RYIELD=0.0D0
        RETURN
      ENDIF
C
      IF(E.LT.EL) THEN
        EE=EL
      ELSE IF (E.GT.EU) THEN
        EE=EU
      ELSE
        EE=E
      ENDIF
      XEL=LOG(EE)
      XE=1.0D0+(XEL-DLEMP1)*DLFC
      KE=XE
      IF(KE.LT.1) KE=1
      IF(KE.GE.NEGP) KE=NEGP-1
      XEK=XE-KE
C
      IF(KPAR.EQ.1) THEN
        RYIELD=EXP(EBRY(M,KE)+(EBRY(M,KE+1)-EBRY(M,KE))*XEK)
      ELSE
        RYIELD=EXP(PBRY(M,KE)+(PBRY(M,KE+1)-PBRY(M,KE))*XEK)
      ENDIF
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE EELa
C  *********************************************************************
      SUBROUTINE EELa(A,B,RNDC,RMU)
C
C  Simulation of hard elastic events. Modified-Wentzel model.
C
C  Input arguments:
C    A, B ... angular distribution parameters.
C    RNDC ... cutoff probability.
C  Output values:
C    RMU .... angular deflection, =(1-CDT)/2.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      EXTERNAL RAND
C
      A1=A+1.0D0
      IF(B.GE.0.0D0) THEN
C
C  ****  Case I.
C
        RMUAV=A*A1*LOG(A1/A)-A
        B1=1.0D0-B
        RND0=B1*A1*RMUAV/(A+RMUAV)
        RND=RNDC+RAND(1.0D0)*(1.0D0-RNDC)
        IF(RND.LT.RND0) THEN
          RMU=RND*A/(B1*A1-RND)
        ELSE IF(RND.GT.RND0+B) THEN
          RNDMB=RND-B
          RMU=RNDMB*A/(B1*A1-RNDMB)
        ELSE
          RMU=RMUAV
        ENDIF
      ELSE
C
C  ****  Case II.
C
        BB=-B
        B1=1.0D0-BB
        RMUC=RNDC*A/(B1*A1-RNDC)
        PW=B1*A*(1.0D0-RMUC)/(A+RMUC)
        IF(RAND(2.0D0)*(BB+PW).LT.BB) THEN
          RMU=0.5D0*(1.0D0+SQRT(RAND(3.0D0)))
        ELSE
          RNDRC=RAND(3.0D0)*(1.0D0-RMUC)
          RMU=(A*RNDRC+A1*RMUC)/(A1-RNDRC)
        ENDIF
      ENDIF
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE EELaR
C  *********************************************************************
      SUBROUTINE EELaR(M,IRD,IWR,INFO)
C
C  This subroutine reads elastic cross sections for electrons and posi-
C  trons in material M from the material data file. It also initialises
C  the algorithm for simulation of elastic scattering of electrons and
C  positrons.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Simulation parameters.
      PARAMETER (MAXMAT=10)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
C  ****  Composition data.
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Electron simulation tables.
      COMMON/CEIMFP/SEHEL(MAXMAT,NEGP),SEHIN(MAXMAT,NEGP),
     1  SEISI(MAXMAT,NEGP),SEHBR(MAXMAT,NEGP),SEAUX(MAXMAT,NEGP),
     2  SETOT(MAXMAT,NEGP),CSTPE(MAXMAT,NEGP),RSTPE(MAXMAT,NEGP),
     3  DEL(MAXMAT,NEGP),W1E(MAXMAT,NEGP),W2E(MAXMAT,NEGP),
     4  DW1EL(MAXMAT,NEGP),DW2EL(MAXMAT,NEGP),
     5  RNDCE(MAXMAT,NEGP),AE(MAXMAT,NEGP),BE(MAXMAT,NEGP),
     6  T1E(MAXMAT,NEGP),T2E(MAXMAT,NEGP)
C  ****  Positron simulation tables.
      COMMON/CPIMFP/SPHEL(MAXMAT,NEGP),SPHIN(MAXMAT,NEGP),
     1  SPISI(MAXMAT,NEGP),SPHBR(MAXMAT,NEGP),SPAN(MAXMAT,NEGP),
     2  SPAUX(MAXMAT,NEGP),SPTOT(MAXMAT,NEGP),CSTPP(MAXMAT,NEGP),
     3  RSTPP(MAXMAT,NEGP),W1P(MAXMAT,NEGP),W2P(MAXMAT,NEGP),
     4  DW1PL(MAXMAT,NEGP),DW2PL(MAXMAT,NEGP),
     5  RNDCP(MAXMAT,NEGP),AP(MAXMAT,NEGP),BP(MAXMAT,NEGP),
     6  T1P(MAXMAT,NEGP),T2P(MAXMAT,NEGP)
C  ****  Total and transport cross sections.
      COMMON/CEEL00/EIT(NEGP),XE0(NEGP),XE1(NEGP),XE2(NEGP),XP0(NEGP),
     1  XP1(NEGP),XP2(NEGP),T1E0(NEGP),T2E0(NEGP),T1P0(NEGP),T2P0(NEGP),
     2  EITL(NEGP),FL(NEGP),A(NEGP),B(NEGP),C(NEGP),D(NEGP)
      COMMON/CEINTF/T1EI(NEGP),T2EI(NEGP),T1PI(NEGP),T2PI(NEGP)
C
C  ****  Reading the input cross section table.
C
      READ(IRD,2001) NDATA
 2001 FORMAT(60X,I4)
      IF(INFO.GE.2) WRITE(IWR,1001) NDATA
 1001 FORMAT(/1X,'***  Electron and positron elastic cross sections',
     1  ',  NDATA =',I4)
      IF(INFO.GE.2) WRITE(IWR,1101)
 1101 FORMAT(/2X,'Energy',7X,'CS0,e-',6X,'CS1,e-',6X,'CS2,e-',6X,
     1  'CS0,e+',6X,'CS1,e+',6X,'CS2,e+',/3X,'(eV)',8X,'(cm**2)',
     2  5X,'(cm**2)',5X,'(cm**2)',5X,'(cm**2)',5X,'(cm**2)',5X,
     3  '(cm**2)',/1X,84('-'))
      DO I=1,NDATA
        READ(IRD,*) EIT(I),XE0(I),XE1(I),XE2(I),XP0(I),XP1(I),XP2(I)
        IF(INFO.GE.2) WRITE(IWR,'(1P,7E12.5)')
     1    EIT(I),XE0(I),XE1(I),XE2(I),XP0(I),XP1(I),XP2(I)
        EITL(I)=LOG(EIT(I))
      ENDDO
C
C  ****  Elastic scattering of electrons.
C
      DO I=1,NDATA
        FL(I)=LOG(XE0(I))
      ENDDO
      CALL SPLINE(EITL,FL,A,B,C,D,0.0D0,0.0D0,NDATA)
      DO I=1,NEGP
        EC=DLEMP(I)
        CALL FINDI(EITL,EC,NDATA,J)
        XE0(I)=EXP(A(J)+EC*(B(J)+EC*(C(J)+EC*D(J))))
      ENDDO
C
      DO I=1,NDATA
        FL(I)=LOG(XE1(I))
      ENDDO
      CALL SPLINE(EITL,FL,A,B,C,D,0.0D0,0.0D0,NDATA)
      DO I=1,NEGP
        EC=DLEMP(I)
        CALL FINDI(EITL,EC,NDATA,J)
        XE1(I)=EXP(A(J)+EC*(B(J)+EC*(C(J)+EC*D(J))))
      ENDDO
C
      DO I=1,NDATA
        FL(I)=LOG(XE2(I))
      ENDDO
      CALL SPLINE(EITL,FL,A,B,C,D,0.0D0,0.0D0,NDATA)
      DO I=1,NEGP
        EC=DLEMP(I)
        CALL FINDI(EITL,EC,NDATA,J)
        XE2(I)=EXP(A(J)+EC*(B(J)+EC*(C(J)+EC*D(J))))
      ENDDO
C
      DO I=1,NEGP
        XS0=XE0(I)
        XS1=XE1(I)
        XS2=XE2(I)
        FPEL=1.0D0/(XS0*VMOL(M))
        FPT1=1.0D0/(XS1*VMOL(M))
        FPST=ET(I)/(CSTPE(M,I)+RSTPE(M,I))
        XS0H=1.0D0/(VMOL(M)*MAX(FPEL,MIN(C1(M)*FPT1,C2(M)*FPST)))
        CALL EELa0(XS0,XS1,XS2,XS0H,AAA,BBB,RNDC,XS1S,XS2S)
        SEHEL(M,I)=XS0H*VMOL(M)
        RNDCE(M,I)=RNDC
        AE(M,I)=AAA
        BE(M,I)=BBB
        T1E0(I)=XS1S
        T1E(M,I)=T1EI(I)+XS1S*VMOL(M)
        T2E0(I)=XS2S
        T2E(M,I)=T2EI(I)+XS2S*VMOL(M)
      ENDDO
C
C  ****  Print electron elastic scattering tables.
C
      IF(INFO.GE.3) WRITE(IWR,1002)
 1002 FORMAT(/1X,'PENELOPE >>>  Elastic scattering of electrons')
      IF(INFO.GE.3) WRITE(IWR,1003)
 1003 FORMAT(/3X,'E (eV)',6X,'MFP (mtu)',3X,'TMFP1 (mtu)',2X,
     1  'MFPh (mtu)',8X,'A',11X,'B',11X,'RNDC',/1X,90('-'))
      DO I=1,NEGP
        FP0=RHO(M)/(XE0(I)*VMOL(M))
        FP1=RHO(M)/(XE1(I)*VMOL(M))
        HMFP=RHO(M)/SEHEL(M,I)
        IF(INFO.GE.3) WRITE(IWR,'(1P,7(E12.5,1X))') ET(I),FP0,FP1,
     1    HMFP,AE(M,I),BE(M,I),RNDCE(M,I)
        SEHEL(M,I)=LOG(SEHEL(M,I))
        AE(M,I)=LOG(AE(M,I))
C  ****  Soft scattering events are switched off when T1E is too small.
        IF(T1E(M,I).GT.1.0D-6*XE1(I)*VMOL(M)) THEN
          T1E(M,I)=LOG(MAX(T1E(M,I),1.0D-35))
          T2E(M,I)=LOG(MAX(T2E(M,I),1.0D-35))
        ELSE
          T1E(M,I)=-100.0D0
          T2E(M,I)=-100.0D0
        ENDIF
      ENDDO
C
C  ****  Elastic scattering of positrons.
C
      DO I=1,NDATA
        FL(I)=LOG(XP0(I))
      ENDDO
      CALL SPLINE(EITL,FL,A,B,C,D,0.0D0,0.0D0,NDATA)
      DO I=1,NEGP
        EC=DLEMP(I)
        CALL FINDI(EITL,EC,NDATA,J)
        XP0(I)=EXP(A(J)+EC*(B(J)+EC*(C(J)+EC*D(J))))
      ENDDO
C
      DO I=1,NDATA
        FL(I)=LOG(XP1(I))
      ENDDO
      CALL SPLINE(EITL,FL,A,B,C,D,0.0D0,0.0D0,NDATA)
      DO I=1,NEGP
        EC=DLEMP(I)
        CALL FINDI(EITL,EC,NDATA,J)
        XP1(I)=EXP(A(J)+EC*(B(J)+EC*(C(J)+EC*D(J))))
      ENDDO
C
      DO I=1,NDATA
        FL(I)=LOG(XP2(I))
      ENDDO
      CALL SPLINE(EITL,FL,A,B,C,D,0.0D0,0.0D0,NDATA)
      DO I=1,NEGP
        EC=DLEMP(I)
        CALL FINDI(EITL,EC,NDATA,J)
        XP2(I)=EXP(A(J)+EC*(B(J)+EC*(C(J)+EC*D(J))))
      ENDDO
C
      DO I=1,NEGP
        XS0=XP0(I)
        XS1=XP1(I)
        XS2=XP2(I)
        FPEL=1.0D0/(XS0*VMOL(M))
        FPT1=1.0D0/(XS1*VMOL(M))
        FPST=ET(I)/(CSTPP(M,I)+RSTPP(M,I))
        XS0H=1.0D0/(VMOL(M)*MAX(FPEL,MIN(C1(M)*FPT1,C2(M)*FPST)))
        CALL EELa0(XS0,XS1,XS2,XS0H,AAA,BBB,RNDC,XS1S,XS2S)
        SPHEL(M,I)=XS0H*VMOL(M)
        RNDCP(M,I)=RNDC
        AP(M,I)=AAA
        BP(M,I)=BBB
        T1P0(I)=XS1S
        T1P(M,I)=T1PI(I)+XS1S*VMOL(M)
        T2P0(I)=XS2S
        T2P(M,I)=T2PI(I)+XS2S*VMOL(M)
      ENDDO
C
C  ****  Print positron elastic scattering tables.
C
      IF(INFO.GE.3) WRITE(IWR,1004)
 1004 FORMAT(/1X,'PENELOPE >>>  Elastic scattering of positrons')
      IF(INFO.GE.3) WRITE(IWR,1005)
 1005 FORMAT(/3X,'E (eV)',6X,'MFP (mtu)',3X,'TMFP1 (mtu)',2X,
     1  'MFPh (mtu)',8X,'A',11X,'B',11X,'RNDC',/1X,90('-'))
      DO I=1,NEGP
        FP0=RHO(M)/(XP0(I)*VMOL(M))
        FP1=RHO(M)/(XP1(I)*VMOL(M))
        HMFP=RHO(M)/SPHEL(M,I)
        IF(INFO.GE.3) WRITE(IWR,'(1P,7(E12.5,1X))') ET(I),FP0,FP1,
     1    HMFP,AP(M,I),BP(M,I),RNDCP(M,I)
        SPHEL(M,I)=LOG(SPHEL(M,I))
        AP(M,I)=LOG(AP(M,I))
C  ****  Soft scattering events are switched off when T1P is too small.
        IF(T1P(M,I).GT.1.0D-6*XP1(I)*VMOL(M)) THEN
          T1P(M,I)=LOG(MAX(T1P(M,I),1.0D-35))
          T2P(M,I)=LOG(MAX(T2P(M,I),1.0D-35))
        ELSE
          T1P(M,I)=-100.0D0
          T2P(M,I)=-100.0D0
        ENDIF
      ENDDO
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE EELa0
C  *********************************************************************
      SUBROUTINE EELa0(XS0,XS1,XS2,XS0H,A,B,RNDC,XS1S,XS2S)
C
C     This subroutine determines the parameters of the MW model for
C  elastic scattering of electrons and positrons and initialises the
C  mixed simulation algorithm (for particles with a given energy).
C
C  Input arguments:
C    XS0 .... total x-section (cm**2).
C    XS1 .... 1st transport x-section (cm**2).
C    XS2 .... 2nd transport x-section (cm**2).
C    XS0H ... suggested x-section for hard events (cm**2).
C
C  Output values:
C    A, B ... angular distribution parameters.
C    RNDC ... cutoff probability.
C    XS0H ... adopted x-section for hard events (cm**2).
C    XS1S ... 1st transport x-section for soft events (cm**2).
C    XS2S ... 2nd transport x-section for soft events (cm**2).
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C
      IF(XS0.LT.0.0D0) CALL PISTOP(
     1  'EELa0. Negative total cross section.')
      RMU1=MIN(XS1/(2.0D0*XS0),0.48D0)  ! Ensures numerical consistency.
      RMU2=MIN((3.0D0*XS1-XS2)/(6.0D0*XS0),0.32D0)
      IF(RMU1.LT.0.0D0.OR.RMU1.LT.RMU2) THEN
        WRITE(26,1001) XS0,XS1
 1001   FORMAT(/3X,'*** The arguments in subroutine EELa0 are inconsi',
     1    'stent.'/7X,'XS0 = ',1P,E14.7,', XS1 = ',E14.7)
        CALL PISTOP('EELa0. Inconsistent arguments.')
      ENDIF
C
C  ****  Wentzel screening parameter.
C
      A=1.0D0
   10 A=A+A
      TST=A*(A+1.0D0)*LOG((1.0D0+A)/A)-A-RMU1
      IF(TST.LT.0.0D0) GO TO 10
      AU=A
      AL=0.0D0
    1 A=0.5D0*(AL+AU)
      TST=A*(A+1.0D0)*LOG((1.0D0+A)/A)-A-RMU1
      IF(TST.GT.0.0D0) THEN
        AU=A
      ELSE
        AL=A
      ENDIF
      IF(ABS(TST).GT.1.0D-15) GO TO 1
C  ****  At high energies, when truncation errors in the input tables
C  are significant, we use delta scattering.
      IF(RMU2-RMU1**2.LT.1.0D-12.OR.A.LT.1.0D-9) THEN
        B=1.0D0
        RNDC=1.0D0-XS0H/XS0
        IF(RNDC.LT.1.0D-14) RNDC=0.0D0
        XS1S=XS1*RNDC
        XS2S=XS2*RNDC
        RETURN
      ENDIF
C
      RMU1W=A*(A+1.0D0)*LOG((1.0D0+A)/A)-A
      RMU2W=A*(1.0D0-2.0D0*RMU1W)
      B=(RMU2W-RMU2)/(RMU2W-RMU1W*RMU1W)
C
C  ****  Case I.
C
      IF(B.GT.0.0D0) THEN
        RNDC=1.0D0-XS0H/XS0
        IF(RNDC.LT.1.0D-6) THEN
          RNDC=0.0D0
          XS0H=XS0
          XS1S=0.0D0
          XS2S=0.0D0
          RETURN
        ENDIF
C
        A1=A+1.0D0
        B1=1.0D0-B
        RND0=B1*A1*RMU1/(A+RMU1)
        RNDC=1.0D0-XS0H/XS0
        IF(RNDC.LT.RND0) THEN
          RMUC=RNDC*A/(B1*A1-RNDC)
          XS1S=B1*A*A1*(LOG((A+RMUC)/A)-(RMUC/(A+RMUC)))
          XS2S=B1*(A*A1*RMUC**2/(A+RMUC))-2.0D0*A*XS1S
        ELSE IF(RNDC.GT.RND0+B) THEN
          RNDMB=RNDC-B
          RMUC=RNDMB*A/(B1*A1-RNDMB)
          XS1S=B1*A*A1*(LOG((A+RMUC)/A)-(RMUC/(A+RMUC)))
          XS2S=B1*(A*A1*RMUC**2/(A+RMUC))-2.0D0*A*XS1S
          XS1S=XS1S+B*RMU1
          XS2S=XS2S+B*RMU1**2
        ELSE
          RMUC=RMU1
          WB=RNDC-RND0
          XS1S=B1*A*A1*(LOG((A+RMUC)/A)-(RMUC/(A+RMUC)))
          XS2S=B1*(A*A1*RMUC**2/(A+RMUC))-2.0D0*A*XS1S
          XS1S=XS1S+WB*RMU1
          XS2S=XS2S+WB*RMU1**2
        ENDIF
        XS2S=6.0D0*XS0*(XS1S-XS2S)
        XS1S=2.0D0*XS0*XS1S
        RETURN
      ENDIF
      IF(B.GT.-1.0D-12) THEN
        B=0.0D0
        RNDC=1.0D0-XS0H/XS0
        A1=A+1.0D0
        RMUC=RNDC*A/(A1-RNDC)
        XS1S=A*A1*(LOG((A+RMUC)/A)-(RMUC/(A+RMUC)))
        XS2S=(A*A1*RMUC**2/(A+RMUC))-2.0D0*A*XS1S
        XS2S=6.0D0*XS0*(XS1S-XS2S)
        XS1S=2.0D0*XS0*XS1S
        RETURN
      ENDIF
C
C  ****  Case II.
C
      C1=8.333333333333333D-1
      C2=7.083333333333333D-1
      D1=C2-RMU2
      D2=C1-RMU1
      D3=C2*RMU1-C1*RMU2
      AL=1.0D-24
      AU=A
    2 A=0.5D0*(AL+AU)
      RMU1W=A*(A+1.0D0)*LOG((1.0D0+A)/A)-A
      RMU2W=A*(1.0D0-2.0D0*RMU1W)
      F=D1*RMU1W-D2*RMU2W-D3
      IF(F.LT.0.0D0) THEN
        AL=A
      ELSE
        AU=A
      ENDIF
      IF(AU-AL.GT.1.0D-14*A) GO TO 2
      B=(RMU1W-RMU1)/(C1-RMU1W)
C
      RNDC=1.0D0-XS0H/XS0
      IF(RNDC.LT.1.0D-10) THEN
        RNDC=0.0D0
        XS0H=XS0
        XS1S=0.0D0
        XS2S=0.0D0
        RETURN
      ENDIF
      A1=A+1.0D0
      B1=1.0D0+B
      RNDCM=B1*A1*0.5D0/(A+0.5D0)
      IF(RNDC.GT.RNDCM) THEN
        RNDC=RNDCM
        XS0H=XS0*(1.0D0-RNDC)
      ENDIF
      RMUC=RNDC*A/(B1*A1-RNDC)
      XS1S=B1*A*A1*(LOG((A+RMUC)/A)-(RMUC/(A+RMUC)))
      XS2S=B1*(A*A1*RMUC**2/(A+RMUC))-2.0D0*A*XS1S
      XS2S=6.0D0*XS0*(XS1S-XS2S)
      XS1S=2.0D0*XS0*XS1S
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE EELaW
C  *********************************************************************
      SUBROUTINE EELaW(M,IWR)
C
C  This subroutine generates a table of integrated cross sections for
C  elastic scattering of electrons and positrons in material M, and
C  writes it on the material definition file. Data are read from the
C  files 'pdeelZZ.p08'.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C
      CHARACTER*12 FILEN
      CHARACTER*1 LDIG(10),LDIG1,LDIG2
      DATA LDIG/'0','1','2','3','4','5','6','7','8','9'/
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****  Total and transport cross sections.
      PARAMETER (NEGP=200)
C  ****  Total and transport cross sections.
      COMMON/CEEL00/EIT(NEGP),XE0(NEGP),XE1(NEGP),XE2(NEGP),XP0(NEGP),
     1  XP1(NEGP),XP2(NEGP),T1E0(NEGP),T2E0(NEGP),T1P0(NEGP),T2P0(NEGP),
     2  EITL(NEGP),FL(NEGP),A(NEGP),B(NEGP),C(NEGP),D(NEGP)
C
C  ****  Building the cross section table.
C
      DO I=1,NEGP
        XE0(I)=0.0D0
        XE1(I)=0.0D0
        XE2(I)=0.0D0
        XP0(I)=0.0D0
        XP1(I)=0.0D0
        XP2(I)=0.0D0
      ENDDO
C
      DO IEL=1,NELEM(M)
        IZZ=IZ(M,IEL)
        WGHT=STF(M,IEL)
        NLD=IZZ
        NLD1=NLD-10*(NLD/10)
        NLD2=(NLD-NLD1)/10
        LDIG1=LDIG(NLD1+1)
        LDIG2=LDIG(NLD2+1)
        FILEN='pdeel'//LDIG2//LDIG1//'.p08'
        OPEN(3,FILE='./pdfiles/'//FILEN)
        READ(3,*) IZZZ
        IF(IZZZ.NE.IZZ) CALL PISTOP('EELaW. Wrong file.')
        DO I=1,NEGP
          READ(3,*,END=1) EIT(I),XE0P,XE1P,XE2P,XP0P,XP1P,XP2P
          XE0(I)=XE0(I)+WGHT*XE0P
          XE1(I)=XE1(I)+WGHT*XE1P
          XE2(I)=XE2(I)+WGHT*XE2P
          XP0(I)=XP0(I)+WGHT*XP0P
          XP1(I)=XP1(I)+WGHT*XP1P
          XP2(I)=XP2(I)+WGHT*XP2P
          NPTAB=I
        ENDDO
    1   CONTINUE
        CLOSE(3)
      ENDDO
C
C  ****  Write final x-section table.
C
      WRITE(IWR,2001) NPTAB
 2001 FORMAT(1X,'***  Electron and positron elastic cross sections',
     1  ',  NDATA =',I4)
      DO I=1,NPTAB
        WRITE(IWR,2002) EIT(I),XE0(I),XE1(I),XE2(I),XP0(I),XP1(I),
     1    XP2(I)
      ENDDO
 2002 FORMAT(1P,E10.3,6E12.5)
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE EINa
C  *********************************************************************
      SUBROUTINE EINa(E,DELTA,DE,EP,CDT,ES,CDTS,M,IOSC)
C
C  Random sampling of hard inelastic collisions of electrons.
C
C  Sternheimer-Liljequist GOS model
C
C  Input arguments:
C    E ....... electron energy (eV).
C    M ....... material where electrons propagate.
C    DELTA ... Fermi's density effect correction.
C  Output arguments:
C    DE ...... energy loss (eV).
C    EP ...... energy of the scattered electron (eV).
C    CDT ..... cosine of the polar scattering angle.
C    ES ...... energy of the emitted secondary electron (eV).
C    CDTS .... polar cosine of direction of the secondary electron.
C    IOSC .... index of the oscillator that has been 'ionised'.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      LOGICAL LDIST
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (RREV=1.0D0/REV,TREV=2.0D0*REV,RTREV=1.0D0/TREV)
C  ****  Simulation parameters.
      PARAMETER (MAXMAT=10)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
      COMMON/CECUTR/ECUTR(MAXMAT)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  E/P inelastic collisions.
      PARAMETER (NO=128)
      COMMON/CEIN/EXPOT(MAXMAT),OP2(MAXMAT),F(MAXMAT,NO),UI(MAXMAT,NO),
     1  WRI(MAXMAT,NO),KZ(MAXMAT,NO),KS(MAXMAT,NO),NOSC(MAXMAT)
      COMMON/CEINAC/EINAC(MAXMAT,NEGP,NO),PINAC(MAXMAT,NEGP,NO)
C
      EXTERNAL RAND
C
      WCCM=WCC(M)
      IF(WCCM.GT.E) THEN
        DE=0.0D0
        EP=E
        CDT=1.0D0
        ES=0.0D0
        CDTS=0.0D0
        IOSC=NO
        RETURN
      ENDIF
C  ****  Energy grid point.
      PK=(XEL-DLEMP(KE))*DLFC
      IF(RAND(1.0D0).LT.PK) THEN
        JE=KE+1
      ELSE
        JE=KE
      ENDIF
C
C  ************  Selection of the active oscillator.
C
      TST=RAND(2.0D0)
C  ****  Binary search.
      IOSC=1
      JO=NOSC(M)+1
    1 IT=(IOSC+JO)/2
      IF(TST.GT.EINAC(M,JE,IT)) THEN
        IOSC=IT
      ELSE
        JO=IT
      ENDIF
      IF(JO-IOSC.GT.1) GO TO 1
C
      UK=UI(M,IOSC)
      WK=WRI(M,IOSC)
      IF(UK.GT.1.0D-3) THEN
        WTHR=MAX(WCCM,UK)
      ELSE
        WTHR=MAX(WCCM,WK)
      ENDIF
C
      IF(E.LT.WTHR+1.0D-6) THEN
        DE=0.0D0
        EP=E
        CDT=1.0D0
        ES=0.0D0
        CDTS=0.0D0
        IOSC=NO
        RETURN
      ENDIF
C
C  ****  Trick: The resonance energy and the cutoff recoil energy of
C        inner shells are varied to yield a smooth threshold.
C
      LDIST=.TRUE.
      IF(UK.GT.1.0D-3) THEN
        WM=3.0D0*WK-2.0D0*UK
        IF(E.GT.WM) THEN
          WKP=WK
          QKP=UK
        ELSE
          WKP=(E+2.0D0*UK)/3.0D0
          QKP=UK*(E/WM)
          WM=E
        ENDIF
        IF(WCCM.GT.WM) LDIST=.FALSE.
        EE=E+UK
        WCMAX=0.5D0*EE
        WDMAX=MIN(WM,WCMAX)
        IF(WTHR.GT.WDMAX) LDIST=.FALSE.
      ELSE
        IF(WCCM.GT.WK) LDIST=.FALSE.
        WKP=WK
        QKP=WK
        WM=E
        EE=E
        WCMAX=0.5D0*EE
        WDMAX=WKP+1.0D0
      ENDIF
C
C  ****  Constants.
C
      RB=E+TREV
      GAM=1.0D0+E*RREV
      GAM2=GAM*GAM
      BETA2=(GAM2-1.0D0)/GAM2
      AMOL=((GAM-1.0D0)/GAM)**2
      CPS=E*RB
      CP=SQRT(CPS)
C
C  ************  Partial cross sections of the active oscillator.
C
C  ****  Distant excitations.
      IF(LDIST) THEN
        CPPS=(E-WKP)*(E-WKP+TREV)
        CPP=SQRT(CPPS)
        IF(WKP.GT.1.0D-6*E) THEN
          QM=SQRT((CP-CPP)**2+REV*REV)-REV
        ELSE
          QM=WKP**2/(BETA2*TREV)
          QM=QM*(1.0D0-QM*RTREV)
        ENDIF
        IF(QM.LT.QKP) THEN
          RWKP=1.0D0/WKP
          XHDL=LOG(QKP*(QM+TREV)/(QM*(QKP+TREV)))*RWKP
          XHDT=MAX(LOG(GAM2)-BETA2-DELTA,0.0D0)*RWKP
          IF(UK.GT.1.0D-3) THEN
            F0=(WDMAX-WTHR)*(WM+WM-WDMAX-WTHR)/(WM-UK)**2
            XHDL=F0*XHDL
            XHDT=F0*XHDT
          ENDIF
        ELSE
          XHDL=0.0D0
          XHDT=0.0D0
        ENDIF
      ELSE
        QM=0.0D0    ! Defined to avoid compilation warnings.
        CPP=0.0D0   ! Defined to avoid compilation warnings.
        CPPS=0.0D0  ! Defined to avoid compilation warnings.
        XHDL=0.0D0
        XHDT=0.0D0
      ENDIF
C  ****  Close collisions.
      RCL=WTHR/EE
      IF(RCL.LT.0.5D0) THEN
        RL1=1.0D0-RCL
        RRL1=1.0D0/RL1
        XHC=(AMOL*(0.5D0-RCL)+1.0D0/RCL-RRL1
     1       +(1.0D0-AMOL)*LOG(RCL*RRL1))/EE
      ELSE
        XHC=0.0D0
      ENDIF
C
      XHTOT=XHC+XHDL+XHDT
      IF(XHTOT.LT.1.0D-35) THEN
        DE=0.0D0
        EP=E
        CDT=1.0D0
        ES=0.0D0
        CDTS=0.0D0
        IOSC=NO
        RETURN
      ENDIF
C
C  ************  Sampling of final-state variables.
C
      TST=RAND(3.0D0)*XHTOT
C
C  ****  Hard close collision.
C
      TS1=XHC
      IF(TST.LT.TS1) THEN
        A=5.0D0*AMOL
        ARCL=A*0.5D0*RCL
    2   CONTINUE
        FB=(1.0D0+ARCL)*RAND(4.0D0)
        IF(FB.LT.1.0D0) THEN
          RK=RCL/(1.0D0-FB*(1.0D0-(RCL+RCL)))
        ELSE
          RK=RCL+(FB-1.0D0)*(0.5D0-RCL)/ARCL
        ENDIF
        RK2=RK*RK
        RKF=RK/(1.0D0-RK)
        PHI=1.0D0+RKF**2-RKF+AMOL*(RK2+RKF)
        IF(RAND(5.0D0)*(1.0D0+A*RK2).GT.PHI) GO TO 2
C  ****  Energy and scattering angle (primary electron).
        DE=RK*EE
        EP=E-DE
        CDT=SQRT(EP*RB/(E*(RB-DE)))
C  ****  Energy and emission angle of the delta ray.
        IF(KS(M,IOSC).LT.10) THEN
          IF(UK.GT.ECUTR(M)) THEN
            ES=DE-UK  ! Inner shells only.
          ELSE
            ES=DE
          ENDIF
        ELSE
          ES=DE
        ENDIF
        CDTS=SQRT(DE*RB/(E*(DE+TREV)))
        RETURN
      ENDIF
C
C  ****  Hard distant longitudinal interaction.
C
      TS1=TS1+XHDL
      IF(UK.GT.1.0D-3) THEN
        DE=WM-SQRT((WM-WTHR)**2-RAND(7.0D0)*(WDMAX-WTHR)
     1    *(WM+WM-WDMAX-WTHR))
      ELSE
        DE=WKP
      ENDIF
      EP=E-DE
      IF(TST.LT.TS1) THEN
        QS=QM/(1.0D0+QM*RTREV)
        Q=QS/(((QS/QKP)*(1.0D0+QKP*RTREV))**RAND(6.0D0)-(QS*RTREV))
        QTREV=Q*(Q+TREV)
        CDT=(CPPS+CPS-QTREV)/(2.0D0*CP*CPP)
        IF(CDT.GT.1.0D0) CDT=1.0D0
C  ****  Energy and emission angle of the delta ray.
        IF(KS(M,IOSC).LT.10) THEN
          ES=DE-UK  ! Inner shells only.
        ELSE
          ES=DE
        ENDIF
        CDTS=0.5D0*(WKP*(E+RB-WKP)+QTREV)/SQRT(CPS*QTREV)
        IF(CDTS.GT.1.0D0) CDTS=1.0D0
        RETURN
      ENDIF
C
C  ****  Hard distant transverse interaction.
C
      CDT=1.0D0
C  ****  Energy and emission angle of the delta ray.
      IF(KS(M,IOSC).LT.10) THEN
        IF(UK.GT.ECUTR(M)) THEN
          ES=DE-UK  ! Inner shells only.
        ELSE
          ES=DE
        ENDIF
      ELSE
        ES=DE
      ENDIF
      CDTS=1.0D0
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE EINaT
C  *********************************************************************
      SUBROUTINE EINaT(E,WCC,XH0,XH1,XH2,XS0,XS1,XS2,XT1,XT2,DELTA,M)
C
C  Integrated cross sections for inelastic collisions of electrons of
C  energy E in material M, restricted to energy losses larger than and
C  less than the cutoff energy WCC.
C
C  Sternheimer-Liljequist GOS model.
C
C  Output arguments:
C    XH0 ... total cross section for hard colls. (cm**2).
C    XH1 ... stopping cross section for hard colls. (eV*cm**2).
C    XH2 ... straggling cross section for hard colls. (eV**2*cm**2).
C    XS0 ... total cross section for soft colls. (cm**2).
C    XS1 ... stopping cross section for soft colls. (eV*cm**2)
C    XS2 ... straggling cross section for soft colls. (eV**2*cm**2).
C    XT1 ... 1st transport cross section for soft colls. (cm**2).
C    XT2 ... 2nd transport cross section for soft colls. (cm**2).
C    DELTA ... Fermi's density effect correction.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (ELRAD=2.817940325D-13)  ! Class. electron radius (cm)
      PARAMETER (PI=3.1415926535897932D0, TREV=2.0D0*REV,
     1  PIELR2=PI*ELRAD*ELRAD)
      PARAMETER (MAXMAT=10)
C  ****  Composition data.
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****  E/P inelastic collisions.
      PARAMETER (NO=128)
      COMMON/CEIN/EXPOT(MAXMAT),OP2(MAXMAT),F(MAXMAT,NO),UI(MAXMAT,NO),
     1  WRI(MAXMAT,NO),KZ(MAXMAT,NO),KS(MAXMAT,NO),NOSC(MAXMAT)
C  ****  Partial cross sections of individual shells/oscillators.
      COMMON/CEIN00/SXH0(NO),SXH1(NO),SXH2(NO),SXS0(NO),SXS1(NO),
     1              SXS2(NO),SXT0(NO),SXT1(NO),SXT2(NO)
C
C  ****  Constants.
C
      GAM=1.0D0+E/REV
      GAM2=GAM*GAM
C
C  ************  Density effect.
C
C  ****  Sternheimer's resonance energy (WL2=L**2).
      TST=ZT(M)/(GAM2*OP2(M))
      WL2=0.0D0
      FDEL=0.0D0
      DO I=1,NOSC(M)
        FDEL=FDEL+F(M,I)/(WRI(M,I)**2+WL2)
      ENDDO
      IF(FDEL.LT.TST) THEN
        DELTA=0.0D0
        GO TO 3
      ENDIF
      WL2=WRI(M,NOSC(M))**2
    1 WL2=WL2+WL2
      FDEL=0.0D0
      DO I=1,NOSC(M)
        FDEL=FDEL+F(M,I)/(WRI(M,I)**2+WL2)
      ENDDO
      IF(FDEL.GT.TST) GO TO 1
      WL2L=0.0D0
      WL2U=WL2
    2 WL2=0.5D0*(WL2L+WL2U)
      FDEL=0.0D0
      DO I=1,NOSC(M)
        FDEL=FDEL+F(M,I)/(WRI(M,I)**2+WL2)
      ENDDO
      IF(FDEL.GT.TST) THEN
        WL2L=WL2
      ELSE
        WL2U=WL2
      ENDIF
      IF(WL2U-WL2L.GT.1.0D-12*WL2) GO TO 2
C  ****  Density effect correction (delta).
      DELTA=0.0D0
      DO I=1,NOSC(M)
        DELTA=DELTA+F(M,I)*LOG(1.0D0+WL2/WRI(M,I)**2)
      ENDDO
      DELTA=(DELTA/ZT(M))-WL2/(GAM2*OP2(M))
    3 CONTINUE
C
C  ****  Shell-oscillator cross sections.
C
      DO I=1,NOSC(M)
        SXH0(I)=0.0D0
        SXH1(I)=0.0D0
        SXH2(I)=0.0D0
        SXS0(I)=0.0D0
        SXS1(I)=0.0D0
        SXS2(I)=0.0D0
        SXT0(I)=0.0D0
        SXT1(I)=0.0D0
        SXT2(I)=0.0D0
      ENDDO
      XH0=0.0D0
      XH1=0.0D0
      XH2=0.0D0
      XS0=0.0D0
      XS1=0.0D0
      XS2=0.0D0
      XT0=0.0D0
      XT1=0.0D0
      XT2=0.0D0
C
      DO K=1,NOSC(M)
        UK=UI(M,K)
        WK=WRI(M,K)
        CALL EINaT1(E,UK,WK,DELTA,WCC,H0,H1,H2,S0,S1,S2,R0,R1,R2)
        SXH0(K)=F(M,K)*H0
        SXH1(K)=F(M,K)*H1
        SXH2(K)=F(M,K)*H2
        SXS0(K)=F(M,K)*S0
        SXS1(K)=F(M,K)*S1
        SXS2(K)=F(M,K)*S2
        SXT0(K)=F(M,K)*R0
        SXT1(K)=F(M,K)*2.0D0*R1
        SXT2(K)=F(M,K)*6.0D0*(R1-R2)
        XH0=XH0+SXH0(K)
        XH1=XH1+SXH1(K)
        XH2=XH2+SXH2(K)
        XS0=XS0+SXS0(K)
        XS1=XS1+SXS1(K)
        XS2=XS2+SXS2(K)
        XT0=XT0+SXT0(K)
        XT1=XT1+SXT1(K)
        XT2=XT2+SXT2(K)
      ENDDO
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE EINaT1
C  *********************************************************************
      SUBROUTINE EINaT1(E,UK,WK,DELTA,WCC,H0,H1,H2,S0,S1,S2,R0,R1,R2)
C
C  Integrated cross sections for inelastic collisions of electrons with
C  a single-shell oscillator, restricted to energy losses larger than,
C  and smaller than, the cutoff energy loss WCC.
C
C  Sternheimer-Liljequist oscillator model.
C
C  Input arguments:
C    E ..... kinetic energy (eV).
C    UK .... ionization energy (eV).
C    WK .... resonance energy (eV).
C    DELTA ... Fermi's density effect correction.
C    WCC ... cutoff energy loss (eV).
C
C  Output arguments:
C    H0 .... total cross section for hard colls. (cm**2).
C    H1 .... stopping cross section for hard colls. (eV*cm**2).
C    H2 .... straggling cross section for hard colls. (eV**2*cm**2).
C    S0 .... total cross section for soft colls. (cm**2).
C    S1 .... stopping cross section for soft colls. (eV*cm**2).
C    S2 .... straggling cross section for soft colls. (eV**2*cm**2).
C    R0 .... total cross section for soft colls. (cm**2).
C    R1 .... 1st transport cross section for soft colls. (cm**2).
C    R2 .... 2nd transport cross section for soft colls. (cm**2).
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Fundamental constants and related quantities.
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (ELRAD=2.817940325D-13)  ! Class. electron radius (cm)
      PARAMETER (TREV=2.0D0*REV,RTREV=1.0D0/TREV)
      PARAMETER (PI=3.1415926535897932D0,PIELR2=PI*ELRAD*ELRAD)
C
      COMMON/CEIN01/EI,EE,CPS,AMOL,MOM
      EXTERNAL EINaDS
C
      H0=0.0D0
      H1=0.0D0
      H2=0.0D0
      S0=0.0D0
      S1=0.0D0
      S2=0.0D0
      R0=0.0D0
      R1=0.0D0
      R2=0.0D0
C
      IF(UK.GT.1.0D-3) THEN
        WTHR=UK
      ELSE
        WTHR=WK
      ENDIF
      IF(E.LT.WTHR+1.0D-6) RETURN
C
C  ****  Constants.
C
      EI=E
      GAM=1.0D0+E/REV
      GAM2=GAM*GAM
      BETA2=(GAM2-1.0D0)/GAM2
      CONST=PIELR2*TREV/BETA2
C
      CPS=E*(E+TREV)
      CP=SQRT(CPS)
      AMOL=(E/(E+REV))**2
C
C  ****  Trick: The resonance energy and the cutoff recoil energy of
C        inner shells are varied to yield a smooth threshold.
C
      IF(UK.GT.1.0D-3) THEN
        WM=3.0D0*WK-2.0D0*UK
        IF(E.GT.WM) THEN
          WKP=WK
          QKP=UK
        ELSE
          WKP=(E+2.0D0*UK)/3.0D0
          QKP=UK*(E/WM)
          WM=E
        ENDIF
        EE=E+UK
        WCMAX=0.5D0*EE
        WDMAX=MIN(WM,WCMAX)
      ELSE
        WM=E
        WKP=WK
        QKP=WK
        EE=E
        WCMAX=0.5D0*EE
        WDMAX=WKP+1.0D0
      ENDIF
C
C  ****  Distant interactions.
C
      SDL1=0.0D0
      SDT1=0.0D0
      IF(WDMAX.GT.WTHR+1.0D-6) THEN
        CPPS=(E-WKP)*(E-WKP+TREV)
        CPP=SQRT(CPPS)
        A=4.0D0*CP*CPP
        B=(CP-CPP)**2
C
        IF(WKP.GT.1.0D-6*E) THEN
          QM=SQRT((CP-CPP)**2+REV**2)-REV
        ELSE
          QM=WKP*WKP/(BETA2*TREV)
          QM=QM*(1.0D0-QM*RTREV)
        ENDIF
        IF(QM.LT.QKP) THEN
          SDL1=LOG(QKP*(QM+TREV)/(QM*(QKP+TREV)))
          SDT1=MAX(LOG(GAM2)-BETA2-DELTA,0.0D0)
C  ****  Soft distant transport moments of orders 0-2.
          IF(WCC.GT.WTHR) THEN
            BA=B/A
            RMU1=(QKP*(QKP+TREV)-B)/A
            R0=LOG((RMU1+BA)/BA)
            R1=RMU1-BA*R0
            R2=BA**2*R0+0.5D0*RMU1*(RMU1-2.0D0*BA)
            R0=R0/WKP
            R1=R1/WKP
            R2=R2/WKP
            R0=R0+SDT1/WKP
          ENDIF
        ENDIF
      ENDIF
C
      SD1=SDL1+SDT1
      IF(SD1.GT.0.0D0) THEN
        IF(UK.GT.1.0D-3) THEN
C  ****  Inner-shell excitations (triangle distribution).
          F0=1.0D0/(WM-UK)**2
          F1=2.0D0*F0*SD1/WKP
          IF(WCC.LT.UK) THEN
            WL=UK
            WU=WDMAX
            H0=F1*(WM*(WU-WL)-(WU**2-WL**2)/2.0D0)
            H1=F1*(WM*(WU**2-WL**2)/2.0D0-(WU**3-WL**3)/3.0D0)
            H2=F1*(WM*(WU**3-WL**3)/3.0D0-(WU**4-WL**4)/4.0D0)
          ELSE
            IF(WCC.GT.WDMAX) THEN
              WL=UK
              WU=WDMAX
              S0=F1*(WM*(WU-WL)-(WU**2-WL**2)/2.0D0)
              S1=F1*(WM*(WU**2-WL**2)/2.0D0-(WU**3-WL**3)/3.0D0)
              S2=F1*(WM*(WU**3-WL**3)/3.0D0-(WU**4-WL**4)/4.0D0)
            ELSE
              WL=WCC
              WU=WDMAX
              H0=F1*(WM*(WU-WL)-(WU**2-WL**2)/2.0D0)
              H1=F1*(WM*(WU**2-WL**2)/2.0D0-(WU**3-WL**3)/3.0D0)
              H2=F1*(WM*(WU**3-WL**3)/3.0D0-(WU**4-WL**4)/4.0D0)
              WL=UK
              WU=WCC
              S0=F1*(WM*(WU-WL)-(WU**2-WL**2)/2.0D0)
              S1=F1*(WM*(WU**2-WL**2)/2.0D0-(WU**3-WL**3)/3.0D0)
              S2=F1*(WM*(WU**3-WL**3)/3.0D0-(WU**4-WL**4)/4.0D0)
            ENDIF
            F2=F0*(2.0D0*WM*(WU-WL)-(WU**2-WL**2))
            R0=F2*R0
            R1=F2*R1
            R2=F2*R2
          ENDIF
        ELSE
C  ****  Outer-shell excitations (delta oscillator).
          IF(WCC.LT.WKP) THEN
            H1=SD1
            H0=SD1/WKP
            H2=SD1*WKP
          ELSE
            S1=SD1
            S0=SD1/WKP
            S2=SD1*WKP
          ENDIF
        ENDIF
      ENDIF
C
C  ****  Close collisions (Moller's cross section).
C
      IF(WCMAX.LT.WTHR+1.0D-6) GO TO 1
      IF(WCC.LT.WTHR) THEN  ! No soft interactions.
        WL=WTHR
        WU=WCMAX
        H0=H0+(1.0D0/(EE-WU))-(1.0D0/(EE-WL))
     1    -(1.0D0/WU)+(1.0D0/WL)
     2    +(1.0D0-AMOL)*LOG(((EE-WU)*WL)/((EE-WL)*WU))/EE
     3    +AMOL*(WU-WL)/EE**2
        H1=H1+LOG(WU/WL)+(EE/(EE-WU))-(EE/(EE-WL))
     1    +(2.0D0-AMOL)*LOG((EE-WU)/(EE-WL))
     2    +AMOL*(WU**2-WL**2)/(2.0D0*EE**2)
        H2=H2+(2.0D0-AMOL)*(WU-WL)+(WU*(2.0D0*EE-WU)/(EE-WU))
     1    -(WL*(2.0D0*EE-WL)/(EE-WL))
     2    +(3.0D0-AMOL)*EE*LOG((EE-WU)/(EE-WL))
     3    +AMOL*(WU**3-WL**3)/(3.0D0*EE**2)
      ELSE
        IF(WCC.GT.WCMAX) THEN
          WL=WTHR
          WU=WCMAX
          S0=S0+(1.0D0/(EE-WU))-(1.0D0/(EE-WL))
     1      -(1.0D0/WU)+(1.0D0/WL)
     2      +(1.0D0-AMOL)*LOG(((EE-WU)*WL)/((EE-WL)*WU))/EE
     3      +AMOL*(WU-WL)/EE**2
          S1=S1+LOG(WU/WL)+(EE/(EE-WU))-(EE/(EE-WL))
     1      +(2.0D0-AMOL)*LOG((EE-WU)/(EE-WL))
     2      +AMOL*(WU**2-WL**2)/(2.0D0*EE**2)
          S2=S2+(2.0D0-AMOL)*(WU-WL)+(WU*(2.0D0*EE-WU)/(EE-WU))
     1      -(WL*(2.0D0*EE-WL)/(EE-WL))
     2      +(3.0D0-AMOL)*EE*LOG((EE-WU)/(EE-WL))
     3      +AMOL*(WU**3-WL**3)/(3.0D0*EE**2)
        ELSE
          WL=WCC
          WU=WCMAX
          H0=H0+(1.0D0/(EE-WU))-(1.0D0/(EE-WL))
     1      -(1.0D0/WU)+(1.0D0/WL)
     2      +(1.0D0-AMOL)*LOG(((EE-WU)*WL)/((EE-WL)*WU))/EE
     3      +AMOL*(WU-WL)/EE**2
          H1=H1+LOG(WU/WL)+(EE/(EE-WU))-(EE/(EE-WL))
     1      +(2.0D0-AMOL)*LOG((EE-WU)/(EE-WL))
     2      +AMOL*(WU**2-WL**2)/(2.0D0*EE**2)
          H2=H2+(2.0D0-AMOL)*(WU-WL)+(WU*(2.0D0*EE-WU)/(EE-WU))
     1      -(WL*(2.0D0*EE-WL)/(EE-WL))
     2      +(3.0D0-AMOL)*EE*LOG((EE-WU)/(EE-WL))
     3      +AMOL*(WU**3-WL**3)/(3.0D0*EE**2)
          WL=WTHR
          WU=WCC
          S0=S0+(1.0D0/(EE-WU))-(1.0D0/(EE-WL))
     1      -(1.0D0/WU)+(1.0D0/WL)
     2      +(1.0D0-AMOL)*LOG(((EE-WU)*WL)/((EE-WL)*WU))/EE
     3      +AMOL*(WU-WL)/EE**2
          S1=S1+LOG(WU/WL)+(EE/(EE-WU))-(EE/(EE-WL))
     1      +(2.0D0-AMOL)*LOG((EE-WU)/(EE-WL))
     2      +AMOL*(WU**2-WL**2)/(2.0D0*EE**2)
          S2=S2+(2.0D0-AMOL)*(WU-WL)+(WU*(2.0D0*EE-WU)/(EE-WU))
     1      -(WL*(2.0D0*EE-WL)/(EE-WL))
     2      +(3.0D0-AMOL)*EE*LOG((EE-WU)/(EE-WL))
     3      +AMOL*(WU**3-WL**3)/(3.0D0*EE**2)
        ENDIF
C  ****  Soft close transport moments of orders 0-2.
        CP2S=(E-WL)*(E-WL+TREV)
        CP2=SQRT(CP2S)
        RMU2=(WL*(WL+TREV)-(CP-CP2)**2)/(4.0D0*CP*CP2)
        CP3S=(E-WU)*(E-WU+TREV)
        CP3=SQRT(CP3S)
        RMU3=(WU*(WU+TREV)-(CP-CP3)**2)/(4.0D0*CP*CP3)
        MOM=0
        R0=R0+SUMGA(EINaDS,RMU2,RMU3,1.0D-7)
        MOM=1
        R1=R1+SUMGA(EINaDS,RMU2,RMU3,1.0D-7)
        MOM=2
        R2=R2+SUMGA(EINaDS,RMU2,RMU3,1.0D-7)
      ENDIF
C
    1 CONTINUE
      H0=CONST*H0
      H1=CONST*H1
      H2=CONST*H2
      S0=CONST*S0
      S1=CONST*S1
      S2=CONST*S2
      R0=CONST*R0
      R1=CONST*R1
      R2=CONST*R2
C
      RETURN
      END
C  *********************************************************************
C                       FUNCTION EINaDS
C  *********************************************************************
      FUNCTION EINaDS(RMU)
C
C  Angular differential cross section for soft close inelastic colli-
C  sions of electrons.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
C  ****  Coefficients transferred from subroutine EINaT1.
      COMMON/CEIN01/EI,EE,CPS,AMOL,MOM
C
      AUX=2.0D0*RMU*(1.0D0-RMU)
      DEN=EI*AUX+REV
      W=CPS*AUX/DEN
      DWDMU=CPS*REV*(2.0D0-4.0D0*RMU)/DEN**2
      EINaDS=(1.0D0+(W/(EE-W))**2-(1.0D0-AMOL)*(W/(EE-W))
     1      +AMOL*(W/EE)**2)*DWDMU*RMU**MOM/W**2
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PINa
C  *********************************************************************
      SUBROUTINE PINa(E,DELTA,DE,EP,CDT,ES,CDTS,M,IOSC)
C
C  Random sampling of hard inelastic collisions of positrons.
C
C  Sternheimer-Liljequist GOS model
C
C  Input arguments:
C    E ....... positron energy (eV).
C    M ....... material where positrons propagate.
C    DELTA ... Fermi's density effect correction.
C  Output arguments:
C    DE ...... energy loss (eV).
C    EP ...... energy of the scattered positron (eV).
C    CDT ..... cosine of the polar scattering angle.
C    ES ...... energy of the emitted secondary electron (eV).
C    CDTS .... polar cosine of direction of the secondary electron.
C    IOSC .... index of the oscillator that has been 'ionised'.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      LOGICAL LDIST
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (RREV=1.0D0/REV,TREV=2.0D0*REV,RTREV=1.0D0/TREV)
C  ****  Simulation parameters.
      PARAMETER (MAXMAT=10)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
      COMMON/CECUTR/ECUTR(MAXMAT)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  E/P inelastic collisions.
      PARAMETER (NO=128)
      COMMON/CEIN/EXPOT(MAXMAT),OP2(MAXMAT),F(MAXMAT,NO),UI(MAXMAT,NO),
     1  WRI(MAXMAT,NO),KZ(MAXMAT,NO),KS(MAXMAT,NO),NOSC(MAXMAT)
      COMMON/CEINAC/EINAC(MAXMAT,NEGP,NO),PINAC(MAXMAT,NEGP,NO)
C
      EXTERNAL RAND
C
      WCCM=WCC(M)
      IF(WCCM.GT.E) THEN
        DE=0.0D0
        EP=E
        CDT=1.0D0
        ES=0.0D0
        CDTS=0.0D0
        IOSC=NO
        RETURN
      ENDIF
C  ****  Energy grid point.
      PK=(XEL-DLEMP(KE))*DLFC
      IF(RAND(1.0D0).LT.PK) THEN
        JE=KE+1
      ELSE
        JE=KE
      ENDIF
C
C  ************  Selection of the active oscillator.
C
      TST=RAND(2.0D0)
C  ****  Binary search.
      IOSC=1
      JO=NOSC(M)+1
    1 IT=(IOSC+JO)/2
      IF(TST.GT.PINAC(M,JE,IT)) THEN
        IOSC=IT
      ELSE
        JO=IT
      ENDIF
      IF(JO-IOSC.GT.1) GO TO 1
C
      UK=UI(M,IOSC)
      WK=WRI(M,IOSC)
      IF(UK.GT.1.0D-3) THEN
        WTHR=MAX(WCCM,UK)
      ELSE
        WTHR=MAX(WCCM,WK)
      ENDIF
C
      IF(E.LT.WTHR+1.0D-6) THEN
        DE=0.0D0
        EP=E
        CDT=1.0D0
        ES=0.0D0
        CDTS=0.0D0
        IOSC=NO
        RETURN
      ENDIF
C
C  ****  Trick: The resonance energy and the cutoff recoil energy of
C        inner shells are varied to yield a smooth threshold.
C
      LDIST=.TRUE.
      IF(UK.GT.1.0D-3) THEN
        WM=3.0D0*WK-2.0D0*UK
        IF(E.GT.WM) THEN
          WKP=WK
          QKP=UK
        ELSE
          WKP=(E+2.0D0*UK)/3.0D0
          QKP=UK*(E/WM)
          WM=E
        ENDIF
        IF(WCCM.GT.WM) LDIST=.FALSE.
        WCMAX=E
        WDMAX=MIN(WM,WCMAX)
        IF(WTHR.GT.WDMAX) LDIST=.FALSE.
      ELSE
        IF(WCCM.GT.WK) LDIST=.FALSE.
        WKP=WK
        QKP=WK
        WM=E
        WCMAX=E
        WDMAX=WKP+1.0D0
      ENDIF
C
C  ****  Constants.
C
      RB=E+TREV
      GAM=1.0D0+E*RREV
      GAM2=GAM*GAM
      BETA2=(GAM2-1.0D0)/GAM2
      G12=(GAM+1.0D0)**2
      AMOL=((GAM-1.0D0)/GAM)**2
      BHA1=AMOL*(2.0D0*G12-1.0D0)/(GAM2-1.0D0)
      BHA2=AMOL*(3.0D0+1.0D0/G12)
      BHA3=AMOL*2.0D0*GAM*(GAM-1.0D0)/G12
      BHA4=AMOL*(GAM-1.0D0)**2/G12
      CPS=E*RB
      CP=SQRT(CPS)
C
C  ************  Partial cross sections of the active oscillator.
C
C  ****  Distant excitations.
      IF(LDIST) THEN
        CPPS=(E-WKP)*(E-WKP+TREV)
        CPP=SQRT(CPPS)
        IF(WKP.GT.1.0D-6*E) THEN
          QM=SQRT((CP-CPP)**2+REV*REV)-REV
        ELSE
          QM=WKP**2/(BETA2*TREV)
          QM=QM*(1.0D0-QM*RTREV)
        ENDIF
        IF(QM.LT.QKP) THEN
          RWKP=1.0D0/WKP
          XHDL=LOG(QKP*(QM+TREV)/(QM*(QKP+TREV)))*RWKP
          XHDT=MAX(LOG(GAM2)-BETA2-DELTA,0.0D0)*RWKP
          IF(UK.GT.1.0D-3) THEN
            F0=(WDMAX-WTHR)*(WM+WM-WDMAX-WTHR)/(WM-UK)**2
            XHDL=F0*XHDL
            XHDT=F0*XHDT
          ENDIF
        ELSE
          XHDL=0.0D0
          XHDT=0.0D0
        ENDIF
      ELSE
        QM=0.0D0    ! Defined to avoid compilation warnings.
        CPP=0.0D0   ! Defined to avoid compilation warnings.
        CPPS=0.0D0  ! Defined to avoid compilation warnings.
        XHDL=0.0D0
        XHDT=0.0D0
      ENDIF
C  ****  Close collisions.
      RCL=WTHR/E
      RL1=1.0D0-RCL
      XHC=((1.0D0/RCL-1.0D0)+BHA1*LOG(RCL)+BHA2*RL1
     1     +(BHA3/2.0D0)*(RCL**2-1.0D0)+(BHA4/3.0D0)*(1.0D0-RCL**3))/E
C
      XHTOT=XHC+XHDL+XHDT
      IF(XHTOT.LT.1.0D-35) THEN
        DE=0.0D0
        EP=E
        CDT=1.0D0
        ES=0.0D0
        CDTS=0.0D0
        IOSC=NO
        RETURN
      ENDIF
C
C  ************  Sampling of final-state variables.
C
      TST=RAND(3.0D0)*XHTOT
C
C  ****  Hard close collision.
C
      TS1=XHC
      IF(TST.LT.TS1) THEN
    2   CONTINUE
        RK=RCL/(1.0D0-RAND(4.0D0)*RL1)
        PHI=1.0D0-RK*(BHA1-RK*(BHA2-RK*(BHA3-BHA4*RK)))
        IF(RAND(5.0D0).GT.PHI) GO TO 2
C  ****  Energy and scattering angle (primary positron).
        DE=RK*E
        EP=E-DE
        CDT=SQRT(EP*RB/(E*(RB-DE)))
C  ****  Energy and emission angle of the delta ray.
        IF(KS(M,IOSC).LT.10) THEN
          IF(UK.GT.ECUTR(M)) THEN
            ES=DE-UK  ! Inner shells only.
          ELSE
            ES=DE
          ENDIF
        ELSE
          ES=DE
        ENDIF
        CDTS=SQRT(DE*RB/(E*(DE+TREV)))
        RETURN
      ENDIF
C
C  ****  Hard distant longitudinal interaction.
C
      TS1=TS1+XHDL
      IF(UK.GT.1.0D-3) THEN
        DE=WM-SQRT((WM-WTHR)**2-RAND(7.0D0)*(WDMAX-WTHR)
     1    *(WM+WM-WDMAX-WTHR))
      ELSE
        DE=WKP
      ENDIF
      EP=E-DE
      IF(TST.LT.TS1) THEN
        QS=QM/(1.0D0+QM*RTREV)
        Q=QS/(((QS/QKP)*(1.0D0+QKP*RTREV))**RAND(6.0D0)-(QS*RTREV))
        QTREV=Q*(Q+TREV)
        CDT=(CPPS+CPS-QTREV)/(2.0D0*CP*CPP)
        IF(CDT.GT.1.0D0) CDT=1.0D0
C  ****  Energy and emission angle of the delta ray.
        IF(KS(M,IOSC).LT.10) THEN
          ES=DE-UK  ! Inner shells only.
        ELSE
          ES=DE
        ENDIF
        CDTS=0.5D0*(WKP*(E+RB-WKP)+QTREV)/SQRT(CPS*QTREV)
        IF(CDTS.GT.1.0D0) CDTS=1.0D0
        RETURN
      ENDIF
C
C  ****  Hard distant transverse interaction.
C
      CDT=1.0D0
C  ****  Energy and emission angle of the delta ray.
      IF(KS(M,IOSC).LT.10) THEN
        IF(UK.GT.ECUTR(M)) THEN
          ES=DE-UK  ! Inner shells only.
        ELSE
          ES=DE
        ENDIF
      ELSE
        ES=DE
      ENDIF
      CDTS=1.0D0
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PINaT
C  *********************************************************************
      SUBROUTINE PINaT(E,WCC,XH0,XH1,XH2,XS0,XS1,XS2,XT1,XT2,DELTA,M)
C
C  Integrated cross sections for inelastic collisions of positrons of
C  energy E in material M, restricted to energy losses larger than and
C  less than the cutoff energy WCC.
C
C  Sternheimer-Liljequist GOS model.
C
C  Output arguments:
C    XH0 ... total cross section for hard colls. (cm**2).
C    XH1 ... stopping cross section for hard colls. (eV*cm**2).
C    XH2 ... straggling cross section for hard colls. (eV**2*cm**2).
C    XS0 ... total cross section for soft colls. (cm**2).
C    XS1 ... stopping cross section for soft colls. (eV*cm**2)
C    XS2 ... straggling cross section for soft colls. (eV**2*cm**2).
C    XT1 ... 1st transport cross section for soft colls. (cm**2).
C    XT2 ... 2nd transport cross section for soft colls. (cm**2).
C    DELTA ... Fermi's density effect correction.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (ELRAD=2.817940325D-13)  ! Class. electron radius (cm)
      PARAMETER (PI=3.1415926535897932D0, TREV=2.0D0*REV,
     1  PIELR2=PI*ELRAD*ELRAD)
      PARAMETER (MAXMAT=10)
C  ****  Composition data.
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****  E/P inelastic collisions.
      PARAMETER (NO=128)
      COMMON/CEIN/EXPOT(MAXMAT),OP2(MAXMAT),F(MAXMAT,NO),UI(MAXMAT,NO),
     1  WRI(MAXMAT,NO),KZ(MAXMAT,NO),KS(MAXMAT,NO),NOSC(MAXMAT)
C  ****  Partial cross sections of individual shells/oscillators.
      COMMON/CPIN00/SXH0(NO),SXH1(NO),SXH2(NO),SXS0(NO),SXS1(NO),
     1              SXS2(NO),SXT0(NO),SXT1(NO),SXT2(NO)
C
C  ****  Constants.
C
      GAM=1.0D0+E/REV
      GAM2=GAM*GAM
C
C  ************  Density effect.
C
C  ****  Sternheimer's resonance energy (WL2=L**2).
      TST=ZT(M)/(GAM2*OP2(M))
      WL2=0.0D0
      FDEL=0.0D0
      DO I=1,NOSC(M)
        FDEL=FDEL+F(M,I)/(WRI(M,I)**2+WL2)
      ENDDO
      IF(FDEL.LT.TST) THEN
        DELTA=0.0D0
        GO TO 3
      ENDIF
      WL2=WRI(M,NOSC(M))**2
    1 WL2=WL2+WL2
      FDEL=0.0D0
      DO I=1,NOSC(M)
        FDEL=FDEL+F(M,I)/(WRI(M,I)**2+WL2)
      ENDDO
      IF(FDEL.GT.TST) GO TO 1
      WL2L=0.0D0
      WL2U=WL2
    2 WL2=0.5D0*(WL2L+WL2U)
      FDEL=0.0D0
      DO I=1,NOSC(M)
        FDEL=FDEL+F(M,I)/(WRI(M,I)**2+WL2)
      ENDDO
      IF(FDEL.GT.TST) THEN
        WL2L=WL2
      ELSE
        WL2U=WL2
      ENDIF
      IF(WL2U-WL2L.GT.1.0D-12*WL2) GO TO 2
C  ****  Density effect correction (delta).
      DELTA=0.0D0
      DO I=1,NOSC(M)
        DELTA=DELTA+F(M,I)*LOG(1.0D0+WL2/WRI(M,I)**2)
      ENDDO
      DELTA=(DELTA/ZT(M))-WL2/(GAM2*OP2(M))
    3 CONTINUE
C
C  ****  Shell-oscillator cross sections.
C
      DO I=1,NOSC(M)
        SXH0(I)=0.0D0
        SXH1(I)=0.0D0
        SXH2(I)=0.0D0
        SXS0(I)=0.0D0
        SXS1(I)=0.0D0
        SXS2(I)=0.0D0
        SXT0(I)=0.0D0
        SXT1(I)=0.0D0
        SXT2(I)=0.0D0
      ENDDO
      XH0=0.0D0
      XH1=0.0D0
      XH2=0.0D0
      XS0=0.0D0
      XS1=0.0D0
      XS2=0.0D0
      XT0=0.0D0
      XT1=0.0D0
      XT2=0.0D0
C
      DO K=1,NOSC(M)
        UK=UI(M,K)
        WK=WRI(M,K)
        CALL PINaT1(E,UK,WK,DELTA,WCC,H0,H1,H2,S0,S1,S2,R0,R1,R2)
        SXH0(K)=F(M,K)*H0
        SXH1(K)=F(M,K)*H1
        SXH2(K)=F(M,K)*H2
        SXS0(K)=F(M,K)*S0
        SXS1(K)=F(M,K)*S1
        SXS2(K)=F(M,K)*S2
        SXT0(K)=F(M,K)*R0
        SXT1(K)=F(M,K)*2.0D0*R1
        SXT2(K)=F(M,K)*6.0D0*(R1-R2)
        XH0=XH0+SXH0(K)
        XH1=XH1+SXH1(K)
        XH2=XH2+SXH2(K)
        XS0=XS0+SXS0(K)
        XS1=XS1+SXS1(K)
        XS2=XS2+SXS2(K)
        XT0=XT0+SXT0(K)
        XT1=XT1+SXT1(K)
        XT2=XT2+SXT2(K)
      ENDDO
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PINaT1
C  *********************************************************************
      SUBROUTINE PINaT1(E,UK,WK,DELTA,WCC,H0,H1,H2,S0,S1,S2,R0,R1,R2)
C
C  Integrated cross sections for inelastic collisions of positrons with
C  a single-shell oscillator, restricted to energy losses larger than,
C  and smaller than, the cutoff energy loss WCC.
C
C  Sternheimer-Liljequist oscillator model.
C
C  Input arguments:
C    E ..... kinetic energy (eV).
C    UK .... ionization energy (eV).
C    WK .... resonance energy (eV).
C    DELTA ... Fermi's density effect correction.
C    WCC ... cutoff energy loss (eV).
C
C  Output arguments:
C    H0 .... total cross section for hard colls. (cm**2).
C    H1 .... stopping cross section for hard colls. (eV*cm**2).
C    H2 .... straggling cross section for hard colls. (eV**2*cm**2).
C    S0 .... total cross section for soft colls. (cm**2).
C    S1 .... stopping cross section for soft colls. (eV*cm**2).
C    S2 .... straggling cross section for soft colls. (eV**2*cm**2).
C    R0 .... total cross section for soft colls. (cm**2).
C    R1 .... 1st transport cross section for soft colls. (cm**2).
C    R2 .... 2nd transport cross section for soft colls. (cm**2).
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Fundamental constants and related quantities.
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (ELRAD=2.817940325D-13)  ! Class. electron radius (cm)
      PARAMETER (TREV=2.0D0*REV,RTREV=1.0D0/TREV)
      PARAMETER (PI=3.1415926535897932D0,PIELR2=PI*ELRAD*ELRAD)
C
      COMMON/CPIN01/EI,CPS,BHA1,BHA2,BHA3,BHA4,MOM
      EXTERNAL PINaDS
C
      H0=0.0D0
      H1=0.0D0
      H2=0.0D0
      S0=0.0D0
      S1=0.0D0
      S2=0.0D0
      R0=0.0D0
      R1=0.0D0
      R2=0.0D0
C
      IF(UK.GT.1.0D-3) THEN
        WTHR=UK
      ELSE
        WTHR=WK
      ENDIF
      IF(E.LT.WTHR+1.0D-6) RETURN
C
C  ****  Constants.
C
      EI=E
      GAM=1.0D0+E/REV
      GAM2=GAM*GAM
      BETA2=(GAM2-1.0D0)/GAM2
      CONST=PIELR2*TREV/BETA2
C
      CPS=E*(E+TREV)
      CP=SQRT(CPS)
      AMOL=(E/(E+REV))**2
      G12=(GAM+1.0D0)**2
      BHA1=AMOL*(2.0D0*G12-1.0D0)/(GAM2-1.0D0)
      BHA2=AMOL*(3.0D0+1.0D0/G12)
      BHA3=AMOL*2.0D0*GAM*(GAM-1.0D0)/G12
      BHA4=AMOL*(GAM-1.0D0)**2/G12
C
C  ****  Trick: The resonance energy and the cutoff recoil energy of
C        inner shells are varied to yield a smooth threshold.
C
      IF(UK.GT.1.0D-3) THEN
        WM=3.0D0*WK-2.0D0*UK
        IF(E.GT.WM) THEN
          WKP=WK
          QKP=UK
        ELSE
          WKP=(E+2.0D0*UK)/3.0D0
          QKP=UK*(E/WM)
          WM=E
        ENDIF
        WCMAX=E
        WDMAX=MIN(WM,WCMAX)
      ELSE
        WM=E
        WKP=WK
        QKP=WK
        EE=E
        WCMAX=E
        WDMAX=WKP+1.0D0
      ENDIF
C
C  ****  Distant interactions.
C
      SDL1=0.0D0
      SDT1=0.0D0
      IF(WDMAX.GT.WTHR+1.0D-6) THEN
        CPPS=(E-WKP)*(E-WKP+TREV)
        CPP=SQRT(CPPS)
        A=4.0D0*CP*CPP
        B=(CP-CPP)**2
C
        IF(WKP.GT.1.0D-6*E) THEN
          QM=SQRT((CP-CPP)**2+REV**2)-REV
        ELSE
          QM=WKP*WKP/(BETA2*TREV)
          QM=QM*(1.0D0-QM*RTREV)
        ENDIF
        IF(QM.LT.QKP) THEN
          SDL1=LOG(QKP*(QM+TREV)/(QM*(QKP+TREV)))
          SDT1=MAX(LOG(GAM2)-BETA2-DELTA,0.0D0)
C  ****  Soft distant transport moments of orders 0-2.
          IF(WCC.GT.WTHR) THEN
            BA=B/A
            RMU1=(QKP*(QKP+TREV)-B)/A
            R0=LOG((RMU1+BA)/BA)
            R1=RMU1-BA*R0
            R2=BA**2*R0+0.5D0*RMU1*(RMU1-2.0D0*BA)
            R0=R0/WKP
            R1=R1/WKP
            R2=R2/WKP
            R0=R0+SDT1/WKP
          ENDIF
        ENDIF
      ENDIF
C
      SD1=SDL1+SDT1
      IF(SD1.GT.0.0D0) THEN
        IF(UK.GT.1.0D-3) THEN
C  ****  Inner-shell excitations (triangle distribution).
          F0=1.0D0/(WM-UK)**2
          F1=2.0D0*F0*SD1/WKP
          IF(WCC.LT.UK) THEN
            WL=UK
            WU=WDMAX
            H0=F1*(WM*(WU-WL)-(WU**2-WL**2)/2.0D0)
            H1=F1*(WM*(WU**2-WL**2)/2.0D0-(WU**3-WL**3)/3.0D0)
            H2=F1*(WM*(WU**3-WL**3)/3.0D0-(WU**4-WL**4)/4.0D0)
          ELSE
            IF(WCC.GT.WDMAX) THEN
              WL=UK
              WU=WDMAX
              S0=F1*(WM*(WU-WL)-(WU**2-WL**2)/2.0D0)
              S1=F1*(WM*(WU**2-WL**2)/2.0D0-(WU**3-WL**3)/3.0D0)
              S2=F1*(WM*(WU**3-WL**3)/3.0D0-(WU**4-WL**4)/4.0D0)
            ELSE
              WL=WCC
              WU=WDMAX
              H0=F1*(WM*(WU-WL)-(WU**2-WL**2)/2.0D0)
              H1=F1*(WM*(WU**2-WL**2)/2.0D0-(WU**3-WL**3)/3.0D0)
              H2=F1*(WM*(WU**3-WL**3)/3.0D0-(WU**4-WL**4)/4.0D0)
              WL=UK
              WU=WCC
              S0=F1*(WM*(WU-WL)-(WU**2-WL**2)/2.0D0)
              S1=F1*(WM*(WU**2-WL**2)/2.0D0-(WU**3-WL**3)/3.0D0)
              S2=F1*(WM*(WU**3-WL**3)/3.0D0-(WU**4-WL**4)/4.0D0)
            ENDIF
            F2=F0*(2.0D0*WM*(WU-WL)-(WU**2-WL**2))
            R0=F2*R0
            R1=F2*R1
            R2=F2*R2
          ENDIF
        ELSE
C  ****  Outer-shell excitations (delta oscillator).
          IF(WCC.LT.WKP) THEN
            H1=SD1
            H0=SD1/WKP
            H2=SD1*WKP
          ELSE
            S1=SD1
            S0=SD1/WKP
            S2=SD1*WKP
          ENDIF
        ENDIF
      ENDIF
C
C  ****  Close collisions (Bhabha's cross section).
C
      IF(WCMAX.LT.WTHR+1.0D-6) GO TO 1
      IF(WCC.LT.WTHR) THEN  ! No soft interactions.
        WL=WTHR
        WU=WCMAX
        H0=H0+(1.0D0/WL)-(1.0D0/WU)-BHA1*LOG(WU/WL)/E
     1    +BHA2*(WU-WL)/E**2-BHA3*(WU**2-WL**2)/(2.0D0*E**3)
     2    +BHA4*(WU**3-WL**3)/(3.0D0*E**4)
        H1=H1+LOG(WU/WL)-BHA1*(WU-WL)/E
     1    +BHA2*(WU**2-WL**2)/(2.0D0*E**2)
     2    -BHA3*(WU**3-WL**3)/(3.0D0*E**3)
     3    +BHA4*(WU**4-WL**4)/(4.0D0*E**4)
        H2=H2+WU-WL-BHA1*(WU**2-WL**2)/(2.0D0*E)
     1    +BHA2*(WU**3-WL**3)/(3.0D0*E**2)
     2    -BHA3*(WU**4-WL**4)/(4.0D0*E**3)
     3    +BHA4*(WU**5-WL**5)/(5.0D0*E**4)
      ELSE
        IF(WCC.GT.WCMAX) THEN
          WL=WTHR
          WU=WCMAX
          S0=S0+(1.0D0/WL)-(1.0D0/WU)-BHA1*LOG(WU/WL)/E
     1      +BHA2*(WU-WL)/E**2-BHA3*(WU**2-WL**2)/(2.0D0*E**3)
     2      +BHA4*(WU**3-WL**3)/(3.0D0*E**4)
          S1=S1+LOG(WU/WL)-BHA1*(WU-WL)/E
     1      +BHA2*(WU**2-WL**2)/(2.0D0*E**2)
     2      -BHA3*(WU**3-WL**3)/(3.0D0*E**3)
     3      +BHA4*(WU**4-WL**4)/(4.0D0*E**4)
          S2=S2+WU-WL-BHA1*(WU**2-WL**2)/(2.0D0*E)
     1      +BHA2*(WU**3-WL**3)/(3.0D0*E**2)
     2      -BHA3*(WU**4-WL**4)/(4.0D0*E**3)
     3      +BHA4*(WU**5-WL**5)/(5.0D0*E**4)
        ELSE
          WL=WCC
          WU=WCMAX
          H0=H0+(1.0D0/WL)-(1.0D0/WU)-BHA1*LOG(WU/WL)/E
     1      +BHA2*(WU-WL)/E**2-BHA3*(WU**2-WL**2)/(2.0D0*E**3)
     2      +BHA4*(WU**3-WL**3)/(3.0D0*E**4)
          H1=H1+LOG(WU/WL)-BHA1*(WU-WL)/E
     1      +BHA2*(WU**2-WL**2)/(2.0D0*E**2)
     2      -BHA3*(WU**3-WL**3)/(3.0D0*E**3)
     3      +BHA4*(WU**4-WL**4)/(4.0D0*E**4)
          H2=H2+WU-WL-BHA1*(WU**2-WL**2)/(2.0D0*E)
     1      +BHA2*(WU**3-WL**3)/(3.0D0*E**2)
     2      -BHA3*(WU**4-WL**4)/(4.0D0*E**3)
     3      +BHA4*(WU**5-WL**5)/(5.0D0*E**4)
          WL=WTHR
          WU=WCC
          S0=S0+(1.0D0/WL)-(1.0D0/WU)-BHA1*LOG(WU/WL)/E
     1      +BHA2*(WU-WL)/E**2-BHA3*(WU**2-WL**2)/(2.0D0*E**3)
     2      +BHA4*(WU**3-WL**3)/(3.0D0*E**4)
          S1=S1+LOG(WU/WL)-BHA1*(WU-WL)/E
     1      +BHA2*(WU**2-WL**2)/(2.0D0*E**2)
     2      -BHA3*(WU**3-WL**3)/(3.0D0*E**3)
     3      +BHA4*(WU**4-WL**4)/(4.0D0*E**4)
          S2=S2+WU-WL-BHA1*(WU**2-WL**2)/(2.0D0*E)
     1      +BHA2*(WU**3-WL**3)/(3.0D0*E**2)
     2      -BHA3*(WU**4-WL**4)/(4.0D0*E**3)
     3      +BHA4*(WU**5-WL**5)/(5.0D0*E**4)
        ENDIF
C  ****  Soft close transport moments of orders 0-2.
        CP2S=(E-WL)*(E-WL+TREV)
        CP2=SQRT(CP2S)
        RMU2=(WL*(WL+TREV)-(CP-CP2)**2)/(4.0D0*CP*CP2)
        IF(WU.LT.E-1.0D0) THEN
          CP3S=(E-WU)*(E-WU+TREV)
          CP3=SQRT(CP3S)
          RMU3=(WU*(WU+TREV)-(CP-CP3)**2)/(4.0D0*CP*CP3)
        ELSE
          RMU3=0.5D0
        ENDIF
        MOM=0
        R0=R0+SUMGA(PINaDS,RMU2,RMU3,1.0D-7)
        MOM=1
        R1=R1+SUMGA(PINaDS,RMU2,RMU3,1.0D-7)
        MOM=2
        R2=R2+SUMGA(PINaDS,RMU2,RMU3,1.0D-7)
      ENDIF
C
    1 CONTINUE
      H0=CONST*H0
      H1=CONST*H1
      H2=CONST*H2
      S0=CONST*S0
      S1=CONST*S1
      S2=CONST*S2
      R0=CONST*R0
      R1=CONST*R1
      R2=CONST*R2
C
      RETURN
      END
C  *********************************************************************
C                       FUNCTION PINaDS
C  *********************************************************************
      FUNCTION PINaDS(RMU)
C
C  Angular differential cross section for soft close inelastic colli-
C  sions of positrons.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
C  ****  Coefficients transferred from subroutine PINaT1.
      COMMON/CPIN01/EI,CPS,BHA1,BHA2,BHA3,BHA4,MOM
C
      AUX=2.0D0*RMU*(1.0D0-RMU)
      DEN=EI*AUX+REV
      W=CPS*AUX/DEN
      DWDMU=CPS*REV*(2.0D0-4.0D0*RMU)/DEN**2
      WE=W/EI
      PINaDS=(1.0D0-WE*(BHA1-WE*(BHA2-WE*(BHA3-WE*BHA4))))
     1      *DWDMU*RMU**MOM/W**2
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE ESIa
C  *********************************************************************
      SUBROUTINE ESIa(IZZ,ISH)
C
C  Ionisation of inner shells by impact of electrons.
C
C  Output arguments:
C    IZZ .... atomic number of the element where ionisation has
C             occurred.
C    ISH .... atomic electron shell that has been ionised.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*2 LASYMB
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C  ****  Simulation parameters.
      PARAMETER (MAXMAT=10)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
      COMMON/CECUTR/ECUTR(MAXMAT)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Element data.
      COMMON/CADATA/ATW(99),EPX(99),RSCR(99),ETA(99),EB(99,30),
     1  IFI(99,30),IKS(99,30),NSHT(99),LASYMB(99)
C  ****  Composition data.
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****  Inner-shell ionisation by electron impact.
      PARAMETER (NRP=8000)
      COMMON/CESI0/XESI(NRP,16),IESIF(99),IESIL(99),NSESI(99),NCURE
      DIMENSION PACSI(120),IZSI(120),ISHSI(120)
C
      EXTERNAL RAND
C
      KT=1
      SEIST=0.0D0
      PACSI(1)=0.0D0
C
      DO J=1,NELEM(M)
        IZZ=IZ(M,J)
        INDC=IESIF(IZZ)-1
        DO ISH=1,NSESI(IZZ)
          WCUT=EB(IZZ,ISH)
          IF(WCUT.GT.ECUTR(M).AND.WCUT.LT.E) THEN
            PCSI=EXP(XESI(INDC+KE,ISH)
     1          +(XESI(INDC+KE+1,ISH)-XESI(INDC+KE,ISH))*XEK)
            IF(PCSI.GT.1.1D-35) THEN
              SEIST=SEIST+PCSI*STF(M,J)
              IZSI(KT)=IZZ
              ISHSI(KT)=ISH
              KT=KT+1
              PACSI(KT)=SEIST
            ENDIF
          ENDIF
        ENDDO
      ENDDO
C
      IF(KT.EQ.1) THEN
        IZZ=0
        ISH=0
        RETURN
      ENDIF
C
      TST=PACSI(KT)*RAND(1.0D0)
C  ****  Binary search.
      IS=1
      JS=KT
    1 IT=(IS+JS)/2
      IF(TST.GT.PACSI(IT)) IS=IT
      IF(TST.LE.PACSI(IT)) JS=IT
      IF(JS-IS.GT.1) GO TO 1
C
      IZZ=IZSI(IS)
      ISH=ISHSI(IS)
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE ESIaR
C  *********************************************************************
      SUBROUTINE ESIaR(M,IRD,IWR,INFO)
C
C  This subroutine reads cross sections for inner-shell ionisation by
C  electron impact of the elements in material M and prepares simulation
C  tables.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*2 LASYMB
      CHARACTER CS5(16)*5
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
      COMMON/CECUTR/ECUTR(MAXMAT)
C  ****  Element data.
      COMMON/CADATA/ATW(99),EPX(99),RSCR(99),ETA(99),EB(99,30),
     1  IFI(99,30),IKS(99,30),NSHT(99),LASYMB(99)
C  ****  Electron impact ionisation cross section tables.
      PARAMETER (NRP=8000)
      COMMON/CESI0/XESI(NRP,16),IESIF(99),IESIL(99),NSESI(99),NCURE
      PARAMETER (NDIM=850)
      DIMENSION E(NDIM),XESIR(NDIM,16),X(NDIM),Y(NDIM)
C
      CS5(1) ='CS-K '
      CS5(2) ='CS-L1'
      CS5(3) ='CS-L2'
      CS5(4) ='CS-L3'
      CS5(5) ='CS-M1'
      CS5(6) ='CS-M2'
      CS5(7) ='CS-M3'
      CS5(8) ='CS-M4'
      CS5(9) ='CS-M5'
      CS5(10)='CS-N1'
      CS5(11)='CS-N2'
      CS5(12)='CS-N3'
      CS5(13)='CS-N4'
      CS5(14)='CS-N5'
      CS5(15)='CS-N6'
      CS5(16)='CS-N7'
C
C  ************  Read element x-section tables
C
      DO IEL=1,NELEM(M)
        READ(IRD,1001) IZZ,NSHR,NDATA
 1001   FORMAT(47X,I3,11X,I3,10X,I4)
        IF(INFO.GE.2) WRITE(IWR,2001) IZZ,NSHR,NDATA
 2001   FORMAT(/1X,'***  Electron impact ionisation cross sections, ',
     1    ' IZ =',I3,',  NSHELL =',I3,',  NDATA =',I4)
        IF(IZZ.NE.IZ(M,IEL))
     1    CALL PISTOP('ESIaR. Corrupt material data file.')
        IF(NDATA.GT.NDIM) CALL PISTOP('ESIaR. Too many data points.')
        IF(NSHR.GT.16) CALL PISTOP('ESIaR. Too many shells.')
        DO IE=1,NDATA
          READ(IRD,*) E(IE),(XESIR(IE,IS),IS=1,NSHR)
        ENDDO
C
C  ****  Remove shells with ionisation energies less than 50 eV.
C
        IF(NSHR.GT.1) THEN
          NSHA=NSHR
          DO IS=NSHA,1,-1
            IF(EB(IZZ,IS).LT.50.0D0) THEN
              NSHR=NSHR-1
            ELSE
              GO TO 1
            ENDIF
          ENDDO
          IF(NSHR.LT.1) NSHR=1
        ENDIF
    1   CONTINUE
C
        IF(INFO.GE.2) THEN
          WRITE(IWR,'(/3X,''Energy'',7X,60(A,7X))') (CS5(Is),IS=1,NSHR)
          DO IE=1,NDATA
            WRITE(IWR,'(1P,20E12.5)') E(IE),(XESIR(IE,IS),IS=1,NSHR)
          ENDDO
        ENDIF
C
        NSESI(IZZ)=NSHR
        IF(IESIF(IZZ).EQ.0) THEN
          IESIF(IZZ)=NCURE+1
          IF(NCURE+NEGP.GT.NRP) THEN
            WRITE(IWR,*) 'Insufficient memory storage in ESIaR.'
            WRITE(IWR,*) 'Increase the value of the parameter NRP to',
     1        NCURE+NEGP
            WRITE(26,*) 'Insufficient memory storage in ESIaR.'
            WRITE(26,*) 'Increase the value of the parameter NRP to',
     1        NCURE+NEGP
            CALL PISTOP('ESIaR. Insufficient memory storage.')
          ENDIF
          DO IS=1,NSHR
            N=0
            DO I=1,NDATA
              IF(XESIR(I,IS).GT.1.0D-35) THEN
                N=N+1
                X(N)=LOG(E(I))
                IF(N.GT.1) X(N)=MAX(X(N),X(N-1)+1.0D-6)
                Y(N)=LOG(XESIR(I,IS))
              ENDIF
            ENDDO
            IF(N.GT.4) THEN
              DO I=1,NEGP
                IC=NCURE+I
                XC=DLEMP(I)
                IF(XC.GT.X(1)) THEN
                  CALL FINDI(X,XC,N,J)
                  IF(J.EQ.N) J=N-1
                  DX=X(J+1)-X(J)
                  IF(DX.GT.1.0D-6) THEN
                    XESI(IC,IS)=Y(J)+(XC-X(J))*(Y(J+1)-Y(J))/DX
                  ELSE
                    XESI(IC,IS)=(Y(J+1)+Y(J))/2.0D0
                  ENDIF
                ELSE
                  XESI(IC,IS)=-80.6D0
                ENDIF
              ENDDO
            ELSE
              DO I=1,NEGP
                IC=NCURE+I
                XESI(IC,IS)=-80.6D0
              ENDDO
            ENDIF
          ENDDO
          NCURE=NCURE+NEGP
          IESIL(IZZ)=NCURE
        ENDIF
      ENDDO
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE ESIa0
C  *********************************************************************
      SUBROUTINE ESIa0
C
C  This subroutine sets all variables in common /CESI0/ to zero.
C
C  It has to be invoked before reading the first material definition
C  file.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Ionisation cross section tables.
      PARAMETER (NRP=8000)
      COMMON/CESI0/XESI(NRP,16),IESIF(99),IESIL(99),NSESI(99),NCURE
C
      DO I=1,99
        IESIF(I)=0
        IESIL(I)=0
        NSESI(I)=0
      ENDDO
C
      DO I=1,NRP
        DO J=1,16
          XESI(I,J)=-80.6D0
        ENDDO
      ENDDO
      NCURE=0
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE ESIaW
C  *********************************************************************
      SUBROUTINE ESIaW(M,IWR)
C
C  This subroutine generates tables of cross sections for inner-shell
C  ionisation by electron impact for the elements in material M and
C  writes them on the material data file.
C
C  Data are read from the files 'pdesiZZ.p08'.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C
      CHARACTER*12 FILEN,LDUMMY
      CHARACTER*1 LDIG(10),LDIG1,LDIG2
      DATA LDIG/'0','1','2','3','4','5','6','7','8','9'/
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C
      PARAMETER (NES=850)
      DIMENSION E(NES),XESIR(NES,16)
C
      DO IEL=1,NELEM(M)
        IZZ=IZ(M,IEL)
        NLD=IZZ
        NLD1=NLD-10*(NLD/10)
        NLD2=(NLD-NLD1)/10
        LDIG1=LDIG(NLD1+1)
        LDIG2=LDIG(NLD2+1)
        FILEN='pdesi'//LDIG2//LDIG1//'.p11'
        OPEN(3,FILE='./pdfiles/'//FILEN)
        READ(3,'(16X,I2,6X,I2)') IZZZ,NSHR
        IF(IZZZ.NE.IZZ) CALL PISTOP('ESIaW. Corrupt data file.')
        IF(NSHR.GT.16) CALL PISTOP('ESIaW. Too many shells.')
        READ(3,'(A12)') LDUMMY
        READ(3,'(A12)') LDUMMY
        DO IE=1,NES
          READ(3,*,END=1) E(IE),(XESIR(IE,IS),IS=1,NSHR)
          NPTAB=IE
          IF(E(IE).GT.0.999D9) GO TO 1
        ENDDO
    1   CONTINUE
        CLOSE(3)
        WRITE(IWR,2001) IZZ,NSHR,NPTAB
 2001 FORMAT(1X,'***  Electron ionisation cross sections,  IZ =',I3,
     1  ',  NSHELL =',I3,',  NDATA =',I4)
        DO IE=1,NPTAB
          WRITE(IWR,2002) E(IE),(XESIR(IE,IS),IS=1,NSHR)
        ENDDO
 2002 FORMAT(1P,20E12.5)
      ENDDO
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PSIa
C  *********************************************************************
      SUBROUTINE PSIa(IZZ,ISH)
C
C  Ionisation of inner shells by impact of positrons.
C
C  Output arguments:
C    IZZ .... atomic number of the element where ionisation has
C             occurred.
C    ISH .... atomic electron shell that has been ionised.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*2 LASYMB
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C  ****  Simulation parameters.
      PARAMETER (MAXMAT=10)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
      COMMON/CECUTR/ECUTR(MAXMAT)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Element data.
      COMMON/CADATA/ATW(99),EPX(99),RSCR(99),ETA(99),EB(99,30),
     1  IFI(99,30),IKS(99,30),NSHT(99),LASYMB(99)
C  ****  Composition data.
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****  Inner-shell ionisation by positron impact.
      PARAMETER (NRP=8000)
      COMMON/CPSI0/XPSI(NRP,16),IPSIF(99),IPSIL(99),NSPSI(99),NCURP
      DIMENSION PACSI(120),IZSI(120),ISHSI(120)
C
      EXTERNAL RAND
C
      KT=1
      SPIST=0.0D0
      PACSI(1)=0.0D0
C
      DO J=1,NELEM(M)
        IZZ=IZ(M,J)
        INDC=IPSIF(IZZ)-1
        DO ISH=1,NSPSI(IZZ)
          WCUT=EB(IZZ,ISH)
          IF(WCUT.GT.ECUTR(M).AND.WCUT.LT.E) THEN
            PCSI=EXP(XPSI(INDC+KE,ISH)
     1          +(XPSI(INDC+KE+1,ISH)-XPSI(INDC+KE,ISH))*XEK)
            IF(PCSI.GT.1.1D-35) THEN
              SPIST=SPIST+PCSI*STF(M,J)
              IZSI(KT)=IZZ
              ISHSI(KT)=ISH
              KT=KT+1
              PACSI(KT)=SPIST
            ENDIF
          ENDIF
        ENDDO
      ENDDO
C
      IF(KT.EQ.1) THEN
        IZZ=0
        ISH=0
        RETURN
      ENDIF
C
      TST=PACSI(KT)*RAND(1.0D0)
C  ****  Binary search.
      IS=1
      JS=KT
    1 IT=(IS+JS)/2
      IF(TST.GT.PACSI(IT)) IS=IT
      IF(TST.LE.PACSI(IT)) JS=IT
      IF(JS-IS.GT.1) GO TO 1
C
      IZZ=IZSI(IS)
      ISH=ISHSI(IS)
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PSIaR
C  *********************************************************************
      SUBROUTINE PSIaR(M,IRD,IWR,INFO)
C
C  This subroutine reads cross sections for inner-shell ionisation by
C  positron impact of the elements in material M and prepares simulation
C  tables.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*2 LASYMB
      CHARACTER CS5(16)*5
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
      COMMON/CECUTR/ECUTR(MAXMAT)
C  ****  Element data.
      COMMON/CADATA/ATW(99),EPX(99),RSCR(99),ETA(99),EB(99,30),
     1  IFI(99,30),IKS(99,30),NSHT(99),LASYMB(99)
C  ****  Positron impact ionisation cross section tables.
      PARAMETER (NRP=8000)
      COMMON/CPSI0/XPSI(NRP,16),IPSIF(99),IPSIL(99),NSPSI(99),NCURP
      PARAMETER (NDIM=800)
      DIMENSION E(NDIM),XPSIR(NDIM,16),X(NDIM),Y(NDIM)
C
      CS5(1) ='CS-K '
      CS5(2) ='CS-L1'
      CS5(3) ='CS-L2'
      CS5(4) ='CS-L3'
      CS5(5) ='CS-M1'
      CS5(6) ='CS-M2'
      CS5(7) ='CS-M3'
      CS5(8) ='CS-M4'
      CS5(9) ='CS-M5'
      CS5(10)='CS-N1'
      CS5(11)='CS-N2'
      CS5(12)='CS-N3'
      CS5(13)='CS-N4'
      CS5(14)='CS-N5'
      CS5(15)='CS-N6'
      CS5(16)='CS-N7'
C
C  ************  Read element x-section tables
C
      DO IEL=1,NELEM(M)
        READ(IRD,1001) IZZ,NSHR,NDATA
 1001   FORMAT(47X,I3,11X,I3,10X,I4)
        IF(INFO.GE.2) WRITE(IWR,2001) IZZ,NSHR,NDATA
 2001   FORMAT(/1X,'***  Positron impact ionisation cross sections, ',
     1    ' IZ =',I3,',  NSHELL =',I3,',  NDATA =',I4)
        IF(IZZ.NE.IZ(M,IEL))
     1    CALL PISTOP('PSIaR. Corrupt material data file.')
        IF(NDATA.GT.NDIM) CALL PISTOP('PSIaR. Too many data points.')
        IF(NSHR.GT.16) CALL PISTOP('PSIaR. Too many shells.')
        DO IE=1,NDATA
          READ(IRD,*) E(IE),(XPSIR(IE,IS),IS=1,NSHR)
        ENDDO
C
C  ****  Remove shells with ionisation energies less than 50 eV.
C
        IF(NSHR.GT.1) THEN
          NSHA=NSHR
          DO IS=NSHA,1,-1
            IF(EB(IZZ,IS).LT.50.0D0) THEN
              NSHR=NSHR-1
            ELSE
              GO TO 1
            ENDIF
          ENDDO
          IF(NSHR.LT.1) NSHR=1
        ENDIF
    1   CONTINUE
C
        IF(INFO.GE.2) THEN
          WRITE(IWR,'(/3X,''Energy'',7X,60(A,7X))') (CS5(Is),IS=1,NSHR)
          DO IE=1,NDATA
            WRITE(IWR,'(1P,20E12.5)') E(IE),(XPSIR(IE,IS),IS=1,NSHR)
          ENDDO
        ENDIF
C
        NSPSI(IZZ)=NSHR
        IF(IPSIF(IZZ).EQ.0) THEN
          IPSIF(IZZ)=NCURP+1
          IF(NCURP+NEGP.GT.NRP) THEN
            WRITE(IWR,*) 'Insufficient memory storage in PSIaR.'
            WRITE(IWR,*) 'Increase the value of the parameter NRP to',
     1        NCURP+NEGP
            WRITE(26,*) 'Insufficient memory storage in PSIaR.'
            WRITE(26,*) 'Increase the value of the parameter NRP to',
     1        NCURP+NEGP
            CALL PISTOP('PSIaR. Insufficient memory storage.')
          ENDIF
          DO IS=1,NSHR
            N=0
            DO I=1,NDATA
              IF(XPSIR(I,IS).GT.1.0D-35) THEN
                N=N+1
                X(N)=LOG(E(I))
                IF(N.GT.1) X(N)=MAX(X(N),X(N-1)+1.0D-6)
                Y(N)=LOG(XPSIR(I,IS))
              ENDIF
            ENDDO
            IF(N.GT.4) THEN
              DO I=1,NEGP
                IC=NCURP+I
                XC=DLEMP(I)
                IF(XC.GT.X(1)) THEN
                  CALL FINDI(X,XC,N,J)
                  IF(J.EQ.N) J=N-1
                  DX=X(J+1)-X(J)
                  IF(DX.GT.1.0D-6) THEN
                    XPSI(IC,IS)=Y(J)+(XC-X(J))*(Y(J+1)-Y(J))/DX
                  ELSE
                    XPSI(IC,IS)=(Y(J+1)+Y(J))/2.0D0
                  ENDIF
                ELSE
                  XPSI(IC,IS)=-80.6D0
                ENDIF
              ENDDO
            ELSE
              DO I=1,NEGP
                IC=NCURP+I
                XPSI(IC,IS)=-80.6D0
              ENDDO
            ENDIF
          ENDDO
          NCURP=NCURP+NEGP
          IPSIL(IZZ)=NCURP
        ENDIF
      ENDDO
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PSIa0
C  *********************************************************************
      SUBROUTINE PSIa0
C
C  This subroutine sets all variables in common /CPSI0/ to zero.
C
C  It has to be invoked before reading the first material definition
C  file.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Ionisation cross section tables.
      PARAMETER (NRP=8000)
      COMMON/CPSI0/XPSI(NRP,16),IPSIF(99),IPSIL(99),NSPSI(99),NCURP
C
      DO I=1,99
        IPSIF(I)=0
        IPSIL(I)=0
        NSPSI(I)=0
      ENDDO
C
      DO I=1,NRP
        DO J=1,16
          XPSI(I,J)=-80.6D0
        ENDDO
      ENDDO
      NCURP=0
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PSIaW
C  *********************************************************************
      SUBROUTINE PSIaW(M,IWR)
C
C  This subroutine generates tables of cross sections for inner-shell
C  ionisation by positron impact for the elements in material M and
C  writes them on the material data file.
C
C  Data are read from the files 'pdpsiZZ.p08'.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C
      CHARACTER*12 FILEN,LDUMMY
      CHARACTER*1 LDIG(10),LDIG1,LDIG2
      DATA LDIG/'0','1','2','3','4','5','6','7','8','9'/
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C
      PARAMETER (NES=800)
      DIMENSION E(NES),XPSIR(NES,16)
C
      DO IEL=1,NELEM(M)
        IZZ=IZ(M,IEL)
        NLD=IZZ
        NLD1=NLD-10*(NLD/10)
        NLD2=(NLD-NLD1)/10
        LDIG1=LDIG(NLD1+1)
        LDIG2=LDIG(NLD2+1)
        FILEN='pdpsi'//LDIG2//LDIG1//'.p11'
        OPEN(3,FILE='./pdfiles/'//FILEN)
        READ(3,'(16X,I2,6X,I2)') IZZZ,NSHR
        IF(IZZZ.NE.IZZ) CALL PISTOP('PSIaW. Corrupt data file.')
        IF(NSHR.GT.16) CALL PISTOP('PSIaW. Too many shells.')
        READ(3,'(A12)') LDUMMY
        READ(3,'(A12)') LDUMMY
        DO IE=1,NES
          READ(3,*,END=1) E(IE),(XPSIR(IE,IS),IS=1,NSHR)
          NPTAB=IE
          IF(E(IE).GT.0.999D9) GO TO 1
        ENDDO
    1   CONTINUE
        CLOSE(3)
        WRITE(IWR,2001) IZZ,NSHR,NPTAB
 2001 FORMAT(1X,'***  Positron ionisation cross sections,  IZ =',I3,
     1  ',  NSHELL =',I3,',  NDATA =',I4)
        DO IE=1,NPTAB
          WRITE(IWR,2002) E(IE),(XPSIR(IE,IS),IS=1,NSHR)
        ENDDO
 2002 FORMAT(1P,20E12.5)
      ENDDO
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE EBRa
C  *********************************************************************
      SUBROUTINE EBRa(E,W,M)
C
C  Simulation of bremsstrahlung emission by electrons or positrons in
C  the material M.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Simulation parameters.
      PARAMETER (MAXMAT=10)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Bremsstrahlung emission.
      PARAMETER (NBW=32)
      COMMON/CEBR/WB(NBW),PBCUT(MAXMAT,NEGP),WBCUT(MAXMAT,NEGP),
     1  PDFB(MAXMAT,NEGP,NBW),DPDFB(MAXMAT,NEGP,NBW),
     2  PACB(MAXMAT,NEGP,NBW),ZBR2(MAXMAT)
C
      EXTERNAL RAND
C
      IF(WCR(M).GT.E) THEN
        W=0.0D0
        RETURN
      ENDIF
C
C  ****  Selection of the energy grid point.
C
      IF(RAND(1.0D0).LT.XEK) THEN
        IE=KE+1
      ELSE
        IE=KE
      ENDIF
C  ****  Pointer.
    1 CONTINUE
      PT=PBCUT(M,IE)+RAND(2.0D0)*(PACB(M,IE,NBW)-PBCUT(M,IE))
C  ****  Binary search of the W-interval.
      I=1
      J=NBW
    2 K=(I+J)/2
      IF(PT.GT.PACB(M,IE,K)) THEN
        I=K
      ELSE
        J=K
      ENDIF
      IF(J-I.GT.1) GO TO 2
C  ****  Sampling the photon energy (rejection method).
      W1=WB(I)
      W2=WB(I+1)
      DW=W2-W1
      B=DPDFB(M,IE,I)/DW
      A=PDFB(M,IE,I)-B*W1
      IF(W1.LT.WBCUT(M,IE)) W1=WBCUT(M,IE)
      IF(W2.LT.W1) THEN
        WRITE(26,*) ' **** WARNING: EBR. Conflicting end-point values.'
        W=W1
        RETURN
      ENDIF
      PMAX=MAX(A+B*W1,A+B*W2)
    3 CONTINUE
      W=W1*(W2/W1)**RAND(3.0D0)
      IF(RAND(4.0D0)*PMAX.GT.A+B*W) GO TO 3
      W=W*E
      IF(W.LT.WCR(M)) GO TO 1
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE EBRaR
C  *********************************************************************
      SUBROUTINE EBRaR(WCR,M,IRD,IWR,INFO)
C
C  This subroutine reads the bremss scaled cross section for electrons
C  in material M from the material data file. It computes restricted
C  integrated cross sections and initialises the algorithm for simula-
C  tion of bremss emission by electrons and positrons.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Physical constants (values adopted by Seltzer and Berger).
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (ELRAD=2.817940325D-13)  ! Class. electron radius (cm)
      PARAMETER (TREV=2.0D0*REV)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
      DIMENSION A(NEGP),B(NEGP),C(NEGP),D(NEGP),PAC(NEGP),PDF(NEGP)
C  ****  Bremsstrahlung emission.
      PARAMETER (MAXMAT=10)
      PARAMETER (NBE=57, NBW=32)
      COMMON/CEBR/WB(NBW),PBCUT(MAXMAT,NEGP),WBCUT(MAXMAT,NEGP),
     1  PDFB(MAXMAT,NEGP,NBW),DPDFB(MAXMAT,NEGP,NBW),
     2  PACB(MAXMAT,NEGP,NBW),ZBR2(MAXMAT)
      COMMON/CEBR01/EBT(NBE),XS(NBE,NBW),TXS(NBE),X(NBE),Y(NBE)
      COMMON/CEBR02/P0(MAXMAT,NEGP,NBW)
      DIMENSION WB0(NBW)
      DATA WB0/1.0D-12,0.025D0,0.05D0,0.075D0,0.1D0,0.15D0,0.2D0,0.25D0,
     1   0.3D0,0.35D0,0.4D0,0.45D0,0.5D0,0.55D0,0.6D0,0.65D0,0.7D0,
     2   0.75D0,0.8D0,0.85D0,0.9D0,0.925D0,0.95D0,0.97D0,0.99D0,
     3   0.995D0,0.999D0,0.9995D0,0.9999D0,0.99995D0,0.99999D0,1.0D0/
C
C  ****  Reading the scaled cross section table.
C
      READ(IRD,5001) ZBR,NBER
 5001 FORMAT(45X,E12.5,10X,I4)
      IF(INFO.GE.2) WRITE(IWR,2001) ZBR,NBER
 2001 FORMAT(/1X,'*** Electron scaled bremss x-section,  ZEQ =',
     1  1P,E12.5,',  NDATA =',I4)
      IF(NBER.NE.NBE) CALL PISTOP('EBRR. Inconsistent format.')
      ZBR2(M)=ZBR*ZBR
C
      DO IE=1,NBE
        READ(IRD,5002) EBT(IE),(XS(IE,IW),IW=1,NBW),TXS(IE)
        IF(INFO.GE.2) WRITE(IWR,2002)
     1    EBT(IE),(XS(IE,IW),IW=1,NBW),TXS(IE)
        X(IE)=LOG(EBT(IE))
      ENDDO
 5002 FORMAT(E9.2,5E12.5,/9X,5E12.5,/9X,5E12.5,/9X,5E12.5,
     1  /9X,5E12.5,/9X,5E12.5,/9X,2E12.5,36X,E10.3)
 2002 FORMAT(1P,E9.2,5E12.5,/9X,5E12.5,/9X,5E12.5,/9X,5E12.5,
     1  /9X,5E12.5,/9X,5E12.5,/9X,2E12.5,36X,E10.3)
C
C  ************  Initialisation of the calculation routines.
C
      DO I=1,NBW
        WB(I)=WB0(I)
      ENDDO
C
C  ****  Compute the scaled energy loss distribution and sampling
C        parameters for the energies in the simulation grid.
C
C  ****  Interpolation in E.
C
      DO IW=1,NBW
        DO IE=1,NBE
          Y(IE)=LOG(XS(IE,IW))
        ENDDO
        CALL SPLINE(X,Y,A,B,C,D,0.0D0,0.0D0,NBE)
        DO I=1,NEGP
          ELL=DLEMP(I)
          CALL FINDI(X,ELL,NBE,J)
          IF(ELL.GT.X(1)) THEN
            P0(M,I,IW)=EXP(A(J)+ELL*(B(J)+ELL*(C(J)+ELL*D(J))))
          ELSE
            F1=A(1)+X(1)*(B(1)+X(1)*(C(1)+X(1)*D(1)))
            FP1=B(1)+X(1)*(2.0D0*C(1)+X(1)*3.0D0*D(1))
            P0(M,I,IW)=EXP(F1+FP1*(ELL-X(1)))
          ENDIF
        ENDDO
      ENDDO
C
      DO IE=1,NEGP
        DO IW=1,NBW
          PDF(IW)=P0(M,IE,IW)
        ENDDO
C
        CALL RLPAC(WB,PDF,PAC,NBW)
        DO IW=1,NBW
          PDFB(M,IE,IW)=PDF(IW)
          PACB(M,IE,IW)=PAC(IW)
        ENDDO
        DO IW=1,NBW-1
         DPDFB(M,IE,IW)=PDFB(M,IE,IW+1)-PDFB(M,IE,IW)
        ENDDO
        DPDFB(M,IE,NBW)=0.0D0
C  ****  The cutoff scaled energy loss is slightly modified to ensure
C that the sampling routine EBR covers the allowed energy loss interval.
        IF(IE.LT.NEGP) THEN
          XC=WCR/ET(IE+1)
        ELSE
          XC=WCR/ET(NEGP)
        ENDIF
        IF(XC.LT.1.0D0) THEN
          PBCUT(M,IE)=RLMOM(WB,PDF,XC,NBW,-1)
          WBCUT(M,IE)=XC
        ELSE
          PBCUT(M,IE)=RLMOM(WB,PDF,1.0D0,NBW,-1)
          WBCUT(M,IE)=1.0D0
        ENDIF
      ENDDO
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE EBRaW
C  *********************************************************************
      SUBROUTINE EBRaW(M,IWR)
C
C  This subroutine generates a table of the scaled energy-loss cross
C  section for bremsstrahlung emission by electrons in material M. Data
C  are read from the files 'pdebrZZ.p08'.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Physical constants (values adopted by Seltzer and Berger).
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (ELRAD=2.817940325D-13)  ! Class. electron radius (cm)
      PARAMETER (TREV=2.0D0*REV)
C
      CHARACTER*12 FILEN
      CHARACTER*1 LDIG(10),LDIG1,LDIG2
      DATA LDIG/'0','1','2','3','4','5','6','7','8','9'/
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
      DIMENSION A(NEGP),B(NEGP),C(NEGP),D(NEGP)
C  ****  Bremsstrahlung emission.
      PARAMETER (NBE=57, NBW=32)
      COMMON/CEBR/WB(NBW),PBCUT(MAXMAT,NEGP),WBCUT(MAXMAT,NEGP),
     1  PDFB(MAXMAT,NEGP,NBW),DPDFB(MAXMAT,NEGP,NBW),
     2  PACB(MAXMAT,NEGP,NBW),ZBR2(MAXMAT)
      COMMON/CEBR01/EBT(NBE),XS(NBE,NBW),TXS(NBE),X(NBE),Y(NBE)
      COMMON/CEBR02/P0(MAXMAT,NEGP,NBW)
      DIMENSION WB0(NBW),PDF(NBE)
      DATA WB0/1.0D-12,0.025D0,0.05D0,0.075D0,0.1D0,0.15D0,0.2D0,0.25D0,
     1   0.3D0,0.35D0,0.4D0,0.45D0,0.5D0,0.55D0,0.6D0,0.65D0,0.7D0,
     2   0.75D0,0.8D0,0.85D0,0.9D0,0.925D0,0.95D0,0.97D0,0.99D0,
     3   0.995D0,0.999D0,0.9995D0,0.9999D0,0.99995D0,0.99999D0,1.0D0/
C
C  ****  'Equivalent' atomic number.
C
      SUMZ2=0.0D0
      SUMS=0.0D0
      DO IEL=1,NELEM(M)
        SUMZ2=SUMZ2+STF(M,IEL)*IZ(M,IEL)**2
        SUMS=SUMS+STF(M,IEL)
      ENDDO
      ZBR2(M)=SUMZ2/SUMS
C
C  ****  Building the scaled cross section table.
C
      DO IE=1,NBE
        TXS(IE)=0.0D0
        DO IW=1,NBW
          XS(IE,IW)=0.0D0
        ENDDO
      ENDDO
C
      DO IEL=1,NELEM(M)
        IZZ=IZ(M,IEL)
        WGHT=STF(M,IEL)*IZZ*IZZ/ZBR2(M)
        NLD=IZZ
        NLD1=NLD-10*(NLD/10)
        NLD2=(NLD-NLD1)/10
        LDIG1=LDIG(NLD1+1)
        LDIG2=LDIG(NLD2+1)
        FILEN='pdebr'//LDIG2//LDIG1//'.p08'
        OPEN(3,FILE='./pdfiles/'//FILEN)
        READ(3,*) IZZZ
        IF(IZZZ.NE.IZZ) CALL PISTOP('EBRW. Corrupt file.')
        DO IE=1,NBE
          READ(3,1001) EBT(IE),(PDF(IW),IW=1,NBW),TXSP
 1001     FORMAT(E9.2,5E12.5,/9X,5E12.5,/9X,5E12.5,/9X,5E12.5,
     1      /9X,5E12.5,/9X,5E12.5,/9X,2E12.5,36X,E10.3)
          TXS(IE)=TXS(IE)+WGHT*TXSP
          DO IW=1,NBW
            XS(IE,IW)=XS(IE,IW)+WGHT*PDF(IW)
          ENDDO
        ENDDO
        CLOSE(3)
      ENDDO
C
C  ****  The energy loss spectrum is re-normalised to reproduce the
C        total scaled cross section of Berger and Seltzer.
C
      DO IE=1,NBE
        DO IW=1,NBW
          X(IW)=WB0(IW)
          Y(IW)=XS(IE,IW)
        ENDDO
        RSUM=RLMOM(X,Y,1.0D0,NBW,0)
        FACT=(EBT(IE)+REV)*1.0D-27*137.03604D0/(ELRAD**2*(EBT(IE)+TREV))
        FNORM=TXS(IE)/(RSUM*FACT)
        TST=100.0D0*ABS(FNORM-1.0D0)
        IF(TST.GT.1.0D0)
     1    CALL PISTOP('EBRW. Check the bremss database file.')
        DO IW=1,NBW
          XS(IE,IW)=XS(IE,IW)*FNORM
        ENDDO
      ENDDO
C
C  ****  Write output scaled x-section table.
C
      WRITE(IWR,2001) SQRT(ZBR2(M)),NBE
 2001 FORMAT(1X,'*** Electron scaled bremss x-section,  ZEQ =',1P,E12.5,
     1  ',  NDATA =',I4)
      DO IE=1,NBE
        WRITE(IWR,2002) EBT(IE),(XS(IE,IW),IW=1,NBW),TXS(IE)
      ENDDO
 2002 FORMAT(1P,E9.2,5E12.5,/9X,5E12.5,/9X,5E12.5,/9X,5E12.5,
     1  /9X,5E12.5,/9X,5E12.5,/9X,2E12.5,36X,E10.3)
C
C  ************  Initialisation of the calculation routines.
C
      DO I=1,NBW
        WB(I)=WB0(I)
      ENDDO
C
C  ****  Compute the scaled energy loss distribution and sampling
C        parameters for the energies in the simulation grid.
C
C  ****  Interpolation in E.

      DO IE=1,NBE
        X(IE)=LOG(EBT(IE))
      ENDDO
      DO IW=1,NBW
        DO IE=1,NBE
          Y(IE)=LOG(XS(IE,IW))
        ENDDO
        CALL SPLINE(X,Y,A,B,C,D,0.0D0,0.0D0,NBE)
        DO I=1,NEGP
          ELL=DLEMP(I)
          IF(ELL.GT.X(1)) THEN
            CALL FINDI(X,ELL,NBE,J)
            P0(M,I,IW)=EXP(A(J)+ELL*(B(J)+ELL*(C(J)+ELL*D(J))))
          ELSE
            F1=A(1)+X(1)*(B(1)+X(1)*(C(1)+X(1)*D(1)))
            FP1=B(1)+X(1)*(2.0D0*C(1)+X(1)*3.0D0*D(1))
            P0(M,I,IW)=EXP(F1+FP1*(ELL-X(1)))
          ENDIF
        ENDDO
      ENDDO
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE EBRaT
C  *********************************************************************
      SUBROUTINE EBRaT(E,WCR,XH0,XH1,XH2,XS1,XS2,M)
C
C  Integrated cross sections for bremss emission by electrons of energy
C  E, restricted to energy losses larger than and less than the cutoff
C  energy WCR.
C
C  Output arguments:
C    XH0 ... total cross section for hard emission (cm**2).
C    XH1 ... stopping cross section for hard emission (eV*cm**2).
C    XH2 ... straggling cross section for hard emission (eV**2*cm**2).
C    XS1 ... stopping cross section for soft emission (eV*cm**2).
C    XS2 ... straggling cross section for soft emission (eV**2*cm**2).
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (TREV=2.0D0*REV)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Bremsstrahlung emission.
      PARAMETER (MAXMAT=10)
      PARAMETER (NBE=57, NBW=32)
      COMMON/CEBR/WB(NBW),PBCUT(MAXMAT,NEGP),WBCUT(MAXMAT,NEGP),
     1  PDFB(MAXMAT,NEGP,NBW),DPDFB(MAXMAT,NEGP,NBW),
     2  PACB(MAXMAT,NEGP,NBW),ZBR2(MAXMAT)
      COMMON/CEBR01/EBT(NBE),XS(NBE,NBW),TXS(NBE),X(NBE),Y(NBE)
      COMMON/CEBR02/P0(MAXMAT,NEGP,NBW)
C
      XEL=MAX(LOG(E),DLEMP1)
      XE=1.0D0+(XEL-DLEMP1)*DLFC
      KE=XE
      XEK=XE-KE
C  ****  Global x-section factor.
      FACT=ZBR2(M)*((E+REV)**2/(E*(E+TREV)))*1.0D-27
C
C  ****  Moments of the scaled bremss x-section.
C
      WCRE=WCR/E
      DO IW=1,NBW
        X(IW)=WB(IW)
        Y(IW)=P0(M,KE,IW)
      ENDDO
      XH0A=RLMOM(X,Y,X(NBW),NBW,-1)-RLMOM(X,Y,WCRE,NBW,-1)
      XS1A=RLMOM(X,Y,WCRE,NBW,0)
      XS2A=RLMOM(X,Y,WCRE,NBW,1)
      XH1A=RLMOM(X,Y,X(NBW),NBW,0)-XS1A
      XH2A=RLMOM(X,Y,X(NBW),NBW,1)-XS2A
      DO IW=1,NBW
        Y(IW)=P0(M,MIN(KE+1,NEGP),IW)
      ENDDO
      XH0B=RLMOM(X,Y,X(NBW),NBW,-1)-RLMOM(X,Y,WCRE,NBW,-1)
      XS1B=RLMOM(X,Y,WCRE,NBW,0)
      XS2B=RLMOM(X,Y,WCRE,NBW,1)
      XH1B=RLMOM(X,Y,X(NBW),NBW,0)-XS1B
      XH2B=RLMOM(X,Y,X(NBW),NBW,1)-XS2B
C
      XH0=((1.0D0-XEK)*XH0A+XEK*XH0B)*FACT
      XS1=((1.0D0-XEK)*XS1A+XEK*XS1B)*FACT*E
      XH1=((1.0D0-XEK)*XH1A+XEK*XH1B)*FACT*E
      XS2=((1.0D0-XEK)*XS2A+XEK*XS2B)*FACT*E*E
      XH2=((1.0D0-XEK)*XH2A+XEK*XH2B)*FACT*E*E
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PBRaT
C  *********************************************************************
      SUBROUTINE PBRaT(E,WCR,XH0,XH1,XH2,XS1,XS2,M)
C
C  Integrated cross sections for bremss emission by positrons of energy
C  E, restricted to energy losses larger than and less than the cutoff
C  energy WCR.
C
C  Output arguments:
C    XH0 ... total cross section for hard emission (cm**2).
C    XH1 ... stopping cross section for hard emission (eV*cm**2).
C    XH2 ... straggling cross section for hard emission (eV**2*cm**2).
C    XS1 ... stopping cross section for soft emission (eV*cm**2).
C    XS2 ... straggling cross section for soft emission (eV**2*cm**2).
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (TREV=2.0D0*REV)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Bremsstrahlung emission.
      PARAMETER (MAXMAT=10)
      PARAMETER (NBE=57, NBW=32)
      COMMON/CEBR/WB(NBW),PBCUT(MAXMAT,NEGP),WBCUT(MAXMAT,NEGP),
     1  PDFB(MAXMAT,NEGP,NBW),DPDFB(MAXMAT,NEGP,NBW),
     2  PACB(MAXMAT,NEGP,NBW),ZBR2(MAXMAT)
      COMMON/CEBR01/EBT(NBE),XS(NBE,NBW),TXS(NBE),X(NBE),Y(NBE)
      COMMON/CEBR02/P0(MAXMAT,NEGP,NBW)
C
      XEL=MAX(LOG(E),DLEMP1)
      XE=1.0D0+(XEL-DLEMP1)*DLFC
      KE=XE
      XEK=XE-KE
C  ****  Global x-section factor.
      FACT=ZBR2(M)*((E+REV)**2/(E*(E+TREV)))*1.0D-27
C  ****  Positron correction factor.
      T=LOG(1.0D0+1.0D6*E/(REV*ZBR2(M)))
      FPOS=1.0D0-EXP(-T*(1.2359D-1-T*(6.1274D-2-T*(3.1516D-2-T
     1    *(7.7446D-3-T*(1.0595D-3-T*(7.0568D-5-T*1.8080D-6)))))))
      FACT=FACT*FPOS
C
C  ****  Moments of the scaled bremss x-section.
C
      WCRE=WCR/E
      DO IW=1,NBW
        X(IW)=WB(IW)
        Y(IW)=P0(M,KE,IW)
      ENDDO
      XH0A=RLMOM(X,Y,X(NBW),NBW,-1)-RLMOM(X,Y,WCRE,NBW,-1)
      XS1A=RLMOM(X,Y,WCRE,NBW,0)
      XS2A=RLMOM(X,Y,WCRE,NBW,1)
      XH1A=RLMOM(X,Y,X(NBW),NBW,0)-XS1A
      XH2A=RLMOM(X,Y,X(NBW),NBW,1)-XS2A
      DO IW=1,NBW
        Y(IW)=P0(M,MIN(KE+1,NEGP),IW)
      ENDDO
      XH0B=RLMOM(X,Y,X(NBW),NBW,-1)-RLMOM(X,Y,WCRE,NBW,-1)
      XS1B=RLMOM(X,Y,WCRE,NBW,0)
      XS2B=RLMOM(X,Y,WCRE,NBW,1)
      XH1B=RLMOM(X,Y,X(NBW),NBW,0)-XS1B
      XH2B=RLMOM(X,Y,X(NBW),NBW,1)-XS2B
C
      XH0=((1.0D0-XEK)*XH0A+XEK*XH0B)*FACT
      XS1=((1.0D0-XEK)*XS1A+XEK*XS1B)*FACT*E
      XH1=((1.0D0-XEK)*XH1A+XEK*XH1B)*FACT*E
      XS2=((1.0D0-XEK)*XS2A+XEK*XS2B)*FACT*E*E
      XH2=((1.0D0-XEK)*XH2A+XEK*XH2B)*FACT*E*E
      RETURN
      END
C  *********************************************************************
C                       FUNCTION RLMOM
C  *********************************************************************
      FUNCTION RLMOM(X,FCT,XC,NP,MOM)
C
C  Calculation of the integral of (X**MOM)*FCT(X) over the interval from
C  X(1) to XC, obtained by linear interpolation on a table of FCT.
C  The independent variable X is assumed to take only positive values.
C
C    X ....... array of values of the variable (in increasing order).
C    FCT ..... corresponding FCT values.
C    NP ...... number of points in the table.
C    XC ...... upper limit of the integral, X(1).LE.XC.LE.X(NP).
C    MOM ..... moment order (GE.-1).
C    RLMOM ... integral of (X**MOM)*FCT(X) over the interval from X(1)
C              to XC.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (EPS=1.0D-35)
      DIMENSION X(NP),FCT(NP)
C
      IF(MOM.LT.-1) STOP 'RLMOM. Error code 0.'
      IF(NP.LT.2) STOP 'RLMOM. Error code 1.'
      IF(X(1).LT.0.0D0) STOP 'RLMOM. Error code 2.'
      DO I=2,NP
        IF(X(I).LT.0.0D0) STOP 'RLMOM. Error code 3.'
        IF(X(I).LT.X(I-1)) STOP 'RLMOM. Error code 4.'
      ENDDO
C
      RLMOM=0.0D0
      IF(XC.LT.X(1)) RETURN
      IEND=0
      XT=MIN(XC,X(NP))
      DO I=1,NP-1
        X1=MAX(X(I),EPS)
        Y1=FCT(I)
        X2=MAX(X(I+1),EPS)
        Y2=FCT(I+1)
        IF(XT.LT.X2) THEN
          XTC=XT
          IEND=1
        ELSE
          XTC=X2
        ENDIF
        DX=X2-X1
        DY=Y2-Y1
        IF(ABS(DX).GT.1.0D-14*ABS(DY)) THEN
          B=DY/DX
          A=Y1-B*X1
          IF(MOM.EQ.-1) THEN
            DS=A*LOG(XTC/X1)+B*(XTC-X1)
          ELSE
            DS=A*(XTC**(MOM+1)-X1**(MOM+1))/DBLE(MOM+1)
     1        +B*(XTC**(MOM+2)-X1**(MOM+2))/DBLE(MOM+2)
          ENDIF
        ELSE
          DS=0.5D0*(Y1+Y2)*(XTC-X1)*XTC**MOM
        ENDIF
        RLMOM=RLMOM+DS
        IF(IEND.NE.0) RETURN
      ENDDO
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE RLPAC
C  *********************************************************************
      SUBROUTINE RLPAC(X,PDF,PAC,NP)
C
C  Cumulative distribution function of PDF(X)/X, obtained from linear
C  interpolation on a table of PDF.
C  The independent variable X is assumed to take only positive values.
C
C    X ..... array of values of the variable (in increasing order).
C    PDF ... corresponding PDF values.
C    PAC ... cumulative probability function.
C    NP .... number of points in the table.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (EPS=1.0D-35)
      DIMENSION X(NP),PDF(NP),PAC(NP)
C
      PAC(1)=0.0D0
      DO I=2,NP
        X1=MAX(X(I-1),EPS)
        Y1=PDF(I-1)
        X2=MAX(X(I),EPS)
        Y2=PDF(I)
        DX=X2-X1
        DY=Y2-Y1
        B=DY/DX
        A=Y1-B*X1
        DS=A*LOG(X2/X1)+B*(X2-X1)
        PAC(I)=PAC(I-1)+DS
      ENDDO
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE EBRaA
C  *********************************************************************
      SUBROUTINE EBRaA(E,DE,CDT,M)
C
C  Random sampling of the initial direction of bremss photons, relative
C  to the direction of the projectile.
C  Numerical fit/interpolation of partial-wave shape functions given by
C  Kissel, Quarles and Pratt; ANDT 28(1993)381.
C
C  Input parameters:
C    M ..... material where the projectile moves.
C    E ..... kinetic energy of the projectile.
C    DE .... energy of the emitted photon.
C  Output parameter:
C    CDT ... cosine of the polar emission angle.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (TREV=2.0D0*REV)
C  ****  Bremsstrahlung angular distributions.
      PARAMETER (MAXMAT=10)
      COMMON/CBRANG/BET(6),BK(21),BP1(MAXMAT,6,21,4),BP2(MAXMAT,6,21,4),
     1              ZBEQ(MAXMAT)
C
      EXTERNAL RAND
C
C  ****  Distribution parameters.
C
      BETA=SQRT(E*(E+TREV))/(E+REV)
C
C  A pure dipole distribution is used for E>500 keV.
      IF(E.GT.500.0D3) THEN
        CDT=2.0D0*RAND(1.0D0)-1.0D0
        IF(RAND(2.0D0).GT.0.75D0) THEN
          IF(CDT.LT.0.0D0) THEN
            CDT=-(-CDT)**0.333333333333333D0
          ELSE
            CDT=CDT**0.333333333333333D0
          ENDIF
        ENDIF
        CDT=(CDT+BETA)/(1.0D0+BETA*CDT)
        RETURN
      ENDIF
C
      IF(BETA.GT.BET(6)) THEN
        IE=6
        GO TO 20
      ENDIF
      IF(BETA.LT.BET(1)) THEN
        IE=1
        GO TO 20
      ENDIF
      IE=1
      IE1=6
   10 IET=(IE+IE1)/2
      IF(BETA.GT.BET(IET)) THEN
        IE=IET
      ELSE
        IE1=IET
      ENDIF
      IF(IE1-IE.GT.1) GO TO 10
   20 CONTINUE
C
      RK=1.0D0+20.0D0*DE/E
      IK=MIN(INT(RK),20)
C
      P10=BP1(M,IE,IK,1)+BETA*(BP1(M,IE,IK,2)
     1   +BETA*(BP1(M,IE,IK,3)+BETA*BP1(M,IE,IK,4)))
      P11=BP1(M,IE,IK+1,1)+BETA*(BP1(M,IE,IK+1,2)
     1   +BETA*(BP1(M,IE,IK+1,3)+BETA*BP1(M,IE,IK+1,4)))
      P1=P10+(RK-IK)*(P11-P10)
C
      P20=BP2(M,IE,IK,1)+BETA*(BP2(M,IE,IK,2)
     1   +BETA*(BP2(M,IE,IK,3)+BETA*BP2(M,IE,IK,4)))
      P21=BP2(M,IE,IK+1,1)+BETA*(BP2(M,IE,IK+1,2)
     1   +BETA*(BP2(M,IE,IK+1,3)+BETA*BP2(M,IE,IK+1,4)))
      P2=P20+(RK-IK)*(P21-P20)
C
C  ****  Sampling from the Lorentz-transformed dipole distributions.
C
      P1=MIN(EXP(P1)/BETA,1.0D0)
      BETAP=MIN(MAX(BETA*(1.0D0+P2/BETA),0.0D0),0.999999999D0)
C
      IF(RAND(3.0D0).LT.P1) THEN
    1   CDT=2.0D0*RAND(4.0D0)-1.0D0
        IF(2.0D0*RAND(5.0D0).GT.1.0D0+CDT*CDT) GO TO 1
      ELSE
    2   CDT=2.0D0*RAND(4.0D0)-1.0D0
        IF(RAND(5.0D0).GT.1.0D0-CDT*CDT) GO TO 2
      ENDIF
      CDT=(CDT+BETAP)/(1.0D0+BETAP*CDT)
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE BRaAR
C  *********************************************************************
      SUBROUTINE BRaAR(M,IRD,IWR,INFO)
C
C  This subroutine reads bremsstrahlung angular distribution parameters
C  of material M from the material data file. It also initialises the
C  algorithm for generation of the initial direction of bremsstrahlung
C  photons.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (TREV=2.0D0*REV)
C  ****  Bremsstrahlung emission.
      PARAMETER (MAXMAT=10, NEGP=200, NBW=32)
      COMMON/CEBR/WB(NBW),PBCUT(MAXMAT,NEGP),WBCUT(MAXMAT,NEGP),
     1  PDFB(MAXMAT,NEGP,NBW),DPDFB(MAXMAT,NEGP,NBW),
     2  PACB(MAXMAT,NEGP,NBW),ZBR2(MAXMAT)
C  ****  Bremsstrahlung angular distributions.
      COMMON/CBRANG/BET(6),BK(21),BP1(MAXMAT,6,21,4),BP2(MAXMAT,6,21,4),
     1              ZBEQ(MAXMAT)
C
      DIMENSION E(6),RK(4),Q1R(6,4),Q2R(6,4),Q1(6,21),Q2(6,21)
      DIMENSION X(6),A(6),B(6),C(6),D(6)
C
      E(1)=1.0D3
      E(2)=5.0D3
      E(3)=1.0D4
      E(4)=5.0D4
      E(5)=1.0D5
      E(6)=5.0D5
C
      RK(1)=0.0D0
      RK(2)=0.6D0
      RK(3)=0.8D0
      RK(4)=0.95D0
C
      DO IE=1,6
        BET(IE)=SQRT(E(IE)*(E(IE)+TREV))/(E(IE)+REV)
      ENDDO
C
C  ****  Grid of reduced photon energies.
C
      DO IK=1,21
        BK(IK)=(IK-1)*0.05D0
      ENDDO
C
C  ****  Read angular distribution parameters from file (unit IRD).
C
      READ(IRD,5001) ZEQ,NDATA
 5001 FORMAT(40X,E12.5,10X,I4)
      IF(INFO.GE.2) WRITE(IWR,2001) ZEQ,NDATA
 2001 FORMAT(/1X,'*** Bremss angular distribution,  ZEQ =',
     1  1P,E12.5,',  NDATA =',I4)
      IF(NDATA.NE.24) CALL PISTOP('BRAR. Inconsistent data.')
      ZBEQ(M)=MIN(MAX(ZEQ,2.0D0),92.0D0)
C
      DO IE1=1,6
        DO IK1=1,4
          READ(IRD,*) IE,IK,ER,RKR,Q1RR,Q2RR
          IF((ABS(ER-E(IE)).LT.1.0D-6).AND.
     1       (ABS(RKR-RK(IK)).LT.1.0D-6)) THEN
            Q1R(IE,IK)=Q1RR/ZEQ
            Q2R(IE,IK)=Q2RR
          ELSE
            WRITE(26,*) 'Corrupt data file (pdbrang.p08).'
            CALL PISTOP('BRAR. Corrupt data file (pdbrang.p08).')
          ENDIF
        ENDDO
      ENDDO
C
      IF(INFO.GE.2) THEN
        DO IE=1,6
          DO IK=1,4
            WRITE(IWR,2002) E(IE),RK(IK),Q1R(IE,IK)*ZEQ,Q2R(IE,IK)
          ENDDO
        ENDDO
 2002   FORMAT(1P,E10.3,E11.3,2E15.7)
      ENDIF
C
C  ****  Expanded table of distribution parameters.
C
      DO IE=1,6
        DO IK=1,4
          X(IK)=LOG(Q1R(IE,IK))
        ENDDO
        CALL SPLINE(RK,X,A,B,C,D,0.0D0,0.0D0,4)
        DO IK=1,21
          CALL FINDI(RK,BK(IK),4,J)
          Q1(IE,IK)=A(J)+BK(IK)*(B(J)+BK(IK)*(C(J)+BK(IK)*D(J)))
        ENDDO
        DO IK=1,4
          X(IK)=Q2R(IE,IK)
        ENDDO
        CALL SPLINE(RK,X,A,B,C,D,0.0D0,0.0D0,4)
        DO IK=1,21
          CALL FINDI(RK,BK(IK),4,J)
          Q2(IE,IK)=A(J)+BK(IK)*(B(J)+BK(IK)*(C(J)+BK(IK)*D(J)))
        ENDDO
      ENDDO
C
C  ****  ... and natural cubic spline interpolations.
C
      DO IK=1,21
        DO IE=1,6
          X(IE)=Q1(IE,IK)
        ENDDO
        CALL SPLINE(BET,X,A,B,C,D,0.0D0,0.0D0,6)
        DO IE=1,6
          BP1(M,IE,IK,1)=A(IE)
          BP1(M,IE,IK,2)=B(IE)
          BP1(M,IE,IK,3)=C(IE)
          BP1(M,IE,IK,4)=D(IE)
        ENDDO
        DO IE=1,6
          X(IE)=Q2(IE,IK)
        ENDDO
        CALL SPLINE(BET,X,A,B,C,D,0.0D0,0.0D0,6)
        DO IE=1,6
          BP2(M,IE,IK,1)=A(IE)
          BP2(M,IE,IK,2)=B(IE)
          BP2(M,IE,IK,3)=C(IE)
          BP2(M,IE,IK,4)=D(IE)
        ENDDO
      ENDDO
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE BRaAW
C  *********************************************************************
      SUBROUTINE BRaAW(ZEQ,IWR)
C
C  This subroutine generates the parameters of the angular distribution
C  of bremsstrahlung photons for the element of atomic number ZEQ. In
C  the case of compounds (and mixtures) ZEQ is the average atomic number
C  of the elements in the molecule. The evaluated parameters are written
C  on the material definition file. Data are read from the database file
C  'pdbrang.p08'.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (TREV=2.0D0*REV)
C
      PARAMETER (MAXMAT=10)
C  ****  Bremsstrahlung angular distributions.
      COMMON/CBRANG/BET(6),BK(21),BP1(MAXMAT,6,21,4),BP2(MAXMAT,6,21,4),
     1              ZBEQ(MAXMAT)
C
      DIMENSION Z(6),E(6),RK(4),P1(6,6,4),P2(6,6,4),Q1(6,4),Q2(6,4)
      DIMENSION X(6),Y(6),A(6),B(6),C(6),D(6)
C
      Z(1)=2.0D0
      Z(2)=8.0D0
      Z(3)=13.0D0
      Z(4)=47.0D0
      Z(5)=79.0D0
      Z(6)=92.0D0
C
      E(1)=1.0D3
      E(2)=5.0D3
      E(3)=1.0D4
      E(4)=5.0D4
      E(5)=1.0D5
      E(6)=5.0D5
C
      RK(1)=0.0D0
      RK(2)=0.6D0
      RK(3)=0.8D0
      RK(4)=0.95D0
C
C  ****  Read database file.
C
      OPEN(3,FILE='./pdfiles/pdbrang.p08')
      DO IK1=1,4
        DO IZ1=1,6
          DO IE1=1,6
            READ(3,*) IZ,IE,IK,ZR,ER,RKR,P1R,P2R
             IF((ABS(ZR-Z(IZ)).LT.1.0D-6).AND.
     1          (ABS(ER-E(IE)).LT.1.0D-6).AND.
     2          (ABS(RKR-RK(IK)).LT.1.0D-6)) THEN
               P1(IZ,IE,IK)=P1R
               P2(IZ,IE,IK)=P2R
             ELSE
               WRITE(26,*) 'Corrupt data file (pdbrang.p08).'
               CALL PISTOP('BRAW. Corrupt data file (pdbrang.p08).')
             ENDIF
          ENDDO
        ENDDO
      ENDDO
      CLOSE(3)
C
C  ****  Interpolation in Z.
C
      DO IE=1,6
        DO IK=1,4
          DO IZ=1,6
            X(IZ)=LOG(P1(IZ,IE,IK))
            Y(IZ)=P2(IZ,IE,IK)
          ENDDO
          CALL SPLINE(Z,X,A,B,C,D,0.0D0,0.0D0,6)
          CALL FINDI(Z,ZEQ,6,I)
          Q1(IE,IK)=EXP(A(I)+ZEQ*(B(I)+ZEQ*(C(I)+ZEQ*D(I))))
          CALL SPLINE(Z,Y,A,B,C,D,0.0D0,0.0D0,6)
          CALL FINDI(Z,ZEQ,6,I)
          Q2(IE,IK)=A(I)+ZEQ*(B(I)+ZEQ*(C(I)+ZEQ*D(I)))
        ENDDO
      ENDDO
C
C  ****  Write final table of parameters.
C
      NDATA=24
      WRITE(IWR,2001) ZEQ,NDATA
 2001 FORMAT(1X,'*** Bremss angular distribution,  ZEQ =',
     1  1P,E12.5,',  NDATA =',I4)
      DO IE=1,6
        DO IK=1,4
          WRITE(IWR,2002) IE,IK,E(IE),RK(IK),Q1(IE,IK),Q2(IE,IK)
        ENDDO
      ENDDO
 2002 FORMAT(2I2,1P,2E11.3,2E15.7)
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PANaR
C  *********************************************************************
      SUBROUTINE PANaR
C
C  Simulation of annihilation of positrons at rest.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (PI=3.1415926535897932D0, TWOPI=PI+PI, TREV=2.0D0*REV)
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
      DIMENSION ILBA(5)
C  ****  Simulation parameters.
      PARAMETER (MAXMAT=10)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
C
      EXTERNAL RAND
C
      IF(REV.LT.EABS(2,M)) RETURN
C
      US=U
      VS=V
      WS=W
      CDT1=-1.0D0+2.0D0*RAND(1.0D0)
      DF=TWOPI*RAND(2.0D0)
      CALL DIRECT(CDT1,DF,US,VS,WS)
      ILBA(1)=ILB(1)+1
      ILBA(2)=3
      ILBA(3)=6
      ILBA(4)=0
      ILBA(5)=ILB(5)
      CALL STORES(REV,X,Y,Z,US,VS,WS,WGHT,2,ILBA)
      CALL STORES(REV,X,Y,Z,-US,-VS,-WS,WGHT,2,ILBA)
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PANa
C  *********************************************************************
      SUBROUTINE PANa(E1,CDT1,E2,CDT2)
C
C  Simulation of positron annihilation (either at rest or in flight).
C  Ei and CDTi are the energies and polar direction cosines of the two
C  annihilation photons.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (PI=3.1415926535897932D0, TWOPI=PI+PI, TREV=2.0D0*REV)
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C  ****  Simulation parameters.
      PARAMETER (MAXMAT=10)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
C
      EXTERNAL RAND
C
C  ****  Slow positrons (assumed at rest).
C
      IF(E.LT.EABS(3,M)) THEN
        E1=0.5D0*(E+TREV)
        E2=E1
        CDT1=-1.0D0+2.0D0*RAND(1.0D0)
        CDT2=-CDT1
      ELSE
C  ****  Annihilation in flight (two photons with energy and directions
C        determined from the dcs and energy-momentum conservation).
        GAM=1.0D0+MAX(E,1.0D0)/REV
        GAM21=SQRT(GAM*GAM-1.0D0)
        ANI=1.0D0+GAM
        CHIMIN=1.0D0/(ANI+GAM21)
        RCHI=(1.0D0-CHIMIN)/CHIMIN
        GT0=ANI*ANI-2.0D0
    1   CONTINUE
        CHI=CHIMIN*RCHI**RAND(2.0D0)
        GREJ=ANI*ANI*(1.0D0-CHI)+GAM+GAM-1.0D0/CHI
        IF(RAND(3.0D0)*GT0.GT.GREJ) GO TO 1
C
        DET=E+TREV
        E1=CHI*DET
        CDT1=(ANI-1.0D0/CHI)/GAM21
        CHIP=1.0D0-CHI
        E2=DET-E1
        CDT2=(ANI-1.0D0/CHIP)/GAM21
      ENDIF
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PANaT
C  *********************************************************************
      SUBROUTINE PANaT(E,TXS)
C
C  Total cross section (per electron) for annihilation of positrons with
C  kinetic energy E. Computed from Heitler's dcs formula for annihila-
C  tion with free electrons at rest.
C
C  Output argument:
C    XST ... total annihilation cross section (cm**2).
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (ELRAD=2.817940325D-13)  ! Class. electron radius (cm)
      PARAMETER (PI=3.1415926535897932D0, PIELR2=PI*ELRAD*ELRAD)
C
      GAM=1.0D0+MAX(E,1.0D0)/REV
      GAM2=GAM*GAM
      F2=GAM2-1.0D0
      F1=SQRT(F2)
      TXS=PIELR2*((GAM2+4.0D0*GAM+1.0D0)*LOG(GAM+F1)/F2
     1   -(GAM+3.0D0)/F1)/(GAM+1.0D0)
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE GRAa
C  *********************************************************************
      SUBROUTINE GRAa(E,CDT,M,IEFF)
C
C  Random sampling of coherent (Rayleigh) scattering.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*2 LASYMB
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (RREV=1.0D0/REV)
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****  Element data.
      COMMON/CADATA/ATW(99),EPX(99),RSCR(99),ETA(99),EB(99,30),
     1  IFI(99,30),IKS(99,30),NSHT(99),LASYMB(99)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Photon simulation tables.
      COMMON/CGIMFP/SGRA(MAXMAT,NEGP),SGCO(MAXMAT,NEGP),
     1  SGPH(MAXMAT,NEGP),SGPP(MAXMAT,NEGP),SGAUX(MAXMAT,NEGP)
C  ****  Rayleigh scattering.
      PARAMETER (NQ=250,NEX=1024)
      COMMON/CGRA01/FF2(MAXMAT,NQ),ERA(NEX),XSRA(MAXMAT,NEX),
     1    IED(NEGP),IEU(NEGP),NE
      PARAMETER (NP=150,NPM1=NP-1)
      COMMON/CGRA03/QRA(NP,MAXMAT),PRA(NP,MAXMAT),DPRA(NP,MAXMAT),
     1  ARA(NP,MAXMAT),BRA(NP,MAXMAT),PMAX(NEGP,MAXMAT),
     2  ITLRA(NP,MAXMAT),ITURA(NP,MAXMAT)
C
      EXTERNAL RAND
C
C  ****  Binary search.
C
      II=IED(KE)
      IU=IEU(KE)
    1 IT=(II+IU)/2
      IF(XEL.GT.ERA(IT)) THEN
        II=IT
      ELSE
        IU=IT
      ENDIF
      IF(IU-II.GT.1) GO TO 1
      XSE=EXP(XSRA(M,II)+(XSRA(M,II+1)-XSRA(M,II))*(XEL-ERA(II))
     1   /(ERA(II+1)-ERA(II)))
C
      IF(RAND(1.0D0)*SGRA(M,KE).GT.XSE) THEN
        IEFF=0
        CDT=1.0D0
        RETURN
      ENDIF
C
      IEFF=1
      QMAX=2.0D0*E*RREV
      IF(QMAX.LT.1.0D-10) THEN
    2   CONTINUE
        CDT=1.0D0-2.0D0*RAND(1.0D0)
        G=0.5D0*(1.0D0+CDT*CDT)
        IF(RAND(2.0D0).GT.G) GO TO 2
        RETURN
      ENDIF
      Q2MAX=MIN(QMAX*QMAX,QRA(NP,M))
C
    3 CONTINUE
      RU=RAND(3.0D0)*PMAX(KE+1,M)
C
C  ****  Selection of the interval
C        (binary search within pre-calculated limits).
C
      ITN=RU*NPM1+1
      I=ITLRA(ITN,M)
      J=ITURA(ITN,M)
      IF(J-I.LT.2) GO TO 5
    4 K=(I+J)/2
      IF(RU.GT.PRA(K,M)) THEN
        I=K
      ELSE
        J=K
      ENDIF
      IF(J-I.GT.1) GO TO 4
C
C  ****  Sampling from the rational inverse cumulative distribution.
C
    5 CONTINUE
      RR=RU-PRA(I,M)
      IF(RR.GT.1.0D-16) THEN
        D=DPRA(I,M)
        XX=QRA(I,M)+((1.0D0+ARA(I,M)+BRA(I,M))*D*RR
     1    /(D*D+(ARA(I,M)*D+BRA(I,M)*RR)*RR))*(QRA(I+1,M)-QRA(I,M))
      ELSE
        XX=QRA(I,M)
      ENDIF
      IF(XX.GT.Q2MAX) GO TO 3
      CDT=1.0D0-2.0D0*XX/Q2MAX
C  ****  Rejection.
      G=0.5D0*(1.0D0+CDT*CDT)
      IF(RAND(4.0D0).GT.G) GO TO 3
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE GRAbT
C  *********************************************************************
      SUBROUTINE GRAbT(E,CS,M)
C
C  Total cross section for Rayleigh (coherent) photon scattering. Form-
C  factor approximation. Not used in the simulation!
C
C  Input arguments:
C    E ........ photon energy (eV).
C    M ........ material where photons propagate.
C  Output argument:
C    CS ....... coherent total cross section (cm**2/molecule).
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (RREV=1.0D0/REV)
      PARAMETER (ELRAD=2.817940325D-13)  ! Class. electron radius (cm)
      PARAMETER (PI=3.1415926535897932D0, PIELR2=PI*ELRAD*ELRAD)
C
      COMMON/CGRA00/FACTE,Q2MAX,MM,MOM
      EXTERNAL GRAaD
C
      MM=M
      MOM=0
      IF(E.LT.5.0D7) THEN
        FACTE=2.0D0*(E*RREV)**2
        SUM=SUMGA(GRAaD,-1.0D0,0.90D0,1.0D-6)
     1     +SUMGA(GRAaD,0.90D0,0.99D0,1.0D-6)
     2     +SUMGA(GRAaD,0.99D0,0.995D0,1.0D-6)
     3     +SUMGA(GRAaD,0.995D0,1.00D0,1.0D-6)
        CS=PIELR2*SUM
      ELSE
        EC=5.0D7
        FACTE=2.0D0*(EC*RREV)**2
        Q2MAX=2.0D0*FACTE
        SUM=SUMGA(GRAaD,-1.0D0,0.90D0,1.0D-6)
     1     +SUMGA(GRAaD,0.90D0,0.99D0,1.0D-6)
     2     +SUMGA(GRAaD,0.99D0,0.995D0,1.0D-6)
     3     +SUMGA(GRAaD,0.995D0,1.00D0,1.0D-6)
        CS=PIELR2*SUM
        CS=(EC/E)**2*CS
        FACTE=2.0D0*(E*RREV)**2
      ENDIF
      RETURN
      END
C  *********************************************************************
C                       FUNCTION GRAaD
C  *********************************************************************
      FUNCTION GRAaD(CDT)
C
C  Differential x-section for Rayleigh scattering. Form-factor approx.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (MAXMAT=10,NQ=250)
      COMMON/CGRA00/FACTE,Q2MAX,M,MOM
      COMMON/CGRA02/QQ(NQ),AR(MAXMAT,NQ),BR(MAXMAT,NQ),CR(MAXMAT,NQ),
     1              DR(MAXMAT,NQ),FF0(MAXMAT),QQM
C
      Q2=FACTE*(1.0D0-CDT)
      IF(Q2.GT.QQM) THEN
        GRAaD=0.0D0
        RETURN
      ENDIF
      GRAaD=(1.0D0+CDT*CDT)*GRAaF2(Q2)
      IF(MOM.GT.0) GRAaD=GRAaD*((1.0D0-CDT)*0.5D0)**MOM
      RETURN
      END
C  *********************************************************************
C                       FUNCTION GRAaF2
C  *********************************************************************
      FUNCTION GRAaF2(Q2)
C
C  Squared molecular form factor, as a function of (Q*SL/REV)**2.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (MAXMAT=10,NQ=250)
      COMMON/CGRA00/FACTE,Q2MAX,M,MOM
      COMMON/CGRA02/QQ(NQ),AR(MAXMAT,NQ),BR(MAXMAT,NQ),CR(MAXMAT,NQ),
     1              DR(MAXMAT,NQ),FF0(MAXMAT),QQM
C
      IF(Q2.LT.1.0D-9) THEN
        GRAaF2=FF0(M)
      ELSE IF(Q2.GT.QQM) THEN
        GRAaF2=0.0D0
      ELSE
        QL=LOG(Q2)
        CALL FINDI(QQ,QL,NQ,I)
        F2=AR(M,I)+QL*(BR(M,I)+QL*(CR(M,I)+QL*DR(M,I)))
        GRAaF2=EXP(F2)
      ENDIF
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE GRAaTI
C  *********************************************************************
      SUBROUTINE GRAaTI(E,ECS,M)
C
C  Total cross section for Rayleigh (coherent) photon scattering, in
C  cm**2. Interpolated from input data.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****  Rayleigh scattering.
      PARAMETER (NQ=250,NEX=1024)
      COMMON/CGRA00/FACTE,Q2MAX,MM,MOM
      COMMON/CGRA01/FF(MAXMAT,NQ),ERA(NEX),XSRA(MAXMAT,NEX),
     1    IED(NEGP),IEU(NEGP),NE
C
      XELN=LOG(E)
      XEN=1.0D0+(XELN-DLEMP1)*DLFC
      KEN=XEN
      IF(KEN.EQ.0) KEN=1
C
C  ****  Binary search.
C
      II=IED(KEN)
      IU=IEU(KEN)
    1 IT=(II+IU)/2
      IF(XELN.GT.ERA(IT)) THEN
        II=IT
      ELSE
        IU=IT
      ENDIF
      IF(IU-II.GT.1) GO TO 1
      ECS=EXP(XSRA(M,II)+(XSRA(M,II+1)-XSRA(M,II))*(XELN-ERA(II))
     1   /(ERA(II+1)-ERA(II)))/VMOL(M)
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE GRAaR
C  *********************************************************************
      SUBROUTINE GRAaR(M,IRD,IWR,INFO)
C
C  This subroutine reads the squared molecular form factor and the DCS
C  for Rayleigh scattering of photons in material M. These two functions
C  are tabulated using the same grids for all materials.
C     The random sampling of the scattering angle is performed using the
C  RITA algorithm.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*2 LASYMB
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (RREV=1.0D0/REV)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****  Element data.
      COMMON/CADATA/ATW(99),EPX(99),RSCR(99),ETA(99),EB(99,30),
     1  IFI(99,30),IKS(99,30),NSHT(99),LASYMB(99)
C  ****  Photon simulation tables.
      COMMON/CGIMFP/SGRA(MAXMAT,NEGP),SGCO(MAXMAT,NEGP),
     1  SGPH(MAXMAT,NEGP),SGPP(MAXMAT,NEGP),SGAUX(MAXMAT,NEGP)
C  ****  Rayleigh scattering.
      PARAMETER (NQ=250,NEX=1024)
      COMMON/CGRA00/FACTE,Q2MAX,MM,MOM
      COMMON/CGRA01/FF(MAXMAT,NQ),ERA(NEX),XSRA(MAXMAT,NEX),
     1    IED(NEGP),IEU(NEGP),NE
      COMMON/CGRA02/QQ(NQ),AR(MAXMAT,NQ),BR(MAXMAT,NQ),CR(MAXMAT,NQ),
     1              DR(MAXMAT,NQ),FF0(MAXMAT),QQM
      PARAMETER (NP=150)
      COMMON/CGRA03/QRA(NP,MAXMAT),PRA(NP,MAXMAT),DPRA(NP,MAXMAT),
     1  ARA(NP,MAXMAT),BRA(NP,MAXMAT),PMAX(NEGP,MAXMAT),
     2  ITLRA(NP,MAXMAT),ITURA(NP,MAXMAT)
      DIMENSION Q(NQ),F(NQ),FFI(NQ),ER(NEX),A(NQ),B(NQ),C(NQ),D(NQ)
      PARAMETER (NIP=51)
      DIMENSION QI(NIP),FUN(NIP),SUM(NIP)
C  ****  Random sampling (RITA).
      PARAMETER (NM=512)
      COMMON/CRITA/QTI(NM),PACI(NM),DPACI(NM),AI(NM),BI(NM),
     1             ITLI(NM),ITUI(NM),NPM1I
C
      EXTERNAL GRAaF2
C
      READ(IRD,1001) NQQ,NE
 1001 FORMAT(33X,I3,8X,I4)
      IF(INFO.GE.2) WRITE(IWR,2001) NQ,NE
 2001 FORMAT(/1X,'***  Rayleigh scattering.  NQ = ',I3,',  NE = ',I4)
C
      DO I=1,NQ
        READ(IRD,*) Q(I),FFI(I)
        IF(I.EQ.1) FF0(M)=FFI(I)**2
        F(I)=LOG(FFI(I)**2)
        FF(M,I)=FFI(I)
      ENDDO
      DO I=1,NE
        READ(IRD,*) ER(I),XSRA(M,I)
        XSRA(M,I)=LOG(XSRA(M,I)*VMOL(M))
      ENDDO
      IF(ER(NE).LT.EU) THEN
        XS1=XSRA(M,NE-1)+(XSRA(M,NE)-XSRA(M,NE-1))
     1     *(LOG(EU)-LOG(ER(NE-1)))/(LOG(ER(NE))-LOG(ER(NE-1)))
        XSRA(M,NE)=XS1
        ER(NE)=EU
      ENDIF
C
      IF(M.EQ.1) THEN
        QQM=Q(NQ)**2
        DO I=1,NQ
          QQ(I)=LOG(Q(I)**2)
        ENDDO
        DO I=1,NE
          ERA(I)=LOG(ER(I))
        ENDDO
        DO I=1,NEGP
         CALL FINDI(ERA,DLEMP(I),NE,J)
         IED(I)=J
        ENDDO
        DO I=1,NEGP-1
         IEU(I)=MIN(IED(I+1)+1,NE)
        ENDDO
        IEU(NEGP)=MIN(IED(NEGP)+1,NE)
      ENDIF
C
      CALL SPLINE(QQ,F,A,B,C,D,0.0D0,0.0D0,NQ)
      DO I=1,NQ
        AR(M,I)=A(I)
        BR(M,I)=B(I)
        CR(M,I)=C(I)
        DR(M,I)=D(I)
      ENDDO
C
C  ****  Total cross section at the simulation grid points (slightly
C        increased to simplify interpolation).
C
      EE=DLEMP(1)
      CALL FINDI(ERA,EE,NE,J)
      XS1=XSRA(M,J)
     1   +(XSRA(M,J+1)-XSRA(M,J))*(EE-ERA(J))/(ERA(J+1)-ERA(J))
      DO IE=1,NEGP-1
        XSMAX=XS1
        J1=J+1
        EE=DLEMP(IE+1)
        CALL FINDI(ERA,EE,NE,J)
        XS1=XSRA(M,J)
     1     +(XSRA(M,J+1)-XSRA(M,J))*(EE-ERA(J))/(ERA(J+1)-ERA(J))
        XSMAX=MAX(XSMAX,XS1)
C
        IF(J1.LT.J) THEN
          DO I=J1,J
            XSMAX=MAX(XSMAX,XSRA(M,I))
          ENDDO
        ENDIF
        SGRA(M,IE)=EXP(XSMAX)
      ENDDO
      SGRA(M,NEGP)=SGPH(M,NEGP-1)
C
      IF(INFO.GE.2) THEN
        WRITE(IWR,2002)
 2002   FORMAT(/3X,'Q/me*c',5X,'Form factor',/1X,25('-'))
        DO I=1,NQ
          WRITE(IWR,'(1P,E12.5,E13.5)') Q(I),FFI(I)
        ENDDO
        WRITE(IWR,2003)
 2003   FORMAT(/3X,'Energy',7X,'CS-Rayl',/4X,'(eV)',8X,'(cm**2)',
     1    /1X,25('-'))
        DO I=1,NE
          WRITE(IWR,'(1P,E12.5,E13.5)') ER(I),EXP(XSRA(M,I))/VMOL(M)
        ENDDO
      ENDIF
C
C  ****  Initialization of the RITA algorithm for random sampling of the
C  squared momentum transfer from the squared molecular form factor.
C
      MM=M
      Q2MIN=0.0D0
      Q2MAX=0.0D0
      NPT=NP
      NU=NPT/4
      DO I=2,NQ
        IF(GRAaF2(Q(I)**2).GT.1.0D-35) Q2MAX=Q(I-1)**2
      ENDDO
      CALL RITAI0(GRAaF2,Q2MIN,Q2MAX,NPT,NU,ERRM,0)
      NPI=NPM1I+1
      IF(NPI.NE.NP) THEN
        WRITE(26,*) 'GRAaR. RITA initialisation error.'
        WRITE(26,*) 'The number of fixed grid points is ',NPI
        WRITE(26,*) 'The required number of grid points was ',NP
        CALL PISTOP('GRAaR. RITA initialisation error.')
      ENDIF
      IF(ERRM.GT.1.0D-5) THEN
        WRITE(26,*) 'GRAaR. RITA interpolation error is too large.'
        WRITE(26,*) 'The interpolation error is ',ERRM
        CALL PISTOP('GRAaR. RITA interpolation error is too large.')
      ENDIF
C
C  ****  Upper limit of the X2 interval for the PENELOPE grid energies.
C
      DO IE=1,NEGP
        QM=2.0D0*ET(IE)*RREV
        Q2M=QM*QM
        IF(Q2M.GT.QTI(1)) THEN
          IF(Q2M.LT.QTI(NP)) THEN
            I=1
            J=NPI
    1       IT=(I+J)/2
            IF(Q2M.GT.QTI(IT)) THEN
              I=IT
            ELSE
              J=IT
            ENDIF
            IF(J-I.GT.1) GO TO 1
C
            Q1=QTI(I)
            Q2=Q2M
            DQ=(Q2-Q1)/DBLE(NIP-1)
            DO K=1,NIP
              QI(K)=Q1+DBLE(K-1)*DQ
              TAU=(QI(K)-QTI(I))/(QTI(I+1)-QTI(I))
              CON1=2.0D0*BI(I)*TAU
              CI=1.0D0+AI(I)+BI(I)
              CON2=CI-AI(I)*TAU
              IF(ABS(CON1).GT.1.0D-16*ABS(CON2)) THEN
                ETAP=CON2*(1.0D0-SQRT(1.0D0-2.0D0*TAU*CON1/CON2**2))
     1              /CON1
              ELSE
                ETAP=TAU/CON2
              ENDIF
              FUN(K)=DPACI(I)*(1.0D0+(AI(I)+BI(I)*ETAP)*ETAP)**2
     1              /((1.0D0-BI(I)*ETAP*ETAP)*CI*(QTI(I+1)-QTI(I)))
            ENDDO
            CALL SLAG6(DQ,FUN,SUM,NIP)
            PMAX(IE,M)=PACI(I)+SUM(NIP)
          ELSE
            PMAX(IE,M)=1.0D0
          ENDIF
        ELSE
          PMAX(IE,M)=PACI(1)
        ENDIF
      ENDDO
C
      DO I=1,NP
        QRA(I,M)=QTI(I)
        PRA(I,M)=PACI(I)
        DPRA(I,M)=DPACI(I)
        ARA(I,M)=AI(I)
        BRA(I,M)=BI(I)
        ITLRA(I,M)=ITLI(I)
        ITURA(I,M)=ITUI(I)
      ENDDO
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE GRAaW
C  *********************************************************************
      SUBROUTINE GRAaW(M,IWR)
C
C  This subroutine generates tables of molecular form factors and cross
C  sections for Rayleigh scattering of photons in material M and writes
C  them on the material data file. Data are read from the files
C  'pdgraZZ.p08'.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C
      CHARACTER*12 FILEN
      CHARACTER*1 LDIG(10),LDIG1,LDIG2
      DATA LDIG/'0','1','2','3','4','5','6','7','8','9'/
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C
      PARAMETER (NQ=250,NEM=1500)
      DIMENSION Q(NQ),FF(NQ),FF2(NQ),ER(NEM),XSR(NEM)
      DIMENSION EI(NEM),XS(NEM)
C
C  ****  Momentum-transfer grid points and atomic form factor.
      DO I=1,NQ
        Q(I)=0.0D0
        FF2(I)=0.0D0
      ENDDO
C  ****  Energy grid points and Rayleigh x sections.
      EL=10.0D0
      FACT1=10.0D0**(1.0D0/250.0D0)
      FACT2=10.0D0**(1.0D0/25.0D0)
      E=10.0D0/FACT1
      NE=0
      DO I=1,2*NEM
        IF(E.LT.1.5848D5) THEN
          E=E*FACT1
        ELSE
          E=E*FACT2
        ENDIF
        IF(E.GT.49.0D0) THEN
          NE=NE+1
          ER(NE)=E
          XSR(NE)=0.0D0
          IF(E.GT.1.2D9) GO TO 1
        ENDIF
      ENDDO
    1 CONTINUE
C
      DO IEL=1,NELEM(M)
        IZZ=IZ(M,IEL)
        NLD=IZZ
        NLD1=NLD-10*(NLD/10)
        NLD2=(NLD-NLD1)/10
        LDIG1=LDIG(NLD1+1)
        LDIG2=LDIG(NLD2+1)
C
        FILEN='pdaff'//LDIG2//LDIG1//'.p08'
        OPEN(3,FILE='./pdfiles/'//FILEN)
        READ(3,*) IZZZ,NQI
        IF(IZZZ.NE.IZZ) CALL PISTOP('GRAaW. Corrupt file.')
        IF(NQI.NE.NQ) CALL PISTOP('GRAaW. Corrupt file.')
        DO I=1,NQ
          READ(3,*) Q(I),FF(I)
        ENDDO
        CLOSE(3)
C
        FILEN='pdgra'//LDIG2//LDIG1//'.p08'
        OPEN(3,FILE='./pdfiles/'//FILEN)
        READ(3,*) IZZZ,NEI
        IF(IZZZ.NE.IZZ) CALL PISTOP('GRAaW. Corrupt file.')
        DO I=1,NEI
          READ(3,*) EI(I),FA1,FA2,XS(I)
          EI(I)=LOG(EI(I))
          XS(I)=LOG(XS(I))
        ENDDO
        CLOSE(3)
C
        DO I=1,NQ
          FF2(I)=FF2(I)+STF(M,IEL)*FF(I)**2
        ENDDO
        DO I=1,NE
          EE=LOG(ER(I))
          CALL FINDI(EI,EE,NEI,J)
          XSE=EXP(XS(J)+(XS(J+1)-XS(J))*(EE-EI(J))/(EI(J+1)-EI(J)))
          XSR(I)=XSR(I)+STF(M,IEL)*XSE
        ENDDO
      ENDDO
C
      WRITE(IWR,2001) NQ,NE
 2001 FORMAT(1X,'***  Rayleigh scattering.  NQ = ',I3,',  NE = ',I4)
      DO I=1,NQ
        WRITE(IWR,'(1P,E9.2,E12.5)') Q(I),SQRT(FF2(I))
      ENDDO
      DO I=1,NE
        WRITE(IWR,'(1P,3E12.5)') ER(I),XSR(I)
      ENDDO
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE GCOa
C  *********************************************************************
      SUBROUTINE GCOa(E,DE,EP,CDT,ES,CDTS,M,ISHELL)
C
C  Random sampling of incoherent (Compton) scattering of photons. Relat-
C  ivistic impulse approximation with analytical one-electron Compton
C  profiles.
C
C  Input arguments:
C    E ........ incident photon energy (eV).
C    M ........ material where photons propagate.
C  Output argument:
C    DE ....... energy loss (eV).
C    EP ....... energy of the scattered photon (eV).
C    CDT ...... cosine of the polar scattering angle.
C    ES ....... energy of the emitted electron (eV).
C    CDTS ..... polar cosine of direction of the electron.
C    ISHELL ... index of the shell that has been 'ionised'.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (RREV=1.0D0/REV)
      PARAMETER (D2=1.4142135623731D0, D1=1.0D0/D2, D12=0.5D0)
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
      COMMON/CECUTR/ECUTR(MAXMAT)
C  ****  Compton scattering.
      PARAMETER (NOCO=128)
      COMMON/CGCO/FCO(MAXMAT,NOCO),UICO(MAXMAT,NOCO),FJ0(MAXMAT,NOCO),
     2  KZCO(MAXMAT,NOCO),KSCO(MAXMAT,NOCO),NOSCCO(MAXMAT)
C
      DIMENSION RN(NOCO),PAC(NOCO)
      EXTERNAL RAND
C
      EK=E*RREV
      EK2=EK+EK+1.0D0
      EKS=EK*EK
      EK1=EKS-EK2-1.0D0
      TAUMIN=1.0D0/EK2
      TAUM2=TAUMIN*TAUMIN
      A1=LOG(EK2)
      A2=A1+2.0D0*EK*(1.0D0+EK)*TAUM2
      IF(E.GT.5.0D6) GO TO 4
C
C  ****  Incoherent scattering function for theta=PI.
C
      S0=0.0D0
      DO I=1,NOSCCO(M)
        IF(UICO(M,I).LT.E) THEN
          AUX=E*(E-UICO(M,I))*2.0D0
          PZOMC=FJ0(M,I)*(AUX-REV*UICO(M,I))
     1         /(REV*SQRT(AUX+AUX+UICO(M,I)**2))
          IF(PZOMC.GT.0.0D0) THEN
            RNI=1.0D0-0.5D0*EXP(D12-(D1+D2*PZOMC)**2)
          ELSE
            RNI=0.5D0*EXP(D12-(D1-D2*PZOMC)**2)
          ENDIF
          S0=S0+FCO(M,I)*RNI
        ENDIF
      ENDDO
C
C  ****  Sampling tau.
C
    1 CONTINUE
      IF(RAND(1.0D0)*A2.LT.A1) THEN
        TAU=TAUMIN**RAND(2.0D0)
      ELSE
        TAU=SQRT(1.0D0+RAND(3.0D0)*(TAUM2-1.0D0))
      ENDIF
      CDT1=(1.0D0-TAU)/(EK*TAU)
C  ****  Incoherent scattering function.
      S=0.0D0
      DO I=1,NOSCCO(M)
        IF(UICO(M,I).LT.E) THEN
          AUX=E*(E-UICO(M,I))*CDT1
          PZOMC=FJ0(M,I)*(AUX-REV*UICO(M,I))
     1         /(REV*SQRT(AUX+AUX+UICO(M,I)**2))
          IF(PZOMC.GT.0.0D0) THEN
            RN(I)=1.0D0-0.5D0*EXP(D12-(D1+D2*PZOMC)**2)
          ELSE
            RN(I)=0.5D0*EXP(D12-(D1-D2*PZOMC)**2)
          ENDIF
          S=S+FCO(M,I)*RN(I)
          PAC(I)=S
        ELSE
          PAC(I)=S-1.0D-6
        ENDIF
      ENDDO
C  ****  Rejection function.
      TST=S*(1.0D0+TAU*(EK1+TAU*(EK2+TAU*EKS)))
     1   /(EKS*TAU*(1.0D0+TAU*TAU))
      IF(RAND(4.0D0)*S0.GT.TST) GO TO 1
      CDT=1.0D0-CDT1
C
C  ****  Target electron shell.
C
    2 CONTINUE
      TST=S*RAND(5.0D0)
      DO I=1,NOSCCO(M)
        IF(PAC(I).GT.TST) THEN
          ISHELL=I
          GO TO 3
        ENDIF
      ENDDO
      ISHELL=NOSCCO(M)
    3 CONTINUE
C
C  ****  Projected momentum of the target electron.
C
      A=RAND(6.0D0)*RN(ISHELL)
      IF(A.LT.0.5D0) THEN
        PZOMC=(D1-SQRT(D12-LOG(A+A)))/(D2*FJ0(M,ISHELL))
      ELSE
        PZOMC=(SQRT(D12-LOG(2.0D0-A-A))-D1)/(D2*FJ0(M,ISHELL))
      ENDIF
      IF(PZOMC.LT.-1.0D0) GO TO 2
C
C  ****  F(EP) rejection.
C
      XQC=1.0D0+TAU*(TAU-2.0D0*CDT)
      AF=SQRT(XQC)*(1.0D0+TAU*(TAU-CDT)/XQC)
      IF(AF.GT.0.0D0) THEN
        FPZMAX=1.0D0+AF*0.2D0
      ELSE
        FPZMAX=1.0D0-AF*0.2D0
      ENDIF
      FPZ=1.0D0+AF*MAX(MIN(PZOMC,0.2D0),-0.2D0)
      IF(RAND(7.0D0)*FPZMAX.GT.FPZ) GO TO 2
C
C  ****  Energy of the scattered photon.
C
      T=PZOMC**2
      B1=1.0D0-T*TAU*TAU
      B2=1.0D0-T*TAU*CDT
      IF(PZOMC.GT.0.0D0) THEN
        EP=E*(TAU/B1)*(B2+SQRT(ABS(B2*B2-B1*(1.0D0-T))))
      ELSE
        EP=E*(TAU/B1)*(B2-SQRT(ABS(B2*B2-B1*(1.0D0-T))))
      ENDIF
      GO TO 6
C
C  ****  No Doppler broadening for E greater than 5 MeV.
C
    4 CONTINUE
      IF(RAND(8.0D0)*A2.LT.A1) THEN
        TAU=TAUMIN**RAND(9.0D0)
      ELSE
        TAU=SQRT(1.0D0+RAND(10.0D0)*(TAUM2-1.0D0))
      ENDIF
C  ****  Rejection function.
      TST=(1.0D0+TAU*(EK1+TAU*(EK2+TAU*EKS)))
     1   /(EKS*TAU*(1.0D0+TAU*TAU))
      IF(RAND(11.0D0).GT.TST) GO TO 4
      EP=TAU*E
      CDT=1.0D0-(1.0D0-TAU)/(EK*TAU)
C
C  ****  Target electron shell.
C
      TST=ZT(M)*RAND(12.0D0)
      S=0.0D0
      DO I=1,NOSCCO(M)
        S=S+FCO(M,I)
        IF(S.GT.TST) THEN
          ISHELL=I
          GO TO 5
        ENDIF
      ENDDO
      ISHELL=NOSCCO(M)
    5 CONTINUE
      IF(EP.GT.E-UICO(M,ISHELL)) GO TO 4
C
    6 CONTINUE
      DE=E-EP
      IF(KSCO(M,ISHELL).LT.10) THEN
        IF(UICO(M,ISHELL).GT.ECUTR(M)) THEN
          ES=DE-UICO(M,ISHELL)
        ELSE
          ES=DE
        ENDIF
      ELSE
        ES=DE
      ENDIF
C
      Q2=E*E+EP*(EP-2.0D0*E*CDT)
      IF(Q2.GT.1.0D-12) THEN
        CDTS=(E-EP*CDT)/SQRT(Q2)
      ELSE
        CDTS=1.0D0
      ENDIF
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE GCOaT
C  *********************************************************************
      SUBROUTINE GCOaT(E,CS,M)
C
C  Total cross section for incoherent (Compton) scattering. Relativistic
C  Impulse approximation with analytical Compton profiles.
C
C  Input arguments:
C    E ........ photon energy (eV).
C    M ........ material where photons propagate.
C  Output argument:
C    CS ....... incoherent total cross section (cm**2/molecule).
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (MAXMAT=10)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (RREV=1.0D0/REV)
      PARAMETER (ELRAD=2.817940325D-13)  ! Class. electron radius (cm)
      PARAMETER (PI=3.1415926535897932D0, PIELR2=PI*ELRAD*ELRAD)
C  ****  Compton scattering.
      PARAMETER (NOCO=128)
      COMMON/CGCO/FCO(MAXMAT,NOCO),UICO(MAXMAT,NOCO),FJ0(MAXMAT,NOCO),
     2  KZCO(MAXMAT,NOCO),KSCO(MAXMAT,NOCO),NOSCCO(MAXMAT)
C  ****  Partial cross sections of individual shells.
      DIMENSION SXCO(NOCO)
C
      COMMON/CGCO00/EE,MM,IOSC
      EXTERNAL GCOaD
C
      EE=E
      MM=M
C
      CS=0.0D0
      IF(E.LT.5.0D6) THEN
        DO IO=1,NOSCCO(M)
          IOSC=IO
          SXCO(IO)=FCO(M,IO)*PIELR2*SUMGA(GCOaD,-1.0D0,1.0D0,1.0D-6)
          CS=CS+SXCO(IO)
        ENDDO
      ELSE
C  ****  Klein-Nishina total cross section.
        EK=E*RREV
        EKS=EK*EK
        EK2=1.0D0+EK+EK
        EK1=EKS-EK2-1.0D0
        T0=1.0D0/(1.0D0+EK+EK)
        CSL=0.5D0*EKS*T0*T0+EK2*T0+EK1*LOG(T0)-1.0D0/T0
        DO IO=1,NOSCCO(M)
          TAU=(E-UICO(M,IO))/E
          IF(TAU.LT.T0) THEN
            CSKN=0.0D0
          ELSE
            CSU=0.5D0*EKS*TAU*TAU+EK2*TAU+EK1*LOG(TAU)-1.0D0/TAU
            CSKN=PIELR2*(CSU-CSL)/(EK*EKS)
          ENDIF
          SXCO(IO)=FCO(M,IO)*CSKN
          CS=CS+SXCO(IO)
        ENDDO
      ENDIF
      RETURN
      END
C  *********************************************************************
C                        FUNCTION GCOaD
C  *********************************************************************
      FUNCTION GCOaD(CDT)
C
C  Single differential cross section for photon Compton scattering by
C  electrons in the IO-th shell, differential in the direction of the
C  scattered photon only. Evaluated from the incoherent scattering
C  function.
C
C  The energy E of the primary photon is entered through common CGCO00.
C  The output value GCOaD is the DCS per electron in units of PIELR2.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (MAXMAT=10)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (RREV=1.0D0/REV)
      PARAMETER (ELRAD=2.817940325D-13)  ! Class. electron radius (cm)
      PARAMETER (PI=3.1415926535897932D0, PIELR2=PI*ELRAD*ELRAD)
      PARAMETER (D2=1.4142135623731D0, D1=1.0D0/D2, D12=0.5D0)
C  ****  Compton scattering.
      PARAMETER (NOCO=128)
      COMMON/CGCO/FCO(MAXMAT,NOCO),UICO(MAXMAT,NOCO),FJ0(MAXMAT,NOCO),
     2  KZCO(MAXMAT,NOCO),KSCO(MAXMAT,NOCO),NOSCCO(MAXMAT)
C
      COMMON/CGCO00/E,M,IO
C
      IF(E.LT.UICO(M,IO)) THEN
        GCOaD=0.0D0
        RETURN
      ENDIF
C  ****  Energy of the Compton line.
      CDT1=1.0D0-CDT
      EOEC=1.0D0+(E*RREV)*CDT1
      ECOE=1.0D0/EOEC
C  ****  Klein-Nishina X-factor.
      XKN=EOEC+ECOE-1.0D0+CDT*CDT
C  ****  Incoherent scattering function (analytical profile).
      AUX=E*(E-UICO(M,IO))*CDT1
      PIMAX=(AUX-REV*UICO(M,IO))/(REV*SQRT(AUX+AUX+UICO(M,IO)**2))
      IF(PIMAX.GT.0.0D0) THEN
        SIA=1.0D0-0.5D0*EXP(D12-(D1+D2*FJ0(M,IO)*PIMAX)**2)
      ELSE
        SIA=0.5D0*EXP(D12-(D1-D2*FJ0(M,IO)*PIMAX)**2)
      ENDIF
C  ****  1st order correction, integral of Pz times the Compton profile.
C        Calculated approximately using a free-electron gas profile.
      PF=3.0D0/(4.0D0*FJ0(M,IO))
      IF(ABS(PIMAX).LT.PF) THEN
        QCOE2=1.0D0+ECOE**2-2.0D0*ECOE*CDT
        P2=PIMAX**2
        DSPZ=SQRT(QCOE2)*(1.0D0+ECOE*(ECOE-CDT)/QCOE2)
     1      *FJ0(M,IO)*0.25D0*(2*P2-P2**2/PF**2-PF**2)
        SIA=SIA+MAX(DSPZ,-SIA)
      ENDIF
C  ****  Differential cross section (per electron, in units of PIELR2).
      GCOaD=ECOE**2*XKN*SIA
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE GPHa
C  *********************************************************************
      SUBROUTINE GPHa(ES,IZZ,ISH)
C
C  Simulation of photoelectric absorption in material M.
C
C  Output arguments:
C    ES .... kinetic energy of the photoelectron.
C    IZZ ... atomic number of the element where absorption has occurred.
C    ISH ... atomic electron shell that has been ionised.
C
C  NOTE: JUMP uses a photoelectric cross section that is slightly larger
C  than its 'true' value. To correct for this, the photon is allowed to
C  'survive' a photoelectric event. Survival of the photon is flagged by
C  setting IZZ=0, ISH=0, ES=0.0D0 (the energy E of the photon is kept
C  unaltered.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*2 LASYMB
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C  ****  Simulation parameters.
      PARAMETER (MAXMAT=10)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
      COMMON/CECUTR/ECUTR(MAXMAT)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Element data.
      COMMON/CADATA/ATW(99),EPX(99),RSCR(99),ETA(99),EB(99,30),
     1  IFI(99,30),IKS(99,30),NSHT(99),LASYMB(99)
C  ****  Composition data.
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****  Photon simulation tables.
      COMMON/CGIMFP/SGRA(MAXMAT,NEGP),SGCO(MAXMAT,NEGP),
     1  SGPH(MAXMAT,NEGP),SGPP(MAXMAT,NEGP),SGAUX(MAXMAT,NEGP)
C  ****  Photoelectric cross sections.
      PARAMETER (NTP=8000)
      COMMON/CGPH00/EPH(NTP),XPH(NTP,17),IPHF(99),IPHL(99),NPHS(99),NCUR
      DIMENSION ACP(35),IP(35)
C
      PARAMETER (PI=3.1415926535897932D0, TWOPI=PI+PI)
C
      EXTERNAL RAND
C
C  ****  Partial attenuation coefficients.
C
      PTOT=0.0D0
      DO IEL=1,NELEM(M)
        IZZ=IZ(M,IEL)
C  ****  Binary search.
        I=IPHF(IZZ)
        IU=IPHL(IZZ)
    1   IT=(I+IU)/2
        IF(XEL.GT.EPH(IT)) THEN
          I=IT
        ELSE
          IU=IT
        ENDIF
        IF(IU-I.GT.1) GO TO 1
C
        IP(IEL)=I
        DEE=EPH(I+1)-EPH(I)
        IF(DEE.GT.1.0D-15) THEN
          PCSL=XPH(I,1)+(XPH(I+1,1)-XPH(I,1))*(XEL-EPH(I))/DEE
        ELSE
          PCSL=XPH(I,1)
        ENDIF
        PTOT=PTOT+STF(M,IEL)*EXP(PCSL)
        ACP(IEL)=PTOT
      ENDDO
      IF(PTOT*VMOL(M).GT.SGPH(M,KE)) THEN
        WRITE(26,*) 'WARNING: SGPH is less than the actual mac.'
      ENDIF
C
C  ****  Sample the active element.
C
      TST=RAND(1.0D0)*SGPH(M,KE)/VMOL(M)
      DO IEL=1,NELEM(M)
        IF(ACP(IEL).GT.TST) THEN
          IELAC=IEL
          IZZ=IZ(M,IEL)
          GO TO 2
        ENDIF
      ENDDO
C  ****  Delta interaction. Introduced to correct for the use of an
C        upper bound of the photoelectric attenuation coefficient.
      IZZ=0  ! Flags delta interactions.
      ISH=0
      ES=0.0D0
      RETURN
C
    2 CONTINUE
C  ****  Selection of the active shell.
      I=IP(IELAC)
      DEE=EPH(I+1)-EPH(I)
      PIS=0.0D0
      IF(DEE.GT.1.0D-15) THEN
        PTOT=EXP(XPH(I,1)+(XPH(I+1,1)-XPH(I,1))*(XEL-EPH(I))/DEE)
        TST=RAND(2.0D0)*PTOT
        DO IS=1,NPHS(IZZ)
          J=IS+1
          PCSL=XPH(I,J)+(XPH(I+1,J)-XPH(I,J))*(XEL-EPH(I))/DEE
          PIS=PIS+EXP(PCSL)
          IF(PIS.GT.TST) THEN
            ISH=IS
            GO TO 3
          ENDIF
        ENDDO
      ELSE
        PTOT=EXP(XPH(I,1))
        TST=RAND(2.0D0)*PTOT
        DO IS=1,NPHS(IZZ)
          PIS=PIS+EXP(XPH(I,IS+1))
          IF(PIS.GT.TST) THEN
            ISH=IS
            GO TO 3
          ENDIF
        ENDDO
      ENDIF
      ISH=17
C
C  ****  Photoelectron emission.
C
    3 CONTINUE
      IF(ISH.LT.17) THEN
        EBB=EB(IZZ,ISH)
        IF(EBB.GT.ECUTR(M)) THEN
          ES=E-EBB
        ELSE
          ES=E
          ISH=17
        ENDIF
      ELSE
        ES=E
      ENDIF
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE SAUTER
C  *********************************************************************
      SUBROUTINE SAUTER(ES,CDTS)
C
C  Random sampling of the initial direction of photoelectrons from the
C  Sauter distribution.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      EXTERNAL RAND
C
      IF(ES.GT.1.0D9) THEN
        CDTS=1.0D0
        RETURN
      ENDIF
      GAM=1.0D0+ES/REV
      GAM2=GAM*GAM
      BETA=SQRT((GAM2-1.0D0)/GAM2)
      AC=1.0D0/BETA-1.0D0
      A1=0.5D0*BETA*GAM*(GAM-1.0D0)*(GAM-2.0D0)
      A2=AC+2.0D0
      GTMAX=2.0D0*(A1+1.0D0/AC)
    1 CONTINUE
      RU=RAND(1.0D0)
      TSAM=2.0D0*AC*(2.0D0*RU+A2*SQRT(RU))/(A2*A2-4.0D0*RU)
      GTR=(2.0D0-TSAM)*(A1+1.0D0/(AC+TSAM))
      IF(RAND(2.0D0)*GTMAX.GT.GTR) GO TO 1
      CDTS=1.0D0-TSAM
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE GPHaR
C  *********************************************************************
      SUBROUTINE GPHaR(M,IRD,IWR,INFO)
C
C  This subroutine reads photoelectric cross sections of the elements in
C  material M and prepares simulation tables.
C
C  NOTE: The array SGPH(M,IE) defines a piecewise constant function that
C  is larger than the actual photoelectric cross section. SGPH(M,IE) is
C  defined as the largest value of the photoelectric x-section in the
C  energy interval from ET(IE) to ET(IE+1). The photon mean free path is
C  sampled by using this 'augmented' cross section and, to compensate
C  for this, the photon survives (i.e., it is not absorbed) with a prob-
C  ability such that the 'exact' photoelectric attenuation coefficient
C  is reproduced. This trick allows subroutine JUMP to disregard the
C  existence of absorption edges in the photoelectric x-section and to
C  perform the tracking of photons faster.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*2 LASYMB
      CHARACTER CS5(17)*5
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
      COMMON/CECUTR/ECUTR(MAXMAT)
C  ****  Element data.
      COMMON/CADATA/ATW(99),EPX(99),RSCR(99),ETA(99),EB(99,30),
     1  IFI(99,30),IKS(99,30),NSHT(99),LASYMB(99)
C  ****  Photon simulation tables.
      COMMON/CGIMFP/SGRA(MAXMAT,NEGP),SGCO(MAXMAT,NEGP),
     1  SGPH(MAXMAT,NEGP),SGPP(MAXMAT,NEGP),SGAUX(MAXMAT,NEGP)
C  ****  Photoelectric cross sections.
      PARAMETER (NTP=8000)
      COMMON/CGPH00/EPH(NTP),XPH(NTP,17),IPHF(99),IPHL(99),NPHS(99),NCUR
      PARAMETER (NDIM=1500)
      COMMON/CGPH01/ER(NDIM),XSR(NDIM),NPHD
      DIMENSION XGPHR(NDIM,17),X1(NDIM),Y1(NDIM),X2(NDIM),Y2(NDIM),
     1  ISH(17)
C
      CS5(1)='total'
      CS5(2)='CS-K '
      CS5(3)='CS-L1'
      CS5(4)='CS-L2'
      CS5(5)='CS-L3'
      CS5(6)='CS-M1'
      CS5(7)='CS-M2'
      CS5(8)='CS-M3'
      CS5(9)='CS-M4'
      CS5(10)='CS-M5'
      CS5(11)='CS-N1'
      CS5(12)='CS-N2'
      CS5(13)='CS-N3'
      CS5(14)='CS-N4'
      CS5(15)='CS-N5'
      CS5(16)='CS-N6'
      CS5(17)='CS-N7'
C
C  ************  Read element x-section tables
C
      DO IEL=1,NELEM(M)
        READ(IRD,1001) IZZ,NSHR,NDATA
 1001   FORMAT(41X,I3,11X,I3,10X,I4)
        IF(INFO.GE.2) WRITE(IWR,2001) IZZ,NSHR,NDATA
 2001   FORMAT(/1X,'***  Photoelectric cross sections,  IZ =',I3,
     1    ',  NSHELL =',I3,',  NDATA =',I4)
        IF(IZZ.NE.IZ(M,IEL))
     1    CALL PISTOP('GPHaR. Corrupt material data file.')
        IF(NDATA.GT.NDIM) CALL PISTOP('GPHaR. Too many data points.')
        IF(NSHR.GT.16) CALL PISTOP ('GPHaR. Too many shells.')
        READ(IRD,*) (ISH(IS),IS=1,NSHR+1)
        DO IE=1,NDATA
          READ(IRD,*) ER(IE),(XGPHR(IE,IS),IS=1,NSHR+1)
        ENDDO
C
C  ****  Remove shells with ionisation energies less than 50 eV.
C
        IF(NSHR.GT.1) THEN
          NSHA=NSHR
          DO IS=NSHA+1,2,-1
            IF(EB(IZZ,ISH(IS)).LT.50.0D0) THEN
              NSHR=NSHR-1
            ELSE
              GO TO 1
            ENDIF
          ENDDO
          IF(NSHR.LT.0) NSHR=0
        ENDIF
    1   CONTINUE
C
        IF(INFO.GE.2) THEN
          WRITE(IWR,'(/3X,''Energy'',7X,60(A,7X))')
     1      (CS5(ISH(IS)+1),IS=1,NSHR+1)
          DO IE=1,NDATA
            WRITE(IWR,'(1P,26E12.5)') ER(IE),(XGPHR(IE,IS),IS=1,NSHR+1)
          ENDDO
        ENDIF
C
        IF(NPHS(IZZ).EQ.0) THEN
          IPHF(IZZ)=NCUR+1
          IF(NCUR+NDATA.GT.NTP) THEN
            WRITE(IWR,*) 'Insufficient memory storage in GPHaR.'
            WRITE(IWR,*) 'Increase the value of the parameter NTP to',
     1        NCUR+NDATA
            WRITE(26,*) 'Insufficient memory storage in GPHaR.'
            WRITE(26,*) 'Increase the value of the parameter NTP to',
     1        NCUR+NDATA
            CALL PISTOP('GPHaR. Insufficient memory storage.')
          ENDIF
          DO IE=1,NDATA
            IC=NCUR+IE
            EPH(IC)=LOG(ER(IE))
            DO IS=1,NSHR+1
              XPH(IC,ISH(IS)+1)=LOG(MAX(XGPHR(IE,ISH(IS)+1),1.0D-35))
            ENDDO
          ENDDO
          NCUR=NCUR+NDATA
          IPHL(IZZ)=NCUR
          NPHS(IZZ)=NSHR
        ENDIF
      ENDDO
C
C  ****  Total photoelectric attenuation coefficient.
C
      IZZ=IZ(M,1)
      IST=IPHF(IZZ)
      LST=IPHL(IZZ)
      NPHD=0
      DO I=IST,LST
        NPHD=NPHD+1
        ER(NPHD)=EXP(EPH(I))
        XSR(NPHD)=STF(M,1)*EXP(XPH(I,1))
      ENDDO
      IF(NELEM(M).GT.1) THEN
        DO IEL=2,NELEM(M)
          N1=NPHD
          DO I=1,N1
            X1(I)=ER(I)
            Y1(I)=XSR(I)
          ENDDO
          IZZ=IZ(M,IEL)
          IST=IPHF(IZZ)
          LST=IPHL(IZZ)
          N2=0
          DO I=IST,LST
            N2=N2+1
            X2(N2)=EXP(EPH(I))
            Y2(N2)=STF(M,IEL)*EXP(XPH(I,1))
          ENDDO
          CALL MERGE2(X1,Y1,X2,Y2,ER,XSR,N1,N2,NPHD)
        ENDDO
      ENDIF
C
C  ****  Total photoelectric cross section at the simulation grid points
C        (slightly increased to simplify the interpolation).
C
      DO I=1,NPHD
        X1(I)=LOG(ER(I))
        Y1(I)=LOG(XSR(I)*VMOL(M))
      ENDDO
C
      DO IE=1,NEGP-1
        EG1=DLEMP(IE)
        CALL FINDI(X1,EG1,NPHD,I1)
        IF(I1.EQ.NPHD) I1=NPHD-1
        DX=X1(I1+1)-X1(I1)
        IF(DX.GT.1.0D-15) THEN
          F1=Y1(I1)+(Y1(I1+1)-Y1(I1))*(EG1-X1(I1))/DX
        ELSE
          F1=Y1(I1)
        ENDIF
        EG2=DLEMP(IE+1)
        CALL FINDI(X1,EG2,NPHD,I2)
        IF(I2.EQ.NPHD) I2=NPHD-1
        DX=X1(I2+1)-X1(I2)
        IF(DX.GT.1.0D-15) THEN
          F2=Y1(I2)+(Y1(I2+1)-Y1(I2))*(EG2-X1(I2))/DX
        ELSE
          F2=Y1(I2)
        ENDIF
C  ****  To avoid interpolating the attenuation coefficient tables, we
C        replace the photoelectric inverse mean free path (imfp) in each
C        energy interval by its upper bound. The increase of the imfp
C        is interpreted as the imfp of delta interactions.
        FM=MAX(F1,F2)
        IF(I1+1.LE.I2) THEN
          DO I=I1+1,I2
           FM=MAX(FM,Y1(I))
          ENDDO
        ENDIF
        SGPH(M,IE)=EXP(FM)
      ENDDO
      SGPH(M,NEGP)=SGPH(M,NEGP-1)
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE GPHa0
C  *********************************************************************
      SUBROUTINE GPHa0
C
C  This subroutine sets all variables in common /CGPH00/ to zero.
C  It has to be invoked before reading the first material definition
C  file.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*2 LASYMB
C  ****  Element data.
      COMMON/CADATA/ATW(99),EPX(99),RSCR(99),ETA(99),EB(99,30),
     1  IFI(99,30),IKS(99,30),NSHT(99),LASYMB(99)
C  ****  Photoelectric cross sections.
      PARAMETER (NTP=8000)
      COMMON/CGPH00/EPH(NTP),XPH(NTP,17),IPHF(99),IPHL(99),NPHS(99),NCUR
C
      DO I=1,99
        NPHS(I)=0
        IPHF(I)=0
        IPHL(I)=0
      ENDDO
C
      DO I=1,NTP
        EPH(I)=0.0D0
        DO J=1,17
          XPH(I,J)=1.0D-35
        ENDDO
      ENDDO
      NCUR=0
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE GPHaW
C  *********************************************************************
      SUBROUTINE GPHaW(M,IWR)
C
C  This subroutine generates the table of photoelectric cross sections
C  for photons in material M and writes it on the material data file.
C  Data are read from the files 'pdgphZZ.p08'.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C
      CHARACTER*12 FILEN
      CHARACTER*1 LDIG(10),LDIG1,LDIG2,LNULL
      DATA LDIG/'0','1','2','3','4','5','6','7','8','9'/
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C
      PARAMETER (NPHM=400)
      DIMENSION XS(17),E0(NPHM),XS0(NPHM,17),ISH(17)
C
      DO IEL=1,NELEM(M)
        IZZ=IZ(M,IEL)
        NLD=IZZ
        NLD1=NLD-10*(NLD/10)
        NLD2=(NLD-NLD1)/10
        LDIG1=LDIG(NLD1+1)
        LDIG2=LDIG(NLD2+1)
        FILEN='pdgph'//LDIG2//LDIG1//'.p11'
        OPEN(3,FILE='./pdfiles/'//FILEN)
        READ(3,'(15X,I2,1X,I3,1X,I2)') IZZZ,NGP,NSHR
        IF(NGP.GT.NPHM) CALL PISTOP('GPHaW. Too many energies.')
        IF(IZZZ.NE.IZZ) CALL PISTOP('GPHaW. Corrupt file.')
        IF(NSHR.GT.16) CALL PISTOP('GPHaW. Too many shells.')
        ISH(1)=0
        READ(3,'(25X,60(I2,10X))') (ISH(IS),IS=2,NSHR+1)
        READ(3,'(A)') LNULL
        NPTAB=0
        DO IE=1,NGP
          READ(3,*,END=1) ER,(XS(IS),IS=1,NSHR+1)
          IF(ER.GT.49.9D0.AND.ER.LT.1.01D9) THEN
            NPTAB=NPTAB+1
            E0(NPTAB)=ER
            DO IS=1,NSHR+1
              XS0(NPTAB,IS)=XS(IS)*1.0D-24
            ENDDO
          ENDIF
        ENDDO
    1   CONTINUE
        CLOSE(3)
        WRITE(IWR,2001) IZZ,NSHR,NPTAB
 2001 FORMAT(1X,'***  Photoelectric cross sections,  IZ =',I3,
     1  ',  NSHELL =',I3,',  NDATA =',I4)
        WRITE(IWR,'(13X,60(I2,10X))') 0,(ISH(IS),IS=2,NSHR+1)
        DO IE=1,NPTAB
          WRITE(IWR,'(1P,26E12.5)') E0(IE),(XS0(IE,IS),IS=1,NSHR+1)
        ENDDO
      ENDDO
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE GPPa
C  *********************************************************************
      SUBROUTINE GPPa(EE,CDTE,EP,CDTP,IZZ,ISH)
C
C  Random sampling of electron-positron pair and triplet production by
C  photons. Bethe-Heitler differential cross section.
C
C  Output values:
C    EE .....  kinetic energy of the electron.
C    CDTE ...  polar direction cosine of the electron.
C    EP .....  kinetic energy of the positron.
C    CDTP ...  polar direction cosine of the positron.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (SL=137.03599911D0)  ! Speed of light (1/alpha)
      PARAMETER (PI=3.1415926535897932D0, TWOPI=PI+PI, TREV=2.0D0*REV)
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Simulation parameters.
      PARAMETER (MAXMAT=10)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
      COMMON/CECUTR/ECUTR(MAXMAT)
C
      PARAMETER (NOCO=128)
      COMMON/CGCO/FCO(MAXMAT,NOCO),UICO(MAXMAT,NOCO),FJ0(MAXMAT,NOCO),
     2  KZCO(MAXMAT,NOCO),KSCO(MAXMAT,NOCO),NOSCCO(MAXMAT)
C  ****  Pair-production cross section parameters.
      COMMON/CGPP00/ZEQPP(MAXMAT),F0(MAXMAT,2),BCB(MAXMAT)
      COMMON/CGPP01/TRIP(MAXMAT,NEGP),PKSCO(MAXMAT,NOCO)
C
      EXTERNAL RAND
C
      EKI=REV/E
      IF(E.LT.1.1D6) THEN
        EPS=EKI+(1.0D0-2.0D0*EKI)*RAND(1.0D0)
        GO TO 3
      ENDIF
C  ****  Low-energy and Coulomb corrections.
      ALZ=ZEQPP(M)/SL
      T=SQRT(2.0D0*EKI)
      F00=(-1.774D0-1.210D1*ALZ+1.118D1*ALZ*ALZ)*T
     1    +(8.523D0+7.326D1*ALZ-4.441D1*ALZ*ALZ)*T**2
     2    -(1.352D1+1.211D2*ALZ-9.641D1*ALZ*ALZ)*T**3
     3    +(8.946D0+6.205D1*ALZ-6.341D1*ALZ*ALZ)*T**4
      G0=F0(M,2)+F00
      BMIN=4.0D0*EKI/BCB(M)
      CALL SCHIFF(BMIN,G1,G2)
      G1MIN=G1+G0
      G2MIN=G2+G0
      XR=0.5D0-EKI
      A1=6.666666666666666D-1*G1MIN*XR**2
      P1=A1/(A1+G2MIN)
C  ****  Random sampling of EPS.
    1 CONTINUE
      IF(RAND(2.0D0).GT.P1) GO TO 2
      RU2M1=2.0D0*RAND(3.0D0)-1.0D0
      IF(RU2M1.LT.0.0D0) THEN
        EPS=0.5D0-XR*ABS(RU2M1)**3.333333333333333D-1
      ELSE
        EPS=0.5D0+XR*RU2M1**3.333333333333333D-1
      ENDIF
      B=EKI/(BCB(M)*EPS*(1.0D0-EPS))
      CALL SCHIFF(B,G1,G2)
      G1=MAX(G1+G0,0.0D0)
      IF(RAND(4.0D0)*G1MIN.GT.G1) GO TO 1
      GO TO 3
    2 CONTINUE
      EPS=EKI+2.0D0*XR*RAND(5.0D0)
      B=EKI/(BCB(M)*EPS*(1.0D0-EPS))
      CALL SCHIFF(B,G1,G2)
      G2=MAX(G2+G0,0.0D0)
      IF(RAND(6.0D0)*G2MIN.GT.G2) GO TO 1
    3 CONTINUE
C  ****  Electron.
      EE=EPS*E-REV
      IF(EE.GT.EABS(1,M)) THEN
        CDTE=2.0D0*RAND(7.0D0)-1.0D0
        A1=EE+REV
        A2=SQRT(EE*(EE+TREV))
        CDTE=(CDTE*A1+A2)/(A1+CDTE*A2)
      ELSE
        CDTE=1.0D0
      ENDIF
C  ****  Positron.
      EP=(1.0D0-EPS)*E-REV
      IF(EP.GT.EABS(3,M)) THEN
        CDTP=2.0D0*RAND(8.0D0)-1.0D0
        A1=EP+REV
        A2=SQRT(EP*(EP+TREV))
        CDTP=(CDTP*A1+A2)/(A1+CDTP*A2)
      ELSE
        CDTP=1.0D0
      ENDIF
C
C  ****  Triplet production.
C
      TRIPL=TRIP(M,KE)+(TRIP(M,KE+1)-TRIP(M,KE))*XEK
      IZZ=0
      ISH=30
      IF(TRIPL.LT.1.0D-5) RETURN
      IF(RAND(9.0D0).GT.TRIPL) RETURN
      TST=RAND(10.0D0)
      IOSC=1
      JO=NOSCCO(M)+1
    4 IT=(IOSC+JO)/2
      IF(TST.GT.PKSCO(M,IT)) THEN
        IOSC=IT
      ELSE
        JO=IT
      ENDIF
      IF(JO-IOSC.GT.1) GO TO 4
      IF(UICO(M,IOSC).LT.ECUTR(M)) RETURN
      IZZ=KZCO(M,IOSC)
      ISH=KSCO(M,IOSC)
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE SCHIFF
C  *********************************************************************
      SUBROUTINE SCHIFF(B,G1,G2)
C
C  Screening functions F1(B) and F2(B) in the Bethe-Heitler differential
C  cross section for pair production.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (PI=3.1415926535897932D0, TWOPI=PI+PI)
      B2=B*B
      F1=2.0D0-2.0D0*LOG(1.0D0+B2)
      F2=F1-6.666666666666666D-1
      IF(B.LT.1.0D-10) THEN
        F1=F1-TWOPI*B
      ELSE
        A0=4.0D0*B*ATAN2(1.0D0,B)
        F1=F1-A0
        F2=F2+2.0D0*B2*(4.0D0-A0-3.0D0*LOG((1.0D0+B2)/B2))
      ENDIF
      G1=0.5D0*(3.0D0*F1-F2)
      G2=0.25D0*(3.0D0*F1+F2)
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE GPPa0
C  *********************************************************************
      SUBROUTINE GPPa0(M)
C
C  Initialisation of the sampling algorithm for electron-positron pair
C  production by photons in material M. Bethe-Heitler differential cross
C  section.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (SL=137.03599911D0)  ! Speed of light (1/alpha)
C  ****  Element data.
      CHARACTER*2 LASYMB
      COMMON/CADATA/ATW(99),EPX(99),RSCR(99),ETA(99),EB(99,30),
     1  IFI(99,30),IKS(99,30),NSHT(99),LASYMB(99)
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****  Pair-production cross section parameters.
      COMMON/CGPP00/ZEQPP(MAXMAT),F0(MAXMAT,2),BCB(MAXMAT)
C
C  ***  Effective atomic number.
C
      FACT=0.0D0
      DO I=1,NELEM(M)
        IZZ=IZ(M,I)
        FACT=FACT+IZZ*ATW(IZZ)*STF(M,I)
      ENDDO
      ZEQPP(M)=FACT/AT(M)
      IZZ=ZEQPP(M)+0.25D0
      IF(IZZ.LE.0) IZZ=1
      IF(IZZ.GT.99) IZZ=99
C  ****  DBM Coulomb correction.
      ALZ=ZEQPP(M)/SL
      A=ALZ*ALZ
      FC=A*(0.202059D0-A*(0.03693D0-A*(0.00835D0-A*(0.00201D0-A*
     1 (0.00049D0-A*(0.00012D0-A*0.00003D0)))))+1.0D0/(A+1.0D0))
C  ****  Screening functions and low-energy correction.
      BCB(M)=2.0D0/RSCR(IZZ)
      F0(M,1)=4.0D0*LOG(RSCR(IZZ))
      F0(M,2)=F0(M,1)-4.0D0*FC
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE GPPaW
C  *********************************************************************
      SUBROUTINE GPPaW(EIT,XGP0,XGT0,NPTAB,M)
C
C  This subroutine generates a table of electron-positron pair produc-
C  tion cross sections for photons in material M. Data are read from the
C  files 'pdgppZZ.p11'.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C
      CHARACTER*12 FILEN
      CHARACTER*1 LDIG(10),LDIG1,LDIG2
      DATA LDIG/'0','1','2','3','4','5','6','7','8','9'/
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****
      PARAMETER (NEGP=1500)
      DIMENSION EIT(NEGP),XGP0(NEGP),XGT0(NEGP)
C
C  ****  Building the cross section table.
C
      DO I=1,NEGP
        XGP0(I)=0.0D0
        XGT0(I)=0.0D0
      ENDDO
C
      DO IEL=1,NELEM(M)
        IZZ=IZ(M,IEL)
        WGHT=STF(M,IEL)*1.0D-24
        NLD=IZZ
        NLD1=NLD-10*(NLD/10)
        NLD2=(NLD-NLD1)/10
        LDIG1=LDIG(NLD1+1)
        LDIG2=LDIG(NLD2+1)
        FILEN='pdgpp'//LDIG2//LDIG1//'.p11'
        OPEN(3,FILE='./pdfiles/'//FILEN)
        READ(3,*) IZZZ
        IF(IZZZ.NE.IZZ) CALL PISTOP('GPPaW. Corrupt file.')
        DO I=1,NEGP
          READ(3,*,END=1) EIT(I),XG0P,XG0T
          XGP0(I)=XGP0(I)+WGHT*XG0P
          XGT0(I)=XGT0(I)+WGHT*XG0T
          NPTAB=I
          IF(EIT(I).GT.0.999D9) GO TO 1
        ENDDO
    1   CONTINUE
        CLOSE(3)
      ENDDO
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE RELAX
C  *********************************************************************
      SUBROUTINE RELAX(IZ,IS)
C
C  This subroutine simulates the relaxation of a singly ionised atom of
C  the element IZ with a vacancy in the IS shell (the K shell or an L
C  or M subshell). This initial vacancy is filled by electrons from
C  outer shells through radiative and non-radiative transitions, which
C  may produce additional vacancies.
C
C  We use the following notation to designate the possible transitions:
C  *  Radiative: IS0-IS1 (an electron from the IS1 shell fills the
C     vacancy in the IS0 shell, leaving a hole in the IS1 shell).
C  *  Non-radiative: IS0-IS1-IS2 (an electron from the IS1 shell fills
C     the vacancy in the IS0 shell, and the released energy is taken
C     away by an electron in the IS2 shell; this process leaves two
C     holes, in the IS1 and IS2 shells).
C  The de-excitation cascade (i.e. the set of transitions that occur for
C  a given initial vacancy) is sampled from the transition probabilities
C  contained in the Livermore Evaluated Atomic Data Library (EADL). The
C  energy of the radiation emitted in each transition is read from the
C  PENELOPE database.
C
C  The simulation of the de-excitation cascade is discontinued either
C  when the K, L and M shells have been filled up or when there is not
C  enough energy to produce 'active' radiation (with energy larger than
C  EABS). The excitation energy of the residual ion is assumed to be
C  deposited locally. We disregard the emission and transport of soft
C  x-rays and slow electrons, whose energies are less than the binding
C  energy of the N1 shell of the heavier element in the medium. This
C  sets a lower limit for the energy interval that can be covered by the
C  simulation program in a consistent way.
C
C  De-excitation data for the loaded elements are stored in the common
C  block /CRELAX/, in a form designed to minimise the amount of memory
C  and to facilitate the random sampling. The quantities in the common
C  block are the following:
C  IFIRST(99,16) ... de-excitation data for a vacancy in the shell IS of
C     the element IZ start at the position K=IFIRST(IZ,IS) in the
C     storage arrays. The allowed values for IS are 1 to 16 (K shell
C     and L, M and N subshells).
C  ILAST(99,16) ... the de-excitation data for a vacancy in the shell
C     IS of the element IZ end at the position K=ILAST(IZ,IS) in the
C     storage arrays.
C  IS1(K), IS2(K) ... shells that are active in the transition (see the
C     shell label code below). For radiative transitions, IS2(K)=0.
C  P(K) ... relative probability for the transition IS-IS1(K)-IS2(K).
C  ET(K) ... energy of the secondary particle emitted in the transition.
C  F(K), IAL(K) ... cutoff and alias values (Walker's sampling method).
C
C  ---------------------------------------------------------------------
C  Label code IS for electron shells:
C      1 = K  (1s1/2),     11 = N2 (4p1/2),     21 = O5 (5d5/2),
C      2 = L1 (2s1/2),     12 = N3 (4p3/2),     22 = O6 (5f5/2),
C      3 = L2 (2p1/2),     13 = N4 (4d3/2),     23 = O7 (5f7/2),
C      4 = L3 (2p3/2),     14 = N5 (4d5/2),     24 = P1 (6s1/2),
C      5 = M1 (3s1/2),     15 = N6 (4f5/2),     25 = P2 (6p1/2),
C      6 = M2 (3p1/2),     16 = N7 (4f7/2),     26 = P3 (6p3/2),
C      7 = M3 (3p3/2),     17 = O1 (5s1/2),     27 = P4 (6d3/2),
C      8 = M4 (3d3/2),     18 = O2 (5p1/2),     28 = P5 (6d5/2),
C      9 = M5 (3d5/2),     19 = O3 (5p3/2),     29 = Q1 (7s1/2),
C     10 = N1 (4s1/2),     20 = O4 (5d3/2),     30 = outer shells.
C  ---------------------------------------------------------------------
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*2 LASYMB
      PARAMETER (PI=3.1415926535897932D0, TWOPI=PI+PI)
      DIMENSION ISV(256)
C  ****  Element data.
      COMMON/CADATA/ATW(99),EPX(99),RSCR(99),ETA(99),EB(99,30),
     1  IFI(99,30),IKS(99,30),NSHT(99),LASYMB(99)
C  ****  Main-PENELOPE commons.
      PARAMETER (MAXMAT=10)
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
      COMMON/CECUTR/ECUTR(MAXMAT)
C  ****  Atomic relaxation data.
      PARAMETER (NRX=30000)
      COMMON/CRELAX/P(NRX),ET(NRX),F(NRX),IAL(NRX),IS1(NRX),IS2(NRX),
     1              IFIRST(99,16),ILAST(99,16),NCUR,KS,MODER
      COMMON/CHIST/ILBA(5)
C
      EXTERNAL RAND
C
C  ****  Initialisation.
C
      IF(IZ.LT.6.OR.IS.GT.16) RETURN
C  ****  If the shell ionisation energy is less than ECUTR, the cascade
C        is not followed.
      IF(EB(IZ,IS).LT.ECUTR(M)) RETURN
C
      NV=1
      ISV(1)=IS
C
C  ****  Next transition.
C
    1 CONTINUE
      ISP=ISV(NV)
      KF=IFIRST(IZ,ISP)
      KL=ILAST(IZ,ISP)
      NV=NV-1
      IF(KL.GT.KF) THEN
C  ****  Walker's sampling algorithm.
        RN=RAND(1.0D0)*(KL-KF+1)
        K1=INT(RN)
        TST=RN-K1
        IF(TST.GT.F(KF+K1)) THEN
          KS=IAL(KF+K1)
        ELSE
          KS=KF+K1
        ENDIF
      ELSE
        KS=KF
      ENDIF
C  ****  If MODER=0, control is returned to the calling program after
C  determining the first transition, KS. Useful for testing the random
C  sampling. For normal operation, we can comment out the following
C  statement.
      IF(MODER.EQ.0) RETURN
C
C  ****  Fluorescence radiation.
C
      IS1K=IS1(KS)
      IS2K=IS2(KS)
      IF(IS2K.EQ.0) THEN
        KPARS=2
        IF(IS1K.LT.17) THEN
          IF(EB(IZ,IS1K).GT.ECUTR(M)) THEN
            NV=NV+1
            ISV(NV)=IS1K
          ENDIF
        ENDIF
      ELSE
        KPARS=1
        IF(IS1K.LT.17) THEN
          IF(EB(IZ,IS1K).GT.ECUTR(M)) THEN
            NV=NV+1
            ISV(NV)=IS1K
          ENDIF
        ENDIF
        IF(IS2K.LT.17) THEN
          IF(EB(IZ,IS2K).GT.ECUTR(M)) THEN
            NV=NV+1
            ISV(NV)=IS2K
          ENDIF
        ENDIF
      ENDIF
C
C  ****  The emitted particle is stored in the secondary stack when
C        its energy ET(K) is greater than EABS.
C
      IF(ET(KS).GT.EABS(KPARS,M)) THEN
C  ****  Initial direction (isotropic).
        WS=-1.0D0+2.0D0*RAND(2.0D0)
        SDTS=SQRT(1.0D0-WS*WS)
        DF=TWOPI*RAND(3.0D0)
        US=COS(DF)*SDTS
        VS=SIN(DF)*SDTS
        ILBA(1)=ILB(1)+1
        ILBA(2)=KPAR
        ILBA(4)=IZ*1000000+ISP*10000+IS1K*100+IS2K
        ILBA(5)=ILB(5)
        CALL STORES(ET(KS),X,Y,Z,US,VS,WS,WGHT,KPARS,ILBA)
      ENDIF
C
C  ****  Are there any unfilled vacancies in inner shells?
C
      IF(NV.GT.0) GO TO 1
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE RELAXE
C  *********************************************************************
      SUBROUTINE RELAXE(IZ,JS0,JS1,JS2,ENERGY,TRPROB)
C
C  This subroutine gives the energy (ENERGY, in eV) and the probability
C  (PROB) of the transition JS0-JS1-JS2 of an atom of the element IZ
C  with an initial vacancy in shell JS0.
C
C  The output values ENERGY=1.0D35 and TRPROB=1.0D35 indicate that the
C  transition data are not loaded, or that the transition does not
C  exist.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Atomic relaxation data.
      PARAMETER (NRX=30000)
      COMMON/CRELAX/P(NRX),ET(NRX),F(NRX),IAL(NRX),IS1(NRX),IS2(NRX),
     1              IFIRST(99,16),ILAST(99,16),NCUR,KS,MODER
C
      ENERGY=1.0D35
      TRPROB=1.0D35
      IF(IZ.LT.1.OR.IZ.GT.99.OR.JS0.LT.1.OR.JS0.GT.16) RETURN
C
      N1=IFIRST(IZ,JS0)
      IF(N1.EQ.0) RETURN
      NL=ILAST(IZ,JS0)
      IF(NL.LT.N1) RETURN
C
      DO N=N1,NL
        IF(JS1.EQ.IS1(N).AND.JS2.EQ.IS2(N)) THEN
          ENERGY=ET(N)
          TRPROB=P(N)
          RETURN
        ENDIF
      ENDDO
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE RELAX0
C  *********************************************************************
      SUBROUTINE RELAX0
C
C  This subroutine sets all variables in common /CRELAX/ to zero.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*2 LASYMB
C  ****  Element data.
      COMMON/CADATA/ATW(99),EPX(99),RSCR(99),ETA(99),EB(99,30),
     1  IFI(99,30),IKS(99,30),NSHT(99),LASYMB(99)
C  ****  Atomic relaxation data.
      PARAMETER (NRX=30000)
      COMMON/CRELAX/P(NRX),ET(NRX),F(NRX),IS0(NRX),IS1(NRX),IS2(NRX),
     1              IFIRST(99,16),ILAST(99,16),NCUR,KS,MODER
C
      DO I=1,99
        NSHT(I)=0
        DO J=1,16
          IFIRST(I,J)=0
          ILAST(I,J)=0
        ENDDO
        DO J=1,30
          IFI(I,J)=0
          EB(I,J)=0.0D0
          IKS(I,J)=0
        ENDDO
      ENDDO
C
      DO I=1,NRX
        IS0(I)=0
        IS1(I)=0
        IS2(I)=0
        ET(I)=0.0D0
        P(I)=0.0D0
        F(I)=0.0D0
      ENDDO
      NCUR=0
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE RELAXR
C  *********************************************************************
      SUBROUTINE RELAXR(IRD,IWR,INFO)
C
C  This subroutine reads atomic relaxation data, for a single element,
C  from the material definition file (unit IRD) and initialises the
C  algorithm for random sampling of de-excitation cascades of this
C  element. (See heading comments in subroutine RELAX).
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*2 LASYMB
      CHARACTER*5 CH5
C  ****  Element data.
      COMMON/CADATA/ATW(99),EPX(99),RSCR(99),ETA(99),EB(99,30),
     1  IFI(99,30),IKS(99,30),NSHT(99),LASYMB(99)
C  ****  Atomic relaxation data.
      PARAMETER (NRX=30000, NTRAN=2500)
      COMMON/CRELAX/P(NRX),ET(NRX),F(NRX),IS0(NRX),IS1(NRX),IS2(NRX),
     1              IFIRST(99,16),ILAST(99,16),NCUR,KS,MODER
      DIMENSION JS0(NTRAN),JS1(NTRAN),JS2(NTRAN),PR(NTRAN),ER(NTRAN),
     1          WW(NTRAN),FF(NTRAN),KK(NTRAN),IORD(NTRAN),ISR(NTRAN),
     2          IQQ(30),EE(30)
C
      CHARACTER*2 LSHELL(0:30)
      DATA LSHELL/'  ','K ','L1','L2','L3','M1','M2','M3','M4','M5',
     1   'N1','N2','N3','N4','N5','N6','N7','O1','O2','O3','O4',
     1   'O5','O6','O7','P1','P2','P3','P4','P5','Q1','X '/
C
      MODER=1  ! RELAX normal operation mode.
C
C  ****  Input transition data.
C
      READ(IRD,5001) IZ,NSHR,NT
 5001 FORMAT(16X,I3,18X,I3,23X,I4)
      IF(INFO.GE.2) WRITE(IWR,2001) IZ,NSHR,NT
 2001 FORMAT(/1X,'*** RELAX:  Z =',I3,',  no. of shells =',I3,
     1          ',  no. of transitions =',I4)
      IF(NT.GT.NTRAN)
     1   CALL PISTOP('RELAXR. NTRAN needs to be increased.')
      IF(NCUR+NT.GT.NRX) THEN
        WRITE(IWR,*) 'Insufficient memory storage in RELAXR.'
        WRITE(IWR,*) 'Increase the value of the parameter NRX to',
     1    NCUR+NT
        WRITE(26,*) 'Insufficient memory storage in RELAXR.'
        WRITE(26,*) 'Increase the value of the parameter NRX to',
     1    NCUR+NT
        CALL PISTOP('RELAXR. Insufficient memory storage.')
      ENDIF
C
      IF(INFO.GE.2) WRITE(IWR,2002)
 2002 FORMAT(/2X,'i',2X,' Shell    f',5X,'Ui (eV)',/1X,28('-'))
      DO IS=1,NSHR
        READ(IRD,5002) ISR(IS),CH5,IQQ(IS),EE(IS)
 5002   FORMAT(1X,I3,1X,A5,1X,I1,E16.8)
        IF(INFO.GE.2) WRITE(IWR,2003) ISR(IS),CH5,LSHELL(ISR(IS)),
     1    IQQ(IS),EE(IS)
 2003   FORMAT(1X,I3,1X,A5,1X,A2,2X,I1,1P,E16.8)
      ENDDO
C
      IF(NT.GT.0) THEN
        IF(INFO.GE.2) WRITE(IWR,2004)
 2004   FORMAT(/2X,'S0 S1 S2',3X,'Probability',5X,'Energy (eV)',
     1    /1X,42('-'))
        DO I=1,NT
          READ(IRD,*) JS0(I),JS1(I),JS2(I),PR(I),ER(I)
          IF(INFO.GE.2) WRITE(IWR,2005) LSHELL(JS0(I)),LSHELL(JS1(I)),
     1      LSHELL(JS2(I)),PR(I),ER(I)
 2005     FORMAT(1X,3(1X,A2),1P,2E16.8)
          IF(PR(I).LT.1.0D-35) THEN
            IF(INFO.LT.2) WRITE(IWR,2005) LSHELL(JS0(I)),LSHELL(JS1(I)),
     1      LSHELL(JS2(I)),PR(I),ER(I)
            CALL PISTOP('RELAXR. Negative transition probability?')
          ENDIF
        ENDDO
      ENDIF
C
C  ****  Check if this element's data have already been loaded.
C
      IF(IFIRST(IZ,1).NE.0) RETURN
C
      NSHT(IZ)=NSHR
      DO IS=1,NSHR
        IFI(IZ,ISR(IS))=IQQ(IS)
        EB(IZ,ISR(IS))=EE(IS)
      ENDDO
      IF(NT.EQ.0) THEN
        DO IS=1,16
          IFIRST(IZ,IS)=NCUR+1
          ILAST(IZ,IS)=NCUR+1
C  ****  The array IS0 contains the alias values.
          IS0(NCUR+1)=NCUR+1
          P(NCUR+1)=1.0D0
          F(NCUR+1)=1.0D0
          ET(NCUR+1)=0.0D0
          IS1(NCUR+1)=1
          IS2(NCUR+1)=1
          NCUR=NCUR+1
        ENDDO
        RETURN
      ENDIF
C
C  ****  Walker's aliasing.
C
      DO IS=1,16
        N=0
        DO J=1,NT
          IF(JS0(J).EQ.IS) THEN
            N=N+1
            IORD(N)=J
            WW(N)=PR(J)
          ENDIF
        ENDDO
        IF(N.GT.1) THEN
          CALL IRND0(WW,FF,KK,N)
          IFIRST(IZ,IS)=NCUR+1
          ILAST(IZ,IS)=NCUR+N
          DO L=1,N
            P(NCUR+L)=WW(L)
            F(NCUR+L)=FF(L)
            ET(NCUR+L)=ER(IORD(L))
C  ****  The array IS0 contains the alias values.
            IS0(NCUR+L)=IFIRST(IZ,IS)+KK(L)-1
            IS1(NCUR+L)=JS1(IORD(L))
            IS2(NCUR+L)=JS2(IORD(L))
          ENDDO
          NCUR=NCUR+N
        ELSE
          NCUR=NCUR+1
          IFIRST(IZ,IS)=NCUR
          ILAST(IZ,IS)=NCUR
          IS0(NCUR+1)=NCUR
          P(NCUR)=1.0D0
          F(NCUR)=1.0D0
          ET(NCUR)=ER(1)
          IS1(NCUR)=JS1(1)
          IS2(NCUR)=JS2(1)
        ENDIF
      ENDDO
C
C  ****  Verify that transition probabilities are correctly reproduced.
C
      TST=0.0D0
      DO IS=1,16
        I0=IFIRST(IZ,IS)
        IN=ILAST(IZ,IS)
        PT=0.0D0
        DO I=I0,IN
          PT=PT+P(I)
        ENDDO
        DO I=I0,IN
          PPI=0.0D0
          DO J=I0,IN
            IF(IS0(J).EQ.I) PPI=PPI+(1.0D0-F(J))
          ENDDO
          PPI=(PPI+F(I))/DBLE(IN-I0+1)
          TST=MAX(TST,ABS(1.0D0-PPI*PT/P(I)))
        ENDDO
      ENDDO
      IF(TST.GT.1.0D-12)
     1  CALL PISTOP('RELAXR. Rounding error is too large.')
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE RELAXW
C  *********************************************************************
      SUBROUTINE RELAXW(IZ,IWR)
C
C  This subroutine produces a table of atomic relaxation data for the
C  element IZ, and prints it on unit IWR. The output table is part of
C  PENELOPE's material definition file.
C
C  Data are read from file 'pdrelax.p11', which contains data pertaining
C  to singly ionised atoms with the initial vacancy in one of the K, L,
C  M and N shells. This file was prepared from the Livermore Evaluated
C  Atomic Data Library (EADL). The energies of x-ray lines were replaced
C  by more accurate experimental and theoretical values given by
C  Deslattes et al. (2003) -K and L shells- and by Burr (1967) -M
C  shells.
C
C  NOTE: The transition probabilities and emission energies can be
C  modified by editing the material data file. For each initial vacancy,
C  the sum of transition probabilities _must_ be equal to unity.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*2 LASYMB
      CHARACTER*5 CSH5(30)
C  ****  ELEMENT DATA.
      COMMON/CADATA/ATW(99),EPX(99),RSCR(99),ETA(99),EB(99,30),
     1  IFI(99,30),IKS(99,30),NSHT(99),LASYMB(99)
C
      PARAMETER (NM=2500)
      DIMENSION IS0(NM),IS1(NM),IS2(NM),P(NM),EI(NM),EE(99)
C
      DATA CSH5/'1s1/2','2s1/2','2p1/2','2p3/2','3s1/2','3p1/2',
     1          '3p3/2','3d3/2','3d5/2','4s1/2','4p1/2','4p3/2',
     2          '4d3/2','4d5/2','4f5/2','4f7/2','5s1/2','5p1/2',
     3          '5p3/2','5d3/2','5d5/2','5f5/2','5f7/2','6s1/2',
     4          '6p1/2','6p3/2','6d3/2','6d5/2','7s1/2',' free'/
C
      IF(NSHT(IZ).LE.0)
     1  CALL PISTOP('RELAXW. The element is not loaded.')
C
      OPEN(3,FILE='./pdfiles/pdrelax.p11')
      READ(3,*,END=1) IZR,IS0R  ! Ignores the data.
      NT=0
      DO I=1,150000
        READ(3,*,END=1) IZR,IS0R,IS1R,IS2R,PR,EIN
        IF(IZR.EQ.IZ) THEN
          NT=NT+1
          IF(NT.GT.NM) CALL PISTOP('RELAXW. NM needs to be increased.')
          IS0(NT)=IS0R
          IS1(NT)=IS1R
          IS2(NT)=IS2R
          P(NT)=PR
          EI(NT)=EIN
        ENDIF
      ENDDO
    1 CONTINUE
      CLOSE(3)
C
      WRITE(IWR,2001) IZ,NSHT(IZ),NT
 2001 FORMAT(1X,'*** RELAX:  Z =',I3,',  no. of shells =',I3,
     1          ',  no. of transitions =',I4)
C
      DO I=1,99
        EE(I)=0.0D0
      ENDDO
      DO J=1,30
        KS=IKS(IZ,J)
        IF(KS.GT.0) THEN
          IF(IFI(IZ,KS).NE.0) THEN
            WRITE(IWR,2002) KS,CSH5(KS),IFI(IZ,KS),EB(IZ,KS)
 2002       FORMAT(1X,I3,1X,A5,1X,I1,1P,E13.5)
            EE(KS)=EB(IZ,KS)
          ENDIF
        ENDIF
      ENDDO
C
      IF(NT.GT.0) THEN
        DO I=1,NT
          IF(IS2(I).EQ.0) THEN
            IF(EI(I).LT.1.0D0) THEN
              ET=EE(IS0(I))-EE(IS1(I))
            ELSE
              ET=EI(I)
            ENDIF
          ELSE
            IF(EI(I).LT.1.0D0) THEN
              ET=EE(IS0(I))-EE(IS1(I))-EE(IS2(I))
            ELSE
              ET=EI(I)
            ENDIF
          ENDIF
          ET=MAX(ET,1.0D0)
          WRITE(IWR,2003) IS0(I),IS1(I),IS2(I),P(I),ET
        ENDDO
 2003   FORMAT(1X,3I3,1P,2E13.5)
      ENDIF
      RETURN
      END
C  *********************************************************************
C                       BLOCK DATA PENDAT
C  *********************************************************************
      BLOCK DATA PENDAT
C
C  Physical data for the elements Z=1-99.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*2 LASYMB
C
      COMMON/CADATA/ATW(99),EPX(99),RSCR(99),ETA(99),EB(99,30),
     1  IFI(99,30),IKS(99,30),NSHT(99),LASYMB(99)
C
C  ************  Chemical symbols of the elements.
C
      DATA LASYMB/'H ','He','Li','Be','B ','C ','N ','O ','F ',
     1     'Ne','Na','Mg','Al','Si','P ','S ','Cl','Ar','K ',
     2     'Ca','Sc','Ti','V ','Cr','Mn','Fe','Co','Ni','Cu',
     3     'Zn','Ga','Ge','As','Se','Br','Kr','Rb','Sr','Y ',
     4     'Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In',
     5     'Sn','Sb','Te','I ','Xe','Cs','Ba','La','Ce','Pr',
     6     'Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm',
     7     'Yb','Lu','Hf','Ta','W ','Re','Os','Ir','Pt','Au',
     8     'Hg','Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac',
     9     'Th','Pa','U ','Np','Pu','Am','Cm','Bk','Cf','Es'/
C
C  ************  Molar masses of the elements (g/mol).
C
      DATA ATW  /1.0079D0,4.0026D0,6.9410D0,9.0122D0,1.0811D1,
     1  1.2011D1,1.4007D1,1.5999D1,1.8998D1,2.0179D1,2.2990D1,
     2  2.4305D1,2.6982D1,2.8086D1,3.0974D1,3.2066D1,3.5453D1,
     3  3.9948D1,3.9098D1,4.0078D1,4.4956D1,4.7880D1,5.0942D1,
     4  5.1996D1,5.4938D1,5.5847D1,5.8933D1,5.8690D1,6.3546D1,
     5  6.5390D1,6.9723D1,7.2610D1,7.4922D1,7.8960D1,7.9904D1,
     6  8.3800D1,8.5468D1,8.7620D1,8.8906D1,9.1224D1,9.2906D1,
     7  9.5940D1,9.7907D1,1.0107D2,1.0291D2,1.0642D2,1.0787D2,
     8  1.1241D2,1.1482D2,1.1871D2,1.2175D2,1.2760D2,1.2690D2,
     9  1.3129D2,1.3291D2,1.3733D2,1.3891D2,1.4012D2,1.4091D2,
     A  1.4424D2,1.4491D2,1.5036D2,1.5196D2,1.5725D2,1.5893D2,
     B  1.6250D2,1.6493D2,1.6726D2,1.6893D2,1.7304D2,1.7497D2,
     C  1.7849D2,1.8095D2,1.8385D2,1.8621D2,1.9020D2,1.9222D2,
     D  1.9508D2,1.9697D2,2.0059D2,2.0438D2,2.0720D2,2.0898D2,
     E  2.0898D2,2.0999D2,2.2202D2,2.2302D2,2.2603D2,2.2703D2,
     F  2.3204D2,2.3104D2,2.3803D2,2.3705D2,2.3905D2,2.4306D2,
     G  2.4707D2,2.4707D2,2.5108D2,2.5208D2/
C
C  ************  Mean excitation energies of the elements (eV).
C
      DATA EPX / 19.2D0, 41.8D0, 40.0D0, 63.7D0, 76.0D0, 81.0D0,
     1   82.0D0, 95.0D0,115.0D0,137.0D0,149.0D0,156.0D0,166.0D0,
     2  173.0D0,173.0D0,180.0D0,174.0D0,188.0D0,190.0D0,191.0D0,
     3  216.0D0,233.0D0,245.0D0,257.0D0,272.0D0,286.0D0,297.0D0,
     4  311.0D0,322.0D0,330.0D0,334.0D0,350.0D0,347.0D0,348.0D0,
     5  343.0D0,352.0D0,363.0D0,366.0D0,379.0D0,393.0D0,417.0D0,
     6  424.0D0,428.0D0,441.0D0,449.0D0,470.0D0,470.0D0,469.0D0,
     7  488.0D0,488.0D0,487.0D0,485.0D0,491.0D0,482.0D0,488.0D0,
     8  491.0D0,501.0D0,523.0D0,535.0D0,546.0D0,560.0D0,574.0D0,
     9  580.0D0,591.0D0,614.0D0,628.0D0,650.0D0,658.0D0,674.0D0,
     A  684.0D0,694.0D0,705.0D0,718.0D0,727.0D0,736.0D0,746.0D0,
     B  757.0D0,790.0D0,790.0D0,800.0D0,810.0D0,823.0D0,823.0D0,
     C  830.0D0,825.0D0,794.0D0,827.0D0,826.0D0,841.0D0,847.0D0,
     D  878.0D0,890.0D0,902.0D0,921.0D0,934.0D0,939.0D0,952.0D0,
     E  966.0D0,980.0D0/
C
C  ************  Pair-production cross section parameters.
C
C  ****  Screening parameter (R mc/hbar).
      DATA RSCR  /1.2281D2,7.3167D1,6.9228D1,6.7301D1,6.4696D1,
     1   6.1228D1,5.7524D1,5.4033D1,5.0787D1,4.7851D1,4.6373D1,
     2   4.5401D1,4.4503D1,4.3815D1,4.3074D1,4.2321D1,4.1586D1,
     3   4.0953D1,4.0524D1,4.0256D1,3.9756D1,3.9144D1,3.8462D1,
     4   3.7778D1,3.7174D1,3.6663D1,3.5986D1,3.5317D1,3.4688D1,
     5   3.4197D1,3.3786D1,3.3422D1,3.3068D1,3.2740D1,3.2438D1,
     6   3.2143D1,3.1884D1,3.1622D1,3.1438D1,3.1142D1,3.0950D1,
     7   3.0758D1,3.0561D1,3.0285D1,3.0097D1,2.9832D1,2.9581D1,
     8   2.9411D1,2.9247D1,2.9085D1,2.8930D1,2.8721D1,2.8580D1,
     9   2.8442D1,2.8312D1,2.8139D1,2.7973D1,2.7819D1,2.7675D1,
     A   2.7496D1,2.7285D1,2.7093D1,2.6911D1,2.6705D1,2.6516D1,
     B   2.6304D1,2.6108D1,2.5929D1,2.5730D1,2.5577D1,2.5403D1,
     C   2.5245D1,2.5100D1,2.4941D1,2.4790D1,2.4655D1,2.4506D1,
     D   2.4391D1,2.4262D1,2.4145D1,2.4039D1,2.3922D1,2.3813D1,
     E   2.3712D1,2.3621D1,2.3523D1,2.3430D1,2.3331D1,2.3238D1,
     F   2.3139D1,2.3048D1,2.2967D1,2.2833D1,2.2694D1,2.2624D1,
     G   2.2545D1,2.2446D1,2.2358D1,2.2264D1/
C  ****  Asymptotic triplet contribution (eta).
      DATA ETA   /1.1570D0,1.1690D0,1.2190D0,1.2010D0,1.1890D0,
     1   1.1740D0,1.1760D0,1.1690D0,1.1630D0,1.1570D0,1.1740D0,
     2   1.1830D0,1.1860D0,1.1840D0,1.1800D0,1.1780D0,1.1750D0,
     3   1.1700D0,1.1800D0,1.1870D0,1.1840D0,1.1800D0,1.1770D0,
     4   1.1660D0,1.1690D0,1.1660D0,1.1640D0,1.1620D0,1.1540D0,
     5   1.1560D0,1.1570D0,1.1580D0,1.1570D0,1.1580D0,1.1580D0,
     6   1.1580D0,1.1660D0,1.1730D0,1.1740D0,1.1750D0,1.1700D0,
     7   1.1690D0,1.1720D0,1.1690D0,1.1680D0,1.1640D0,1.1670D0,
     8   1.1700D0,1.1720D0,1.1740D0,1.1750D0,1.1780D0,1.1790D0,
     9   1.1800D0,1.1870D0,1.1940D0,1.1970D0,1.1960D0,1.1940D0,
     A   1.1940D0,1.1940D0,1.1940D0,1.1940D0,1.1960D0,1.1970D0,
     B   1.1960D0,1.1970D0,1.1970D0,1.1980D0,1.1980D0,1.2000D0,
     C   1.2010D0,1.2020D0,1.2040D0,1.2050D0,1.2060D0,1.2080D0,
     D   1.2070D0,1.2080D0,1.2120D0,1.2150D0,1.2180D0,1.2210D0,
     E   1.2240D0,1.2270D0,1.2300D0,1.2370D0,1.2430D0,1.2470D0,
     F   1.2500D0,1.2510D0,1.2520D0,1.2550D0,1.2560D0,1.2570D0,
     G   1.2590D0,1.2620D0,1.2620D0,1.2650D0/
C
      END

CXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
C                                                                      C
C  NUMERICAL TOOLS     (Francesc Salvat. Barcelona. February, 2001.)   C
C                                                                      C
CXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

C  *********************************************************************
C                       SUBROUTINE MERGE2
C  *********************************************************************
      SUBROUTINE MERGE2(X1,Y1,X2,Y2,XM,YM,N1,N2,N)
C
C  This subroutine merges two tables (X1,Y1), (X2,Y2) of two functions
C  to produce a table (XM,YM) of the sum of these functions, with abs-
C  cissas in increasing order. The abscissas and function values are
C  assumed to be positive. N1, N2 and N are the numbers of grid points
C  in the input and merged tables. A discontinuity in the function is
C  described by giving twice the abscissa. Log-log linear interpolation
C  is used to interpolate the input tables.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (EPS=1.0D-10,NP=1500,NP2=NP+NP)
      DIMENSION X1(NP),Y1(NP),X2(NP),Y2(NP),XM(NP),YM(NP)
      DIMENSION X(NP2),Y12(NP2)
C
      CALL SORT2(X1,Y1,N1)
      CALL SORT2(X2,Y2,N2)
C
      DO I1=1,N1
        X(I1)=X1(I1)
      ENDDO
      N=N1
      DO I2=1,N2
        XC=X2(I2)
        CALL FINDI(X1,XC,N1,I1)
        IF(I1.EQ.N1) I1=N1-1
        TST1=ABS(XC-X1(I1))
        TST2=ABS(XC-X1(I1+1))
        TST12=MIN(TST1,TST2)
        IF(I2.GT.1) THEN
          TST3=ABS(XC-X2(I2-1))
        ELSE
          TST3=1.0D0
        ENDIF
        IF(I2.LT.N2) THEN
          TST4=ABS(XC-X2(I2+1))
        ELSE
          TST4=1.0D0
        ENDIF
        TST34=MIN(TST3,TST4)
        TST=EPS*XC
        IF(TST34.GT.TST) THEN
          IF(TST12.GT.TST) THEN
            N=N+1
            X(N)=XC
          ENDIF
        ELSE
          N=N+1
          X(N)=XC
        ENDIF
      ENDDO
C
C  ****  Sort and clean the merged grid.
C
    1 CONTINUE
      DO I=1,N-1
        IMIN=I
        XMIN=X(I)
        DO J=I+1,N
          IF(X(J).LT.XMIN) THEN
            IMIN=J
            XMIN=X(J)
          ENDIF
        ENDDO
        SAVE=X(I)
        X(I)=X(IMIN)
        X(IMIN)=SAVE
      ENDDO
C
      DO I=1,N-2
        IF(X(I).GT.X(I+2)*(1.0D0-EPS)) THEN
          X(I+1)=X(N)
          N=N-1
          GO TO 1
        ENDIF
      ENDDO
C
      DO I=1,N
        XC=X(I)
        IF(I.LT.N) THEN
          IF(X(I).GT.X(I+1)*(1.0D0-EPS)) XC=X(I)*(1.0D0-EPS)
        ENDIF
        IF(I.GT.1) THEN
          IF(X(I).LT.X(I-1)*(1.0D0+EPS)) XC=X(I)*(1.0D0+EPS)
        ENDIF
        CALL FINDI(X1,XC,N1,J)
        IF(J.EQ.N1) J=N1-1
        IF(X1(J+1).GT.X1(J)+EPS) THEN
          YI1=EXP(LOG(Y1(J))+LOG(XC/X1(J))*LOG(Y1(J+1)/Y1(J))
     1     /LOG(X1(J+1)/X1(J)))
        ELSE
          YI1=Y1(J)
        ENDIF
        CALL FINDI(X2,XC,N2,J)
        IF(J.EQ.N2) J=N2-1
        IF(X2(J+1).GT.X2(J)+EPS) THEN
          YI2=EXP(LOG(Y2(J))+LOG(XC/X2(J))*LOG(Y2(J+1)/Y2(J))
     1     /LOG(X2(J+1)/X2(J)))
        ELSE
          YI2=Y2(J)
        ENDIF
        Y12(I)=YI1+YI2
        IF(Y12(I).LT.1.0D-75) Y12(I)=1.0D-75
      ENDDO
C
      DO I=1,N
        XM(I)=X(I)
        YM(I)=Y12(I)
      ENDDO
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE SORT2
C  *********************************************************************
      SUBROUTINE SORT2(X,Y,N)
C
C  This subroutine sorts a table (X,Y) of a function with n data points.
C  A discontinuity of the function is described by giving twice the abs-
C  cissa. It is assumed that the function is strictly positive (negative
C  values of Y are set to zero).
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (EPS=1.0D-10,NP=1500)
      DIMENSION X(NP),Y(NP),IORDER(NP)
C
      IF(N.EQ.1) RETURN
      DO I=1,N
        IORDER(I)=I
        IF(Y(I).LT.1.0D-75) Y(I)=1.0D-75
      ENDDO
C
      DO 1 I=1,N-1
        IMIN=I
        XMIN=X(I)
        DO J=I+1,N
          IF(X(J).LT.XMIN) THEN
            IMIN=J
            XMIN=X(J)
          ENDIF
        ENDDO
        SAVE=X(I)
        X(I)=X(IMIN)
        X(IMIN)=SAVE
        SAVE=Y(I)
        Y(I)=Y(IMIN)
        Y(IMIN)=SAVE
        ISAVE=IORDER(I)
        IORDER(I)=IORDER(IMIN)
        IORDER(IMIN)=ISAVE
        IF(I.EQ.1) GO TO 1
        IF(IORDER(I).LT.IORDER(I-1).AND.ABS(X(I)-X(I-1)).LT.1.0D-15)
     1    THEN
          SAVE=X(I-1)
          X(I-1)=X(I)
          X(I)=SAVE
          SAVE=Y(I-1)
          Y(I-1)=Y(I)
          Y(I)=SAVE
          ISAVE=IORDER(I-1)
          IORDER(I-1)=IORDER(I)
          IORDER(I)=ISAVE
        ENDIF
    1 CONTINUE
      I=N
      IF(IORDER(I).LT.IORDER(I-1).AND.ABS(X(I)-X(I-1)).LT.1.0D-15) THEN
        SAVE=X(I-1)
        X(I-1)=X(I)
        X(I)=SAVE
        SAVE=Y(I-1)
        Y(I-1)=Y(I)
        Y(I)=SAVE
      ENDIF
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE SPLINE
C  *********************************************************************
      SUBROUTINE SPLINE(X,Y,A,B,C,D,S1,SN,N)
C
C  Cubic spline interpolation of tabulated data.
C
C  Input:
C     X(I) (I=1:N) ... grid points (the X values must be in increasing
C                      order).
C     Y(I) (I=1:N) ... corresponding function values.
C     S1,SN .......... second derivatives at X(1) and X(N). The natural
C                      spline corresponds to taking S1=SN=0.
C     N .............. number of grid points.
C  Output:
C     A(1:N),B(1:N),C(1:N),D(1:N) ... spline coefficients.
C
C  The interpolating cubic polynomial in the I-th interval, from X(I) to
C  X(I+1), is
C               P(x) = A(I)+x*(B(I)+x*(C(I)+x*D(I)))
C
C  Reference: M.J. Maron, 'Numerical Analysis: a Practical Approach',
C             MacMillan Publ. Co., New York, 1982.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      DIMENSION X(N),Y(N),A(N),B(N),C(N),D(N)
C
      IF(N.LT.4) THEN
        WRITE(26,10) N
   10   FORMAT(5X,'Spline interpolation cannot be performed with',
     1    I4,' points. Stop.')
        STOP 'SPLINE. N is less than 4.'
      ENDIF
      N1=N-1
      N2=N-2
C  ****  Auxiliary arrays H(=A) and DELTA(=D).
      DO I=1,N1
        IF(X(I+1)-X(I).LT.1.0D-13) THEN
          WRITE(26,11)
   11     FORMAT(5X,'Spline X values not in increasing order. Stop.')
          STOP 'SPLINE. X values not in increasing order.'
        ENDIF
        A(I)=X(I+1)-X(I)
        D(I)=(Y(I+1)-Y(I))/A(I)
      ENDDO
C  ****  Symmetric coefficient matrix (augmented).
      DO I=1,N2
        B(I)=2.0D0*(A(I)+A(I+1))
        K=N1-I+1
        D(K)=6.0D0*(D(K)-D(K-1))
      ENDDO
      D(2)=D(2)-A(1)*S1
      D(N1)=D(N1)-A(N1)*SN
C  ****  Gauss solution of the tridiagonal system.
      DO I=2,N2
        R=A(I)/B(I-1)
        B(I)=B(I)-R*A(I)
        D(I+1)=D(I+1)-R*D(I)
      ENDDO
C  ****  The SIGMA coefficients are stored in array D.
      D(N1)=D(N1)/B(N2)
      DO I=2,N2
        K=N1-I+1
        D(K)=(D(K)-A(K)*D(K+1))/B(K-1)
      ENDDO
      D(N)=SN
C  ****  Spline coefficients.
      SI1=S1
      DO I=1,N1
        SI=SI1
        SI1=D(I+1)
        H=A(I)
        HI=1.0D0/H
        A(I)=(HI/6.0D0)*(SI*X(I+1)**3-SI1*X(I)**3)
     1      +HI*(Y(I)*X(I+1)-Y(I+1)*X(I))
     2      +(H/6.0D0)*(SI1*X(I)-SI*X(I+1))
        B(I)=(HI/2.0D0)*(SI1*X(I)**2-SI*X(I+1)**2)
     1      +HI*(Y(I+1)-Y(I))+(H/6.0D0)*(SI-SI1)
        C(I)=(HI/2.0D0)*(SI*X(I+1)-SI1*X(I))
        D(I)=(HI/6.0D0)*(SI1-SI)
      ENDDO
C  ****  Natural cubic spline for X.GT.X(N).
      FN=Y(N)
      FNP=B(N1)+X(N)*(2.0D0*C(N1)+X(N)*3.0D0*D(N1))
      A(N)=FN-X(N)*FNP
      B(N)=FNP
      C(N)=0.0D0
      D(N)=0.0D0
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE FINDI
C  *********************************************************************
      SUBROUTINE FINDI(X,XC,N,I)
C
C  Finds the interval (X(I),X(I+1)) that contains the value XC.
C
C  Input:
C     X(I) (I=1:N) ... grid points (the X values must be in increasing
C                      order).
C     XC ............. point to be located.
C     N  ............. number of grid points.
C  Output:
C     I .............. interval index.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      DIMENSION X(N)
C
      IF(XC.GT.X(N)) THEN
        I=N
        RETURN
      ENDIF
      IF(XC.LT.X(1)) THEN
        I=1
        RETURN
      ENDIF
      I=1
      I1=N
    1 IT=(I+I1)/2
      IF(XC.GT.X(IT)) THEN
        I=IT
      ELSE
        I1=IT
      ENDIF
      IF(I1-I.GT.1) GO TO 1
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE SINTEG
C  *********************************************************************
      SUBROUTINE SINTEG(X,A,B,C,D,XL,XU,SUM,N)
C
C  Computes the integral of a cubic spline function.
C
C  Input:
C     X(I) (I=1:N) ... grid points (the X values must be in increasing
C                      order).
C     A(1:N),B(1:N),C(1:N),D(1:N) ... spline coefficients.
C     N  ............. number of grid points.
C     XL ............. lower limit of the integral.
C     XU ............. upper limit of the integral.
C  Output:
C     SUM ............ value of the integral.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      DIMENSION X(N),A(N),B(N),C(N),D(N)
C  ****  Set integration limits in increasing order.
      IF(XU.GT.XL) THEN
        XLL=XL
        XUU=XU
        SIGN=1.0D0
      ELSE
        XLL=XU
        XUU=XL
        SIGN=-1.0D0
      ENDIF
C  ****  Check integral limits.
      IF(XLL.LT.X(1).OR.XUU.GT.X(N)) THEN
        WRITE(26,10)
   10   FORMAT(5X,'Integral limits out of range. Stop.')
        STOP 'SINTEG. Integral limits out of range.'
      ENDIF
C  ****  Find involved intervals.
      SUM=0.0D0
      CALL FINDI(X,XLL,N,IL)
      CALL FINDI(X,XUU,N,IU)
C
      IF(IL.EQ.IU) THEN
C  ****  Only a single interval involved.
        X1=XLL
        X2=XUU
        SUM=X2*(A(IL)+X2*((B(IL)/2)+X2*((C(IL)/3)+X2*D(IL)/4)))
     1     -X1*(A(IL)+X1*((B(IL)/2)+X1*((C(IL)/3)+X1*D(IL)/4)))
      ELSE
C  ****  Contributions from several intervals.
        X1=XLL
        X2=X(IL+1)
        SUM=X2*(A(IL)+X2*((B(IL)/2)+X2*((C(IL)/3)+X2*D(IL)/4)))
     1     -X1*(A(IL)+X1*((B(IL)/2)+X1*((C(IL)/3)+X1*D(IL)/4)))
        IL=IL+1
        DO I=IL,IU
          X1=X(I)
          X2=X(I+1)
          IF(I.EQ.IU) X2=XUU
          SUMP=X2*(A(I)+X2*((B(I)/2)+X2*((C(I)/3)+X2*D(I)/4)))
     1        -X1*(A(I)+X1*((B(I)/2)+X1*((C(I)/3)+X1*D(I)/4)))
          SUM=SUM+SUMP
        ENDDO
      ENDIF
      SUM=SIGN*SUM
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE SLAG6
C  *********************************************************************
      SUBROUTINE SLAG6(H,Y,S,N)
C
C  Piecewise six-point Lagrange integration of a uniformly tabulated
C  function.
C
C  H ...... step length.
C  Y(I) (I=1:N) ... array of function values (ordered abscissas).
C  S(I) (I=1:N) ... array of integral values defined as
C                S(I)=INTEGRAL(Y) from X(1) to X(I)=X(1)+(I-1)*H.
C  N ...... number of data points.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      DIMENSION Y(N),S(N)
      IF(N.LT.6) STOP
      HR=H/1440.0D0
      Y1=0.0D0
      Y2=Y(1)
      Y3=Y(2)
      Y4=Y(3)
      S(1)=0.0D0
      S(2)=HR*(475*Y2+1427*Y3-798*Y4+482*Y(4)-173*Y(5)+27*Y(6))
      S(3)=S(2)
     1    +HR*(-27*Y2+637*Y3+1022*Y4-258*Y(4)+77*Y(5)-11*Y(6))
      DO I=4,N-2
        Y1=Y2
        Y2=Y3
        Y3=Y4
        Y4=Y(I)
        S(I)=S(I-1)
     1      +HR*(11*(Y1+Y(I+2))-93*(Y2+Y(I+1))+802*(Y3+Y4))
      ENDDO
      Y5=Y(N-1)
      Y6=Y(N)
      S(N-1)=S(N-2)
     1      +HR*(-27*Y6+637*Y5+1022*Y4-258*Y3+77*Y2-11*Y1)
      S(N)=S(N-1)
     1    +HR*(475*Y6+1427*Y5-798*Y4+482*Y3-173*Y2+27*Y1)
      RETURN
      END
C  *********************************************************************
C                       FUNCTION SUMGA
C  *********************************************************************
      FUNCTION SUMGA(FCT,XL,XU,TOL)
C
C  This function calculates the value SUMGA of the integral of the
C  (external) function FCT over the interval (XL,XU) using the 20-point
C  Gauss quadrature method with an adaptive-bisection scheme.
C
C  TOL is the tolerance, i.e. maximum allowed relative error; it should
C  not exceed 1.0D-13. A warning message is written in unit 6 when the
C  required accuracy is not attained. The common block CSUMGA can be
C  used to transfer the error flag IERGA to the calling program.
C
C                                     Francesc Salvat. 22 January, 2011.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (NP=10, NOIT=128, NCALLT=1000000)
      DIMENSION X(NP),W(NP),XM(NP),XP(NP)
      DIMENSION S(NOIT),SN(NOIT),XR(NOIT),XRN(NOIT)
C  Output error codes:
C     IERGA = 0, no problem, the calculation has converged.
C           = 1, too many iterations.
C           = 2, subintervals are too narrow.
C           = 3, too many open subintervals.
C           = 4, too many function calls.
      COMMON/CSUMGA/IERGA  ! =0 if the sum converges, >0 otherwise.
C
C  ****  Gauss 20-point integration formula.
C  Abscissas.
      DATA X/7.6526521133497334D-02,2.2778585114164508D-01,
     1       3.7370608871541956D-01,5.1086700195082710D-01,
     2       6.3605368072651503D-01,7.4633190646015079D-01,
     3       8.3911697182221882D-01,9.1223442825132591D-01,
     4       9.6397192727791379D-01,9.9312859918509492D-01/
C  Weights.
      DATA W/1.5275338713072585D-01,1.4917298647260375D-01,
     1       1.4209610931838205D-01,1.3168863844917663D-01,
     2       1.1819453196151842D-01,1.0193011981724044D-01,
     3       8.3276741576704749D-02,6.2672048334109064D-02,
     4       4.0601429800386941D-02,1.7614007139152118D-02/
      DO I=1,NP
        XM(I)=1.0D0-X(I)
        XP(I)=1.0D0+X(I)
      ENDDO
C  ****  Global and partial tolerances.
      TOL1=MIN(MAX(TOL,1.0D-13),1.0D-5)
      TOL2=TOL1
      TOL3=1.0D-13
      SUMGA=0.0D0
      IERGA=0
C  ****  Integration from XL to XU.
      H=XU-XL
      HH=0.5D0*H
      X1=XL
      SP=W(1)*(FCT(X1+XM(1)*HH)+FCT(X1+XP(1)*HH))
      DO J=2,NP
        SP=SP+W(J)*(FCT(X1+XM(J)*HH)+FCT(X1+XP(J)*HH))
      ENDDO
      S(1)=SP*HH
      XR(1)=X1
      NCALL=2*NP
      NOIN=1
C
C  ****  Adaptive-bisection scheme.
C
    1 CONTINUE
      H=HH  ! Subinterval length.
      HH=0.5D0*H
      IF(TOL2.GT.0.01D0*TOL1) TOL2=TOL2*0.5D0
      SUMR=0.0D0
      NOI=NOIN
      NOIN=0
      DO I=1,NOI
        SI=S(I)  ! Bisect the I-th open interval.
        X1=XR(I)
        SP=W(1)*(FCT(X1+XM(1)*HH)+FCT(X1+XP(1)*HH))
        DO J=2,NP
          SP=SP+W(J)*(FCT(X1+XM(J)*HH)+FCT(X1+XP(J)*HH))
        ENDDO
        S1=SP*HH
C
        X2=X1+H
        SP=W(1)*(FCT(X2+XM(1)*HH)+FCT(X2+XP(1)*HH))
        DO J=2,NP
          SP=SP+W(J)*(FCT(X2+XM(J)*HH)+FCT(X2+XP(J)*HH))
        ENDDO
        S2=SP*HH
C
        NCALL=NCALL+4*NP
        S12=S1+S2  ! Sum of integrals on the two subintervals.
        IF(ABS(HH).LT.TOL3*ABS(X2)) THEN
C  ****  Subintervals are too narrow (--> large roundoff errors).
          SUMR=SUMR+S12
          INEXT=I+1
          IERGA=1
          GO TO 2
        ELSE IF(ABS(S12-SI).LT.MAX(TOL2*ABS(S12),1.0D-35)) THEN
C  ****  The integral over the parent interval has converged.
          SUMGA=SUMGA+S12
        ELSE
          SUMR=SUMR+S12
          NOIN=NOIN+2
          IF(NOIN.LT.NOIT) THEN
C  ****  Store open intervals.
            SN(NOIN-1)=S1
            XRN(NOIN-1)=X1
            SN(NOIN)=S2
            XRN(NOIN)=X2
          ELSE
C  ****  Too many open intervals.
            INEXT=I+1
            IERGA=2
            GO TO 2
          ENDIF
        ENDIF
        IF(NCALL.GT.NCALLT) THEN
C  ****  Too many calls to FCT.
          INEXT=I+1
          IERGA=3
          GO TO 2
        ENDIF
      ENDDO
      IF(ABS(SUMR).LT.MAX(TOL1*ABS(SUMGA+SUMR),1.0D-35).
     1  OR.NOIN.EQ.0) THEN
        SUMGA=SUMGA+SUMR
        RETURN
      ENDIF
      DO I=1,NOIN
        S(I)=SN(I)
        XR(I)=XRN(I)
      ENDDO
      GO TO 1
C
C  ****  Warning (low accuracy) message.
C
    2 CONTINUE
      IERGA=IERGA+1
      IF(INEXT.LE.NOI) THEN
        DO I=INEXT,NOI
          SUMR=SUMR+S(I)
        ENDDO
      ENDIF
      SUMGA=SUMGA+SUMR
      IF(IERGA.EQ.2) THEN
        IF(NOI.LT.10) THEN
          IERGA=0
          RETURN
        ENDIF
      ENDIF
      WRITE(6,11)
   11 FORMAT(/2X,'>>> SUMGA. Gauss adaptive-bisection quadrature.')
      WRITE(6,12) XL,XU,TOL1
   12 FORMAT(2X,'XL =',1P,E19.12,',  XU =',E19.12,',  TOL =',E8.1)
      IF(ABS(SUMGA).GT.1.0D-35) THEN
        RERR=ABS(SUMR)/ABS(SUMGA)
        WRITE(6,13) NCALL,SUMGA,RERR,NOI,IERGA
   13   FORMAT(2X,'NCALLS = ',I6,',  SUMGA =',1P,E20.13,',  RelErr =',
     1    E8.1,/2X,'Number of open subintervals = ',I4,',  IERGA =',I2)
      ELSE
        AERR=ABS(SUMR)
        WRITE(6,14) NCALL,SUMGA,AERR,NOI,IERGA
   14   FORMAT(2X,'NCALLS = ',I6,',  SUMGA =',1P,E20.13,',  AbsErr =',
     1    E8.1,/2X,'Number of open subintervals = ',I4,',  IERGA =',I2)
      ENDIF
      WRITE(6,15)
   15 FORMAT(2X,'WARNING: the required accuracy has not been ',
     1  'attained.'/)
      RETURN
      END
C  *********************************************************************
C                       FUNCTION RNDG3
C  *********************************************************************
      FUNCTION RNDG3()
C
C  This function delivers random values in the interval (-3.0,3.0)
C  sampled from a truncated Gaussian distribution that has zero mean and
C  unit variance. The sampling is performed by using the RITA method.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (NR=128)
      COMMON/CRNDG3/X(NR),A(NR),B(NR),F(NR),IA(NR),NP1
      EXTERNAL RAND
C  ****  Selection of the interval (Walker's aliasing).
      RN=RAND(1.0D0)*NP1+1.0D0
      K=INT(RN)
      TST=RN-K
      IF(TST.LT.F(K)) THEN
        I=K
        RR=TST
        D=F(K)
      ELSE
        I=IA(K)
        RR=TST-F(K)
        D=1.0D0-F(K)
      ENDIF
C  ****  Sampling from the rational inverse cumulative distribution.
      IF(RR.GT.1.0D-16) THEN
        CD=(1.0D0+A(I)+B(I))*D
        RNDG3=X(I)+(CD*RR/(D*D+(A(I)*D+B(I)*RR)*RR))*(X(I+1)-X(I))
      ELSE
        RNDG3=X(I)
      ENDIF
C
      RETURN
      END
C  *********************************************************************
      SUBROUTINE RNDG30
C  Initialisation of the RNDG3 sampling function.
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (NM=512)
      COMMON/CRITA/XA(NM),PAC(NM),DPAC(NM),AA(NM),BA(NM),
     1             ITL(NM),ITU(NM),NPM1
      PARAMETER (NR=128)
      COMMON/CRNDG3/X(NR),A(NR),B(NR),F(NR),IA(NR),NP1
      EXTERNAL RNDG3F
C  ****  Interval end points.
      N=NR
      NU=N/4
      XMIN=-3.0D0
      XMAX=+3.0D0
      CALL RITAI0(RNDG3F,XMIN,XMAX,N,NU,ERRM,0)
      NP1=NPM1
      NP=NP1+1
      IF(NP.NE.N) STOP 'RNDG30: initialisation error (1).'
      IF(ERRM.GT.1.0D-6) STOP 'RNDG30: initialisation error (2).'
C  ****  Walker's aliasing; cutoff and alias values.
      DO I=1,NP1
        X(I)=XA(I)
        A(I)=AA(I)
        B(I)=BA(I)
      ENDDO
      X(NP)=XA(NP)
      CALL IRND0(DPAC,F,IA,NP1)
      F(NP)=1.0D0
      IA(NP)=NP1
      RETURN
      END
C  *********************************************************************
      FUNCTION RNDG3F(X)
C  Truncated Gaussian distribution, restricted to the interval (-3.0,
C  3.0), with zero mean and unit variance.
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      IF(ABS(X).LT.3.00001D0) THEN
        RNDG3F=EXP(-X*X*0.5D0/1.01538698D0**2)
      ELSE
        RNDG3F=0.0D0
      ENDIF
      RETURN
      END

CXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
C                                                                      X
C    TRANSPORT ROUTINES (Francesc Salvat. Barcelona. April, 2002.)     X
C                                                                      X
CXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

C  *********************************************************************
C                       SUBROUTINE CLEANS
C  *********************************************************************
      SUBROUTINE CLEANS
C
C  This subroutine initialises the secondary stack. It must be called
C  before starting the simulation of each primary track.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Secondary stack.
      PARAMETER (NMS=1000)
      COMMON/SECST/ES(NMS),XS(NMS),YS(NMS),ZS(NMS),US(NMS),
     1   VS(NMS),WS(NMS),WGHTS(NMS),KS(NMS),IBODYS(NMS),MS(NMS),
     2   ILBS(5,NMS),NSEC
C
      NSEC=0
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE START
C  *********************************************************************
      SUBROUTINE START
C
C  This subroutine forces the next event to be an artificial soft event.
C  It must be called when a new (primary or secondary) electron or posi-
C  tron track is started and when it crosses an interface.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Current simulation state (used only in class II simulation).
      COMMON/CJUMP1/MODE,KSOFTE,KSOFTI,KDELTA
C
      IF(E.LT.EMIN.OR.E.GT.0.99999999D0*EU) THEN
        WRITE(26,1000) KPAR,E,(ILB(J),J=1,5),EL,EU
 1000   FORMAT(/3X,'*** Energy out of range. KPAR = ',I2,',  E = ',
     1  1P,E12.5,' eV',/7X,'ILB''s =',3I4,2I11,
     2  /7X,'EMIN = ',E12.5,' eV,  EMAX = ',E12.5,
     3  ' eV.'/7X,'Check the values of EABS(KPAR,M) and EMAX.')
        CALL PISTOP('START. E out of range.')
      ENDIF
      MODE=0
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE JUMP
C  *********************************************************************
      SUBROUTINE JUMP(DSMAX,DS)
C
C  Calculation of the free path from the starting point to the position
C  of the next event and of the probabilities of occurrence of different
C  events.
C
C  Arguments:
C    DSMAX ... maximum allowed step length (input),
C    DS ...... step length (output).
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C  ****  Simulation parameters.
      PARAMETER (MAXMAT=10)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Electron simulation tables.
      COMMON/CEIMFP/SEHEL(MAXMAT,NEGP),SEHIN(MAXMAT,NEGP),
     1  SEISI(MAXMAT,NEGP),SEHBR(MAXMAT,NEGP),SEAUX(MAXMAT,NEGP),
     2  SETOT(MAXMAT,NEGP),CSTPE(MAXMAT,NEGP),RSTPE(MAXMAT,NEGP),
     3  DEL(MAXMAT,NEGP),W1E(MAXMAT,NEGP),W2E(MAXMAT,NEGP),
     4  DW1EL(MAXMAT,NEGP),DW2EL(MAXMAT,NEGP),
     5  RNDCE(MAXMAT,NEGP),AE(MAXMAT,NEGP),BE(MAXMAT,NEGP),
     6  T1E(MAXMAT,NEGP),T2E(MAXMAT,NEGP)
C  ****  Positron simulation tables.
      COMMON/CPIMFP/SPHEL(MAXMAT,NEGP),SPHIN(MAXMAT,NEGP),
     1  SPISI(MAXMAT,NEGP),SPHBR(MAXMAT,NEGP),SPAN(MAXMAT,NEGP),
     2  SPAUX(MAXMAT,NEGP),SPTOT(MAXMAT,NEGP),CSTPP(MAXMAT,NEGP),
     3  RSTPP(MAXMAT,NEGP),W1P(MAXMAT,NEGP),W2P(MAXMAT,NEGP),
     4  DW1PL(MAXMAT,NEGP),DW2PL(MAXMAT,NEGP),
     5  RNDCP(MAXMAT,NEGP),AP(MAXMAT,NEGP),BP(MAXMAT,NEGP),
     6  T1P(MAXMAT,NEGP),T2P(MAXMAT,NEGP)
C  ****  Current IMFPs.
      COMMON/CJUMP0/P(8),ST,DST,DS1,W1,W2,T1,T2
      COMMON/CJUMP1/MODE,KSOFTE,KSOFTI,KDELTA
C
      EXTERNAL RAND
C
      IF(KPAR.EQ.1) THEN
C
C  ************  Electrons (KPAR=1).
C
        XEL=LOG(E)
        XE=1.0D0+(XEL-DLEMP1)*DLFC
        KE=XE
        XEK=XE-KE
        IF(MODE.EQ.1) THEN
          CALL EIMFP(1)
          DS=DS1
          RETURN
        ENDIF
        CALL EIMFP(2)
C
C  ****  Inverse hard mean free path (interaction probability per unit
C        path length).
C
        ST=P(2)+P(3)+P(4)+P(5)+P(8)
        DSMAXP=DSMAX
C
C  ****  Soft stopping interactions.
C        KSOFTI=1, soft stopping is active,
C        KSOFTI=0, soft stopping is not active.
C
        IF(W1.GT.1.0D-20) THEN
          KSOFTI=1
C  ****  The maximum step length, DSMAXP, is determined in terms of the
C        input DSMAX value (which is specified by the user) and the mean
C        free path for hard interactions (1/ST).
          DSMC=4.0D0/ST
          IF(DSMAXP.GT.DSMC) THEN
            DSMAXP=DSMC
          ELSE IF(DSMAXP.LT.1.0D-8) THEN
            DSMAXP=DSMC
          ENDIF
C  ****  The value of DSMAXP is randomised to eliminate dose artifacts
C        at the end of the first step.
          DSMAXP=(0.5D0+RAND(1.0D0)*0.5D0)*DSMAXP
C
C  ****  Upper bound for the interaction probability along the step
C        (including soft energy straggling).
C
          EDE0=W1*DSMAXP
          VDE0=W2*DSMAXP
          FSEDE=MAX(1.0D0-DW1EL(M,KE)*EDE0,0.75D0)
          FSVDE=MAX(1.0D0-DW2EL(M,KE)*EDE0,0.75D0)
          EDEM=EDE0*FSEDE
          VDEM=VDE0*FSVDE
          W21=VDEM/EDEM
          IF(EDEM.GT.9.0D0*W21) THEN
            ELOWER=MAX(E-(EDEM+3.0D0*SQRT(VDEM)),EMIN)
          ELSE IF(EDEM.GT.3.0D0*W21) THEN
            ELOWER=MAX(E-(EDEM+SQRT(3.0D0*VDEM)),EMIN)
          ELSE
            ELOWER=MAX(E-1.5D0*(EDEM+W21),EMIN)
          ENDIF
          XE1=1.0D0+(LOG(ELOWER)-DLEMP1)*DLFC
          KE1=XE1
          XEK1=XE1-KE1
          STLWR=EXP(SETOT(M,KE1)+(SETOT(M,KE1+1)-SETOT(M,KE1))*XEK1)
          ST=MAX(ST,STLWR)
        ELSE
          KSOFTI=0
        ENDIF
C
C  ****  Soft elastic scattering.
C        KSOFTE=1, soft scattering is active,
C        KSOFTE=0, soft scattering is not active.
C
        IF(T1.GT.1.0D-20) THEN
          KSOFTE=1
        ELSE
          KSOFTE=0
        ENDIF
C
C  ****  Delta interactions.
C        KDELTA=0, a hard interaction follows,
C        KDELTA=1, a delta interaction follows.
C
        DST=-LOG(RAND(2.0D0))/ST
        IF(DST.LT.DSMAXP) THEN
          KDELTA=0
        ELSE
          DST=DSMAXP
          KDELTA=1
        ENDIF
C
        IF(KSOFTE+KSOFTI.EQ.0) THEN
          DS=DST
          DS1=0.0D0
          MODE=1
        ELSE
          DS=DST*RAND(3.0D0)
          DS1=DST-DS
        ENDIF
        RETURN
      ELSE IF(KPAR.EQ.3) THEN
C
C  ************  Positrons (KPAR=3).
C
        XEL=LOG(E)
        XE=1.0D0+(XEL-DLEMP1)*DLFC
        KE=XE
        XEK=XE-KE
        IF(MODE.EQ.1) THEN
          CALL PIMFP(1)
          DS=DS1
          RETURN
        ENDIF
        CALL PIMFP(2)
C
C  ****  Inverse hard mean free path (interaction probability per unit
C        path length).
C
        ST=P(2)+P(3)+P(4)+P(5)+P(6)+P(8)
        DSMAXP=DSMAX
C
C  ****  Soft stopping interactions.
C        KSOFTI=1, soft stopping is active,
C        KSOFTI=0, soft stopping is not active.
C
        IF(W1.GT.1.0D-20) THEN
          KSOFTI=1
C  ****  The maximum step length, DSMAXP, is determined in terms of the
C        input DSMAX value (which is specified by the user) and the mean
C        free path for hard interactions (1/ST).
          DSMC=4.0D0/ST
          IF(DSMAXP.GT.DSMC) THEN
            DSMAXP=DSMC
          ELSE IF(DSMAXP.LT.1.0D-8) THEN
            DSMAXP=DSMC
          ENDIF
C  ****  The value of DSMAXP is randomised to eliminate dose artifacts
C        at the end of the first step.
          DSMAXP=(0.5D0+RAND(1.0D0)*0.5D0)*DSMAXP
C
C  ****  Upper bound for the interaction probability along the step
C        (including soft energy straggling).
C
          EDE0=W1*DSMAXP
          VDE0=W2*DSMAXP
          FSEDE=MAX(1.0D0-DW1PL(M,KE)*EDE0,0.75D0)
          FSVDE=MAX(1.0D0-DW2PL(M,KE)*EDE0,0.75D0)
          EDEM=EDE0*FSEDE
          VDEM=VDE0*FSVDE
          W21=VDEM/EDEM
          IF(EDEM.GT.9.0D0*W21) THEN
            ELOWER=MAX(E-(EDEM+3.0D0*SQRT(VDEM)),EMIN)
          ELSE IF(EDEM.GT.3.0D0*W21) THEN
            ELOWER=MAX(E-(EDEM+SQRT(3.0D0*VDEM)),EMIN)
          ELSE
            ELOWER=MAX(E-1.5D0*(EDEM+W21),EMIN)
          ENDIF
          XE1=1.0D0+(LOG(ELOWER)-DLEMP1)*DLFC
          KE1=XE1
          XEK1=XE1-KE1
          STLWR=EXP(SPTOT(M,KE1)+(SPTOT(M,KE1+1)-SPTOT(M,KE1))*XEK1)
          ST=MAX(ST,STLWR)
        ELSE
          KSOFTI=0
        ENDIF
C
C  ****  Soft elastic scattering.
C        KSOFTE=1, soft scattering is active,
C        KSOFTE=0, soft scattering is not active.
C
        IF(T1.GT.1.0D-20) THEN
          KSOFTE=1
        ELSE
          KSOFTE=0
        ENDIF
C
C  ****  Delta interactions.
C        KDELTA=0, a hard interaction follows,
C        KDELTA=1, a delta interaction follows.
C
        DST=-LOG(RAND(2.0D0))/ST
        IF(DST.LT.DSMAXP) THEN
          KDELTA=0
        ELSE
          DST=DSMAXP
          KDELTA=1
        ENDIF
C
        IF(KSOFTE+KSOFTI.EQ.0) THEN
          DS=DST
          DS1=0.0D0
          MODE=1
        ELSE
          DS=DST*RAND(3.0D0)
          DS1=DST-DS
        ENDIF
        RETURN
      ELSE
C
C  ************  Photons (KPAR=2).
C
        XEL=LOG(E)
        XE=1.0D0+(XEL-DLEMP1)*DLFC
        KE=XE
        XEK=XE-KE
C
        CALL GIMFP
        ST=P(1)+P(2)+P(3)+P(4)+P(8)
        DS=-LOG(RAND(1.0D0))/ST
      ENDIF
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE KNOCK
C  *********************************************************************
      SUBROUTINE KNOCK(DE,ICOL)
C
C     Simulation of random hinges and hard interaction events.
C
C  Output arguments:
C    DE ..... energy deposited by the particle in the material. It is
C             usually equal to the difference between the energies
C             before and after the interaction.
C    ICOL ... kind of interaction suffered by the particle.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*2 LASYMB
      PARAMETER (PI=3.1415926535897932D0, TWOPI=PI+PI)
      PARAMETER (REV=5.10998918D5)  ! Electron rest energy (eV)
      PARAMETER (RREV=1.0D0/REV, TREV=2.0D0*REV)
      PARAMETER (TRUNC=1.01538698D0)
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
      COMMON/STOKES/SP1,SP2,SP3,IPOL
      COMMON/CHIST/ILBA(5)
C  ****  Simulation parameters.
      PARAMETER (MAXMAT=10)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
C  ****  Composition data.
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Element data.
      COMMON/CADATA/ATW(99),EPX(99),RSCR(99),ETA(99),EB(99,30),
     1  IFI(99,30),IKS(99,30),NSHT(99),LASYMB(99)
C  ****  E/P inelastic collisions.
      PARAMETER (NO=128)
      COMMON/CEIN/EXPOT(MAXMAT),OP2(MAXMAT),F(MAXMAT,NO),UI(MAXMAT,NO),
     1  WRI(MAXMAT,NO),KZ(MAXMAT,NO),KS(MAXMAT,NO),NOSC(MAXMAT)
C  ****  Compton scattering.
      PARAMETER (NOCO=128)
      COMMON/CGCO/FCO(MAXMAT,NOCO),UICO(MAXMAT,NOCO),FJ0(MAXMAT,NOCO),
     2  KZCO(MAXMAT,NOCO),KSCO(MAXMAT,NOCO),NOSCCO(MAXMAT)
C  ****  Bremsstrahlung emission.
      PARAMETER (NBW=32)
      COMMON/CEBR/WB(NBW),PBCUT(MAXMAT,NEGP),WBCUT(MAXMAT,NEGP),
     1  PDFB(MAXMAT,NEGP,NBW),DPDFB(MAXMAT,NEGP,NBW),
     2  PACB(MAXMAT,NEGP,NBW),ZBR2(MAXMAT)
C  ****  Electron simulation tables.
      COMMON/CEIMFP/SEHEL(MAXMAT,NEGP),SEHIN(MAXMAT,NEGP),
     1  SEISI(MAXMAT,NEGP),SEHBR(MAXMAT,NEGP),SEAUX(MAXMAT,NEGP),
     2  SETOT(MAXMAT,NEGP),CSTPE(MAXMAT,NEGP),RSTPE(MAXMAT,NEGP),
     3  DEL(MAXMAT,NEGP),W1E(MAXMAT,NEGP),W2E(MAXMAT,NEGP),
     4  DW1EL(MAXMAT,NEGP),DW2EL(MAXMAT,NEGP),
     5  RNDCE(MAXMAT,NEGP),AE(MAXMAT,NEGP),BE(MAXMAT,NEGP),
     6  T1E(MAXMAT,NEGP),T2E(MAXMAT,NEGP)
C  ****  Positron simulation tables.
      COMMON/CPIMFP/SPHEL(MAXMAT,NEGP),SPHIN(MAXMAT,NEGP),
     1  SPISI(MAXMAT,NEGP),SPHBR(MAXMAT,NEGP),SPAN(MAXMAT,NEGP),
     2  SPAUX(MAXMAT,NEGP),SPTOT(MAXMAT,NEGP),CSTPP(MAXMAT,NEGP),
     3  RSTPP(MAXMAT,NEGP),W1P(MAXMAT,NEGP),W2P(MAXMAT,NEGP),
     4  DW1PL(MAXMAT,NEGP),DW2PL(MAXMAT,NEGP),
     5  RNDCP(MAXMAT,NEGP),AP(MAXMAT,NEGP),BP(MAXMAT,NEGP),
     6  T1P(MAXMAT,NEGP),T2P(MAXMAT,NEGP)
C  ****  Current IMFPs.
      COMMON/CJUMP0/P(8),ST,DST,DS1,W1,W2,T1,T2
      COMMON/CJUMP1/MODE,KSOFTE,KSOFTI,KDELTA
C
      COMMON/CELSEP/EELMAX(MAXMAT),PELMAX(MAXMAT),
     1              RNDCEd(MAXMAT,NEGP),RNDCPd(MAXMAT,NEGP)
C
      EXTERNAL RAND
C
      IF(KPAR.EQ.2) GO TO 2000
      IF(KPAR.EQ.3) GO TO 3000
C
C  ************  Electrons (KPAR=1).
C
C1000 CONTINUE
      IF(MODE.EQ.1) GO TO 1100
C
C  ****  Artificial soft event (ICOL=1).
C
      ICOL=1
      MODE=1
C
      IF(KSOFTI.EQ.0) THEN
        DE=0.0D0
      ELSE
        EDE0=W1*DST
        VDE0=W2*DST
        FSEDE=MAX(1.0D0-DW1EL(M,KE)*EDE0,0.75D0)
        FSVDE=MAX(1.0D0-DW2EL(M,KE)*EDE0,0.75D0)
        EDE=EDE0*FSEDE
        VDE=VDE0*FSVDE
C  ****  Generation of random values DE with mean EDE and variance VDE.
        SIGMA=SQRT(VDE)
        IF(SIGMA.LT.0.333333333D0*EDE) THEN
C  ****  Truncated Gaussian distribution.
          DE=EDE+RNDG3()*SIGMA
        ELSE
          RU=RAND(1.0D0)
          EDE2=EDE*EDE
          VDE3=3.0D0*VDE
          IF(EDE2.LT.VDE3) THEN
            PNULL=(VDE3-EDE2)/(VDE3+3.0D0*EDE2)
            IF(RU.LT.PNULL) THEN
              DE=0.0D0
            ELSE
              DE=1.5D0*(EDE+VDE/EDE)*(RU-PNULL)/(1.0D0-PNULL)
            ENDIF
          ELSE
            DE=EDE+(2.0D0*RU-1.0D0)*SQRT(VDE3)
          ENDIF
        ENDIF
      ENDIF
C
      E=E-DE
      IF(E.LT.EABS(1,M)) THEN
        DE=E+DE
        E=0.0D0
        RETURN
      ENDIF
      IF(KSOFTE.EQ.0) RETURN
C
C  ****  Bielajew's randomly alternate hinge.
C
      IF(DE.GT.1.0D-3) THEN
        IF(RAND(2.0D0)*DST.GT.DS1) THEN
          XEL=LOG(E)
          XE=1.0D0+(XEL-DLEMP1)*DLFC
          KE=XE
          XEK=XE-KE
          IF(T1E(M,KE+1).GT.-78.3D0) THEN
            T1=EXP(T1E(M,KE)+(T1E(M,KE+1)-T1E(M,KE))*XEK)
            T2=EXP(T2E(M,KE)+(T2E(M,KE+1)-T2E(M,KE))*XEK)
          ELSE
            T1=0.0D0
            T2=0.0D0
          ENDIF
          IF(T1.LT.1.0D-35) RETURN
        ENDIF
      ENDIF
C  ****  1st and 2nd moments of the angular distribution.
      EMU1=0.5D0*(1.0D0-EXP(-DST*T1))
      EMU2=EMU1-(1.0D0-EXP(-DST*T2))/6.0D0
C  ****  Sampling from a two-bar histogram with these moments.
      PNUM=2.0D0*EMU1-3.0D0*EMU2
      PDEN=1.0D0-2.0D0*EMU1
      PB=PNUM/PDEN
      PA=PDEN+PB
      RND=RAND(3.0D0)
      IF(RND.LT.PA) THEN
        CDT=1.0D0-2.0D0*PB*(RND/PA)
      ELSE
        CDT=1.0D0-2.0D0*(PB+(1.0D0-PB)*((RND-PA)/(1.0D0-PA)))
      ENDIF
      DF=TWOPI*RAND(4.0D0)
      CALL DIRECT(CDT,DF,U,V,W)
      RETURN
C
C  ************  Hard event.
C
 1100 CONTINUE
      MODE=0
C  ****  A delta interaction (ICOL=7) occurs when the maximum
C        allowed step length is exceeded.
      IF(KDELTA.EQ.1) THEN
        ICOL=7
        DE=0.0D0
        RETURN
      ENDIF
C  ****  Interaction probabilities.
      STNOW=P(2)+P(3)+P(4)+P(5)
C  ****  Random sampling of the interaction type.
      STS=MAX(STNOW,ST)*RAND(5.0D0)
      SS=P(2)
      IF(SS.GT.STS) GO TO 1200
      SS=SS+P(3)
      IF(SS.GT.STS) GO TO 1300
      SS=SS+P(4)
      IF(SS.GT.STS) GO TO 1400
      SS=SS+P(5)
      IF(SS.GT.STS) GO TO 1500
      SS=SS+P(8)
      IF(SS.GT.STS) GO TO 1800
C  ****  A delta interaction (ICOL=7) may occur when the total
C        interaction probability per unit path length, ST, is
C        larger than STNOW.
      ICOL=7
      DE=0.0D0
      RETURN
C
C  ****  Hard elastic collision (ICOL=2).
C
 1200 ICOL=2
      IF(E.GE.EELMAX(M)) THEN
        TRNDC=RNDCE(M,KE)+(RNDCE(M,KE+1)-RNDCE(M,KE))*XEK
        TA=EXP(AE(M,KE)+(AE(M,KE+1)-AE(M,KE))*XEK)
        TB=BE(M,KE)+(BE(M,KE+1)-BE(M,KE))*XEK
        CALL EELa(TA,TB,TRNDC,RMU)
      ELSE
        TRNDC=RNDCEd(M,KE)+(RNDCEd(M,KE+1)-RNDCEd(M,KE))*XEK
        CALL EELd(TRNDC,RMU)  ! Uses the ELSEPA database.
      ENDIF
      CDT=1.0D0-(RMU+RMU)
      DF=TWOPI*RAND(6.0D0)
      CALL DIRECT(CDT,DF,U,V,W)
      DE=0.0D0
      RETURN
C
C  ****  Hard inelastic collision (ICOL=3).
C
 1300 ICOL=3
      DELTA=DEL(M,KE)+(DEL(M,KE+1)-DEL(M,KE))*XEK
      CALL EINa(E,DELTA,DE,EP,CDT,ES,CDTS,M,IOSC)
C  ****  Scattering angles (primary electron).
      DF=TWOPI*RAND(7.0D0)
C  ****  Delta ray.
      IF(ES.GT.EABS(1,M)) THEN
        DFS=DF+PI
        US=U
        VS=V
        WS=W
        CALL DIRECT(CDTS,DFS,US,VS,WS)
        ILBA(1)=ILB(1)+1
        ILBA(2)=KPAR
        ILBA(3)=ICOL
        ILBA(4)=0
        ILBA(5)=ILB(5)
        CALL STORES(ES,X,Y,Z,US,VS,WS,WGHT,1,ILBA)
      ENDIF
C  ****  New energy and direction.
      IF(EP.GT.EABS(1,M)) THEN
        E=EP
        CALL DIRECT(CDT,DF,U,V,W)
        RETURN
      ENDIF
      DE=E
      E=0.0D0
      RETURN
C
C  ****  Hard bremsstrahlung emission (ICOL=4).
C
 1400 ICOL=4
      CALL EBRa(E,DE,M)
C  ****  Bremsstrahlung photon.
      IF(DE.GT.EABS(2,M)) THEN
        CALL EBRaA(E,DE,CDTS,M)
        DFS=TWOPI*RAND(8.0D0)
        US=U
        VS=V
        WS=W
        CALL DIRECT(CDTS,DFS,US,VS,WS)
        ILBA(1)=ILB(1)+1
        ILBA(2)=KPAR
        ILBA(3)=ICOL
        ILBA(4)=0
        ILBA(5)=ILB(5)
        CALL STORES(DE,X,Y,Z,US,VS,WS,WGHT,2,ILBA)
      ENDIF
C  ****  New energy.
      E=E-DE
      IF(E.GT.EABS(1,M)) RETURN
      DE=E+DE
      E=0.0D0
      RETURN
C
C  ****  Ionisation of an inner shell (ICOL=5) -does not affect the
C        primary electron.
C
 1500 ICOL=5
      DE=0.0D0
      CALL ESIa(IZA,ISA)
      IF(IZA.LT.1) RETURN
      ILBA(3)=ICOL
      CALL RELAX(IZA,ISA)
      RETURN
C
C  ****  Auxiliary fictitious mechanism (ICOL=8).
C
 1800 ICOL=8
      DE=0.0D0
      CALL EAUX
      RETURN
C
C  ************  Photons (KPAR=2).
C
 2000 CONTINUE
C
      STS=ST*RAND(1.0D0)
      SS=P(1)
      IF(SS.GT.STS) GO TO 2100
      SS=SS+P(2)
      IF(SS.GT.STS) GO TO 2200
      SS=SS+P(3)
      IF(SS.GT.STS) GO TO 2300
      SS=SS+P(4)
      IF(SS.GT.STS) GO TO 2400
      SS=SS+P(8)
      IF(SS.GT.STS) GO TO 2800
C
C  ****  Rayleigh scattering (ICOL=1).
C
 2100 CONTINUE
      DE=0.0D0
      CALL GRAa(E,CDT,M,IEFF)
C  ****  Delta interaction. Introduced to correct for the use of an
C        upper bound of the Rayleigh attenuation coefficient.
      IF(IEFF.EQ.0) THEN
        ICOL=7
        RETURN
      ENDIF
      ICOL=1
      IF(IPOL.EQ.1) THEN
        CALL DIRPOL(CDT,DF,0.0D0,SP1,SP2,SP3,U,V,W)
      ELSE
        DF=TWOPI*RAND(2.0D0)
        CALL DIRECT(CDT,DF,U,V,W)
      ENDIF
      RETURN
C
C  ****  Compton scattering (ICOL=2).
C
 2200 ICOL=2
      CALL GCOa(E,DE,EP,CDT,ES,CDTS,M,ISHELL)
      IZA=KZCO(M,ISHELL)
      ISA=KSCO(M,ISHELL)
      US=U
      VS=V
      WS=W
      DF=-1.0D0
      IF(IZA.GT.0.AND.ISA.LT.10) THEN
        ILBA(3)=ICOL
        CALL RELAX(IZA,ISA)
      ENDIF
C  ****  New direction and energy.
      IF(EP.GT.EABS(2,M)) THEN
        IF(IPOL.EQ.1) THEN
          ECDT=E*RREV*(1.0D0-CDT)
          CONS=ECDT*ECDT/(1.0D0+ECDT)
          CALL DIRPOL(CDT,DF,CONS,SP1,SP2,SP3,U,V,W)
        ELSE
          DF=TWOPI*RAND(3.0D0)
          CALL DIRECT(CDT,DF,U,V,W)
        ENDIF
        E=EP
      ELSE
        DE=E
        E=0.0D0
      ENDIF
C  ****  Compton electron.
      IF(ES.GT.EABS(1,M)) THEN
        IF(DF.LT.-0.5D0) DF=TWOPI*RAND(4.0D0)
        DFS=DF+PI
        CALL DIRECT(CDTS,DFS,US,VS,WS)
        ILBA(1)=ILB(1)+1
        ILBA(2)=KPAR
        ILBA(3)=ICOL
        ILBA(4)=IZA*1000000+ISA
        ILBA(5)=ILB(5)
        CALL STORES(ES,X,Y,Z,US,VS,WS,WGHT,1,ILBA)
      ENDIF
      RETURN
C
C  ****  Photoelectric absorption (ICOL=3).
C
 2300 ICOL=3
      CALL GPHa(ES,IZA,ISA)
C  ****  Delta interaction. Introduced to correct for the use of an
C        upper bound of the photoelectric attenuation coefficient.
      IF(IZA.EQ.0) THEN
        ICOL=7
        DE=0.0D0
        RETURN
      ENDIF
C
      IF(ES.GT.EABS(1,M)) THEN
        CALL SAUTER(ES,CDTS)
        DFS=TWOPI*RAND(5.0D0)
        US=U
        VS=V
        WS=W
        CALL DIRECT(CDTS,DFS,US,VS,WS)
        ILBA(1)=ILB(1)+1
        ILBA(2)=KPAR
        ILBA(3)=ICOL
        ILBA(4)=IZA*1000000+ISA
        ILBA(5)=ILB(5)
        CALL STORES(ES,X,Y,Z,US,VS,WS,WGHT,1,ILBA)
      ENDIF
      IF(ISA.LT.17) THEN
        ILBA(3)=ICOL
        CALL RELAX(IZA,ISA)
      ENDIF
      DE=E
      E=0.0D0
      RETURN
C
C  ****  Electron-positron pair production (ICOL=4).
C
 2400 ICOL=4
      CALL GPPa(EE,CDTE,EP,CDTP,IZA,ISA)
      DE=E
C  ****  Electron.
      IF(EE.GT.EABS(1,M)) THEN
        DF=TWOPI*RAND(6.0D0)
        US=U
        VS=V
        WS=W
        CALL DIRECT(CDTE,DF,US,VS,WS)
        ILBA(1)=ILB(1)+1
        ILBA(2)=KPAR
        ILBA(3)=ICOL
        ILBA(4)=0
        ILBA(5)=ILB(5)
        CALL STORES(EE,X,Y,Z,US,VS,WS,WGHT,1,ILBA)
      ENDIF
C  ****  Positron.
      IF(EP.GT.EABS(3,M)) THEN
        DF=TWOPI*RAND(7.0D0)
        CALL DIRECT(CDTP,DF,U,V,W)
        ILBA(1)=ILB(1)+1
        ILBA(2)=KPAR
        ILBA(3)=ICOL
        ILBA(4)=0
        ILBA(5)=ILB(5)
        CALL STORES(EP,X,Y,Z,U,V,W,WGHT,3,ILBA)
C  ****  The positron carries a 'latent' energy of 1022 keV.
        DE=DE-TREV
      ELSE
        CALL PANaR
      ENDIF
      E=0.0D0
C  ****  Atomic relaxation after triplet production.
      IF(ISA.LT.17) THEN
        ILBA(3)=ICOL
        CALL RELAX(IZA,ISA)
      ENDIF
      RETURN
C
C  ****  Auxiliary fictitious mechanism (ICOL=8).
C
 2800 ICOL=8
      DE=0.0D0
      CALL GAUX
      RETURN
C
C  ************  Positrons (KPAR=3).
C
 3000 CONTINUE
      IF(MODE.EQ.1) GO TO 3100
C
C  ****  Artificial soft event (ICOL=1).
C
      ICOL=1
      MODE=1
C
      IF(KSOFTI.EQ.0) THEN
        DE=0.0D0
      ELSE
        EDE0=W1*DST
        VDE0=W2*DST
        FSEDE=MAX(1.0D0-DW1PL(M,KE)*EDE0,0.75D0)
        FSVDE=MAX(1.0D0-DW2PL(M,KE)*EDE0,0.75D0)
        EDE=EDE0*FSEDE
        VDE=VDE0*FSVDE
C  ****  Generation of random values DE with mean EDE and variance VDE.
        SIGMA=SQRT(VDE)
        IF(SIGMA.LT.0.333333333D0*EDE) THEN
C  ****  Truncated Gaussian distribution.
          DE=EDE+RNDG3()*SIGMA
        ELSE
          RU=RAND(1.0D0)
          EDE2=EDE*EDE
          VDE3=3.0D0*VDE
          IF(EDE2.LT.VDE3) THEN
            PNULL=(VDE3-EDE2)/(VDE3+3.0D0*EDE2)
            IF(RU.LT.PNULL) THEN
              DE=0.0D0
            ELSE
              DE=1.5D0*(EDE+VDE/EDE)*(RU-PNULL)/(1.0D0-PNULL)
            ENDIF
          ELSE
            DE=EDE+(2.0D0*RU-1.0D0)*SQRT(VDE3)
          ENDIF
        ENDIF
      ENDIF
C
      E=E-DE
C  ****  Annihilation at rest.
      IF(E.LT.EABS(3,M)) THEN
        DE=E+DE+TREV
        E=0.0D0
        CALL PANaR
        RETURN
      ENDIF
      IF(KSOFTE.EQ.0) RETURN
C
C  ****  Bielajew's randomly alternate hinge.
C
      IF(DE.GT.1.0D-3) THEN
        IF(RAND(2.0D0)*DST.GT.DS1) THEN
          XEL=LOG(E)
          XE=1.0D0+(XEL-DLEMP1)*DLFC
          KE=XE
          XEK=XE-KE
          IF(T1E(M,KE+1).GT.-78.3D0) THEN
            T1=EXP(T1P(M,KE)+(T1P(M,KE+1)-T1P(M,KE))*XEK)
            T2=EXP(T2P(M,KE)+(T2P(M,KE+1)-T2P(M,KE))*XEK)
          ELSE
            T1=0.0D0
            T2=0.0D0
          ENDIF
          IF(T1.LT.1.0D-35) RETURN
        ENDIF
      ENDIF
C  ****  1st and 2nd moments of the angular distribution.
      EMU1=0.5D0*(1.0D0-EXP(-DST*T1))
      EMU2=EMU1-(1.0D0-EXP(-DST*T2))/6.0D0
C  ****  Sampling from a two-bar histogram with these moments.
      PNUM=2.0D0*EMU1-3.0D0*EMU2
      PDEN=1.0D0-2.0D0*EMU1
      PB=PNUM/PDEN
      PA=PDEN+PB
      RND=RAND(3.0D0)
      IF(RND.LT.PA) THEN
        CDT=1.0D0-2.0D0*PB*(RND/PA)
      ELSE
        CDT=1.0D0-2.0D0*(PB+(1.0D0-PB)*((RND-PA)/(1.0D0-PA)))
      ENDIF
      DF=TWOPI*RAND(4.0D0)
      CALL DIRECT(CDT,DF,U,V,W)
      RETURN
C
C  ************  Hard event.
C
 3100 CONTINUE
      MODE=0
C  ****  A delta interaction (ICOL=7) occurs when the maximum
C        allowed step length is exceeded.
      IF(KDELTA.EQ.1) THEN
        ICOL=7
        DE=0.0D0
        RETURN
      ENDIF
C  ****  Interaction probabilities.
      STNOW=P(2)+P(3)+P(4)+P(5)+P(6)
C  ****  Random sampling of the interaction type.
      STS=MAX(STNOW,ST)*RAND(5.0D0)
      SS=P(2)
      IF(SS.GT.STS) GO TO 3200
      SS=SS+P(3)
      IF(SS.GT.STS) GO TO 3300
      SS=SS+P(4)
      IF(SS.GT.STS) GO TO 3400
      SS=SS+P(5)
      IF(SS.GT.STS) GO TO 3500
      SS=SS+P(6)
      IF(SS.GT.STS) GO TO 3600
      SS=SS+P(8)
      IF(SS.GT.STS) GO TO 3800
C  ****  A delta interaction (ICOL=7) may occur when the total
C        interaction probability per unit path length, ST, is
C        larger than STNOW.
      ICOL=7
      DE=0.0D0
      RETURN
C
C  ****  Hard elastic collision (ICOL=2).
C
 3200 ICOL=2
      IF(E.GE.PELMAX(M)) THEN
        TRNDC=RNDCP(M,KE)+(RNDCP(M,KE+1)-RNDCP(M,KE))*XEK
        TA=EXP(AP(M,KE)+(AP(M,KE+1)-AP(M,KE))*XEK)
        TB=BP(M,KE)+(BP(M,KE+1)-BP(M,KE))*XEK
        CALL EELa(TA,TB,TRNDC,RMU)
      ELSE
        TRNDC=RNDCPd(M,KE)+(RNDCPd(M,KE+1)-RNDCPd(M,KE))*XEK
        CALL PELd(TRNDC,RMU)  ! Uses the ELSEPA database.
      ENDIF
      CDT=1.0D0-2.0D0*RMU
      DF=TWOPI*RAND(6.0D0)
      CALL DIRECT(CDT,DF,U,V,W)
      DE=0.0D0
      RETURN
C
C  ****  Hard inelastic collision (ICOL=3).
C
 3300 ICOL=3
      DELTA=DEL(M,KE)+(DEL(M,KE+1)-DEL(M,KE))*XEK
      CALL PINa(E,DELTA,DE,EP,CDT,ES,CDTS,M,IOSC)
C  ****  Scattering angles (primary particle).
      DF=TWOPI*RAND(7.0D0)
C  ****  Delta ray.
      IF(ES.GT.EABS(1,M)) THEN
        DFS=DF+PI
        US=U
        VS=V
        WS=W
        CALL DIRECT(CDTS,DFS,US,VS,WS)
        ILBA(1)=ILB(1)+1
        ILBA(2)=KPAR
        ILBA(3)=ICOL
        ILBA(4)=0
        ILBA(5)=ILB(5)
        CALL STORES(ES,X,Y,Z,US,VS,WS,WGHT,1,ILBA)
      ENDIF
C  ****  New energy and direction.
      IF(EP.GT.EABS(3,M)) THEN
        E=EP
        CALL DIRECT(CDT,DF,U,V,W)
        RETURN
      ENDIF
      DE=E+TREV
      E=0.0D0
C  ****  Annihilation at rest.
      CALL PANaR
      RETURN
C
C  ****  Hard bremsstrahlung emission (ICOL=4).
C
 3400 ICOL=4
      CALL EBRa(E,DE,M)
C  ****  Bremsstrahlung photon.
      IF(DE.GT.EABS(2,M)) THEN
        CALL EBRaA(E,DE,CDTS,M)
        DFS=TWOPI*RAND(8.0D0)
        US=U
        VS=V
        WS=W
        CALL DIRECT(CDTS,DFS,US,VS,WS)
        ILBA(1)=ILB(1)+1
        ILBA(2)=KPAR
        ILBA(3)=ICOL
        ILBA(4)=0
        ILBA(5)=ILB(5)
        CALL STORES(DE,X,Y,Z,US,VS,WS,WGHT,2,ILBA)
      ENDIF
C  ****  New energy.
      E=E-DE
      IF(E.GT.EABS(3,M)) RETURN
      DE=E+DE+TREV
      E=0.0D0
C  ****  Annihilation at rest.
      CALL PANaR
      RETURN
C
C  ****  Ionisation of an inner shell (ICOL=5) -does not affect the
C        primary positron.
C
 3500 ICOL=5
      DE=0.0D0
      CALL PSIa(IZA,ISA)
      IF(IZA.LT.1) RETURN
      ILBA(3)=ICOL
      CALL RELAX(IZA,ISA)
      RETURN
C
C  ****  Positron annihilation in flight (ICOL=6).
C
 3600 ICOL=6
      CALL PANa(E1,CDT1,E2,CDT2)
      DF=TWOPI*RAND(9.0D0)
      IF(E1.GT.EABS(2,M)) THEN
        US=U
        VS=V
        WS=W
        CALL DIRECT(CDT1,DF,US,VS,WS)
        ILBA(1)=ILB(1)+1
        ILBA(2)=KPAR
        ILBA(3)=ICOL
        ILBA(4)=0
        ILBA(5)=ILB(5)
        CALL STORES(E1,X,Y,Z,US,VS,WS,WGHT,2,ILBA)
      ENDIF
      IF(E2.GT.EABS(2,M)) THEN
        DF=DF+PI
        US=U
        VS=V
        WS=W
        CALL DIRECT(CDT2,DF,US,VS,WS)
        ILBA(1)=ILB(1)+1
        ILBA(2)=KPAR
        ILBA(3)=ICOL
        ILBA(4)=0
        ILBA(5)=ILB(5)
        CALL STORES(E2,X,Y,Z,US,VS,WS,WGHT,2,ILBA)
      ENDIF
      DE=E+TREV
      E=0.0D0
      RETURN
C
C  ****  Auxiliary fictitious mechanism (ICOL=8).
C
 3800 ICOL=8
      DE=0.0D0
      CALL PAUX
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE DIRECT
C  *********************************************************************
      SUBROUTINE DIRECT(CDT,DF,U,V,W)
C
C  This subroutine computes the new direction cosines of the particle
C  velocity after a collision with given polar and azimuthal scattering
C  angles.
C
C  Input:  U,V,W ... initial direction cosines.
C          CDT ..... cosine of the polar scattering angle.
C          DF ...... azimuthal scattering angle (rad).
C
C  Output: U,V,W ... new direction cosines.
C          CDT and DF remain unchanged.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C
      SDF=SIN(DF)
      CDF=COS(DF)
C  ****  Ensure normalisation.
      DXY=U*U+V*V
      DXYZ=DXY+W*W
      IF(ABS(DXYZ-1.0D0).GT.1.0D-14) THEN
        FNORM=1.0D0/SQRT(DXYZ)
        U=FNORM*U
        V=FNORM*V
        W=FNORM*W
        DXY=U*U+V*V
      ENDIF
C
      IF(DXY.GT.1.0D-28) THEN
        SDT=SQRT((1.0D0-CDT*CDT)/DXY)
        UP=U
        U=U*CDT+SDT*(UP*W*CDF-V*SDF)
        V=V*CDT+SDT*(V*W*CDF+UP*SDF)
        W=W*CDT-DXY*SDT*CDF
      ELSE
        SDT=SQRT(1.0D0-CDT*CDT)
        V=SDT*SDF
        IF(W.GT.0.0D0) THEN
          U=SDT*CDF
          W=CDT
        ELSE
          U=-SDT*CDF
          W=-CDT
        ENDIF
      ENDIF
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE DIRPOL
C  *********************************************************************
      SUBROUTINE DIRPOL(CDT,DF,CONS,SP1,SP2,SP3,U,V,W)
C
C     This subroutine computes the direction cosines _and_ the Stokes
C  parameters of a polarised photon after scattering with a given polar
C  angle.
C
C  Input:  U,V,W ... initial direction cosines.
C          SP1,SP2,SP3 ... initial Stokes parameters.
C          CDT ..... cosine of the polar scattering angle.
C          CONS .... constant in the PDF of the azimuthal angle.
C  Output: U,V,W ... new direction cosines.
C          SP1,SP2,SP3 ... new Stokes parameters.
C          DF ...... azimuthal scattering angle.
C          CDT and CONS remain unchanged.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (PI=3.1415926535897932D0, TWOPI=2.0D0*PI)
      EXTERNAL RAND
C
C  ****  Sampling the azimuthal scattering angle.
C
      CDT2=CDT*CDT
      CDT21=CDT2+1.0D0
      PHA=CDT21+CONS
      PHB=1.0D0-CDT2
      SP0MAX=PHA+PHB*DSQRT(SP1*SP1+SP3*SP3+1.0D-16)
    1 CONTINUE
      DF=RAND(1.0D0)*TWOPI
      SDF=SIN(DF)
      CDF=COS(DF)
      S2DF=2.0D0*SDF*CDF
      C2DF=CDF*CDF-SDF*SDF
      SP3P=S2DF*SP1+C2DF*SP3  ! Stokes parameter with new zero-azimuth.
      SP0P=PHA-PHB*SP3P
      IF(RAND(2.0D0)*SP0MAX.GT.SP0P) GO TO 1
C
C  ****  Calculate new Stokes parameters.
C
      SP1P=C2DF*SP1-S2DF*SP3  ! Stokes parameter with new zero-azimuth.
      RSP0=1.0D0/SP0P
C
      SP1=2.0D0*CDT*SP1P*RSP0
      SP2=(2.0D0+CONS)*CDT*SP2*RSP0
      SP3=(CDT21*SP3P-PHB)*RSP0
C
C  ****  Ensure normalisation.
C
      DXY=U*U+V*V
      DXYZ=DXY+W*W
      IF(ABS(DXYZ-1.0D0).GT.1.0D-14) THEN
        FNORM=1.0D0/SQRT(DXYZ)
        U=FNORM*U
        V=FNORM*V
        W=FNORM*W
        DXY=U*U+V*V
      ENDIF
C
C  ****  Calculate new direction.
C
      IF(DXY.GT.1.0D-28) THEN
        SDT=SQRT(PHB/DXY)
        UP=U
        U=U*CDT+SDT*(UP*W*CDF-V*SDF)
        V=V*CDT+SDT*(V*W*CDF+UP*SDF)
        W=W*CDT-DXY*SDT*CDF
      ELSE
        SDT=SQRT(PHB)
        V=SDT*SDF
        IF(W.GT.0.0D0) THEN
          U=SDT*CDF
          W=CDT
        ELSE
          U=-SDT*CDF
          W=-CDT
        ENDIF
      ENDIF
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE STORES
C  *********************************************************************
      SUBROUTINE STORES(EI,XI,YI,ZI,UI,VI,WI,WGHTI,KPARI,ILBI)
C
C  This subroutine stores the initial state of a new secondary particle
C  in the secondary stack. The input values are:
C     EI ........... initial energy.
C     XI, YI, ZI ... initial position coordinates.
C     UI, VI, WI ... initial direction cosines.
C     WGHTI ........ weight (=1 in analogue simulation).
C     KPARI ........ kind of particle (1: electron, 2: photon,
C                    3: positron).
C     ILBI(5) ...... particle labels.
C
C  The parameter NMS fixes the size of the secondary stack (i.e. the
C  maximum number of particles that can be stored). If this number is
C  exceeded, a warning message is printed on unit 26. When the memory
C  storage is exhausted, each new secondary particle is stored on the
C  position of the less energetic secondary electron or photon already
C  produced, which is thus discarded.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (NMS=1000)
      DIMENSION ILBI(5)
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C  ****  Secondary stack.
      COMMON/SECST/ES(NMS),XS(NMS),YS(NMS),ZS(NMS),US(NMS),
     1   VS(NMS),WS(NMS),WGHTS(NMS),KS(NMS),IBODYS(NMS),MS(NMS),
     2   ILBS(5,NMS),NSEC
      COMMON/CERSEC/IERSEC
C
      IF(NSEC.LT.NMS) THEN
        NSEC=NSEC+1
        IS=NSEC
      ELSE
        IF(IERSEC.EQ.0) THEN
          WRITE(26,1001)
 1001     FORMAT(/3X,'*** WARNING: (STORES) not enough storage for ',
     1      'secondaries.',/16X,'EABS(KPAR,m) or the parameter NMS ',
     2      'should be enlarged.')
          IERSEC=1
        ENDIF
        NSEC=NMS
        EME=1.0D35
        EMG=1.0D35
        IE=0
        IG=0
        DO 1 I=1,NMS
        IF(KS(I).EQ.1) THEN
          IF(ES(I).LT.EME) THEN
            EME=ES(I)
            IE=I
          ENDIF
        ELSE IF(KS(I).EQ.2) THEN
          IF (ES(I).LT.EMG) THEN
            EMG=ES(I)
            IG=I
          ENDIF
        ENDIF
    1   CONTINUE
C
        IF(IE.GT.0) THEN
          IS=IE
        ELSE IF(IG.GT.0) THEN
          IS=IG
        ELSE
          WRITE(26,1002)
 1002     FORMAT(/3X,'*** Not enough storage for secondary positrons.',
     1      /7X,'JOB ABORTED.')
          IS=0
          CALL PISTOP(
     1      'STORES. Not enough storage for secondary positrons.')
        ENDIF
C
        DO I=IS,NMS-1
          ES(I)=ES(I+1)
          XS(I)=XS(I+1)
          YS(I)=YS(I+1)
          ZS(I)=ZS(I+1)
          US(I)=US(I+1)
          VS(I)=VS(I+1)
          WS(I)=WS(I+1)
          WGHTS(I)=WGHTS(I+1)
          KS(I)=KS(I+1)
          IBODYS(I)=IBODYS(I+1)
          MS(I)=MS(I+1)
          DO IB=1,5
            ILBS(IB,I)=ILBS(IB,I+1)
          ENDDO
        ENDDO
        IS=NMS
      ENDIF
C
      ES(IS)=EI
      XS(IS)=XI
      YS(IS)=YI
      ZS(IS)=ZI
      US(IS)=UI
      VS(IS)=VI
      WS(IS)=WI
      WGHTS(IS)=WGHTI
      KS(IS)=KPARI
      IBODYS(IS)=IBODY
      MS(IS)=M
      ILBS(1,IS)=ILBI(1)
      ILBS(2,IS)=ILBI(2)
      ILBS(3,IS)=ILBI(3)
      ILBS(4,IS)=ILBI(4)
      ILBS(5,IS)=ILBI(5)
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE SECPAR
C  *********************************************************************
      SUBROUTINE SECPAR(LEFT)
C
C  This subroutine delivers the initial state of a secondary particle
C  produced during the previous simulation of the shower. This particle
C  is removed from the secondary stack, so that it will be lost if a new
C  call to SECPAR is performed before simulating its trajectory up to
C  the end.
C
C  LEFT is the number of particles in the secondary stack at the calling
C  time. When LEFT=0, the simulation of the shower has been completed.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C  ****  Secondary stack.
      PARAMETER (NMS=1000)
      COMMON/SECST/ES(NMS),XS(NMS),YS(NMS),ZS(NMS),US(NMS),
     1   VS(NMS),WS(NMS),WGHTS(NMS),KS(NMS),IBODYS(NMS),MS(NMS),
     2   ILBS(5,NMS),NSEC
C
      IF(NSEC.GT.0) THEN
        LEFT=NSEC
        E=ES(NSEC)
        X=XS(NSEC)
        Y=YS(NSEC)
        Z=ZS(NSEC)
        U=US(NSEC)
        V=VS(NSEC)
        W=WS(NSEC)
        WGHT=WGHTS(NSEC)
        KPAR=KS(NSEC)
        IBODY=IBODYS(NSEC)
        M=MS(NSEC)
        DO I=1,5
          ILB(I)=ILBS(I,NSEC)
        ENDDO
        NSEC=NSEC-1
      ELSE
        LEFT=0
      ENDIF
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE EIMFP
C  *********************************************************************
      SUBROUTINE EIMFP(IEND)
C
C  This subroutine computes the inverse mean free paths for hard inter-
C  actions of electrons with the current energy in material M.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Electron simulation tables.
      PARAMETER (MAXMAT=10)
      COMMON/CEIMFP/SEHEL(MAXMAT,NEGP),SEHIN(MAXMAT,NEGP),
     1  SEISI(MAXMAT,NEGP),SEHBR(MAXMAT,NEGP),SEAUX(MAXMAT,NEGP),
     2  SETOT(MAXMAT,NEGP),CSTPE(MAXMAT,NEGP),RSTPE(MAXMAT,NEGP),
     3  DEL(MAXMAT,NEGP),W1E(MAXMAT,NEGP),W2E(MAXMAT,NEGP),
     4  DW1EL(MAXMAT,NEGP),DW2EL(MAXMAT,NEGP),
     5  RNDCE(MAXMAT,NEGP),AE(MAXMAT,NEGP),BE(MAXMAT,NEGP),
     6  T1E(MAXMAT,NEGP),T2E(MAXMAT,NEGP)
C  ****  Current IMFPs.
      COMMON/CJUMP0/P(8),ST,DST,DS1,W1,W2,T1,T2
C
      P(2)=EXP(SEHEL(M,KE)+(SEHEL(M,KE+1)-SEHEL(M,KE))*XEK)
      P(3)=EXP(SEHIN(M,KE)+(SEHIN(M,KE+1)-SEHIN(M,KE))*XEK)
      P(4)=EXP(SEHBR(M,KE)+(SEHBR(M,KE+1)-SEHBR(M,KE))*XEK)
      P(5)=EXP(SEISI(M,KE)+(SEISI(M,KE+1)-SEISI(M,KE))*XEK)
      P(8)=0.0D0
      IF(IEND.EQ.1) RETURN
      IF(W1E(M,KE+1).GT.-78.3D0) THEN
        W1=EXP(W1E(M,KE)+(W1E(M,KE+1)-W1E(M,KE))*XEK)
        W2=EXP(W2E(M,KE)+(W2E(M,KE+1)-W2E(M,KE))*XEK)
      ELSE
        W1=0.0D0
        W2=0.0D0
      ENDIF
      IF(T1E(M,KE+1).GT.-78.3D0) THEN
        T1=EXP(T1E(M,KE)+(T1E(M,KE+1)-T1E(M,KE))*XEK)
        T2=EXP(T2E(M,KE)+(T2E(M,KE+1)-T2E(M,KE))*XEK)
      ELSE
        T1=0.0D0
        T2=0.0D0
      ENDIF
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PIMFP
C  *********************************************************************
      SUBROUTINE PIMFP(IEND)
C
C  This subroutine computes the inverse mean free paths for hard inter-
C  actions of positrons with the current energy in material M.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Positron simulation tables.
      PARAMETER (MAXMAT=10)
      COMMON/CPIMFP/SPHEL(MAXMAT,NEGP),SPHIN(MAXMAT,NEGP),
     1  SPISI(MAXMAT,NEGP),SPHBR(MAXMAT,NEGP),SPAN(MAXMAT,NEGP),
     2  SPAUX(MAXMAT,NEGP),SPTOT(MAXMAT,NEGP),CSTPP(MAXMAT,NEGP),
     3  RSTPP(MAXMAT,NEGP),W1P(MAXMAT,NEGP),W2P(MAXMAT,NEGP),
     4  DW1PL(MAXMAT,NEGP),DW2PL(MAXMAT,NEGP),
     5  RNDCP(MAXMAT,NEGP),AP(MAXMAT,NEGP),BP(MAXMAT,NEGP),
     6  T1P(MAXMAT,NEGP),T2P(MAXMAT,NEGP)
C  ****  Current IMFPs.
      COMMON/CJUMP0/P(8),ST,DST,DS1,W1,W2,T1,T2
C
      P(2)=EXP(SPHEL(M,KE)+(SPHEL(M,KE+1)-SPHEL(M,KE))*XEK)
      P(3)=EXP(SPHIN(M,KE)+(SPHIN(M,KE+1)-SPHIN(M,KE))*XEK)
      P(4)=EXP(SPHBR(M,KE)+(SPHBR(M,KE+1)-SPHBR(M,KE))*XEK)
      P(5)=EXP(SPISI(M,KE)+(SPISI(M,KE+1)-SPISI(M,KE))*XEK)
      P(6)=EXP(SPAN(M,KE)+(SPAN(M,KE+1)-SPAN(M,KE))*XEK)
      P(8)=0.0D0
      IF(IEND.EQ.1) RETURN
      IF(W1P(M,KE+1).GT.-78.3D0) THEN
        W1=EXP(W1P(M,KE)+(W1P(M,KE+1)-W1P(M,KE))*XEK)
        W2=EXP(W2P(M,KE)+(W2P(M,KE+1)-W2P(M,KE))*XEK)
      ELSE
        W1=0.0D0
        W2=0.0D0
      ENDIF
      IF(T1P(M,KE+1).GT.-78.3D0) THEN
        T1=EXP(T1P(M,KE)+(T1P(M,KE+1)-T1P(M,KE))*XEK)
        T2=EXP(T2P(M,KE)+(T2P(M,KE+1)-T2P(M,KE))*XEK)
      ELSE
        T1=0.0D0
        T2=0.0D0
      ENDIF
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE GIMF
C  *********************************************************************
      SUBROUTINE GIMFP
C
C  This subroutine computes the inverse mean free paths for interactions
C  of photons with the current energy in material M.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Photon simulation tables.
      PARAMETER (MAXMAT=10)
      COMMON/CGIMFP/SGRA(MAXMAT,NEGP),SGCO(MAXMAT,NEGP),
     1  SGPH(MAXMAT,NEGP),SGPP(MAXMAT,NEGP),SGAUX(MAXMAT,NEGP)
C  ****  Current IMFPs.
      COMMON/CJUMP0/P(8),ST,DST,DS1,W1,W2,T1,T2
C
      P(1)=SGRA(M,KE)
      P(2)=EXP(SGCO(M,KE)+(SGCO(M,KE+1)-SGCO(M,KE))*XEK)
      P(3)=SGPH(M,KE)
      IF(E.LT.1.023D6) THEN
        P(4)=0.0D0
      ELSE
        P(4)=EXP(SGPP(M,KE)+(SGPP(M,KE+1)-SGPP(M,KE))*XEK)
      ENDIF
      P(8)=0.0D0
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE EAUX
C  *********************************************************************
      SUBROUTINE EAUX
C
C  Auxiliary interaction mechanism for electrons, definable by the user.
C  Usually it is not active.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C  ****  Simulation parameters.
      PARAMETER (MAXMAT=10)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
C
      WRITE(26,1000)
 1000 FORMAT(1X,'Warning: Subroutine EAUX has been entered.')
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PAUX
C  *********************************************************************
      SUBROUTINE PAUX
C
C  Auxiliary interaction mechanism for positrons, definable by the user.
C  Usually it is not active.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C  ****  Simulation parameters.
      PARAMETER (MAXMAT=10)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
C
      WRITE(26,1000)
 1000 FORMAT(1X,'Warning: Subroutine PAUX has been entered.')
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE GAUX
C  *********************************************************************
      SUBROUTINE GAUX
C
C  Auxiliary interaction mechanism for photons, definable by the user.
C  Usually it is not active.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C  ****  Simulation parameters.
      PARAMETER (MAXMAT=10)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
C
      WRITE(26,1000)
 1000 FORMAT(1X,'Warning: Subroutine GAUX has been entered.')
      RETURN
      END


CXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
CXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
C
C     *********************************
C     *  SUBROUTINE PACKAGE PENELAST  *
C     *********************************
C
C     The following subroutines perform class II simulation of elastic
C  scattering of electrons and positrons using the numerical cross
C  sections of the ELSEPA database, which covers the energy range from
C  50 eV to 100 MeV.
C
C   ****  DO NOT USE THESE SUBROUTINES FOR ENERGIES ABOVE 100 MeV  ****
C
C                                         Francesc Salvat. October 2004.
C
C  *********************************************************************
C                       SUBROUTINE EELdW
C  *********************************************************************
      SUBROUTINE EELdW(M,IWR)
C
C  This subroutine generates a table of differential cross sections for
C  elastic scattering of electrons and positrons in material M, and
C  writes it on the material definition file. Data are read from the
C  ELSEPA elastic database files.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (PI=3.1415926535897932D0)
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
      DIMENSION IZM(30),STFM(30)
C
C  ****  Elastic scattering simulation tables.
C
      PARAMETER (NE=96,NA=606)
      COMMON/CDCSEP/ETS(NE),ETL(NE),TH(NA),THR(NA),XMU(NA),XMUL(NA),
     1       ECS(NE),ETCS1(NE),ETCS2(NE),EDCS(NE,NA),
     2       PCS(NE),PTCS1(NE),PTCS2(NE),PDCS(NE,NA),
     3       DCSI(NA),DCSIL(NA),CSI,TCS1I,TCS2I
C
      DO I=1,NELEM(M)
        IZM(I)=IZ(M,I)
        STFM(I)=STF(M,I)
      ENDDO
      CALL ELINIT(IZM,STFM,NELEM(M))
C
C  ************  Write final DCS tables.
C
C  ****  Electrons.
C
      IELEC=-1
      WRITE(IWR,2001)
 2001 FORMAT(1X,'***  Electron elastic differential cross sections')
      DO IE=1,NE
        DO  K=1,NA
          DCSI(K)=EDCS(IE,K)
        ENDDO
        ECS0=4.0D0*PI*RMOMX(XMU,DCSI,0.0D0,1.0D0,NA,0)
        ECS1=4.0D0*PI*RMOMX(XMU,DCSI,0.0D0,1.0D0,NA,1)
        ECS2=4.0D0*PI*RMOMX(XMU,DCSI,0.0D0,1.0D0,NA,2)
        TCS1=2.0D0*ECS1
        TCS2=6.0D0*(ECS1-ECS2)
        WRITE(IWR,'(I3,1P,E10.3,5E12.5)')
     1    IELEC,ETS(IE),ECS0,TCS1,TCS2
        WRITE(IWR,'(1P,10E12.5)') (EDCS(IE,K),K=1,NA)
C  ****  Consistency test.
        TS0=(ECS0-ECS(IE))/ECS(IE)
        TS1=(TCS1-ETCS1(IE))/ETCS1(IE)
        TS2=(TCS2-ETCS2(IE))/ETCS2(IE)
        TSTE=MAX(ABS(TS0),ABS(TS1),ABS(TS2))
        IF(TSTE.GT.1.0D-2) THEN
          WRITE(IWR,'('' E='',1P,E12.5)') ETS(IE)
          WRITE(IWR,'(3X,3E12.5)') ECS0,TCS1,TCS2
          WRITE(IWR,'(3X,3E12.5)') ECS(IE),ETCS1(IE),ETCS2(IE)
          WRITE(IWR,*) ' Electron cross section data are corrupt.'
          CALL PISTOP('EELdW. Electron cross section data are corrupt.')
        ENDIF
      ENDDO
C
C  ****  Positrons.
C
      IELEC=+1
      WRITE(IWR,2002)
 2002 FORMAT(1X,'***  Positron elastic differential cross sections')
      DO IE=1,NE
        DO  K=1,NA
          DCSI(K)=PDCS(IE,K)
        ENDDO
        ECS0=4.0D0*PI*RMOMX(XMU,DCSI,0.0D0,1.0D0,NA,0)
        ECS1=4.0D0*PI*RMOMX(XMU,DCSI,0.0D0,1.0D0,NA,1)
        ECS2=4.0D0*PI*RMOMX(XMU,DCSI,0.0D0,1.0D0,NA,2)
        TCS1=2.0D0*ECS1
        TCS2=6.0D0*(ECS1-ECS2)
        WRITE(IWR,'(I3,1P,E10.3,5E12.5)')
     1    IELEC,ETS(IE),ECS0,TCS1,TCS2
        WRITE(IWR,'(1P,10E12.5)') (PDCS(IE,K),K=1,NA)
C  ****  Consistency test.
        TS0=(ECS0-PCS(IE))/PCS(IE)
        TS1=(TCS1-PTCS1(IE))/PTCS1(IE)
        TS2=(TCS2-PTCS2(IE))/PTCS2(IE)
        TSTE=MAX(ABS(TS0),ABS(TS1),ABS(TS2))
        IF(TSTE.GT.1.0D-2) THEN
          WRITE(IWR,'('' E='',1P,E12.5)') ETS(IE)
          WRITE(IWR,'(3X,3E12.5)') ECS0,TCS1,TCS2
          WRITE(IWR,'(3X,3E12.5)') PCS(IE),PTCS1(IE),PTCS2(IE)
          WRITE(IWR,*) ' Positron cross section data are corrupt.'
          CALL PISTOP('EELdW. Positron cross section data are corrupt.')
        ENDIF
      ENDDO
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE EELdR
C  *********************************************************************
      SUBROUTINE EELdR(M,IRD,IWR,INFO)
C
C     This subroutine reads elastic cross sections for electrons and
c  positrons in material M from the elastic scattering database. It also
C  initialises the algorithm for simulation of elastic collisions of
C  electrons and positrons.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*50 CTEXT
      PARAMETER (PI=3.1415926535897932D0)
C  ****  Composition data.
      PARAMETER (MAXMAT=10)
      COMMON/COMPOS/STF(MAXMAT,30),ZT(MAXMAT),AT(MAXMAT),RHO(MAXMAT),
     1  VMOL(MAXMAT),IZ(MAXMAT,30),NELEM(MAXMAT)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Simulation parameters.
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
      COMMON/CEINTF/T1EI(NEGP),T2EI(NEGP),T1PI(NEGP),T2PI(NEGP)
C  ****  Electron simulation tables.
      COMMON/CEIMFP/SEHEL(MAXMAT,NEGP),SEHIN(MAXMAT,NEGP),
     1  SEISI(MAXMAT,NEGP),SEHBR(MAXMAT,NEGP),SEAUX(MAXMAT,NEGP),
     2  SETOT(MAXMAT,NEGP),CSTPE(MAXMAT,NEGP),RSTPE(MAXMAT,NEGP),
     3  DEL(MAXMAT,NEGP),W1E(MAXMAT,NEGP),W2E(MAXMAT,NEGP),
     4  DW1EL(MAXMAT,NEGP),DW2EL(MAXMAT,NEGP),
     5  RNDCE(MAXMAT,NEGP),AE(MAXMAT,NEGP),BE(MAXMAT,NEGP),
     6  T1E(MAXMAT,NEGP),T2E(MAXMAT,NEGP)
C  ****  Positron simulation tables.
      COMMON/CPIMFP/SPHEL(MAXMAT,NEGP),SPHIN(MAXMAT,NEGP),
     1  SPISI(MAXMAT,NEGP),SPHBR(MAXMAT,NEGP),SPAN(MAXMAT,NEGP),
     2  SPAUX(MAXMAT,NEGP),SPTOT(MAXMAT,NEGP),CSTPP(MAXMAT,NEGP),
     3  RSTPP(MAXMAT,NEGP),W1P(MAXMAT,NEGP),W2P(MAXMAT,NEGP),
     4  DW1PL(MAXMAT,NEGP),DW2PL(MAXMAT,NEGP),
     5  RNDCP(MAXMAT,NEGP),AP(MAXMAT,NEGP),BP(MAXMAT,NEGP),
     6  T1P(MAXMAT,NEGP),T2P(MAXMAT,NEGP)
C  ****  Total and transport cross sections.
      COMMON/CEEL01/EIT(NEGP),XE0(NEGP),XE1(NEGP),XE2(NEGP),XP0(NEGP),
     1  XP1(NEGP),XP2(NEGP),T1E0(NEGP),T2E0(NEGP),T1P0(NEGP),T2P0(NEGP),
     2  EITL(NEGP),FL(NEGP),A(NEGP),B(NEGP),C(NEGP),D(NEGP)
C
C  ****  Elastic scattering simulation tables.
C
      PARAMETER (NE=96,NA=606)
      COMMON/CDCSEP/ETS(NE),ETL(NE),TH(NA),THR(NA),XMU(NA),XMUL(NA),
     1       ECS(NE),ETCS1(NE),ETCS2(NE),EDCS(NE,NA),
     2       PCS(NE),PTCS1(NE),PTCS2(NE),PDCS(NE,NA),
     3       DCSI(NA),DCSIL(NA),CSI,TCS1I,TCS2I
C
      PARAMETER (NM=512)
      COMMON/CRITA/XTI(NM),PACI(NM),DPACI(NM),AI(NM),BI(NM),
     1             ITLI(NM),ITUI(NM),NPM1I
C
      PARAMETER (NP=128)
      COMMON/CEELDB/XSE(NP,NEGP,MAXMAT),PSE(NP,NEGP,MAXMAT),
     1              ASE(NP,NEGP,MAXMAT),BSE(NP,NEGP,MAXMAT),
     2              ITLE(NP,NEGP,MAXMAT),ITUE(NP,NEGP,MAXMAT)
      COMMON/CPELDB/XSP(NP,NEGP,MAXMAT),PSP(NP,NEGP,MAXMAT),
     1              ASP(NP,NEGP,MAXMAT),BSP(NP,NEGP,MAXMAT),
     2              ITLP(NP,NEGP,MAXMAT),ITUP(NP,NEGP,MAXMAT)
      COMMON/CELSEP/EELMAX(MAXMAT),PELMAX(MAXMAT),
     1              RNDCEd(MAXMAT,NEGP),RNDCPd(MAXMAT,NEGP)
C
      DIMENSION EGRD(16)
      DATA EGRD/1.0D0,1.25D0,1.50D0,1.75D0,2.00D0,2.50D0,3.00D0,
     1  3.50D0,4.00D0,4.50D0,5.00D0,6.00D0,7.00D0,8.00D0,9.00D0,
     2  1.00D1/
C
      EXTERNAL DCSEL
C
C  ****  Energy mesh points (in eV).
C
      IE=0
      IGRID=10
      FGRID=10.0D0
   10 IGRID=IGRID+1
      EV=EGRD(IGRID)*FGRID
      IF(IGRID.EQ.16) THEN
        IGRID=1
        FGRID=10.0D0*FGRID
      ENDIF
      IE=IE+1
      ETS(IE)=EV
      ETL(IE)=LOG(ETS(IE))
      IF(IE.LT.NE) GO TO 10
C
C  ****  Angular grid (TH in deg, XMU=(1.0D0-COS(TH))/2).
C
      I=1
      TH(I)=0.0D0
      THR(I)=TH(I)*PI/180.0D0
      XMU(I)=(1.0D0-COS(THR(I)))/2.0D0
      XMUL(I)=LOG(1.0D-35)
      I=2
      TH(I)=1.0D-4
      THR(I)=TH(I)*PI/180.0D0
      XMU(I)=(1.0D0-COS(THR(I)))/2.0D0
      XMUL(I)=LOG(MAX(XMU(I),1.0D-35))
   20 CONTINUE
      I=I+1
      IF(TH(I-1).LT.0.9999D-3) THEN
        TH(I)=TH(I-1)+2.5D-5
      ELSE IF(TH(I-1).LT.0.9999D-2) THEN
        TH(I)=TH(I-1)+2.5D-4
      ELSE IF(TH(I-1).LT.0.9999D-1) THEN
        TH(I)=TH(I-1)+2.5D-3
      ELSE IF(TH(I-1).LT.0.9999D+0) THEN
        TH(I)=TH(I-1)+2.5D-2
      ELSE IF(TH(I-1).LT.0.9999D+1) THEN
        TH(I)=TH(I-1)+1.0D-1
      ELSE IF(TH(I-1).LT.2.4999D+1) THEN
        TH(I)=TH(I-1)+2.5D-1
      ELSE
        TH(I)=TH(I-1)+5.0D-1
      ENDIF
      THR(I)=TH(I)*PI/180.0D0
      XMU(I)=MAX((1.0D0-COS(THR(I)))/2.0D0,1.0D-35)
      XMUL(I)=LOG(MAX(XMU(I),1.0D-35))
      IF(I.LT.NA) GO TO 20
C
C  ****  Read elastic DCS tables.
C
      IF(INFO.GE.3) WRITE(IWR,2001)
 2001 FORMAT(/1X,'***  Electron elastic differential cross sections')
      IELEC=-1
      READ(IRD,'(A50)') CTEXT
      DO IE=1,NE
        READ(IRD,'(I3,1P,E10.3,5E12.5)')
     1    IELEC,ETSIE,ECS(IE),ETCS1(IE),ETCS2(IE)
        IF(INFO.GE.3) WRITE(IWR,'(I3,1P,E10.3,5E12.5)')
     1    IELEC,ETS(IE),ECS(IE),ETCS1(IE),ETCS2(IE)
        IF(IELEC.NE.-1.OR.ABS(ETSIE-ETS(IE)).GT.0.1D0) THEN
          WRITE(IWR,*) ' Error reading electron elastic DCS data.'
          CALL PISTOP('EELdR. Error reading electron elastic DCS data.')
        ENDIF
        READ(IRD,'(1P,10E12.5)') (EDCS(IE,K),K=1,NA)
        IF(INFO.GE.3) WRITE(IWR,'(1P,10E12.5)') (EDCS(IE,K),K=1,NA)
C  ****  Consistency test.
        DO K=1,NA
          DCSI(K)=EDCS(IE,K)
        ENDDO
        ECS0=4.0D0*PI*RMOMX(XMU,DCSI,0.0D0,1.0D0,NA,0)
        ECS1=4.0D0*PI*RMOMX(XMU,DCSI,0.0D0,1.0D0,NA,1)
        ECS2=4.0D0*PI*RMOMX(XMU,DCSI,0.0D0,1.0D0,NA,2)
        TCS1=2.0D0*ECS1
        TCS2=6.0D0*(ECS1-ECS2)
        TS0=(ECS0-ECS(IE))/ECS(IE)
        TS1=(TCS1-ETCS1(IE))/ETCS1(IE)
        TS2=(TCS2-ETCS2(IE))/ETCS2(IE)
        TSTE=MAX(ABS(TS0),ABS(TS1),ABS(TS2))
        IF(TSTE.GT.1.0D-4) THEN
          WRITE(IWR,'('' E='',1P,E12.5)') ETS(IE)
          WRITE(IWR,*) ' Electron cross section data are corrupt.'
          CALL PISTOP('EELdR. Electron cross section data are corrupt.')
        ENDIF
      ENDDO
C
      IF(INFO.GE.3) WRITE(IWR,2002)
 2002 FORMAT(/1X,'***  Positron elastic differential cross sections')
      IELEC=+1
      READ(IRD,'(A50)') CTEXT
      DO IE=1,NE
        READ(IRD,'(I3,1P,E10.3,5E12.5)')
     1    IELEC,ETSIE,PCS(IE),PTCS1(IE),PTCS2(IE)
        IF(INFO.GE.3) WRITE(IWR,'(I3,1P,E10.3,5E12.5)')
     1    IELEC,ETS(IE),PCS(IE),PTCS1(IE),PTCS2(IE)
        IF(IELEC.NE.+1.OR.ABS(ETSIE-ETS(IE)).GT.0.1D0) THEN
          WRITE(IWR,*) ' Error reading positron elastic DCS data.'
          CALL PISTOP('EELdR. Error reading positron elastic DCS data.')
        ENDIF
        READ(IRD,'(1P,10E12.5)') (PDCS(IE,K),K=1,NA)
        IF(INFO.GE.3) WRITE(IWR,'(1P,10E12.5)') (PDCS(IE,K),K=1,NA)
C  ****  Consistency test.
        DO K=1,NA
          DCSI(K)=PDCS(IE,K)
        ENDDO
        ECS0=4.0D0*PI*RMOMX(XMU,DCSI,0.0D0,1.0D0,NA,0)
        ECS1=4.0D0*PI*RMOMX(XMU,DCSI,0.0D0,1.0D0,NA,1)
        ECS2=4.0D0*PI*RMOMX(XMU,DCSI,0.0D0,1.0D0,NA,2)
        TCS1=2.0D0*ECS1
        TCS2=6.0D0*(ECS1-ECS2)
        TS0=(ECS0-PCS(IE))/PCS(IE)
        TS1=(TCS1-PTCS1(IE))/PTCS1(IE)
        TS2=(TCS2-PTCS2(IE))/PTCS2(IE)
        TSTE=MAX(ABS(TS0),ABS(TS1),ABS(TS2))
        IF(TSTE.GT.1.0D-4) THEN
          WRITE(IWR,'('' E='',1P,E12.5)') ETS(IE)
          WRITE(IWR,*) ' Positron cross section data are corrupt.'
          CALL PISTOP('EELdR. Positron cross section data are corrupt.')
        ENDIF
      ENDDO
C
      NPP=NP
      NU=NPP/4
C
C  ************  Electrons.
C
      IEME=0
      DO KE=1,NEGP
        IF(ET(KE).GT.0.999999D8) GO TO 100
        CALL DCSEL0(ET(KE),-1)
        CALL RITAI0(DCSEL,0.0D0,1.0D0,NPP,NU,ERRM,0)
        DO I=1,NP
          XSE(I,KE,M)=XTI(I)
          PSE(I,KE,M)=PACI(I)
          ASE(I,KE,M)=AI(I)
          BSE(I,KE,M)=BI(I)
          ITLE(I,KE,M)=ITLI(I)
          ITUE(I,KE,M)=ITUI(I)
        ENDDO
        CALL RITAM(0.0D0,1.0D0,XM0A,XM1,XM2)
        ECS0=CSI
        ECS1=CSI*XM1/XM0A
        ECS2=CSI*XM2/XM0A
        XE0(KE)=ECS0
        XE1(KE)=2.0D0*ECS1
        XE2(KE)=6.0D0*(ECS1-ECS2)
C
        FPEL=1.0D0/(XE0(KE)*VMOL(M))
        FPT1=1.0D0/(XE1(KE)*VMOL(M))
        FPST=ET(KE)/(CSTPE(M,KE)+RSTPE(M,KE))
        XS0H=1.0D0/(VMOL(M)*MAX(FPEL,MIN(C1(M)*FPT1,C2(M)*FPST)))
        RNDC=MAX(1.0D0-XS0H/XE0(KE),1.0D-10)
        IF(RNDC.LT.1.0D-6) RNDC=0.0D0
        RNDCEd(M,KE)=RNDC
C
        RU=RNDC
        I=1
        J=NP
    1   K=(I+J)/2
        IF(RU.GT.PSE(K,KE,M)) THEN
          I=K
        ELSE
          J=K
        ENDIF
        IF(J-I.GT.1) GO TO 1
C
        RR=RU-PSE(I,KE,M)
        DPRO=PSE(I+1,KE,M)-PSE(I,KE,M)
        IF(DPRO.LT.1.0D-10) THEN
          RMUC=XSE(I,KE,M)
        ELSE
          CI=(1.0D0+ASE(I,KE,M)+BSE(I,KE,M))*DPRO
          RMUC=XSE(I,KE,M)+(CI*RR/(DPRO**2+(DPRO*ASE(I,KE,M)
     1        +BSE(I,KE,M)*RR)*RR))*(XSE(I+1,KE,M)-XSE(I,KE,M))
        ENDIF
C
C  ****  Moments of the PDF on the restricted interval (0,RMUC).
C        Total and transport cross sections for soft interactions.
C
        CALL RITAM(0.0D0,RMUC,XM0,XM1,XM2)
        ECS1=CSI*XM1/XM0A
        ECS2=CSI*XM2/XM0A
        TCS1=2.0D0*ECS1
        TCS2=6.0D0*(ECS1-ECS2)
        SEHEL(M,KE)=XS0H*VMOL(M)
        T1E0(KE)=TCS1
        T1E(M,KE)=T1EI(KE)+TCS1*VMOL(M)
        T2E0(KE)=TCS2
        T2E(M,KE)=T2EI(KE)+TCS2*VMOL(M)
        IEME=KE
      ENDDO
  100 CONTINUE
      EELMAX(M)=MIN(ET(IEME)-1.0D0,0.999999D8)
C
C  ****  Print electron elastic scattering tables.
C
      IF(INFO.GE.3) WRITE(IWR,1002)
 1002 FORMAT(/1X,'PENELOPE >>>  Elastic scattering of electrons',
     1  ' (ELSEPA database)')
      IF(INFO.GE.3) WRITE(IWR,1003)
 1003 FORMAT(/3X,'E (eV)',6X,'MFP (mtu)',3X,'TMFP1 (mtu)',2X,
     1  'MFPh (mtu)',/1X,50('-'))
      DO I=1,IEME
        FP0=RHO(M)/(XE0(I)*VMOL(M))
        FP1=RHO(M)/(XE1(I)*VMOL(M))
        HMFP=RHO(M)/SEHEL(M,I)
        IF(INFO.GE.3) WRITE(IWR,'(1P,7(E12.5,1X))') ET(I),FP0,FP1,
     1    HMFP
        SEHEL(M,I)=LOG(SEHEL(M,I))
C  ****  Soft scattering events are switched off when T1E is too small.
        IF(T1E(M,I).GT.1.0D-6*XE1(I)*VMOL(M)) THEN
          T1E(M,I)=LOG(MAX(T1E(M,I),1.0D-35))
          T2E(M,I)=LOG(MAX(T2E(M,I),1.0D-35))
        ELSE
          T1E(M,I)=-100.0D0
          T2E(M,I)=-100.0D0
        ENDIF
      ENDDO
C
C  ************  Positrons.
C
      IEMP=0
      DO KE=1,NEGP
        IF(ET(KE).GT.0.999999D8) GO TO 200
        CALL DCSEL0(ET(KE),+1)
        CALL RITAI0(DCSEL,0.0D0,1.0D0,NPP,NU,ERRM,0)
        DO I=1,NP
          XSP(I,KE,M)=XTI(I)
          PSP(I,KE,M)=PACI(I)
          ASP(I,KE,M)=AI(I)
          BSP(I,KE,M)=BI(I)
          ITLP(I,KE,M)=ITLI(I)
          ITUP(I,KE,M)=ITUI(I)
        ENDDO
        CALL RITAM(0.0D0,1.0D0,XM0A,XM1,XM2)
        ECS0=CSI
        ECS1=CSI*XM1/XM0A
        ECS2=CSI*XM2/XM0A
        XP0(KE)=ECS0
        XP1(KE)=2.0D0*ECS1
        XP2(KE)=6.0D0*(ECS1-ECS2)
C
        FPEL=1.0D0/(XP0(KE)*VMOL(M))
        FPT1=1.0D0/(XP1(KE)*VMOL(M))
        FPST=ET(KE)/(CSTPP(M,KE)+RSTPP(M,KE))
        XS0H=1.0D0/(VMOL(M)*MAX(FPEL,MIN(C1(M)*FPT1,C2(M)*FPST)))
        RNDC=MAX(1.0D0-XS0H/XP0(KE),1.0D-10)
        IF(RNDC.LT.1.0D-6) RNDC=0.0D0
        RNDCPd(M,KE)=RNDC
C
        RU=RNDC
        I=1
        J=NP
    2   K=(I+J)/2
        IF(RU.GT.PSP(K,KE,M)) THEN
          I=K
        ELSE
          J=K
        ENDIF
        IF(J-I.GT.1) GO TO 2
C
        RR=RU-PSP(I,KE,M)
        DPRO=PSP(I+1,KE,M)-PSP(I,KE,M)
        IF(DPRO.LT.1.0D-10) THEN
          RMUC=XSP(I,KE,M)
        ELSE
          CI=(1.0D0+ASP(I,KE,M)+BSP(I,KE,M))*DPRO
          RMUC=XSP(I,KE,M)+(CI*RR/(DPRO**2+(DPRO*ASP(I,KE,M)
     1        +BSP(I,KE,M)*RR)*RR))*(XSP(I+1,KE,M)-XSP(I,KE,M))
        ENDIF
C
C  ****  Moments of the PDF on the restricted interval (0,RMUC).
C        Total and transport cross sections for soft interactions.
C
        CALL RITAM(0.0D0,RMUC,XM0,XM1,XM2)
        ECS1=CSI*XM1/XM0A
        ECS2=CSI*XM2/XM0A
        TCS1=2.0D0*ECS1
        TCS2=6.0D0*(ECS1-ECS2)
        SPHEL(M,KE)=XS0H*VMOL(M)
        T1P0(KE)=TCS1
        T1P(M,KE)=T1PI(KE)+TCS1*VMOL(M)
        T2P0(KE)=TCS2
        T2P(M,KE)=T2PI(KE)+TCS2*VMOL(M)
        IEMP=KE
      ENDDO
  200 CONTINUE
      PELMAX(M)=MIN(ET(IEMP)-1.0D0,0.999999D8)
C
C  ****  Print positron elastic scattering tables.
C
      IF(INFO.GE.3) WRITE(IWR,1004)
 1004 FORMAT(/1X,'PENELOPE >>>  Elastic scattering of positrons',
     1  ' (ELSEPA database)')
      IF(INFO.GE.3) WRITE(IWR,1005)
 1005 FORMAT(/3X,'E (eV)',6X,'MFP (mtu)',3X,'TMFP1 (mtu)',2X,
     1  'MFPh (mtu)',/1X,50('-'))
      DO I=1,IEMP
        FP0=RHO(M)/(XP0(I)*VMOL(M))
        FP1=RHO(M)/(XP1(I)*VMOL(M))
        HMFP=RHO(M)/SPHEL(M,I)
        IF(INFO.GE.3) WRITE(IWR,'(1P,7(E12.5,1X))') ET(I),FP0,FP1,
     1    HMFP
        SPHEL(M,I)=LOG(SPHEL(M,I))
C  ****  Soft scattering events are switched off when T1P is too small.
        IF(T1P(M,I).GT.1.0D-6*XP1(I)*VMOL(M)) THEN
          T1P(M,I)=LOG(MAX(T1P(M,I),1.0D-35))
          T2P(M,I)=LOG(MAX(T2P(M,I),1.0D-35))
        ELSE
          T1P(M,I)=-100.0D0
          T2P(M,I)=-100.0D0
        ENDIF
      ENDDO
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE EELd
C  *********************************************************************
      SUBROUTINE EELd(RNDC,RMU)
C
C     Simulation of electron hard elastic events. Cross sections from
C  the ELSEPA numerical database.
C
C  Argument value:
C    RNDC ... cutoff value of the uniform random number
C             (only hard events are simulated).
C    RMU .... sampled angular deflection, =(1-CDT)/2.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Electron simulation tables.
      PARAMETER (MAXMAT=10)
      PARAMETER (NP=128,NPM1=NP-1)
      COMMON/CEELDB/XSE(NP,NEGP,MAXMAT),PSE(NP,NEGP,MAXMAT),
     1              ASE(NP,NEGP,MAXMAT),BSE(NP,NEGP,MAXMAT),
     2              ITLE(NP,NEGP,MAXMAT),ITUE(NP,NEGP,MAXMAT)
C
      EXTERNAL RAND
C  ****  Energy grid point.
      PK=(XEL-DLEMP(KE))*DLFC
      IF(RAND(1.0D0).LT.PK) THEN
        JE=KE+1
      ELSE
        JE=KE
      ENDIF
C  ****  Pointer.
      RU=RNDC+RAND(2.0D0)*(1.0D0-RNDC)
C  ****  Selection of the interval (binary search in a restricted
C        interval).
      ITN=RU*NPM1+1
      I=ITLE(ITN,JE,M)
      J=ITUE(ITN,JE,M)
      IF(J-I.LT.2) GO TO 2
    1 K=(I+J)/2
      IF(RU.GT.PSE(K,JE,M)) THEN
        I=K
      ELSE
        J=K
      ENDIF
      IF(J-I.GT.1) GO TO 1
C  ****  Sampling from the rational inverse cumulative distribution.
    2 CONTINUE
      PP=PSE(I,JE,M)
      RR=RU-PP
      IF(RR.GT.1.0D-16) THEN
        XX=XSE(I,JE,M)
        AA=ASE(I,JE,M)
        BB=BSE(I,JE,M)
        D=PSE(I+1,JE,M)-PP
        RMU=XX+((1.0D0+AA+BB)*D*RR/(D*D+(AA*D+BB*RR)*RR))
     1     *(XSE(I+1,JE,M)-XX)
      ELSE
        RMU=XSE(I,JE,M)
      ENDIF
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PELd
C  *********************************************************************
      SUBROUTINE PELd(RNDC,RMU)
C
C     Simulation of positron hard elastic events. Cross sections from
C  the ELSEPA numerical database.
C
C  Argument value:
C    RNDC ... cutoff value of the uniform random number
C             (only hard events are simulated).
C    RMU .... sampled angular deflection, =(1-CDT)/2.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C  ****  Energy grid and interpolation constants for the current energy.
      PARAMETER (NEGP=200)
      COMMON/CEGRID/EMIN,EL,EU,ET(NEGP),DLEMP(NEGP),DLEMP1,DLFC,
     1  XEL,XE,XEK,KE
C  ****  Positron simulation tables.
      PARAMETER (MAXMAT=10)
      PARAMETER (NP=128,NPM1=NP-1)
      COMMON/CPELDB/XSP(NP,NEGP,MAXMAT),PSP(NP,NEGP,MAXMAT),
     1              ASP(NP,NEGP,MAXMAT),BSP(NP,NEGP,MAXMAT),
     2              ITLP(NP,NEGP,MAXMAT),ITUP(NP,NEGP,MAXMAT)
C
      EXTERNAL RAND
C  ****  Energy grid point.
      PK=(XEL-DLEMP(KE))*DLFC
      IF(RAND(1.0D0).LT.PK) THEN
        JE=KE+1
      ELSE
        JE=KE
      ENDIF
C  ****  Pointer.
      RU=RNDC+RAND(2.0D0)*(1.0D0-RNDC)
C  ****  Selection of the interval (binary search in a restricted
C        interval).
      ITN=RU*NPM1+1
      I=ITLP(ITN,JE,M)
      J=ITUP(ITN,JE,M)
      IF(J-I.LT.2) GO TO 2
    1 K=(I+J)/2
      IF(RU.GT.PSP(K,JE,M)) THEN
        I=K
      ELSE
        J=K
      ENDIF
      IF(J-I.GT.1) GO TO 1
C  ****  Sampling from the rational inverse cumulative distribution.
    2 CONTINUE
      PP=PSP(I,JE,M)
      RR=RU-PP
      IF(RR.GT.1.0D-16) THEN
        XX=XSP(I,JE,M)
        AA=ASP(I,JE,M)
        BB=BSP(I,JE,M)
        D=PSP(I+1,JE,M)-PP
        RMU=XX+((1.0D0+AA+BB)*D*RR/(D*D+(AA*D+BB*RR)*RR))
     1     *(XSP(I+1,JE,M)-XX)
      ELSE
        RMU=XSP(I,JE,M)
      ENDIF
      RETURN
      END
C  *********************************************************************
C                 SUBROUTINES ELINIT, DCSEL0 AND DCSEL
C  *********************************************************************
C
C     These subroutines read the ELSEPA database for elastic scattering
C  of electrons and positrons by neutral atoms, and generate the molecu-
C  lar DCS of a compound for arbitrary values of the energy (from 50 eV
C  to 100 MeV) and the angular deflection RMU=(1-COS(THETA))/2.
C
C  Other subprograms needed: subroutine SPLINE,
C                            function FINDI.
C
C  --> Subroutine ELINIT reads atomic elastic DCSs for electrons and
C  positrons from the database files and determines a table of the mole-
C  cular DCS, for the standard grid of energies and angular deflections,
C  as the incoherent sum of atomic DCSs. It is assumed that the database
C  files are in the same directory as the binary executable module. If
C  you wish to keep the database files on a separate directory, you can
C  edit the present source file and change the string FILE1, which con-
C  tains the names of the database files of the element, to include the
C  directory path.
C
C  --> Subroutine DCSEL0(E,IELEC) initialises the calculation of DCSs
C  for electrons (IELEC=-1) or positrons (IELEC=+1) with kinetic energy
C  E (eV). It builds a table of DCS values for the standard grid of
C  angular deflections RMU using log-log cubic spline interpolation in E
C  of the tables prepared by subroutine ELINIT.
C
C  --> Function DCSEL(RMU) computes the DCS in (cm**2/sr) at RMU by
C  linear log-log interpolation of the values tabulated by subroutine
C  DCSEL0. Notice that the delivered DCSEL value corresponds to the
C  particle and energy defined in the last call to subroutine DCSEL0.
C
C  EXAMPLE: To calculate cross sections for water, our main program must
C  contain the following definitions and calls:
C
C     CALL ELINIT(IZ,STF,NELEM) with NELEM=2
C                                    IZ(1)=1, STF(1)=2   <-- 2 H atoms
C                                    IZ(2)=8, STF(2)=1   <-- 1 O atom
C  (This sets the standard tabulation of cross sections for water.)
C
C  Now, to obtain the DCS for electrons with a kinetic energy of 10 keV
C  at RMU=0.0D0 (forward scattering) we simply insert the following two
C  statements in the main program,
C
C     CALL DCSEL0(1.0D4,-1)
C     DCS=DCSEL(0.0D0)
C
C  *********************************************************************
C                       SUBROUTINE ELINIT
C  *********************************************************************
      SUBROUTINE ELINIT(IZ,STF,NELEM)
C
C  This subroutine reads atomic elastic cross sections for electrons and
C  positrons from the database files and determines the molecular cross
C  section as the incoherent sum of atomic cross sections.
C
C  Input arguments:
C    IZ (1:NELEM) .... atomic numbers of the elements in the compound.
C    STF (1:NELEM) ... stoichiometric indices.
C    NELEM ........... number of different elements.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (PI=3.1415926535897932D0)
C
      DIMENSION IZ(NELEM),STF(NELEM)
C
      PARAMETER (NE=96,NA=606)
      COMMON/CDCSEP/ET(NE),ETL(NE),TH(NA),THR(NA),XMU(NA),XMUL(NA),
     1       ECS(NE),ETCS1(NE),ETCS2(NE),EDCS(NE,NA),
     2       PCS(NE),PTCS1(NE),PTCS2(NE),PDCS(NE,NA),
     3       DCSI(NA),DCSIL(NA),CSI,TCS1I,TCS2I
C
      DIMENSION EGRD(16)
      DATA EGRD/1.0D0,1.25D0,1.50D0,1.75D0,2.00D0,2.50D0,3.00D0,
     1  3.50D0,4.00D0,4.50D0,5.00D0,6.00D0,7.00D0,8.00D0,9.00D0,
     2  1.00D1/
C
      CHARACTER*1 LIT10(10),LIT1,LIT2,LIT3
      DATA LIT10/'0','1','2','3','4','5','6','7','8','9'/
      CHARACTER*12 FILE1
C
C  ****  Energy mesh points (in eV).
C
      IE=0
      IGRID=10
      FGRID=10.0D0
   10 IGRID=IGRID+1
      EV=EGRD(IGRID)*FGRID
      IF(IGRID.EQ.16) THEN
        IGRID=1
        FGRID=10.0D0*FGRID
      ENDIF
      IE=IE+1
      ET(IE)=EV
      ETL(IE)=LOG(ET(IE))
      IF(IE.LT.NE) GO TO 10
C
C  ****  Angular grid (TH in deg, XMU=(1.0D0-COS(TH))/2).
C
      I=1
      TH(I)=0.0D0
      THR(I)=TH(I)*PI/180.0D0
      XMU(I)=(1.0D0-COS(THR(I)))/2.0D0
      XMUL(I)=LOG(1.0D-35)
      I=2
      TH(I)=1.0D-4
      THR(I)=TH(I)*PI/180.0D0
      XMU(I)=(1.0D0-COS(THR(I)))/2.0D0
      XMUL(I)=LOG(MAX(XMU(I),1.0D-35))
   20 CONTINUE
      I=I+1
      IF(TH(I-1).LT.0.9999D-3) THEN
        TH(I)=TH(I-1)+2.5D-5
      ELSE IF(TH(I-1).LT.0.9999D-2) THEN
        TH(I)=TH(I-1)+2.5D-4
      ELSE IF(TH(I-1).LT.0.9999D-1) THEN
        TH(I)=TH(I-1)+2.5D-3
      ELSE IF(TH(I-1).LT.0.9999D+0) THEN
        TH(I)=TH(I-1)+2.5D-2
      ELSE IF(TH(I-1).LT.0.9999D+1) THEN
        TH(I)=TH(I-1)+1.0D-1
      ELSE IF(TH(I-1).LT.2.4999D+1) THEN
        TH(I)=TH(I-1)+2.5D-1
      ELSE
        TH(I)=TH(I-1)+5.0D-1
      ENDIF
      THR(I)=TH(I)*PI/180.0D0
      XMU(I)=MAX((1.0D0-COS(THR(I)))/2.0D0,1.0D-35)
      XMUL(I)=LOG(MAX(XMU(I),1.0D-35))
      IF(I.LT.NA) GO TO 20
C
      DO IE=1,NE
        ECS(IE)=0.0D0
        ETCS1(IE)=0.0D0
        ETCS2(IE)=0.0D0
        PCS(IE)=0.0D0
        PTCS1(IE)=0.0D0
        PTCS2(IE)=0.0D0
        DO IA=1,NA
          EDCS(IE,IA)=0.0D0
          PDCS(IE,IA)=0.0D0
        ENDDO
      ENDDO
C
C  ****  Read atomic DCS tables and compute the molecular DCS as the
C        incoherent sum of atomic DCSs.
C
      DO IEL=1,NELEM
        IZZ=IZ(IEL)
        STFF=STF(IEL)
        NS=IZ(IEL)
        IF(NS.GT.999) NS=999
        NS1=NS-10*(NS/10)
        NS=(NS-NS1)/10
        NS2=NS-10*(NS/10)
        NS=(NS-NS2)/10
        NS3=NS-10*(NS/10)
        LIT1=LIT10(NS1+1)
        LIT2=LIT10(NS2+1)
        LIT3=LIT10(NS3+1)
C
        FILE1='eeldx'//LIT3//LIT2//LIT1//'.p08'
        OPEN(3,FILE='./pdfiles/'//FILE1)
        DO IE=1,NE
          READ(3,'(I3,I4,1P,E10.3,5E12.5)')
     1      IELEC,IZR,ENR,CSE,TCS1E,TCS2E
          IF(IELEC.NE.-1.OR.IZR.NE.IZZ.OR.ABS(ENR-ET(IE)).GT.1.0D-3)
     1      CALL PISTOP('ELINIT. Corrupt data file.')
          READ(3,'(1P,10E12.5)') (DCSI(IA),IA=1,NA)
          ECS(IE)=ECS(IE)+STFF*CSE
          ETCS1(IE)=ETCS1(IE)+STFF*TCS1E
          ETCS2(IE)=ETCS2(IE)+STFF*TCS2E
          DO IA=1,NA
            EDCS(IE,IA)=EDCS(IE,IA)+STFF*DCSI(IA)
          ENDDO
        ENDDO
        CLOSE(3)
C
        FILE1='peldx'//LIT3//LIT2//LIT1//'.p08'
        OPEN(3,FILE='./pdfiles/'//FILE1)
        DO IE=1,NE
          READ(3,'(I3,I4,1P,E10.3,5E12.5)')
     1      IELEC,IZR,ENR,CSP,TCS1P,TCS2P
          IF(IELEC.NE.+1.OR.IZR.NE.IZZ.OR.ABS(ENR-ET(IE)).GT.1.0D-3)
     1      CALL PISTOP('ELINIT. Corrupt data file.')
          READ(3,'(1P,10E12.5)') (DCSI(IA),IA=1,NA)
          PCS(IE)=PCS(IE)+STFF*CSP
          PTCS1(IE)=PTCS1(IE)+STFF*TCS1P
          PTCS2(IE)=PTCS2(IE)+STFF*TCS2P
          DO IA=1,NA
            PDCS(IE,IA)=PDCS(IE,IA)+STFF*DCSI(IA)
          ENDDO
        ENDDO
        CLOSE(3)
      ENDDO
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE DCSEL0
C  *********************************************************************
      SUBROUTINE DCSEL0(E,IELEC)
C
C     This subroutine computes a table of the molecular elastic DCSs for
C  electrons (IELEC=-1) or positrons (IELEC=+1) with kinetic energy  E
C  (in eV) by log-log cubic spline interpolation in E of the DCS table
C  prepared by subroutine ELINIT.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C
      PARAMETER (NE=96,NA=606)
      COMMON/CDCSEP/ET(NE),ETL(NE),TH(NA),THR(NA),XMU(NA),XMUL(NA),
     1       ECS(NE),ETCS1(NE),ETCS2(NE),EDCS(NE,NA),
     2       PCS(NE),PTCS1(NE),PTCS2(NE),PDCS(NE,NA),
     3       DCSI(NA),DCSIL(NA),CSI,TCS1I,TCS2I
C
      DIMENSION Y(NE),A(NE),B(NE),C(NE),D(NE)
C
      IF(E.LT.49.999D0.OR.E.GT.1.0001D8) THEN
        WRITE(26,'('' Error in DCSEL0: Energy out of range.'')')
        CALL PISTOP('DCSEL. Energy out of range.')
      ENDIF
C
      EL=LOG(E)
      CALL FINDI(ETL,EL,NE,JE)
C
      DO IA=1,NA
        DO IE=1,NE
          IF(IELEC.EQ.-1) THEN
            Y(IE)=LOG(EDCS(IE,IA))
          ELSE
            Y(IE)=LOG(PDCS(IE,IA))
          ENDIF
        ENDDO
        CALL SPLINE(ETL,Y,A,B,C,D,0.0D0,0.0D0,NE)
        DCSIL(IA)=A(JE)+EL*(B(JE)+EL*(C(JE)+EL*D(JE)))
        DCSI(IA)=EXP(DCSIL(IA))
      ENDDO
C
      DO IE=1,NE
        IF(IELEC.EQ.-1) THEN
          Y(IE)=LOG(ECS(IE))
        ELSE
          Y(IE)=LOG(PCS(IE))
        ENDIF
      ENDDO
      CALL SPLINE(ETL,Y,A,B,C,D,0.0D0,0.0D0,NE)
      CSI=EXP(A(JE)+EL*(B(JE)+EL*(C(JE)+EL*D(JE))))
C
      DO IE=1,NE
        IF(IELEC.EQ.-1) THEN
          Y(IE)=LOG(ETCS1(IE))
        ELSE
          Y(IE)=LOG(PTCS1(IE))
        ENDIF
      ENDDO
      CALL SPLINE(ETL,Y,A,B,C,D,0.0D0,0.0D0,NE)
      TCS1I=EXP(A(JE)+EL*(B(JE)+EL*(C(JE)+EL*D(JE))))
C
      DO IE=1,NE
        IF(IELEC.EQ.-1) THEN
          Y(IE)=LOG(ETCS2(IE))
        ELSE
          Y(IE)=LOG(PTCS2(IE))
        ENDIF
      ENDDO
      CALL SPLINE(ETL,Y,A,B,C,D,0.0D0,0.0D0,NE)
      TCS2I=EXP(A(JE)+EL*(B(JE)+EL*(C(JE)+EL*D(JE))))
C
      RETURN
      END
C  *********************************************************************
C                       FUNCTION DCSEL
C  *********************************************************************
      FUNCTION DCSEL(RMU)
C
C  This function computes the DCS in (cm**2/sr) by linear log-log inter-
C  polation in RMU=(1-cos(theta))/2. It is initialised by subroutine
C  DCSEL0, which must be called before using DCSEL.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C
      PARAMETER (NE=96,NA=606)
      COMMON/CDCSEP/ET(NE),ETL(NE),TH(NA),THR(NA),XMU(NA),XMUL(NA),
     1       ECS(NE),ETCS1(NE),ETCS2(NE),EDCS(NE,NA),
     2       PCS(NE),PTCS1(NE),PTCS2(NE),PDCS(NE,NA),
     3       DCSI(NA),DCSIL(NA),CSI,TCS1I,TCS2I
C
      RMUL=LOG(MIN(MAX(RMU,1.0D-35),0.999999999999D0))
      CALL FINDI(XMUL,RMUL,NA,I)
      DCSEL=EXP(DCSIL(I)+(DCSIL(I+1)-DCSIL(I))
     1     *((RMUL-XMUL(I))/(XMUL(I+1)-XMUL(I))))
      RETURN
      END
C  *********************************************************************
C                       FUNCTION RMOMX
C  *********************************************************************
      FUNCTION RMOMX(X,PDF,XD,XU,NP,MOM)
C
C     Calculation of momenta of a pdf, PDF(X), obtained from linear
C  log-log interpolation of the input table. The independent variable X
C  is assumed to take only positive values.
C
C     X ........ array of variable values (in increasing order).
C     PDF ...... corresponding PDF values (must be non-negative).
C     NP ....... number of points in the table.
C     XD, XU ... limits of the integration interval.
C     MOM ...... moment order.
C     RMOM = INTEGRAL (X**N)*PDF(X) dX over the interval (XD,XU).
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (EPS=1.0D-12,ZERO=1.0D-35)
      DIMENSION X(NP),PDF(NP)
C
      IF(NP.LT.2) STOP 'RMOMX. Error code 1.'
      IF(X(1).LT.0.0D0.OR.PDF(1).LT.0.0D0) THEN
        WRITE(26,*) 'X(1),PDF(1) =',X(1),PDF(1)
        STOP 'RMOMX. Error code 2.'
      ENDIF
      DO I=2,NP
        IF(X(I).LT.0.0D0.OR.PDF(I).LT.0.0D0) THEN
          WRITE(26,*) 'I,X(I),PDF(I) =',I,X(I),PDF(I)
          STOP 'RMOMX. Error code 3.'
        ENDIF
        IF(X(I).LT.X(I-1)) STOP 'RMOMX. Error code 4.'
      ENDDO
C
      XLOW=MAX(X(1),XD)
      IF(XLOW.LT.ZERO) XLOW=ZERO
      XUP=MIN(X(NP),XU)
C
      IF(XLOW.GE.XUP) THEN
        WRITE(26,*) ' WARNING: XLOW is greater than XUP in RMOMX.'
        WRITE(26,*) ' XLOW =',XLOW,',   XUP =',XUP
        RMOMX=0.0D0
        RETURN
      ENDIF
C
      IL=1
      IU=NP-1
      DO I=1,NP-1
        IF(X(I).LT.XLOW) IL=I
        IF(X(I).LT.XUP) IU=I
      ENDDO
C
C  ****  A single interval.
C
      IF(IU.EQ.IL) THEN
        XIL=LOG(MAX(X(IL),ZERO))
        XFL=LOG(X(IL+1))
        YIL=LOG(MAX(PDF(IL),ZERO))
        YFL=LOG(MAX(PDF(IL+1),ZERO))
        X1=XLOW
        X2=XUP
        DEN=XFL-XIL
        IF(ABS(DEN).GT.ZERO) THEN
          Y1=EXP(YIL+(YFL-YIL)*(LOG(X1)-XIL)/DEN)*X1**MOM
          Y2=EXP(YIL+(YFL-YIL)*(LOG(X2)-XIL)/DEN)*X2**MOM
        ELSE
          Y1=EXP(YIL)*X1**MOM
          Y2=EXP(YIL)*X2**MOM
        ENDIF
        DXL=LOG(X2)-LOG(X1)
        DYL=LOG(MAX(Y2,ZERO))-LOG(MAX(Y1,ZERO))
        IF(ABS(DXL).GT.EPS*ABS(DYL)) THEN
          AP1=1.0D0+(DYL/DXL)
          IF(ABS(AP1).GT.EPS) THEN
            DSUM=(Y2*X2-Y1*X1)/AP1
          ELSE
            DSUM=Y1*X1*DXL
          ENDIF
        ELSE
          DSUM=0.5D0*(Y1+Y2)*(X2-X1)
        ENDIF
        RMOMX=DSUM
        RETURN
      ENDIF
C
C  ****  Multiple intervals.
C
      XIL=LOG(MAX(X(IL),ZERO))
      XFL=LOG(X(IL+1))
      YIL=LOG(MAX(PDF(IL),ZERO))
      YFL=LOG(MAX(PDF(IL+1),ZERO))
      X1=XLOW
      DEN=XFL-XIL
      IF(ABS(DEN).GT.ZERO) THEN
        Y1=EXP(YIL+(YFL-YIL)*(LOG(X1)-XIL)/DEN)*X1**MOM
      ELSE
        Y1=EXP(YIL)*X1**MOM
      ENDIF
      X2=X(IL+1)
      Y2=MAX(PDF(IL+1),ZERO)*X2**MOM
      DXL=LOG(X2)-LOG(X1)
      DYL=LOG(MAX(Y2,ZERO))-LOG(MAX(Y1,ZERO))
      IF(ABS(DXL).GT.EPS*ABS(DYL)) THEN
        AP1=1.0D0+(DYL/DXL)
        IF(ABS(AP1).GT.EPS) THEN
          DSUM=(Y2*X2-Y1*X1)/AP1
        ELSE
          DSUM=Y1*X1*DXL
        ENDIF
      ELSE
        DSUM=0.5D0*(Y1+Y2)*(X2-X1)
      ENDIF
      RMOMX=DSUM
C
      IF(IU.GT.IL+1) THEN
        DO I=IL+1,IU-1
          X1=X(I)
          Y1=MAX(PDF(I),ZERO)*X1**MOM
          X2=X(I+1)
          Y2=MAX(PDF(I+1),ZERO)*X2**MOM
          DXL=LOG(X2)-LOG(X1)
          DYL=LOG(MAX(Y2,ZERO))-LOG(MAX(Y1,ZERO))
          IF(ABS(DXL).GT.EPS*ABS(DYL)) THEN
            AP1=1.0D0+(DYL/DXL)
            IF(ABS(AP1).GT.EPS) THEN
              DSUM=(Y2*X2-Y1*X1)/AP1
            ELSE
              DSUM=Y1*X1*DXL
            ENDIF
          ELSE
            DSUM=0.5D0*(Y1+Y2)*(X2-X1)
          ENDIF
          RMOMX=RMOMX+DSUM
        ENDDO
      ENDIF
C
      X1=X(IU)
      Y1=MAX(PDF(IU),ZERO)*X1**MOM
      XIL=LOG(X(IU))
      XFL=LOG(X(IU+1))
      YIL=LOG(MAX(PDF(IU),ZERO))
      YFL=LOG(MAX(PDF(IU+1),ZERO))
      X2=XUP
      DEN=XFL-XIL
      IF(ABS(DEN).GT.ZERO) THEN
        Y2=EXP(YIL+(YFL-YIL)*(LOG(X2)-XIL)/DEN)*X2**MOM
      ELSE
        Y2=EXP(YIL)*X2**MOM
      ENDIF
      DXL=LOG(X2)-LOG(X1)
      DYL=LOG(MAX(Y2,ZERO))-LOG(MAX(Y1,ZERO))
      IF(ABS(DXL).GT.EPS*ABS(DYL)) THEN
        AP1=1.0D0+(DYL/DXL)
        IF(ABS(AP1).GT.EPS) THEN
          DSUM=(Y2*X2-Y1*X1)/AP1
        ELSE
          DSUM=Y1*X1*DXL
        ENDIF
      ELSE
        DSUM=0.5D0*(Y1+Y2)*(X2-X1)
      ENDIF
      RMOMX=RMOMX+DSUM
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PISTOP
C  *********************************************************************
      SUBROUTINE PISTOP(REASON)
C
C     This subroutine is called when a fatal error or conflict is found;
C  it outputs the error message (REASON) and stops the execution of the
C  program.
C
      CHARACTER REASON*(*)
      WRITE(26,*) REASON
      WRITE(6,*) REASON
      STOP
      END
