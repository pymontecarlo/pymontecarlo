C  *********************************************************************
C                       SUBROUTINE TIMER
C  *********************************************************************
      SUBROUTINE TIMER(SEC)
C
C  This subroutine gives the execution time in seconds. The output value
C  of the variable SEC is the time (in seconds) elapsed since the last
C  call to TIME0.
C
C  ---> It is assumed that subroutine TIMER is called with a frequency
C       of, at least, once per day.
C
C  NEADB-20040221- Modifications to increase the portability towards
C                  Fortran '90 compilers.
C
      IMPLICIT NONE
      DOUBLE PRECISION SEC,TIME,TIMEI,TYEST
      CHARACTER*5 zone
      CHARACTER*8 date
      CHARACTER*10 c_time
      INTEGER*4 values,LASTH
      DIMENSION values(8)
C
      SAVE TIMEI,TYEST,LASTH
C
      CALL DATE_and_TIME(date,c_time,zone,values)
C  ****  values(1) = year,
C        values(2) = month of the year,
C        values(3) = day of the month,
C        values(5) = hour of the day (range 0-23),
C        values(6) = minutes of the hour (range 0-59),
C        values(7) = seconds of the minute (range 0-59),
C        values(8) = milliseconds of the second (range 0-999).
C
      IF(values(5).LT.LASTH) TYEST=TYEST+8.640D4  ! The day has changed.
      LASTH=values(5)
      TIME=(((values(5)*60)+values(6))*60)+values(7)
     1    +0.001D0*values(8)+TYEST
      SEC=TIME-TIMEI
      RETURN
C
C  ****  A call to TIMEO initializes the clock.
C
      ENTRY TIME0
      CALL DATE_and_TIME(date,c_time,zone,values)
      LASTH=values(5)
      TIMEI=(((values(5)*60)+values(6))*60)+values(7)
     1     +0.001D0*values(8)
      TYEST=0.0D0
      RETURN
      END
C  *********************************************************************
C                       FUNCTION CPUTIM
C  *********************************************************************
      FUNCTION CPUTIM()
C
C  This function returns the CPU (user) time used since the start of the
C  calling program, in seconds.
C
C  NEADB-20040221- Modifications to increase the portability towards
C                  Fortran '90 compilers.
C
      IMPLICIT NONE
      REAL*4 TIME
      DOUBLE PRECISION CPUTIM
C
      CALL CPU_TIME(TIME)
      CPUTIM=TIME
      RETURN
      END
C  *********************************************************************
C                       SUBROUTINE PDATET
C  *********************************************************************
      SUBROUTINE PDATET(DATE23)
C
C  Delivers a 23-character string with the date and time.
C  (ddth Mon yyyy. hh:mm:ss)
C
      IMPLICIT NONE
      CHARACTER*23 DATE23
      CHARACTER*2 LORD
      CHARACTER*3 MONTH(12)
      CHARACTER*5 zone
      CHARACTER*8 date
      CHARACTER*10 c_time
      INTEGER*4 values(8),IORD
C
      DATA MONTH/'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep',
     1           'Oct','Nov','Dec'/
C
      CALL DATE_and_TIME(date,c_time,zone,values)
C  ****  values(1) = year,
C        values(2) = month of the year,
C        values(3) = day of the month,
C        values(5) = hour of the day (range 0-23),
C        values(6) = minutes of the hour (range 0-59),
C        values(7) = seconds of the minute (range 0-59),
C        values(8) = milliseconds of the second (range 0-999).
C
      IORD=values(3)-values(3)/10
      IF(IORD.EQ.1) THEN
        LORD='st'
      ELSE IF(IORD.EQ.2) THEN
        LORD='nd'
      ELSE IF(IORD.EQ.3) THEN
        LORD='rd'
      ELSE
        LORD='th'
      ENDIF
C
      WRITE(DATE23,'(I2,A2,1X,A3,I5,''. '',I2.2,'':'',I2.2,'':'',
     1  I2.2)') values(3),LORD,MONTH(values(2)),values(1),values(5),
     1  values(6),values(7)
      RETURN
      END
