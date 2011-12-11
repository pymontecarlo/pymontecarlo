//COMMON/TRACK/E,X,Y,Z,U,V,W,WGHT,KPAR,IBODY,MAT,ILB(5)
extern struct
{
    double e;
    double x;
    double y;
    double z;
    double u;
    double v;
    double w;
    double wght;
    int kpar;
    int ibody;
    int mat;
    int ilb[5];
} track_;

//COMMON/RSEED/ISEED1,ISEED2
extern struct
{
    int seed1;
    int seed2;
} rseed_;

//COMMON/CSIMPA/EABS(3,MAXMAT),C1(MAXMAT),C2(MAXMAT),WCC(MAXMAT),WCR(MAXMAT)
extern struct
{
    double eabs[10][3];
    double c1[10];
    double c2[10];
    double wcc[10];
    double wcr[10];
} csimpa_;

//COMMON/CFORCE/FORCE(NB,3,8)
extern struct
{
    double force[8][3][5000];
} cforce_;

void
peinit_(double * emax, int * nmat, int * iwr, int * info,
        char(*materials)[10][4096]);
void
pemats_(int * nelem, int(*zs)[30], double(*wfs)[30], double * rho,
        char(*name)[62], int * iwr);
void
cleans_(void);
void
start_(void);
void
jump_(double * dsmax, double * ds);
void
knock_(double * de, int * icol);
void
secpar_(int * left);

double
prange_(double * e, int * kpar, int * mat);
double
phmfp_(double * e, int * kpar, int * mat, int * icol);
