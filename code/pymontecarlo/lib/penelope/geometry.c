#include <Python.h>
#include "pengeom.h"
#include "utils_c.h"

////////////////////////////////////////////////////////////////////////////////
// Module functions
////////////////////////////////////////////////////////////////////////////////

static PyObject*
init(PyObject* self, PyObject* args)
{
    const char * input;
    const char * output;
    int nmat;
    int nbody;

    if (!PyArg_ParseTuple(args, "ss", &input, &output))
        return NULL;

    int ird = 15;
    if (_open_fortran_file(input, ird) != 0)
        return NULL;

    int iwr = 16;
    if (_open_fortran_file(output, iwr) != 0)
        return NULL;

    double params[0];
    int npar = 0;

    geomin_(params, &npar, &nmat, &nbody, &ird, &iwr);

    _close_fortran_file(ird);
    _close_fortran_file(iwr);

    return Py_BuildValue("ii", nmat, nbody);
}

static PyMethodDef geometry_methods[] =
{
{ "init", init, METH_VARARGS, "" },
{ NULL } /* Sentinel */
};

////////////////////////////////////////////////////////////////////////////////
// Initialize module
////////////////////////////////////////////////////////////////////////////////

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC init_geometry(void)
{
    // Initialize module
    PyObject* m;
    m = Py_InitModule3("_geometry", geometry_methods,
                    "PENELOPE geometry functions");
    if (m == NULL)
        return;
}
