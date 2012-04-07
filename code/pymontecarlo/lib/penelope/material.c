#include <Python.h>
#include "penelope.h"
#include "utils_c.h"

////////////////////////////////////////////////////////////////////////////////
// Module functions
////////////////////////////////////////////////////////////////////////////////

static PyObject*
create(PyObject* self, PyObject* args)
{
    PyObject * material;
    const char * filepath;

    if (!PyArg_ParseTuple(args, "Os", &material, &filepath))
        return NULL;

    // Extract name
    PyObject * nameobj;
    nameobj = PyObject_GetAttrString(material, "name");
    if (nameobj == NULL) {
        PyErr_SetString(PyExc_ValueError,
                        "Material object has no attribute 'name'");
        return NULL;
    }

    char * namestr = PyString_AsString(nameobj);
    char name[62];
    _strcopyfill(namestr, strlen(namestr), name, 62, ' ');

    // Extract density
    PyObject * densityobj;
    densityobj = PyObject_GetAttrString(material, "density_kg_m3");
    if (densityobj == NULL) {
        PyErr_SetString(PyExc_ValueError,
                        "Material object has no attribute 'density_kg_m3'");
        return NULL;
    }

    double density = PyFloat_AS_DOUBLE(densityobj);

    // Extract composition
    PyObject * composition;
    composition = PyObject_GetAttrString(material, "composition");
    if (composition == NULL) {
        PyErr_SetString(PyExc_ValueError,
                        "Material object has no attribute 'composition'");
        return NULL;
    }

    int32_t zs[30];
    double wfs[30];

    int32_t nelem = PyDict_Size(composition);
    PyObject * keys = PyDict_Keys(composition);
    PyObject * values = PyDict_Values(composition);

    int i = 0;
    while (i < nelem) {
        zs[i] = PyInt_AsLong(PyList_GetItem(keys, i));
        wfs[i] = PyFloat_AsDouble(PyList_GetItem(values, i));
        i++;
    }

    // Create material with PENELOPE
    int iwr = 7;
    if (_open_fortran_file(filepath, iwr) != 0)
        return NULL;

    pemats_(&nelem, &zs, &wfs, &density, &name, &iwr);

    _close_fortran_file(iwr);

    Py_RETURN_NONE;
}

static PyMethodDef material_methods[] =
                {
                                {
                                                "create",
                                                create,
                                                METH_VARARGS,
                                                "Creates a material. Arguments: Composition dictionary (key: atomic number, value: weight fraction), density, name and filename." },
                                { NULL } /* Sentinel */
                };

////////////////////////////////////////////////////////////////////////////////
// Initialize module
////////////////////////////////////////////////////////////////////////////////

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC init_material(void)
{
    // Initialize module
    PyObject* m;
    m = Py_InitModule3("_material", material_methods,
                    "PENELOPE functions to create materials.");
    if (m == NULL)
        return;
}
