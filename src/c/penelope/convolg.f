C  *********************************************************************
C                       PROGRAM CONVOLG
C  *********************************************************************
C
C     This program generates the channel number spectrum of a detector
C  from the energy spectrum of incident photons. The channel number
C  spectrum is obtained as the convolution of the energy spectrum of
C  incident photons with the detector resolution function.
C
C     The incident energy spectrum, which is considered as a histogram,
C  is read from an input file. Energy bins are assumed to have uniform
C  width. Each line in the input file contains the centre of the energy
C  bin (in eV) and the bar height. The energy bin centers must be in
C  increasing order.
C
C     The energy resolution function of the detector is assumed to be a
C  Gaussian distribution with mean equal to the incident photon energy
C  E. Its full width at half maximum (a function of E) is given by the
C  external function FWHM(E), to be defined by the user. The present
C  version of function FWHM(E) corresponds to a typical Si(Li) detector.
C
C                                           Francesc Salvat. July, 2006.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*30 SFILE
      CHARACTER*200 PSFREC
      PARAMETER (NT=4000,NDT=100)
      DIMENSION E(NT),S(NT)
      COMMON/DEHIST/DEH
      COMMON/CCHANN/VL,VU
      EXTERNAL F1
C
C  ****  Reading of the energy spectrum of incident photons from the
C        input file.
C
      WRITE(6,*) '  '
      WRITE(6,*) '  Enter the file path-name of the simulated spect',
     1   'rum ...'
      READ(5,'(A30)') SFILE
      WRITE(6,'(3X,''Simulated spectrum: '',A12,/)') SFILE
C
      OPEN(7,FILE=SFILE)
      OPEN(8,FILE='mcorig.dat')
      NC=0
      AREAC=0.0D0
      DO I=1,NT
        CALL RDPSF(7,PSFREC,KODE)
        IF(KODE.NE.0) GO TO 1
        READ(PSFREC,*,END=1) EE,SS,DD
        WRITE(8,'(1X,1P,3E15.7)') EE,SS,DD
        IF(SS.LT.0.0D0) STOP 'Negative count number.'
        IF(EE.LT.0.0D0) STOP 'Negative input energy.'
        NC=NC+1
        E(NC)=EE
        S(NC)=SS
        AREAC=AREAC+SS
      ENDDO
    1 CONTINUE
      CLOSE(UNIT=7)
      CLOSE(UNIT=8)
      IF(NC.LE.1) STOP 'Less than 1 channel?'
      DEH=(E(NC)-E(1))/DFLOAT(NC-1)
      EMIN=E(1)
      EMAX=E(NC)+0.5D0*DEH
      AREA=AREAC*DEH
      WRITE(6,'(3X,''Maximum energy ='',1P,E14.7,'' eV'')') EMAX
      WRITE(6,'(3X,''Energy bin width ='',1P,E14.7,'' eV'')') DEH
      WRITE(6,'(3X,''Number of energy bins ='',I5,/)') NC
C
      WRITE(6,*) '  Enter channel width of the computed ',
     1 'spectrum (in eV) ...'
      READ(5,*) DV
      VMAX=EMAX+4.0D0*FWHM(EMAX)
      NCHAN=VMAX/DV
      WRITE(6,'(3X,''Number of channels ='',I5)') NCHAN
C
C  ****  PULSE SPECTRUM.
C
      OPEN(7,FILE='chspect.dat')
      WRITE(6,'(3X,''The computed pulse-height spectrum is '',
     1  '' written on file CHSPECT.DAT'')')
C
      AREAC=0.0D0
      DO I=1,NCHAN
        VU=EMIN+I*DV
        VL=VU-DV
        SUMT=0.0D0
        DO J=1,NC
          EL=E(J)-0.5D0*DEH
          IF(EL.LT.1.0D-3) EL=1.0D-3
          EU=EL+DEH
          TST=1.0D20
          IF(EU.LT.VL) THEN
            TST=PULSES(EU,VL)
          ENDIF
          IF(EL.GT.VU) THEN
            TST=PULSES(EL,VU)
          ENDIF
          IF(TST.GT.1.0D-20) THEN
            CALL RMBRG(F1,EL,EU,SUM,1.0D-4,IER)
            SUMT=SUMT+SUM*S(J)
          ENDIF
        ENDDO
        VC=0.5D0*(VL+VU)
        SUMV=SUMT/DV
        AREAC=AREAC+SUMT
        IF(DABS(SUMV).LT.1.0D-25) SUMV=1.0D-25
        WRITE(7,'(1P,2E13.5)') VC,SUMV
      ENDDO
      WRITE(6,'(3X,''Input spectrum area ='',1P,E14.7,'' eV'')') AREA
      WRITE(6,'(3X,''  New spectrum area ='',1P,E14.7,'' eV'')') AREAC
      CLOSE(UNIT=7)
      WRITE(6,*) 'Press enter to continue...'
      READ(*,*)
C
      STOP
      END
C  *********************************************************************
C                       SUBROUTINE RDPSF
C  *********************************************************************
      SUBROUTINE RDPSF(IUNIT,PSFREC,KODE)
