CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C                                                                      C
C    PPPPP   EEEEEE  N    N  V    V    AA    RRRRR   EEEEEE  DDDDD     C
C    P    P  E       NN   N  V    V   A  A   R    R  E       D    D    C
C    P    P  E       N N  N  V    V  A    A  R    R  E       D    D    C
C    PPPPP   EEEE    N  N N  V    V  AAAAAA  RRRRR   EEEE    D    D    C
C    P       E       N   NN   V  V   A    A  R  R    E       D    D    C
C    P       EEEEEE  N    N    VV    A    A  R   R   EEEEEE  DDDDD     C
C                                                                      C
C                                                   (version 2011).    C
C                                                                      C
C     The present routines permit to apply basic variance-reduction    C
C  methods with PENELOPE.                                              C
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
C  -->   SUBROUTINE VSPLIT(NSPLIT)
C  This subroutine splits the current particle into NSPLIT identical
C  particles, defines their weights appropriately, and stores NSPLIT-1
C  of them into the secondary stack. The current particle continues with
C  a reduced weight.
C  Note: NSPLIT must be larger than one (NSPLIT>1).
C
C  -->   SUBROUTINE VKILL(PKILL)
C  This subroutine applies the Russian roulette technique. The particle
C  is killed with probability PKILL; if it survives, its weight is in-
C  creased by a factor 1/(1-PKILL).
C  Note: PKILL must be larger than zero and less than one (0<PKILL<1).
C
C  -->   SUBROUTINE JUMPF(DSMAX,DS)
C        SUBROUTINE KNOCKF(DEF,ICOL)
C  These two subroutines perform interaction forcing. Their action is to
C  artificially insert 'forced' interactions of selected kinds randomly
C  along the particle trajectory. This is accomplished by replacing the
C  inverse mean free path (IMFP) by a larger value, FORCE(.)*IMFP, where
C  FORCE(IBODY,KPAR,ICOL) is the forcing factor specified by the user.
C  Notice that the forcing factor must be larger than unity. To keep the
C  simulation unbiased, interactions are allowed to affect the state of
C  the projectile only with probability WFORCE(.)=1/FORCE(.), which is
C  less than unity, and, at the same time, secondary particles generated
C  in forced interactions are assigned a weight smaller than that of the
C  projectile by a factor =WFORCE(.).
C
C  To apply simulation forcing, the MAIN program must call subroutines
C  'JUMPF' and 'KNOCKF' instead of the usual subroutines 'JUMP' and
C  'KNOCK'. Moreover, subroutine START _must_ be called before starting
C  a track and after each interface crossing, even for photons.
C
C  We recall that different kinds of interactions are identified by the
C  integer label ICOL:
C     Electrons (KPAR=1) and positrons (KPAR=3):
C        ICOL = 1, artificial soft event (hinge).
C             = 2, hard elastic collision.
C             = 3, hard inelastic collision.
C             = 4, hard bremsstrahlung emission.
C             = 5, inner-shell ionization.
C             = 6, positron annihilation.
C             = 7, delta interaction.
C             = 8, 'auxiliary' fictitious interactions.
C     Photons (KPAR=2):
C        ICOL = 1, coherent (Rayleigh) scattering.
C             = 2, incoherent (Compton) scattering.
C             = 3, photoelectric absorption.
C             = 4, electron-positron pair production.
C             = 7, delta interaction.
C             = 8, 'auxiliary' fictitious interactions.
C
C  The forcing factors FORCE(.) have to be specified by the user in the
C  MAIN program and transferred through the common block
C     COMMON/CFORCE/FORCE(NB,3,8)     with NB=5000.
C  Forcing factors must be larger than, or equal to, unity; obviously,
C  the value FORCE(.)=1 means 'no forcing'.
C
C  For the sake of simplicity, we assume that the forcing factors are
C  specified for the three types of particles and for all the bodies in
C  the material structure; they are considered to be independent of the
C  particle energy. Although this scheme is flexible enough for many
C  practical uses, the FORCE(.) values can also be varied during the
C  simulation (provided only the change is performed outside the program
C  segment between a call to subroutine JUMPF and the subsequent call to
C  KNOCKF).
C
C
C  NOTE: Make sure that the value of the parameter NMS (maximum number
C  of secondary particles in the stack) in the present routines is the
C  same as in PENELOPE. The default value, NMS=1000, which is large
C  enough for most applications, may be insufficient with heavy split-
C  ting and interaction forcing. To avoid saturation of the secondary
C  stack, it is advisable to apply these techniques only when the
C  particle weight is in a limited range, say between 0.05 and 20.
C
C  *********************************************************************
C                       SUBROUTINE VSPLIT
C  *********************************************************************
      SUBROUTINE VSPLIT(NSPLIT)
