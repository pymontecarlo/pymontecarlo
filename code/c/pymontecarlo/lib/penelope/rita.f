CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C                                                                      C
C  Subroutine package RITA        (Francesc Salvat. 22 January, 2011)  C
C                                                                      C
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C
C     This package contains subroutines for random sampling from single-
C  variate discrete and continuous probability distributions. Discrete
C  distributions are sampled by using the aliasing method of Walker. The
C  sampling from continuous distributions is performed by means of the
C  RITA (Rational Inverse Transform with Aliasing) algorithm. These
C  methods are described in Chapter 1 of the PENELOPE manual; they are
C  among the fastest sampling techniques available for arbitrary
C  numerical distributions.
C
C  *********************************************************************
C                       FUNCTION IRND
C  *********************************************************************
      FUNCTION IRND(F,IA,N)
C
C  Random sampling from a discrete probability distribution using
C  Walker's aliasing algorithm.
C
C  The arrays F and IA are determined by the initialisation routine
C  IRND0, which must be invoked before using function IRND.
C
C  Input arguments:
C    F(1:N) .... cutoff values.
C    IA(1:N) ... alias values.
C    N ......... number of different values of the random variable.
C
C  Output argument:
C    IRND ...... sampled value.
C
C  Other subprograms needed: function RAND and subroutine IRND0.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      DIMENSION F(N),IA(N)
      EXTERNAL RAND
C
      RN=RAND(1.0D0)*N+1.0D0
      IRND=INT(RN)
      TST=RN-IRND
      IF(TST.GT.F(IRND)) IRND=IA(IRND)
C
      RETURN
      END
C  *********************************************************************
C                       FUNCTION RITA
C  *********************************************************************
      FUNCTION RITA()
C
C  Random sampling of a continuous variable using the RITA (Rational
C  Inverse Transform with Aliasing) method.
C
C  The needed numerical parameters are determined by the initialisa-
C  tion subroutine RITA0, which must be invoked before using function
C  RITA; these parameters are stored in common block /CRITAA/.
C
C  Other subprograms needed: EXTERNAL functions PDF and RAND,
C                            subroutines RITA0, IRND0 and RITAI0.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (NM=512)
      COMMON/CRITAA/X(NM),A(NM),B(NM),F(NM),IA(NM),NPM1
      EXTERNAL RAND