C
C  This subroutine reads the photon energy spectrum from the input file.
C  When KODE=0, a valid channel record has been read and copied into the
C  character variable PSFREC. KODE=-1 indicates that the program tried
C  to read after the end of the input file. Blank lines and lines that
C  start with the pound sign (#) are considered as comments and ignored.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      CHARACTER*200 PSFREC
C
      KODE=0
    1 CONTINUE
      READ(IUNIT,'(A200)',END=2,ERR=1) PSFREC
      READ(PSFREC,*,ERR=1,END=1) S
      RETURN
    2 CONTINUE
      KODE=-1   ! End of file
      RETURN
      END
C  *********************************************************************
C                       FUNCTION PULSES
C  *********************************************************************
      FUNCTION PULSES(E,V)
C
C     This function computes the pulse height spectrum that results from
C  the detection of a photon with energy E. The output value is the
C  probability of having a pulse of height V. The detector response
C  function is assumed to be Gaussian.
C
C
C     Arguments:   E ... deposited energy (eV).
C                  V ... output pulse height.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (SQR2PI=2.506628274631D0)
      COMMON/CCHANN/VL,VU
C
      SIGMA=DMAX1(0.4246609D0*FWHM(E),1.0D-6)
      TST=0.5D0*((V-E)/SIGMA)**2
      IF(TST.LT.80.0D0) THEN
        PULSES=DEXP(-TST)/(SQR2PI*SIGMA)
      ELSE
        PULSES=0.0D0
      ENDIF
      RETURN
      END
C  *********************************************************************
C                       FUNCTION PACN
C  *********************************************************************
      FUNCTION PACN(X)
C
C     Normal cumulative probability function. Hastings' rational approx-
C  imation.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (D1=0.0498673470D0, D2=0.0211410061D0,
     1  D3=0.0032776263D0, D4=0.0000380036D0, D5=0.0000488906D0,
     2  D6=0.0000053830D0)
      IF(X.GT.25.0D0) THEN
        PACN=1.0D0
      ELSE IF(X.GT.0.0D0) THEN
        PACN=1.0D0-0.5D0
     1      /(1.0D0+X*(D1+X*(D2+X*(D3+X*(D4+X*(D5+X*D6))))))**16
      ELSE IF(X.GT.-25.0D0) THEN
        T=-X
        PACN=0.5D0
     1  /(1.0D0+T*(D1+T*(D2+T*(D3+T*(D4+T*(D5+T*D6))))))**16
      ELSE
        PACN=0.0D0
      ENDIF
      RETURN
      END
C  *********************************************************************
      FUNCTION F1(E)
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      COMMON/CCHANN/VL,VU
      SIGMA=0.4246609D0*FWHM(E)
      XL=(VL-E)/SIGMA
      XU=(VU-E)/SIGMA
      F1=PACN(XU)-PACN(XL)
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE RMBRG
C  *********************************************************************
      SUBROUTINE RMBRG(FCT,XL,XU,SUM,TOL,IER)
C
C     Integration of a function by Romberg's method.
C
C     FCT is the (external) function being integrated over the interval
C  (XL,XU). SUM is the resultant value of the integral. TOL is the tole-
C  rance, i.e. maximum relative error required on the computed value
C  (SUM). TOL should not exceed 1.0D-13. IER is an error control para-
C  meter; its output value is IER=0 if the integration algorithm has
C  been able to reach the required accuracy and IER=1 otherwise.
C
C  Reference: H.S. Wilf, 'Mathematical Methods for Digital Computers',
C             Ed. by A.R. Ralston and H.S. Wilf (Wiley: New York 1968),
C             vol.I, p.133.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (NPAR=32)
      DIMENSION T(NPAR)
      IER=0
      HN=XU-XL
      YT=FCT(XL)
      FX=FCT(XU)
      YT=0.5D0*(YT+FX)
      TP=0.0D0  ! To avoid warnings from some compilers.
      NINT=1
      T(1)=HN*YT
      DO I=2,NPAR
        H=HN
        HN=0.5D0*H
        X=XL-HN
C         Trapezoidal rule.
        DO K=1,NINT
          X=X+H
          FX=FCT(X)
          YT=YT+FX
        ENDDO
        SV=T(1)
        T(1)=HN*YT
C         Romberg's extrapolation.
        FN=1.0D0
        DO K=2,I
          FN=4.0D0*FN
          TP=SV
          SV=T(K)
          T(K)=(FN*T(K-1)-TP)/(FN-1.0D0)
        ENDDO
        SUM=T(I)
C         Error control.
        ERR=DABS(SUM-TP)/DMAX1(DABS(SUM),1.0D-10)
        IF(I.GT.4.AND.ERR.LT.TOL) RETURN
        NINT=NINT+NINT
      ENDDO
C
      IER=1
      WRITE(6,'(3X,''*** WARNING: Subroutine RMBRG has not converged.''
     1   )')
      WRITE(6,'(7X,''XL ='',1P,E14.7,'',  XU ='',E14.7,'',  TOL ='',
     1  E14.7,/)') XL,XU,TOL
      RETURN
      END
C  *********************************************************************
C                       FUNCTION FWHM
C  *********************************************************************
      FUNCTION FWHM(E)
C
C     This subprogram gives the FWHM (in eV) of the detector resolution
C  function as a function of the energy E of the incident photon.
C
C     It must be defined explicitly for each particular detector.
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      COMMON/DEHIST/DEH
C  ****  Example of FWHM(E) function for a Si(Li) detector.
      FWHM=DSQRT(7849.255D0+2.237253D0*E)
C  ****  Example of FWHM(E) function for a CdTe detector.
c     FWHM=DSQRT(64.5D0*E)
C  ****  Example of FWHM(E) function for a NaI detector (from Zerby).
c     FWHM=40.0D0*SQRT(E)+0.028D0*E
C  ****  Bin width correction (DEH is subtracted from the FWHM).
      FWHM=MAX(FWHM-DEH,5.0D0)
      RETURN
      END
