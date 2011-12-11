C  *********************************************************************
C                       SUBROUTINE FOPEN
C  *********************************************************************
      SUBROUTINE FOPEN(PFILE,IR)
      CHARACTER*4096 PFILE
      INTEGER IR
C
      OPEN(IR, FILE=PFILE)
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE FCLOSE
C  *********************************************************************
      SUBROUTINE FCLOSE(IR)
      INTEGER IR
C
      CLOSE(UNIT=IR)
      RETURN
      END