C  ****  Selection of the interval (Walker's aliasing).
      RN=RAND(1.0D0)*NPM1+1.0D0
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
      IF(RR.GT.1.0D-12) THEN
        RITA=X(I)+((1.0D0+A(I)+B(I))*D*RR/(D*D+(A(I)*D+B(I)*RR)*RR))
     1      *(X(I+1)-X(I))
      ELSE
        RITA=X(I)+RAND(2.0D0)*(X(I+1)-X(I))
      ENDIF
C
      RETURN
      END
C  *********************************************************************
C                       FUNCTION RITAI
C  *********************************************************************
      FUNCTION RITAI()
C
C  Random sampling of a continuous variable using the RITA (Rational
C  Inverse Transform with Aliasing) method, with binary search within
C  pre-calculated index intervals.
C
C  The needed numerical parameters are determined by the initialisation
C  subroutine RITAI0, which must be invoked before using function RITAY;
C  these parameters are stored in common block /CRITA/.
C
C  Other subprograms needed: EXTERNAL functions PDF and RAND,
C                            subroutine RITAI0.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (NM=512)
      COMMON/CRITA/X(NM),PAC(NM),DPAC(NM),A(NM),B(NM),IL(NM),IU(NM),
     1  NPM1
      EXTERNAL RAND
C
C  ****  Selection of the interval
C        (binary search within pre-calculated limits).
C
      RU=RAND(1.0D0)
      ITN=RU*NPM1+1
      I=IL(ITN)
      J=IU(ITN)
      IF(J-I.LT.2) GO TO 2
    1 K=(I+J)/2
      IF(RU.GT.PAC(K)) THEN
        I=K
      ELSE
        J=K
      ENDIF
      IF(J-I.GT.1) GO TO 1
C
C  ****  Sampling from the rational inverse cumulative distribution.
C
    2 CONTINUE
      RR=RU-PAC(I)
      D=DPAC(I)  ! DPAC(I)=PAC(I+1)-PAC(I)
      IF(D.GT.1.0D-12) THEN
        RITAI=X(I)+((1.0D0+A(I)+B(I))*D*RR/(D*D+(A(I)*D+B(I)*RR)*RR))
     1       *(X(I+1)-X(I))
      ELSE
        RITAI=X(I)+RAND(2.0D0)*(X(I+1)-X(I))
      ENDIF
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE IRND0
C  *********************************************************************
      SUBROUTINE IRND0(W,F,K,N)
C
C  Initialisation of Walker's aliasing algorithm for random sampling
C  from discrete probability distributions.
C
C  Input arguments:
C    N ........ number of different values of the random variable.
C    W(1:N) ... corresponding point probabilities (not necessarily
C               normalised to unity).
C  Output arguments:
C    F(1:N) ... cutoff values.
C    K(1:N) ... alias values.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      DIMENSION W(N),F(N),K(N)
C  ****  Renormalisation.
      WS=0.0D0
      DO I=1,N
        IF(W(I).LT.0.0D0) STOP 'IRND0. Negative point probability.'
        WS=WS+W(I)
      ENDDO
      WS=DBLE(N)/WS
      DO I=1,N
        K(I)=I
        F(I)=W(I)*WS
      ENDDO
      IF(N.EQ.1) RETURN
C  ****  Cutoff and alias values.
      DO I=1,N-1
        HLOW=1.0D0
        HIGH=1.0D0
        ILOW=0
        IHIGH=0
        DO J=1,N
          IF(K(J).EQ.J) THEN
            IF(F(J).LT.HLOW) THEN
              HLOW=F(J)
              ILOW=J
            ELSE IF(F(J).GT.HIGH) THEN
              HIGH=F(J)
              IHIGH=J
            ENDIF
          ENDIF
        ENDDO
        IF(ILOW.EQ.0.OR.IHIGH.EQ.0) RETURN
        K(ILOW)=IHIGH
        F(IHIGH)=HIGH+HLOW-1.0D0
      ENDDO
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE RITA0
C  *********************************************************************
      SUBROUTINE RITA0(PDF,XLOW,XHIG,N,NU,ERRM,IWR)
C
C  Initialisation of the RITA algorithm for random sampling of a
C  continuous random variable X from a probability distribution function
C  PDF(X) defined in the interval (XLOW,XHIG). The external function
C  PDF(X) must be provided by the user. N is the number of points in the
C  sampling grid. These points are determined by means of an adaptive
C  strategy that minimises local interpolation errors. The first NU grid
C  points are uniformly spaced in (XLOW,XHIG); when NU is negative, the
C  initial grid consists of -NU points logarithmically spaced (in this
C  case, XLOW must be nonnegative).
C
C  ERRM is a measure of the interpolation error (the largest value of
C  the absolute error of the rational interpolation integrated over each
C  grid interval).
C
C  ****  Interpolation coefficients and PDF tables are printed on
C        separate files (UNIT=IWR) if IWR is greater than zero.
C
C  Other subprograms needed: EXTERNAL function PDF,
C                            subroutines RITAI0 and IRND0.
C

      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (NM=512)
      COMMON/CRITA/XA(NM),PAC(NM),DPAC(NM),AA(NM),BA(NM),IL(NM),IU(NM),
     1  NPM1A
      COMMON/CRITAA/X(NM),A(NM),B(NM),F(NM),IA(NM),NPM1
      EXTERNAL PDF
C  ****  Initialisation of the RITA algorithm.
      CALL RITAI0(PDF,XLOW,XHIG,N,NU,ERRM,IWR)
C  ****  Walker's aliasing; cutoff and alias values.
      NPM1=NPM1A
      DO I=1,NPM1
        X(I)=XA(I)
        A(I)=AA(I)
        B(I)=BA(I)
      ENDDO
      X(NPM1+1)=XA(NPM1+1)
      CALL IRND0(DPAC,F,IA,NPM1)
      F(NPM1+1)=1.0D0
      IA(NPM1+1)=NPM1
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE RITAI0
C  *********************************************************************
      SUBROUTINE RITAI0(PDF,XLOW,XHIG,N,NU,ERRM,IWR)
C
C  Initialisation of the RITA algorithm for random sampling of a
C  continuous random variable X from a probability distribution function
C  PDF(X) defined in the interval (XLOW,XHIG). The external function
C  PDF(X) must be provided by the user. N is the number of points in the
C  sampling grid. These points are determined by means of an adaptive
C  strategy that minimises local interpolation errors. The first NU grid
C  points are uniformly spaced in (XLOW,XHIG); when NU is negative, the
C  initial grid consists of -NU points logarithmically spaced (in this
C  case, XLOW must be nonnegative).
C
C  ERRM is a measure of the interpolation error (the largest value of
C  the absolute error of the rational interpolation integrated over each
C  grid interval).
C
C  ****  Interpolation coefficients and PDF tables are printed on
C        separate files (UNIT=IWR) if IWR is greater than zero.
C
C  Other subprograms needed: EXTERNAL function PDF.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (EPS=1.0D-10, ZERO=1.0D-45, ZEROT=0.1D0*ZERO)
      PARAMETER (NM=512)
C
C  The information used by the sampling function RITAI is exported
C  through the following common block,
      COMMON/CRITA/X(NM),PAC(NM),DPAC(NM),A(NM),B(NM),IL(NM),IU(NM),
     1  NPM1
C  where
C    X(I) ...... grid points, in increasing order.
C    PAC(I) .... value of the cumulative pdf at X(I).
C    DPAC(I) ... probability of the I-th interval.
C    A(I), B(I) ... rational inverse cumulative distribution parameters.
C    IL(I) .... largest J for which PAC(J) < (I-1)/(NP-1).
C    IU(I) .... smallest J for which PAC(J) > I/(NP-1).
C    NPM1 ..... numner of grid points minus one, NP-1 (8.LE.NP.LE.NM).
C
      COMMON/CRITA0/ERR(NM),C(NM)
      PARAMETER (NIP=51)
      DIMENSION PDFI(NIP),PDFIH(NIP),SUMI(NIP)
      EXTERNAL PDF
C
      IF(N.LE.16) THEN
        WRITE(6,'('' Error in RITAI0: N must be larger than 16.'',
     1    /,'' N='',I11)') N
        STOP 'RITAI0: N must be larger than 16.'
      ENDIF
      IF(N.GT.NM) THEN
        WRITE(6,'('' Error in RITAI0: N must be less than NM=512.'',
     1    /,'' N='',I11)') N
        STOP 'RITAI0: N must be less than NM=512.'
      ENDIF
      IF(XLOW.GT.XHIG-EPS) THEN
        WRITE(6,'('' Error in RITAI0: XLOW must be larger than XHIG.'',
     1    /,'' XLOW='',1P,E13.6,'', XHIG ='',E13.6)') XLOW,XHIG
        STOP 'RITAI0: XLOW must be larger than XHIG.'
      ENDIF
C
C  ****  We start with a grid of NUNIF points uniformly spaced in the
C        interval (XLOW,XHIG).
C
      IF(NU.GE.0) THEN
        NUNIF=MIN(MAX(8,NU),N/2)
        NP=NUNIF
        DX=(XHIG-XLOW)/DBLE(NP-1)
        X(1)=XLOW
        DO I=1,NP-1
          X(I+1)=XLOW+I*DX
        ENDDO
        X(NP)=XHIG
      ELSE
C  ****  If NU.LT.0,the NUNIF points are logarithmically spaced.
C        XLOW must be greater than or equal to zero.
        NUNIF=MIN(MAX(8,-NU),N/2)
        NP=NUNIF
        IF(XLOW.LT.0.0D0) THEN
          WRITE(6,'('' Error in RITAI0: XLOW and NU are negative.'',
     1    /,'' XLOW='',1P,E14.7, '',  NU='',I11)') XLOW,NU
          STOP 'RITAI0: XLOW and NU are negative.'
        ENDIF
        X(1)=XLOW
        IF(XLOW.LT.1.0D-16) THEN
          X(2)=XLOW+1.0D-6*(XHIG-XLOW)
          I1=2
        ELSE
          I1=1
        ENDIF
        FX=EXP(LOG(XHIG/X(I1))/DBLE(NP-I1))
        DO I=I1,NP-1
          X(I+1)=X(I)*FX
        ENDDO
        X(NP)=XHIG
      ENDIF
C
      DO I=1,NP-1
        DX=X(I+1)-X(I)
        DXI=(X(I+1)-X(I))/DBLE(NIP-1)
        PDFMAX=0.0D0
        DO K=1,NIP
          XIK=X(I)+DBLE(K-1)*DXI
          PDFI(K)=MAX(PDF(XIK),ZEROT)
          PDFMAX=MAX(PDFMAX,PDFI(K))
          IF(K.LT.NIP) THEN
            XIH=XIK+0.5D0*DXI
            PDFIH(K)=MAX(PDF(XIH),ZEROT)
            PDFMAX=MAX(PDFMAX,PDFIH(K))
          ENDIF
        ENDDO
C  ****  Simpson's integration.
        CONS=DXI*3.3333333333333333D-1*0.5D0
        SUMI(1)=0.0D0
        DO L=2,NIP
          SUMI(L)=SUMI(L-1)+CONS*(PDFI(L-1)+4.0D0*PDFIH(L-1)+PDFI(L))
        ENDDO
C
        DPAC(I)=SUMI(NIP)
        FACT=1.0D0/DPAC(I)
        DO K=1,NIP
          SUMI(K)=FACT*SUMI(K)
        ENDDO
C  ****  When the PDF vanishes at one of the interval end points, its
C        value is modified.
        IF(PDFI(1).LT.ZERO) PDFI(1)=1.0D-5*PDFMAX
        IF(PDFI(NIP).LT.ZERO) PDFI(NIP)=1.0D-5*PDFMAX
C
        PLI=PDFI(1)*FACT
        PUI=PDFI(NIP)*FACT
        B(I)=1.0D0-1.0D0/(PLI*PUI*DX*DX)
        A(I)=(1.0D0/(PLI*DX))-1.0D0-B(I)
        C(I)=1.0D0+A(I)+B(I)
        IF(C(I).LT.ZERO) THEN
          A(I)=0.0D0
          B(I)=0.0D0
          C(I)=1.0D0
        ENDIF
C
C  ****  ERR(I) is the integral of the absolute difference between the
C        rational interpolation and the true PDF, extended over the
C        interval (X(I),X(I+1)). Calculated using the trapezoidal rule.
C
        ICASE=1
  100   CONTINUE
        ERR(I)=0.0D0
        DO K=1,NIP
          RR=SUMI(K)
          PAP=DPAC(I)*(1.0D0+(A(I)+B(I)*RR)*RR)**2/
     1       ((1.0D0-B(I)*RR*RR)*C(I)*(X(I+1)-X(I)))
          IF(K.EQ.1.OR.K.EQ.NIP) THEN
            ERR(I)=ERR(I)+0.5D0*ABS(PAP-PDFI(K))
          ELSE
            ERR(I)=ERR(I)+ABS(PAP-PDFI(K))
          ENDIF
        ENDDO
        ERR(I)=ERR(I)*DXI
C  ****  If ERR(I) is too large, the PDF is approximated by a uniform
C        distribution.
        IF(ERR(I).GT.0.10D0*DPAC(I).AND.ICASE.EQ.1) THEN
          B(I)=0.0D0
          A(I)=0.0D0
          C(I)=1.0D0
          ICASE=2
          GO TO 100
        ENDIF
      ENDDO
      X(NP)=XHIG
      A(NP)=0.0D0
      B(NP)=0.0D0
      C(NP)=0.0D0
      ERR(NP)=0.0D0
      DPAC(NP)=0.0D0
C
C  ****  New grid points are added by halving the subinterval with the
C        largest absolute error.
C
  200 CONTINUE
      ERRM=0.0D0
      LMAX=1
      DO I=1,NP-1
C  ****  ERRM is the largest of the interval errors ERR(I).
        IF(ERR(I).GT.ERRM) THEN
          ERRM=ERR(I)
          LMAX=I
        ENDIF
      ENDDO
C
      NP=NP+1
      DO I=NP,LMAX+1,-1
        X(I)=X(I-1)
        A(I)=A(I-1)
        B(I)=B(I-1)
        C(I)=C(I-1)
        ERR(I)=ERR(I-1)
        DPAC(I)=DPAC(I-1)
      ENDDO
      X(LMAX+1)=0.5D0*(X(LMAX)+X(LMAX+2))
      DO I=LMAX,LMAX+1
        DX=X(I+1)-X(I)
        DXI=(X(I+1)-X(I))/DBLE(NIP-1)
        PDFMAX=0.0D0
        DO K=1,NIP
          XIK=X(I)+DBLE(K-1)*DXI
          PDFI(K)=MAX(PDF(XIK),ZEROT)
          PDFMAX=MAX(PDFMAX,PDFI(K))
          IF(K.LT.NIP) THEN
            XIH=XIK+0.5D0*DXI
            PDFIH(K)=MAX(PDF(XIH),ZEROT)
            PDFMAX=MAX(PDFMAX,PDFIH(K))
          ENDIF
        ENDDO
C  ****  Simpson's integration.
        CONS=DXI*3.3333333333333333D-1*0.5D0
        SUMI(1)=0.0D0
        DO L=2,NIP
          SUMI(L)=SUMI(L-1)+CONS*(PDFI(L-1)+4.0D0*PDFIH(L-1)+PDFI(L))
        ENDDO
C
        DPAC(I)=SUMI(NIP)
        FACT=1.0D0/DPAC(I)
        DO K=1,NIP
          SUMI(K)=FACT*SUMI(K)
        ENDDO
C
        IF(PDFI(1).LT.ZERO) PDFI(1)=1.0D-5*PDFMAX
        IF(PDFI(NIP).LT.ZERO) PDFI(NIP)=1.0D-5*PDFMAX
        PLI=PDFI(1)*FACT
        PUI=PDFI(NIP)*FACT
        B(I)=1.0D0-1.0D0/(PLI*PUI*DX*DX)
        A(I)=(1.0D0/(PLI*DX))-1.0D0-B(I)
        C(I)=1.0D0+A(I)+B(I)
        IF(C(I).LT.ZERO) THEN
          A(I)=0.0D0
          B(I)=0.0D0
          C(I)=1.0D0
        ENDIF
C
        ICASE=1
  300   CONTINUE
        ERR(I)=0.0D0
        DO K=1,NIP
          RR=SUMI(K)
          PAP=DPAC(I)*(1.0D0+(A(I)+B(I)*RR)*RR)**2/
     1       ((1.0D0-B(I)*RR*RR)*C(I)*(X(I+1)-X(I)))
          IF(K.EQ.1.OR.K.EQ.NIP) THEN
            ERR(I)=ERR(I)+0.5D0*ABS(PAP-PDFI(K))
          ELSE
            ERR(I)=ERR(I)+ABS(PAP-PDFI(K))
          ENDIF
        ENDDO
        ERR(I)=ERR(I)*DXI
C
        IF(ERR(I).GT.0.10D0*DPAC(I).AND.ICASE.EQ.1) THEN
          B(I)=0.0D0
          A(I)=0.0D0
          C(I)=1.0D0
          ICASE=2
          GO TO 300
        ENDIF
      ENDDO
C
      IF(NP.LT.N) GO TO 200
      NPM1=NP-1
C
C  ****  Renormalisation.
C
      WS=0.0D0
      DO I=1,NPM1
        WS=WS+DPAC(I)
      ENDDO
      WS=1.0D0/WS
      ERRM=0.0D0
      DO I=1,NPM1
        DPAC(I)=DPAC(I)*WS
        ERR(I)=ERR(I)*WS
        ERRM=MAX(ERRM,ERR(I))
      ENDDO
C
      PAC(1)=0.0D0
      DO I=1,NPM1
        PAC(I+1)=PAC(I)+DPAC(I)
      ENDDO
      PAC(NP)=1.0D0
C
C  ****  Pre-calculated limits for the initial binary search in
C        subroutine RITAI.
C
      BIN=1.0D0/DBLE(NPM1)
      IL(1)=1
      DO I=2,NPM1
        PTST=(I-1)*BIN
        DO J=IL(I-1),NP
          IF(PAC(J).GT.PTST) THEN
            IL(I)=J-1
            IU(I-1)=J
            GO TO 400
          ENDIF
        ENDDO
  400   CONTINUE
      ENDDO
      IU(NPM1)=NP
      IL(NP)=NP-1
      IU(NP)=NP
C
C  ****  Print interpolation tables (done only when IWR.GT.0).
C
      IF(IWR.GT.0) THEN
        OPEN(IWR,FILE='param.dat')
        WRITE(IWR,1000)
 1000   FORMAT(1X,'#',5X,'X',11X,'PDF(X)',10X,'A',13X,'B',13X,'C',
     1    11X,'error')
        DO I=1,NPM1
          PDFE=MAX(PDF(X(I)),ZEROT)*WS
          WRITE(IWR,'(1P,7E14.6)') X(I),PDFE,A(I),B(I),C(I),ERR(I)
        ENDDO
        CLOSE(IWR)
C
        OPEN(IWR,FILE='table.dat')
        WRITE(IWR,2000)
 2000   FORMAT(1X,'#',6X,'X',13X,'PDF_ex',10X,'PDF_ap',11X,'err')
        DO I=1,NPM1
          DX=(X(I+1)-X(I))/DBLE(NIP-1)
          DO K=1,NIP,5
            XT=X(I)+(K-1)*DX
            P1=MAX(PDF(XT),ZEROT)*WS
C  ****  Rational interpolation.
            TAU=(XT-X(I))/(X(I+1)-X(I))
            CON1=2.0D0*B(I)*TAU
            CON2=C(I)-A(I)*TAU
            IF(ABS(CON1).GT.1.0D-10*ABS(CON2)) THEN
              ETA=CON2*(1.0D0-SQRT(1.0D0-2.0D0*TAU*CON1/CON2**2))/CON1
            ELSE
              ETA=TAU/CON2
            ENDIF
            P2=DPAC(I)*(1.0D0+(A(I)+B(I)*ETA)*ETA)**2
     1        /((1.0D0-B(I)*ETA*ETA)*C(I)*(X(I+1)-X(I)))
            WRITE(IWR,'(1P,5E16.8)') XT,P1,P2,(P1-P2)/P1
          ENDDO
        ENDDO
        CLOSE(IWR)
C
        OPEN(IWR,FILE='limits.dat')
        WRITE(IWR,3000)
 3000   FORMAT(1X,'#  I',6X,'PAC(ITL)',9X,'(I-1)/NPM1',11X,'I/NPM1',
     1    12X,'PAC(ITU)',12X,'PAC(I)')
        DO I=1,NPM1
          WRITE(IWR,'(I5,1P,5E19.11)') I,PAC(IL(I)),(I-1)*BIN,I*BIN,
     1      PAC(IU(I)),PAC(I)
          IF(PAC(IL(I)).GT.(I-1)*BIN+EPS.OR.
     1      PAC(IU(I)).LT.I*BIN-EPS) THEN
            WRITE(IWR,3001)
 3001       FORMAT(' #  WARNING: The first four values should be in in',
     1        'creasing order.')
          ENDIF
        ENDDO
        CLOSE(IWR)
      ENDIF
C
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE RITAV
C  *********************************************************************
      SUBROUTINE RITAV(X,PDF,CDF)
C
C  This subroutine gives the values of the (normalized) pdf, PDF, and of
C  its cumulative distribution function, CDF, at the point X. These
C  values are calculated from the RITA approximation.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C
      PARAMETER (NM=512)
      COMMON/CRITA/XT(NM),PAC(NM),DPAC(NM),A(NM),B(NM),IL(NM),IU(NM),
     1  NPM1
      COMMON/CRITA0/ERR(NM),C(NM)
C
      IF(X.GT.XT(NPM1+1)) THEN
        PDF=0.0D0
        CDF=1.0D0
      ELSE IF(X.LT.XT(1)) THEN
        PDF=0.0D0
        CDF=0.0D0
      ELSE
        I=1
        I1=NPM1+1
    1   IT=(I+I1)/2
        IF(X.GT.XT(IT)) THEN
          I=IT
        ELSE
          I1=IT
        ENDIF
        IF(I1-I.GT.1) GO TO 1
        TAU=(X-XT(I))/(XT(I+1)-XT(I))
        CON1=2.0D0*B(I)*TAU
        CON2=C(I)-A(I)*TAU
        IF(ABS(CON1).GT.1.0D-10*ABS(CON2)) THEN
          ETA=CON2*(1.0D0-SQRT(1.0D0-2.0D0*TAU*CON1/CON2**2))/CON1
        ELSE
          ETA=TAU/CON2
        ENDIF
        PDF=DPAC(I)*(1.0D0+(A(I)+B(I)*ETA)*ETA)**2
     1    /((1.0D0-B(I)*ETA*ETA)*C(I)*(XT(I+1)-XT(I)))
        CDF=PAC(I)+ETA*DPAC(I)
      ENDIF
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE RITAM
C  *********************************************************************
      SUBROUTINE RITAM(XD,XU,XM0,XM1,XM2)
C
C  Calculation of (restricted) momenta of a pdf, PDF(X), obtained from
C  its RITA approximation.
C
C     XD, XU ... limits of the integration interval.
C     XM0 ...... 0th order moment.
C     XM1 ...... 1st order moment.
C     XM2 ...... 2nd order moment.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
C
      PARAMETER (NM=512)
      COMMON/CRITA/XT(NM),PAC(NM),DPAC(NM),A(NM),B(NM),IL(NM),IU(NM),
     1  NPM1
      COMMON/CRITA0/ERR(NM),C(NM)
      PARAMETER (NIP=51)
      DIMENSION XI(NIP),FUN(NIP)
C
      XM0=0.0D0
      XM1=0.0D0
      XM2=0.0D0
      DO I=1,NPM1
        IF(XT(I+1).GE.XD.AND.XT(I).LE.XU) THEN
          X1=MAX(XT(I),XD)
          X2=MIN(XT(I+1),XU)
          DX=(X2-X1)/DBLE(NIP-1)
C
          DO K=1,NIP
            XI(K)=X1+DBLE(K-1)*DX
C  ****  Value of the RITA rational pdf at the point XI(K).
            TAU=(XI(K)-XT(I))/(XT(I+1)-XT(I))
            CON1=2.0D0*B(I)*TAU
            CON2=C(I)-A(I)*TAU
            IF(ABS(CON1).GT.1.0D-10*ABS(CON2)) THEN
              ETA=CON2*(1.0D0-SQRT(1.0D0-2.0D0*TAU*CON1/CON2**2))/CON1
            ELSE
              ETA=TAU/CON2
            ENDIF
            FUN(K)=DPAC(I)*(1.0D0+(A(I)+B(I)*ETA)*ETA)**2
     1        /((1.0D0-B(I)*ETA*ETA)*C(I)*(XT(I+1)-XT(I)))
          ENDDO
C  ****  Simpson's integration.
          CONS=DX*3.3333333333333333D-1
          SUM=0.0D0
          DO L=3,NIP,2
            SUM=SUM+FUN(L-2)+4.0D0*FUN(L-1)+FUN(L)
          ENDDO
          XM0=XM0+SUM*CONS
C
          DO K=1,NIP
            FUN(K)=FUN(K)*XI(K)
          ENDDO
          SUM=0.0D0
          DO L=3,NIP,2
            SUM=SUM+FUN(L-2)+4.0D0*FUN(L-1)+FUN(L)
          ENDDO
          XM1=XM1+SUM*CONS
C
          DO K=1,NIP
            FUN(K)=FUN(K)*XI(K)
          ENDDO
          SUM=0.0D0
          DO L=3,NIP,2
            SUM=SUM+FUN(L-2)+4.0D0*FUN(L-1)+FUN(L)
          ENDDO
          XM2=XM2+SUM*CONS
        ENDIF
      ENDDO
      RETURN
      END
C  *********************************************************************
C                         FUNCTION RAND (Random number generator)
C  *********************************************************************
      FUNCTION RAND(DUMMY)
C
C  This is an adapted version of subroutine RANECU written by F. James
C  (Comput. Phys. Commun. 60 (1990) 329-344), which has been modified to
C  give a single random number at each call.
C
C  The 'seeds' ISEED1 and ISEED2 must be initialised in the main program
C  and transferred through the named common block /RSEED/.
C
C  Some compilers incorporate an intrinsic random number generator with
C  the same name (but with different argument lists). To avoid conflict,
C  it is advisable to declare RAND as an external function in all sub-
C  programs that call it.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (USCALE=1.0D0/2.147483563D9)
      COMMON/RSEED/ISEED1,ISEED2
C
      I1=ISEED1/53668
      ISEED1=40014*(ISEED1-I1*53668)-I1*12211
      IF(ISEED1.LT.0) ISEED1=ISEED1+2147483563
C
      I2=ISEED2/52774
      ISEED2=40692*(ISEED2-I2*52774)-I2*3791
      IF(ISEED2.LT.0) ISEED2=ISEED2+2147483399
C
      IZ=ISEED1-ISEED2
      IF(IZ.LT.1) IZ=IZ+2147483562
      RAND=IZ*USCALE
C
      RETURN
      END
