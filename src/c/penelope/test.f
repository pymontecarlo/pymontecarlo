C  *********************************************************************
C                       SUBROUTINE TSIMPA
C  *********************************************************************
      SUBROUTINE TSIMPA(M,OEABS1,OEABS2,OEABS3,OC1,OC2,OWCC,OWCR)
C
C  Inputs: M
C  Outputs: OEABS1,OEABS2,OEABS3,OC1,OC2,OWCC,OWCR
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (MAXMAT=10)
      COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),
     1  WCR(MAXMAT)
C
      OEABS1=EABS(1,M)
      OEABS2=EABS(2,M)
      OEABS3=EABS(3,M)
      OC1=C1(M)
      OC2=C2(M)
      OWCC=WCC(M)
      OWCR=WCR(M)
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE TTRACK
C  *********************************************************************
      SUBROUTINE TTRACK(OE,OX,OY,OZ,OU,OV,OW,OWGHT,MKPAR,MIBODY,MM,MILB)
C
C  Inputs: none
C  Outputs: OE,OX,OY,OZ,OU,OV,OW,OWGHT,MKPAR,MIBODY,MM,MILB
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,M,ILB(5)
      DIMENSION MILB(5)
C
      OE=E
      OX=X
      OY=Y
      OZ=Z
      OU=U
      OV=V
      OW=W
      OWGHT=WGHT
      MKPAR=KPAR
      MIBODY=IBODY
      MM=M
      MILB=ILB
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE TFORCE
C  *********************************************************************
      FUNCTION TFORCE(IB,KPAR,ICOL)
C
C  Inputs: IB,KPAR,ICOL
C  Outputs: FORCE
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      PARAMETER (NB=5000)
      COMMON/CFORCE/FORCE(NB,3,8)
C
      TFORCE=FORCE(IB,KPAR,ICOL)
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE TRSEED
C  *********************************************************************
      SUBROUTINE TRSEED(MSEED1,MSEED2)
C
C  Inputs: none
C  Outputs: MSEED1,MSEED2
C
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER*4 (I-N)
      COMMON/RSEED/ISEED1,ISEED2
C
      MSEED1=ISEED1
      MSEED2=ISEED2
      RETURN
      END
