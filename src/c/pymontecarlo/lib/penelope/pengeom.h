//COMMON/QTRACK/DSTOT,KSLAST
extern struct
{
  double dstot;
  int kslast;
} qtrack_;

void
locate_(void);
void
step_(double * ds, double * dsef, int * ncross);
void
geomin_(double(*param), int * npar, int * nmat, int * nbody, int * ird, int * iwr);