C
C  This subroutine splits the current particle into NSPLIT identical
C  particles, defines their weights appropriately, and stores NSPLIT-1
C  of them into the secondary stack. The current particle continues with
C  the reduced weight.
C
C  NOTE: NSPLIT must be larger than one.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C
      WGHT=WGHT/NSPLIT
      DO I=2,NSPLIT
        CALL STORES(E,X,Y,Z,U,V,W,WGHT,KPAR,ILB)
      ENDDO
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE VKILL
C  *********************************************************************
      SUBROUTINE VKILL(PKILL)
C
C  This subroutine applies the Russian roulette technique. The particle
C  is killed with probability PKILL; if it survives, its weight is in-
C  creased by a factor 1/(1-PKILL).
C
C  NOTE: PKILL must be larger than zero and less than one.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C
      EXTERNAL RAND
C
      IF(RAND(1.0D0).LT.PKILL) THEN
        E=0.0D0
        WGHT=0.0D0
      ELSE
        WGHT=WGHT/(1.0D0-PKILL)
      ENDIF
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE JUMPF
C  *********************************************************************
      SUBROUTINE JUMPF(DSMAX,DS)
C
C  Modified subroutine 'JUMP' for interaction forcing.
C
C  Calculation of the free path from the starting point to the position
C  of the next event and of the probabilities of occurrence of different
C  events.
C
C  Arguments:
C    DSMAX ... maximum allowed step length (input),
C    DS ...... step length (output).
C
C  This subroutine does not modify the weight of the primary particle.
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
C  ****  Interaction forcing parameters.
      PARAMETER (NB=5000)
      COMMON/CFORCE/FORCE(NB,3,8)
      COMMON/CFORCG/P0(8),IFORC(8)
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
C  ****  Interaction forcing.
          DO KI=2,5
            IF(FORCE(IBODY,1,KI).GT.1.0D0.AND.P(KI).GT.1.0D-16) THEN
              P0(KI)=P(KI)
              P(KI)=P(KI)*FORCE(IBODY,1,KI)
              IFORC(KI)=1
            ELSE
              IFORC(KI)=0
            ENDIF
          ENDDO
          IFORC(1)=0
          IFORC(6)=0
          IFORC(7)=0
          IFORC(8)=0
          DS=DS1
          RETURN
        ENDIF
        CALL EIMFP(2)
C  ****  Interaction forcing.
        TFP=0.0D0
        DO KI=2,5
          IF(FORCE(IBODY,1,KI).GT.1.0D0.AND.P(KI).GT.1.0D-16) THEN
            P0(KI)=P(KI)
            P(KI)=P(KI)*FORCE(IBODY,1,KI)
            TFP=TFP+(P(KI)-P0(KI))
            IFORC(KI)=1
          ELSE
            IFORC(KI)=0
          ENDIF
        ENDDO
        IFORC(1)=0
        IFORC(6)=0
        IFORC(7)=0
        IFORC(8)=0
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
C  ****  The value of DSMAXP is randomized to eliminate dose artifacts
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
          ST=MAX(ST,STLWR+TFP)
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
        DST=-LOG(RAND(3.0D0))/ST
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
          DS=DST*RAND(4.0D0)
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
C  ****  Interaction forcing.
          DO KI=2,6
            IF(FORCE(IBODY,3,KI).GT.1.0D0.AND.P(KI).GT.1.0D-16) THEN
              P0(KI)=P(KI)
              P(KI)=P(KI)*FORCE(IBODY,3,KI)
              IFORC(KI)=1
            ELSE
              IFORC(KI)=0
            ENDIF
          ENDDO
          IFORC(1)=0
          IFORC(7)=0
          IFORC(8)=0
          DS=DS1
          RETURN
        ENDIF
        CALL PIMFP(2)
C  ****  Interaction forcing.
        TFP=0.0D0
        DO KI=2,6
          IF(FORCE(IBODY,3,KI).GT.1.0D0.AND.P(KI).GT.1.0D-16) THEN
            P0(KI)=P(KI)
            P(KI)=P(KI)*FORCE(IBODY,3,KI)
            TFP=TFP+(P(KI)-P0(KI))
            IFORC(KI)=1
          ELSE
            IFORC(KI)=0
          ENDIF
        ENDDO
        IFORC(1)=0
        IFORC(7)=0
        IFORC(8)=0
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
C  ****  The value of DSMAXP is randomized to eliminate dose artifacts
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
          ST=MAX(ST,STLWR+TFP)
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
        DST=-LOG(RAND(3.0D0))/ST
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
          DS=DST*RAND(4.0D0)
          DS1=DST-DS
        ENDIF
        RETURN
      ELSE
C
C  ************  Photons (KPAR=2).
C
        IF(MODE.EQ.1) THEN  ! Energy is the same as in previous calls.
          DS=-DLOG(RAND(1.0D0))/ST  ! IMFPs already computed.
          RETURN
        ENDIF
C
        MODE=0  ! New energy. Full calculation.
        XEL=LOG(E)
        XE=1.0D0+(XEL-DLEMP1)*DLFC
        KE=XE
        XEK=XE-KE
C
        CALL GIMFP
C  ****  Interaction forcing.
        DO KI=1,4
          IF(FORCE(IBODY,2,KI).GT.1.0D0.AND.P(KI).GT.1.0D-16) THEN
            P0(KI)=P(KI)
            P(KI)=P(KI)*FORCE(IBODY,2,KI)
            IFORC(KI)=1
          ELSE
            IFORC(KI)=0
          ENDIF
        ENDDO
        IFORC(5)=0
        IFORC(6)=0
        IFORC(7)=0
        IFORC(8)=0
C
        ST=P(1)+P(2)+P(3)+P(4)+P(8)
        DS=-LOG(RAND(1.0D0))/ST
      ENDIF
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE KNOCKF
C  *********************************************************************
      SUBROUTINE KNOCKF(DEF,ICOL)
C
C  Modified subroutine 'KNOCK' for interaction forcing.
C
C  Output arguments:
C    DEF .... effective energy deposited by the particle in the mater-
C             ial. Includes a weight correction such that no special
C             action needs to be taken in the main program.
C             --> Use with care; when this quantity is considered as
C             the deposited energy, simulated energy deposition spectra
C             are biased.
C    ICOL ... kind of interaction experienced by the particle.
C
C  This subroutine does not modify the weight of the primary particle.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C  ****  Main-PENELOPE common.
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
C  ****  Simulation parameters.
      PARAMETER (MAXMAT=10)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
C  ****  Secondary stack.
      PARAMETER (NMS=1000)
      COMMON/SECST/ES(NMS),XS(NMS),YS(NMS),ZS(NMS),US(NMS),
     1   VS(NMS),WS(NMS),WGHTS(NMS),KS(NMS),IBODYS(NMS),MS(NMS),
     2   ILBS(5,NMS),NSEC
      COMMON/CERSEC/IERSEC
C  ****  Current IMFPs.
      COMMON/CJUMP0/P(8),ST,DST,DS1,W1,W2,T1,T2
      COMMON/CJUMP1/MODE,KSOFTE,KSOFTI,KDELTA
C  ****  Interaction forcing parameters.
      COMMON/CFORCG/P0(8),IFORC(8)
C
      EXTERNAL RAND
C
C  ****  Store particle state variables before the interaction.
C
      EA=E
      UA=U
      VA=V
      WA=W
      NSECA=NSEC
C
C  ****  Simulate a new interaction.
C
      CALL KNOCK(DE,ICOL)
      IF(IFORC(ICOL).EQ.0) THEN  ! Unforced interaction.
        DEF=DE
        RETURN
      ENDIF
C  ****  Modify the weights of generated secondary particles, if any.
      WFORCE=P0(ICOL)/P(ICOL)
      DEF=DE*WFORCE
      IF(NSEC.GT.NSECA) THEN
C  ****  Allow writing multiple stack overflow warnings.
        IF(IERSEC.NE.0) IERSEC=0
        DO I=NSECA+1,NSEC
          WGHTS(I)=WGHTS(I)*WFORCE
        ENDDO
      ENDIF
C  ****  And set the final state of the primary particle.
      IF(RAND(1.0D0).GT.WFORCE) THEN
C  ****  The primary particle state is not affected.
        E=EA
        U=UA
        V=VA
        W=WA
        IF(KPAR.EQ.2) MODE=1  ! Same energy as in previous calls.
      ELSE
        IF(KPAR.EQ.2) THEN
          IF(ABS(E-EA).LT.1.0D0) THEN
            MODE=1  ! Same energy as in previous calls.
          ELSE
            MODE=0
          ENDIF
        ENDIF
      ENDIF
C
      RETURN
      END
