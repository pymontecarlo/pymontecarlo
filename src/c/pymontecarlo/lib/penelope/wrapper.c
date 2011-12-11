#include <Python.h>
#include "penelope.h"
#include "pengeom.h"
#include "penvared.h"
#include "timer.h"
#include "utils.h"

const int FILEPATH_MAX_LENGTH = 4096;

///////////////////////////////////////////////////////////////////////////////
//   Utilities
///////////////////////////////////////////////////////////////////////////////

static void _strcopyfill(const char * str, int strLength, char * array,
                         int arrayLength, char pad)
{
    int i = 0;

    while (i < arrayLength) {
        if (i < strLength)
            *(array + i) = str[i];
        else
            *(array + i) = pad;

        i++;
    }
}

static int _check_filepath_length(const char * filepath)
{
    if (strlen(filepath) > FILEPATH_MAX_LENGTH) {
        char message[100];
        sprintf(message, "Filename is longer than %d characters: '%s'",
                FILEPATH_MAX_LENGTH, filepath);
        PyErr_SetString(PyExc_ValueError, message);
        return -1;
    }

    return 0;
}

static
int _open_fortran_file(const char * filepath, int unit)
{
    if (unit < 0 || unit == 5 || unit == 6) {
        PyErr_SetString(PyExc_ValueError,
                        "Unit must be greater than 0 and different than 5 or 6");
        return -1;
    }

    if (_check_filepath_length(filepath) != 0)
        return -1;

    char filename_array[FILEPATH_MAX_LENGTH];
    _strcopyfill(filepath, strlen(filepath), filename_array,
                 FILEPATH_MAX_LENGTH, ' ');

    fopen_(&filename_array, &unit);

    return 0;
}

static int _close_fortran_file(int unit)
{
    fclose_(&unit);
    return 0;
}

///////////////////////////////////////////////////////////////////////////////
//    Callbacks
///////////////////////////////////////////////////////////////////////////////

static PyObject * TRAJECTORY_END;
static PyObject * KNOCK;

static PyObject * BACKSCATTERED_ELECTRON;
static PyObject * TRANSMITTED_ELECTRON;
static PyObject * ABSORBED_ELECTRON;
static PyObject * GENERATED_ELECTRON;

static PyObject * EXIT_PHOTON;
static PyObject * ABSORBED_PHOTON;
static PyObject * GENERATED_PHOTON;

///////////////////////////////////////////////////////////////////////////////

static void _call_callbacks(PyObject * callbacks, PyObject* name,
                            PyObject* args)
{
    PyObject * result;
    PyObject * callback;

    int i = 0;
    int size = PyList_Size(callbacks);
    while (i < size) {
        callback = PyList_GetItem(callbacks, i);

        result = PyObject_CallMethodObjArgs(callback, name, args, NULL);

        // Ignore result
        if (result != NULL) {
            Py_DECREF(result);
        }

        i++;
    }
}

static int _call_trajectory_end_callbacks(PyObject * callbacks, PyObject* args)
{
    PyObject * result;
    PyObject * callback;

    int i = 0;
    int size = PyList_Size(callbacks);
    while (i < size) {
        callback = PyList_GetItem(callbacks, i);

        result = PyObject_CallMethodObjArgs(callback, TRAJECTORY_END, args,
                                            NULL);

        if (result == NULL) {
            return -1; // Failure
        }

        if (PyObject_IsTrue(result) == 0) {
            return 1; // False
        }

        Py_DECREF(result);

        i++;
    }

    return 0; // True
}

static void _call_knock(PyObject * callbacks, int n, int icol, double de)
{

    PyObject * result;
    PyObject * callback;
    PyObject * args = Py_BuildValue("iid", n, icol, de);

    int i = 0;
    int size = PyList_Size(callbacks);
    while (i < size) {
        callback = PyList_GetItem(callbacks, i);

        result = PyObject_CallMethodObjArgs(callback, KNOCK, args, NULL);
        if (result != NULL) {
            Py_DECREF(result);
        }

        i++;
    }

    Py_DECREF(args);
}

////////////////////////////////////////////////////////////////////////////////
// New type structure
////////////////////////////////////////////////////////////////////////////////

typedef struct
{
    PyObject_HEAD
} wrapper_TrackObject;

typedef struct
{
    PyObject_HEAD
} wrapper_RSeedObject;

typedef struct
{
    PyObject_HEAD
} wrapper_SimParObject;

typedef struct
{
    PyObject_HEAD
} wrapper_IntForcingObject;

////////////////////////////////////////////////////////////////////////////////
// Type methods
////////////////////////////////////////////////////////////////////////////////

static PyObject *
Track_get_energy(wrapper_TrackObject *self, void *closure)
{
    PyObject * ret = Py_BuildValue("d", track_.e);
    Py_INCREF(ret);
    return ret;
}

static int Track_set_energy(wrapper_TrackObject *self, PyObject *value,
                            void *closure)
{
    if (!PyFloat_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "Energy must be a float");
        return -1;
    }

    track_.e = PyFloat_AsDouble(value);
    return 0;
}

static PyObject*
Track_get_position(wrapper_TrackObject* self, void *closure)
{
    PyObject * ret = Py_BuildValue("ddd", track_.x, track_.y, track_.z);
    Py_INCREF(ret);
    return ret;
}

static int Track_set_position(wrapper_TrackObject *self, PyObject *value,
                              void *closure)
{
    double x, y, z;

    if (!PyArg_ParseTuple(value, "ddd", &x, &y, &z)) {
        PyErr_SetString(PyExc_TypeError,
                        "Position must be a tuple of 3 floats");
        return -1;
    }

    track_.x = x;
    track_.y = y;
    track_.z = z;

    return 0;
}

static PyObject*
Track_get_direction(wrapper_TrackObject* self, void *closure)
{
    PyObject * ret = Py_BuildValue("ddd", track_.u, track_.v, track_.w);
    Py_INCREF(ret);
    return ret;
}

static int Track_set_direction(wrapper_TrackObject *self, PyObject *value,
                               void *closure)
{
    double u, v, w;

    if (!PyArg_ParseTuple(value, "ddd", &u, &v, &w)) {
        PyErr_SetString(PyExc_TypeError,
                        "Position must be a tuple of 3 floats");
        return -1;
    }

    track_.u = u;
    track_.v = v;
    track_.w = w;

    return 0;
}

static PyObject*
Track_get_weight(wrapper_TrackObject* self, void *closure)
{
    PyObject * ret = Py_BuildValue("d", track_.wght);
    Py_INCREF(ret);
    return ret;
}

static int Track_set_weight(wrapper_TrackObject *self, PyObject *value,
                            void *closure)
{

    if (!PyFloat_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "Weight must be a float");
        return -1;
    }

    track_.wght = PyFloat_AsDouble(value);
    return 0;
}

static PyObject*
Track_get_particle(wrapper_TrackObject* self, void *closure)
{
    PyObject * ret = Py_BuildValue("i", track_.kpar);
    Py_INCREF(ret);
    return ret;
}

static int Track_set_particle(wrapper_TrackObject *self, PyObject *value,
                              void *closure)
{
    if (!PyInt_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "Particle must be an integer");
        return -1;
    }

    track_.kpar = (int) PyInt_AsLong(value);
    return 0;
}

static PyObject*
Track_get_body(wrapper_TrackObject* self, void *closure)
{
    PyObject * ret = Py_BuildValue("i", track_.ibody);
    Py_INCREF(ret);
    return ret;
}

static int Track_set_body(wrapper_TrackObject *self, PyObject *value,
                          void *closure)
{
    if (!PyInt_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "Body must be an integer");
        return -1;
    }

    track_.ibody = (int) PyInt_AsLong(value);
    return 0;
}

static PyObject*
Track_get_material(wrapper_TrackObject* self, void *closure)
{
    PyObject * ret = Py_BuildValue("i", track_.mat);
    Py_INCREF(ret);
    return ret;
}

static int Track_set_material(wrapper_TrackObject *self, PyObject *value,
                              void *closure)
{
    if (!PyInt_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "Material must be an integer");
        return -1;
    }

    track_.mat = (int) PyInt_AsLong(value);
    return 0;
}

static PyObject*
Track_get_labels(wrapper_TrackObject* self, void *closure)
{
    PyObject * ret = Py_BuildValue("iiiii", track_.ilb[0], track_.ilb[1],
                                   track_.ilb[2], track_.ilb[3],
                                   track_.ilb[4]);
    Py_INCREF(ret);
    return ret;
}
static int Track_set_labels(wrapper_TrackObject *self, PyObject *value,
                            void *closure)
{
    int ilb0, ilb1, ilb2, ilb3, ilb4;

    if (!PyArg_ParseTuple(value, "iiiii", &ilb0, &ilb1, &ilb2, &ilb3, &ilb4)) {
        PyErr_SetString(PyExc_TypeError,
                        "Labels must be a tuple of 5 integers");
        return -1;
    }

    track_.ilb[0] = ilb0;
    track_.ilb[1] = ilb1;
    track_.ilb[2] = ilb2;
    track_.ilb[3] = ilb3;
    track_.ilb[4] = ilb4;
    return 0;
}

static PyObject*
RSeed_get_seed1(wrapper_RSeedObject* self, void *closure)
{
    PyObject * ret = Py_BuildValue("i", rseed_.seed1);
    Py_INCREF(ret);
    return ret;
}
static int RSeed_set_seed1(wrapper_RSeedObject *self, PyObject *value,
                           void *closure)
{
    if (!PyInt_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "Seed must be an integer");
        return -1;
    }

    rseed_.seed1 = (int) PyInt_AsLong(value);
    return 0;
}

static PyObject*
RSeed_get_seed2(wrapper_RSeedObject* self, void *closure)
{
    PyObject * ret = Py_BuildValue("i", rseed_.seed2);
    Py_INCREF(ret);
    return ret;
}
static int RSeed_set_seed2(wrapper_RSeedObject *self, PyObject *value,
                           void *closure)
{
    if (!PyInt_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "Seed must be an integer");
        return -1;
    }

    rseed_.seed2 = (int) PyInt_AsLong(value);
    return 0;
}

static PyObject*
SimPar_get_absorption_energies(wrapper_SimParObject* self, PyObject* args)
{
    int mat;

    if (!PyArg_ParseTuple(args, "i", &mat))
        return NULL;

    return Py_BuildValue("ddd", csimpa_.eabs[mat][0], csimpa_.eabs[mat][1],
                         csimpa_.eabs[mat][2]);
}

static PyObject*
SimPar_set_absorption_energies(wrapper_SimParObject *self, PyObject *args,
                               PyObject *kw)
{
    int mat;
    double eabs0, eabs1, eabs2 = -1.0;

    static char *kwlist[] =
    { "material", "el", "ph", "po", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kw, "i|ddd", kwlist, &mat, &eabs0,
                                     &eabs1, &eabs2))
        return NULL;

    if (eabs0 >= 0.0)
        csimpa_.eabs[mat][0] = eabs0;
    if (eabs1 >= 0.0)
        csimpa_.eabs[mat][1] = eabs1;
    if (eabs2 >= 0.0)
        csimpa_.eabs[mat][2] = eabs2;

    Py_RETURN_NONE;
}

static PyObject*
SimPar_get_constants(wrapper_SimParObject* self, PyObject* args)
{
    int mat;

    if (!PyArg_ParseTuple(args, "i", &mat))
        return NULL;

    return Py_BuildValue("dd", csimpa_.c1[mat], csimpa_.c2[mat]);
}

static PyObject*
SimPar_set_constants(wrapper_SimParObject *self, PyObject *args, PyObject *kw)
{
    int mat;
    double c1, c2 = -1.0;

    static char *kwlist[] =
    { "material", "c1", "c2", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kw, "i|dd", kwlist, &mat, &c1, &c2))
        return NULL;

    if (c1 >= 0.0)
        csimpa_.c1[mat] = c1;
    if (c2 >= 0.0)
        csimpa_.c2[mat] = c2;

    Py_RETURN_NONE;
}

static PyObject*
SimPar_get_cutoffs(wrapper_SimParObject* self, PyObject* args)
{
    int mat;

    if (!PyArg_ParseTuple(args, "i", &mat))
        return NULL;

    return Py_BuildValue("dd", csimpa_.wcc[mat], csimpa_.wcr[mat]);
}

static PyObject*
SimPar_set_cutoffs(wrapper_SimParObject *self, PyObject *args, PyObject *kw)
{
    int mat;
    double wcc, wcr = -1.0;

    static char *kwlist[] =
    { "material", "wcc", "wcr", NULL };

    if (!PyArg_ParseTupleAndKeywords(args, kw, "i|dd", kwlist, &mat, &wcc,
                                     &wcr))
        return NULL;

    if (wcc >= 0.0)
        csimpa_.wcc[mat] = wcc;
    if (wcr >= 0.0)
        csimpa_.wcr[mat] = wcr;

    Py_RETURN_NONE;
}

static PyObject*
IntForcing_get_force(wrapper_IntForcingObject* self, PyObject* args)
{
    int body, par, col;

    if (!PyArg_ParseTuple(args, "iii", &body, &par, &col))
        return NULL;

    return Py_BuildValue("d", cforce_.force[col][par][body]);
}

static PyObject*
IntForcing_set_force(wrapper_IntForcingObject* self, PyObject* args)
{
    int body, par, col;
    double force;

    if (!PyArg_ParseTuple(args, "iiid", &body, &par, &col, &force))
        return NULL;

    cforce_.force[col][par][body] = force;

    Py_RETURN_NONE;
}

////////////////////////////////////////////////////////////////////////////////
// Type methods and get/setters
////////////////////////////////////////////////////////////////////////////////

static PyGetSetDef Track_getseters[] =
                {
                                { "energy", (getter) Track_get_energy,
                                                (setter) Track_set_energy,
                                                "Particle's energy in eV", NULL },
                                { "position", (getter) Track_get_position,
                                                (setter) Track_set_position,
                                                "Particle's position in cm",
                                                NULL },
                                {
                                                "direction",
                                                (getter) Track_get_direction,
                                                (setter) Track_set_direction,
                                                "Particle's direction (direction cosines of the direction of movement)",
                                                NULL },
                                {
                                                "weight",
                                                (getter) Track_get_weight,
                                                (setter) Track_set_weight,
                                                "Particle's weight when variance reduction is used",
                                                NULL },
                                {
                                                "particle",
                                                (getter) Track_get_particle,
                                                (setter) Track_set_particle,
                                                "Kind of particle (1: electron, 2: photon, 3: positron)",
                                                NULL },
                                {
                                                "body",
                                                (getter) Track_get_body,
                                                (setter) Track_set_body,
                                                "Index of the body in which the particle is located (first body = 1)",
                                                NULL },
                                {
                                                "material",
                                                (getter) Track_get_material,
                                                (setter) Track_set_material,
                                                "Index of the material in which the particle is located (first material = 1)",
                                                NULL },
                                { "labels", (getter) Track_get_labels,
                                                (setter) Track_set_labels,
                                                "Labels of the particle", NULL },
                                { NULL } /* Sentinel */
                };

static PyGetSetDef RSeed_getseters[] =
{
{ "seed1", (getter) RSeed_get_seed1, (setter) RSeed_set_seed1, "First seed",
                NULL },
{ "seed2", (getter) RSeed_get_seed2, (setter) RSeed_set_seed2, "Second seed",
                NULL },
{ NULL } /* Sentinel */
};

static PyMethodDef SimPar_methods[] =
                {
                                {
                                                "get_absorption_energies",
                                                (PyCFunction) SimPar_get_absorption_energies,
                                                METH_VARARGS,
                                                "Returns absorption energies of electrons, photons and positrons of the specified material" },
                                {
                                                "set_absorption_energies",
                                                (PyCFunction) SimPar_set_absorption_energies,
                                                METH_VARARGS | METH_KEYWORDS,
                                                "Sets absorption energies of electrons, photons and positrons of the specified material" },
                                {
                                                "get_constants",
                                                (PyCFunction) SimPar_get_constants,
                                                METH_VARARGS,
                                                "Returns elastic scattering coefficients (C1 and C2) for the specified material" },
                                {
                                                "set_constants",
                                                (PyCFunction) SimPar_set_constants,
                                                METH_VARARGS | METH_KEYWORDS,
                                                "Sets elastic scattering coefficients (C1 and C2)  for the specified material" },
                                {
                                                "get_cutoffs",
                                                (PyCFunction) SimPar_get_cutoffs,
                                                METH_VARARGS,
                                                "Returns cutoff energies (WCC and WCR)  for the specified material" },
                                {
                                                "set_cutoffs",
                                                (PyCFunction) SimPar_set_cutoffs,
                                                METH_VARARGS | METH_KEYWORDS,
                                                "Sets cutoff energies (WCC and WCR)  for the specified material" },
                                { NULL } /* Sentinel */
                };

static PyMethodDef IntForcing_methods[] =
                {
                                {
                                                "get_force",
                                                (PyCFunction) IntForcing_get_force,
                                                METH_VARARGS,
                                                "Returns the forcing factor for the specified body, particle and collision type" },
                                {
                                                "set_force",
                                                (PyCFunction) IntForcing_set_force,
                                                METH_VARARGS,
                                                "Sets the forcing factor for the specified body, particle and collision type" },
                                { NULL } /* Sentinel */
                };

////////////////////////////////////////////////////////////////////////////////
// Type definitions
////////////////////////////////////////////////////////////////////////////////

static PyTypeObject wrapper_TrackType =
{ PyObject_HEAD_INIT(NULL) 0, /*ob_size*/
"wrapper.track", /*tp_name*/
sizeof(wrapper_TrackObject), /*tp_basicsize*/
0, /*tp_itemsize*/
0, /*tp_dealloc*/
0, /*tp_print*/
0, /*tp_getattr*/
0, /*tp_setattr*/
0, /*tp_compare*/
0, /*tp_repr*/
0, /*tp_as_number*/
0, /*tp_as_sequence*/
0, /*tp_as_mapping*/
0, /*tp_hash */
0, /*tp_call*/
0, /*tp_str*/
0, /*tp_getattro*/
0, /*tp_setattro*/
0, /*tp_as_buffer*/
Py_TPFLAGS_DEFAULT, /*tp_flags*/
"Access TRACK common block of PENELOPE", /* tp_doc */
0, /* tp_traverse */
0, /* tp_clear */
0, /* tp_richcompare */
0, /* tp_weaklistoffset */
0, /* tp_iter */
0, /* tp_iternext */
0, /* tp_methods */
0, /* tp_members */
Track_getseters, /* tp_getset */
};

static PyTypeObject wrapper_RSeedType =
{ PyObject_HEAD_INIT(NULL) 0, /*ob_size*/
"wrapper.rseed", /*tp_name*/
sizeof(wrapper_RSeedObject), /*tp_basicsize*/
0, /*tp_itemsize*/
0, /*tp_dealloc*/
0, /*tp_print*/
0, /*tp_getattr*/
0, /*tp_setattr*/
0, /*tp_compare*/
0, /*tp_repr*/
0, /*tp_as_number*/
0, /*tp_as_sequence*/
0, /*tp_as_mapping*/
0, /*tp_hash */
0, /*tp_call*/
0, /*tp_str*/
0, /*tp_getattro*/
0, /*tp_setattro*/
0, /*tp_as_buffer*/
Py_TPFLAGS_DEFAULT, /*tp_flags*/
"Access random seeds", /* tp_doc */
0, /* tp_traverse */
0, /* tp_clear */
0, /* tp_richcompare */
0, /* tp_weaklistoffset */
0, /* tp_iter */
0, /* tp_iternext */
0, /* tp_methods */
0, /* tp_members */
RSeed_getseters, /* tp_getset */
};

static PyTypeObject wrapper_SimParType =
{ PyObject_HEAD_INIT(NULL) 0, /*ob_size*/
"wrapper.simpar", /*tp_name*/
sizeof(wrapper_SimParObject), /*tp_basicsize*/
0, /*tp_itemsize*/
0, /*tp_dealloc*/
0, /*tp_print*/
0, /*tp_getattr*/
0, /*tp_setattr*/
0, /*tp_compare*/
0, /*tp_repr*/
0, /*tp_as_number*/
0, /*tp_as_sequence*/
0, /*tp_as_mapping*/
0, /*tp_hash */
0, /*tp_call*/
0, /*tp_str*/
0, /*tp_getattro*/
0, /*tp_setattro*/
0, /*tp_as_buffer*/
Py_TPFLAGS_DEFAULT, /*tp_flags*/
"Access simulation parameters", /* tp_doc */
0, /* tp_traverse */
0, /* tp_clear */
0, /* tp_richcompare */
0, /* tp_weaklistoffset */
0, /* tp_iter */
0, /* tp_iternext */
SimPar_methods, /* tp_methods */
0, /* tp_members */
0, /* tp_getset */
};

static PyTypeObject wrapper_IntForcingType =
{ PyObject_HEAD_INIT(NULL) 0, /*ob_size*/
"wrapper.intforce", /*tp_name*/
sizeof(wrapper_IntForcingObject), /*tp_basicsize*/
0, /*tp_itemsize*/
0, /*tp_dealloc*/
0, /*tp_print*/
0, /*tp_getattr*/
0, /*tp_setattr*/
0, /*tp_compare*/
0, /*tp_repr*/
0, /*tp_as_number*/
0, /*tp_as_sequence*/
0, /*tp_as_mapping*/
0, /*tp_hash */
0, /*tp_call*/
0, /*tp_str*/
0, /*tp_getattro*/
0, /*tp_setattro*/
0, /*tp_as_buffer*/
Py_TPFLAGS_DEFAULT, /*tp_flags*/
"Access interaction forcing values", /* tp_doc */
0, /* tp_traverse */
0, /* tp_clear */
0, /* tp_richcompare */
0, /* tp_weaklistoffset */
0, /* tp_iter */
0, /* tp_iternext */
IntForcing_methods, /* tp_methods */
0, /* tp_members */
0, /* tp_getset */
};

////////////////////////////////////////////////////////////////////////////////
// Module functions
////////////////////////////////////////////////////////////////////////////////

static PyObject*
peinit(PyObject* self, PyObject* args)
{
    double emax; // Maximum energy
    PyObject * listMaterials; // list of materials' filename
    const char * output; // Output file

    if (!PyArg_ParseTuple(args, "dO!s", &emax, &PyList_Type, &listMaterials,
                          &output))
        return NULL;

    // Parse materials' filename
    int nmat = PyList_Size(listMaterials);
    char materials[10][FILEPATH_MAX_LENGTH];

    int i = 0;
    PyObject * strObj;
    int length;
    char *str;
    char material[FILEPATH_MAX_LENGTH];
    while (i < nmat) {
        strObj = PyList_GetItem(listMaterials, i);
        PyString_AsStringAndSize(strObj, &str, &length);

        if (_check_filepath_length(str) != 0)
            return NULL;

        _strcopyfill(str, length, material, FILEPATH_MAX_LENGTH, ' ');
        strcpy(materials[i], material);

        i++;
    }

    int info = 1;
    int iwr = 15;
    if (_open_fortran_file(output, iwr) != 0)
        return NULL;

    time0_(); // Reset timer
    peinit_(&emax, &nmat, &iwr, &info, &materials);

    _close_fortran_file(iwr);

    Py_RETURN_NONE;
}

static PyObject*
geomin(PyObject* self, PyObject* args)
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
static PyObject*
create_material(PyObject* self, PyObject* args)
{
    PyObject * composition;
    double rho;
    const char * name;
    const char * filepath;

    if (!PyArg_ParseTuple(args, "O!dss", &PyDict_Type, &composition, &rho,
                          &name, &filepath))
        return NULL;

    // Extract atomic number and weight fraction from composition dictionary
    int zs[30];
    double wfs[30];

    int nelem = PyDict_Size(composition);
    PyObject * keys = PyDict_Keys(composition);
    PyObject * values = PyDict_Values(composition);

    int i = 0;
    while (i < nelem) {
        zs[i] = PyInt_AsLong(PyList_GetItem(keys, i));
        wfs[i] = PyFloat_AsDouble(PyList_GetItem(values, i));
        i++;
    }

    // Reformat name
    char name_[62];
    _strcopyfill(name, strlen(name), name_, 62, ' ');

    // Create material with PENELOPE
    int iwr = 7;
    if (_open_fortran_file(filepath, iwr) != 0)
        return NULL;

    pemats_(&nelem, &zs, &wfs, &rho, &name_, &iwr);

    _close_fortran_file(iwr);

    Py_RETURN_NONE;
}

static PyObject*
run(PyObject* self, PyObject* args)
{
    ////////////////////////////////////////////////////////////////////////////
    // Parse arguments from Python
    ////////////////////////////////////////////////////////////////////////////

    double ntot;
    double emax;
    int x0, y0, z0, u0, v0, w0;
    double diameter, aperture;
    PyObject * pydsmaxs;
    PyObject * wghts;
    int seed1, seed2;
    PyObject * callbacks;

    if (!PyArg_ParseTuple(args, "ddddddddddO!O!ii|O!", &ntot, &emax, &x0, &y0,
                          &z0, &u0, &v0, &w0, &diameter, &aperture,
                          &PyList_Type, &pydsmaxs, &PyList_Type, &wghts,
                          &seed1, &seed2, &PyList_Type, &callbacks))
        return NULL;

    ////////////////////////////////////////////////////////////////////////////
    // Convert arguments to simulation variables
    ////////////////////////////////////////////////////////////////////////////

    // Maximum step length
    int bodyCount = PyList_Size(pydsmaxs);
    double * dsmaxs = (double *) malloc(sizeof(double) * bodyCount);

    int i = 0;
    while (i < bodyCount) {
        dsmaxs[i] = PyFloat_AsDouble(PyList_GetItem(pydsmaxs, i));
        i++;
    }

    // Interaction forcing
    int ** forcing = (int **) malloc(sizeof(int) * bodyCount);
    double ** wghtlow = (double **) malloc(sizeof(double*) * bodyCount);
    double ** wghthigh = (double **) malloc(sizeof(double*) * bodyCount);

    i = 0;
    while (i < bodyCount) {
        forcing[i] = (int*) malloc(2 * sizeof(int));
        wghtlow[i] = (double*) malloc(2 * sizeof(double));
        wghthigh[i] = (double*) malloc(2 * sizeof(double));

        forcing[i][0] = 0;
        wghtlow[i][0] = 0.0;
        wghthigh[i][0] = 1.0e6;
        forcing[i][1] = 0;
        wghtlow[i][1] = 0.0;
        wghthigh[i][1] = 1.0e6;

        i++;
    }

    int ibody, kpar;
    int wghtCount = PyList_Size(wghts);
    i = 0;
    while (i < wghtCount) {
        ibody = PyInt_AsLong(PyList_GetItem(wghts, 0));
        kpar = PyInt_AsLong(PyList_GetItem(wghts, 1));

        forcing[ibody][kpar] = 1;
        wghtlow[ibody][kpar] = PyFloat_AsDouble(PyTuple_GetItem(wghts, 2));
        wghthigh[ibody][kpar] = PyFloat_AsDouble(PyTuple_GetItem(wghts, 3));

        i++;
    }

    // Random seeds
    rseed_.seed1 = seed1;
    rseed_.seed2 = seed2;

    ////////////////////////////////////////////////////////////////////////////
    // Initialize simulation variables
    ////////////////////////////////////////////////////////////////////////////

    double n = -1.0;
    PyObject * callback_args;
    double ds, dsmax, dsef, de;
    int ncross, icol, left;

    int first_surface = -1;
    int forcing_active = 0;

    ////////////////////////////////////////////////////////////////////////////
    // Start shower
    ////////////////////////////////////////////////////////////////////////////

    while (n < ntot) {
        // New shower
        n = n + 1.0;
        callback_args = Py_BuildValue("i", n);

        // Shower simulation starts here.
        cleans_();

        track_.e = emax;
        track_.x = x0; // FIXME
        track_.y = y0; // FIXME
        track_.z = z0; // FIXME
        track_.u = u0;
        track_.v = v0;
        track_.w = w0;
        track_.wght = 1.0;
        track_.kpar = 1;
        track_.ilb[0] = 1;
        track_.ilb[1] = 0;
        track_.ilb[2] = 0;
        track_.ilb[3] = 0;
        track_.ilb[4] = 1;

        locate_();

        if (track_.mat == 0) {
            ds = 1.0e30;
            step_(&ds, &dsef, &ncross);

            if (track_.mat == 0) // The particle does not enter the system.
                goto l104;

            first_surface = qtrack_.kslast;
        }

        // Track simulation begins here.
        l102:

        start_();

        l103:

        dsmax = dsmaxs[track_.ibody];
        if (forcing[track_.kpar][track_.ibody] == 1
                        && track_.wght >= wghtlow[track_.kpar][track_.ibody]
                        && track_.wght <= wghthigh[track_.kpar][track_.ibody]) {
            jumpf_(&dsmax, &ds);
            forcing_active = 1;
        }
        else {
            jump_(&dsmax, &ds);
            forcing_active = 0;
        }

        step_(&ds, &dsef, &ncross);

        // Exit the sample
        if (track_.mat == 0) {
            switch (track_.kpar) {
            case 1:
                if (qtrack_.kslast == first_surface) {
                    _call_callbacks(callbacks, BACKSCATTERED_ELECTRON,
                                    callback_args);
                }
                else {
                    _call_callbacks(callbacks, TRANSMITTED_ELECTRON,
                                    callback_args);
                }
                break;
            case 2:
                _call_callbacks(callbacks, EXIT_PHOTON, callback_args);
                break;
            }
            goto l104;
        }

        // Particle crossed an interface
        if (ncross > 0)
            goto l102;

        // Knock
        if (forcing_active == 1) {
            knockf_(&de, &icol);
        }
        else {
            knock_(&de, &icol);
        }

        // Check if particle is absorbed
        if (track_.e < csimpa_.eabs[track_.mat - 1][track_.kpar - 1]) {
            switch (track_.kpar) {
            case 1:
                _call_callbacks(callbacks, ABSORBED_ELECTRON, callback_args);
                break;
            case 2:
                _call_callbacks(callbacks, ABSORBED_PHOTON, callback_args);
                break;
            }
            goto l104;
        }

        goto l103;
        // The simulation of the track ends here.

        // Any secondary left?
        l104:

        secpar_(&left);

        if (left > 0) {
            if (track_.ilb[0] > 4) {
                goto l104;
            }

            // Set ILB(5) for 2nd-generation photons, to separate fluorescence
            // from characteristic x rays and from the bremss continuum.
            if (track_.kpar == 2 && track_.ilb[4] == 1) {
                switch (track_.ilb[2]) {
                case 5: // Characteristic x-ray from a shell ionisation.
                    track_.ilb[4] = 2;
                    break;
                case 4: // Bremsstrahlung photon.
                    track_.ilb[4] = 3;
                    break;
                }
            }

            switch (track_.kpar) {
            case 1:
                _call_callbacks(callbacks, GENERATED_ELECTRON, callback_args);
                break;
            case 2:
                _call_callbacks(callbacks, GENERATED_PHOTON, callback_args);
                break;
            }

            goto l102;
        }

        // Special check to see if the simulation shall continue
        if (_call_trajectory_end_callbacks(callbacks, callback_args) != 0)
            break;

        Py_DECREF(callback_args);
    }

    ////////////////////////////////////////////////////////////////////////////
    // Free memory
    ////////////////////////////////////////////////////////////////////////////

    free(dsmaxs);
//
    i = 0;
    while (i < bodyCount) {
        free(forcing[i]);
        free(wghtlow[i]);
        free(wghthigh[i]);
        i++;
    }
    free(forcing);
    free(wghtlow);
    free(wghthigh);

    return Py_BuildValue("d", n + 1);
}

static PyObject*
run_advanced(PyObject* self, PyObject* args)
{
    ////////////////////////////////////////////////////////////////////////////
    // Parse arguments from Python
    ////////////////////////////////////////////////////////////////////////////

    double ntot;
    double emax;
    int x0, y0, z0, u0, v0, w0;
    double diameter, aperture;
    PyObject * pydsmaxs;
    PyObject * wghts;
    int seed1, seed2;
    PyObject * callbacks;

    if (!PyArg_ParseTuple(args, "ddddddddddO!O!ii|O!", &ntot, &emax, &x0, &y0,
                          &z0, &u0, &v0, &w0, &diameter, &aperture,
                          &PyList_Type, &pydsmaxs, &PyList_Type, &wghts,
                          &seed1, &seed2, &PyList_Type, &callbacks))
        return NULL;

    ////////////////////////////////////////////////////////////////////////////
    // Convert arguments to simulation variables
    ////////////////////////////////////////////////////////////////////////////

    // Maximum step length
    int bodyCount = PyList_Size(pydsmaxs);
    double * dsmaxs = (double *) malloc(sizeof(double) * bodyCount);

    int i = 0;
    while (i < bodyCount) {
        dsmaxs[i] = PyFloat_AsDouble(PyList_GetItem(pydsmaxs, i));
        i++;
    }

    // Interaction forcing
    int ** forcing = (int **) malloc(sizeof(int) * bodyCount);
    double ** wghtlow = (double **) malloc(sizeof(double*) * bodyCount);
    double ** wghthigh = (double **) malloc(sizeof(double*) * bodyCount);

    i = 0;
    while (i < bodyCount) {
        forcing[i] = (int*) malloc(2 * sizeof(int));
        wghtlow[i] = (double*) malloc(2 * sizeof(double));
        wghthigh[i] = (double*) malloc(2 * sizeof(double));

        forcing[i][0] = 0;
        wghtlow[i][0] = 0.0;
        wghthigh[i][0] = 1.0e6;
        forcing[i][1] = 0;
        wghtlow[i][1] = 0.0;
        wghthigh[i][1] = 1.0e6;

        i++;
    }

    int ibody, kpar;
    int wghtCount = PyList_Size(wghts);
    i = 0;
    while (i < wghtCount) {
        ibody = PyInt_AsLong(PyList_GetItem(wghts, 0));
        kpar = PyInt_AsLong(PyList_GetItem(wghts, 1));

        forcing[ibody][kpar] = 1;
        wghtlow[ibody][kpar] = PyFloat_AsDouble(PyTuple_GetItem(wghts, 2));
        wghthigh[ibody][kpar] = PyFloat_AsDouble(PyTuple_GetItem(wghts, 3));

        i++;
    }

    // Random seeds
    rseed_.seed1 = seed1;
    rseed_.seed2 = seed2;

    ////////////////////////////////////////////////////////////////////////////
    // Initialize simulation variables
    ////////////////////////////////////////////////////////////////////////////

    double n = -1.0;
    PyObject * callback_args;
    double ds, dsmax, dsef, de;
    int ncross, icol, left;

    int first_surface = -1;
    int forcing_active = 0;

    ////////////////////////////////////////////////////////////////////////////
    // Start shower
    ////////////////////////////////////////////////////////////////////////////

    while (n < ntot) {
        // New shower
        n = n + 1.0;
        callback_args = Py_BuildValue("i", n);

        // Shower simulation starts here.
        cleans_();

        track_.e = emax;
        track_.x = x0; // FIXME
        track_.y = y0; // FIXME
        track_.z = z0; // FIXME
        track_.u = u0;
        track_.v = v0;
        track_.w = w0;
        track_.wght = 1.0;
        track_.kpar = 1;
        track_.ilb[0] = 1;
        track_.ilb[1] = 0;
        track_.ilb[2] = 0;
        track_.ilb[3] = 0;
        track_.ilb[4] = 1;

        locate_();

        if (track_.mat == 0) {
            ds = 1.0e30;
            step_(&ds, &dsef, &ncross);

            if (track_.mat == 0) // The particle does not enter the system.
                goto l104;

            first_surface = qtrack_.kslast;
        }

        // Track simulation begins here.
        l102:

        start_();

        l103:

        dsmax = dsmaxs[track_.ibody];
        if (forcing[track_.kpar][track_.ibody] == 1
                        && track_.wght >= wghtlow[track_.kpar][track_.ibody]
                        && track_.wght <= wghthigh[track_.kpar][track_.ibody]) {
            jumpf_(&dsmax, &ds);
            forcing_active = 1;
        }
        else {
            jump_(&dsmax, &ds);
            forcing_active = 0;
        }

        step_(&ds, &dsef, &ncross);

        // Exit the sample
        if (track_.mat == 0) {
            switch (track_.kpar) {
            case 1:
                if (qtrack_.kslast == first_surface) {
                    _call_callbacks(callbacks, BACKSCATTERED_ELECTRON,
                                    callback_args);
                }
                else {
                    _call_callbacks(callbacks, TRANSMITTED_ELECTRON,
                                    callback_args);
                }
                break;
            case 2:
                _call_callbacks(callbacks, EXIT_PHOTON, callback_args);
                break;
            }
            goto l104;
        }

        // Particle crossed an interface
        if (ncross > 0)
            goto l102;

        // Knock
        if (forcing_active == 1) {
            knockf_(&de, &icol);
        }
        else {
            knock_(&de, &icol);
        }

        // Difference with simple run
        _call_knock(callbacks, n, icol, de);

        // Check if particle is absorbed
        if (track_.e < csimpa_.eabs[track_.mat - 1][track_.kpar - 1]) {
            switch (track_.kpar) {
            case 1:
                _call_callbacks(callbacks, ABSORBED_ELECTRON, callback_args);
                break;
            case 2:
                _call_callbacks(callbacks, ABSORBED_PHOTON, callback_args);
                break;
            }
            goto l104;
        }

        goto l103;
        // The simulation of the track ends here.

        // Any secondary left?
        l104:

        secpar_(&left);

        if (left > 0) {
            if (track_.ilb[0] > 4) {
                goto l104;
            }

            // Set ILB(5) for 2nd-generation photons, to separate fluorescence
            // from characteristic x rays and from the bremss continuum.
            if (track_.kpar == 2 && track_.ilb[4] == 1) {
                switch (track_.ilb[2]) {
                case 5: // Characteristic x-ray from a shell ionisation.
                    track_.ilb[4] = 2;
                    break;
                case 4: // Bremsstrahlung photon.
                    track_.ilb[4] = 3;
                    break;
                }
            }

            switch (track_.kpar) {
            case 1:
                _call_callbacks(callbacks, GENERATED_ELECTRON, callback_args);
                break;
            case 2:
                _call_callbacks(callbacks, GENERATED_PHOTON, callback_args);
                break;
            }

            goto l102;
        }

        // Special check to see if the simulation shall continue
        if (_call_trajectory_end_callbacks(callbacks, callback_args) != 0)
            break;

        Py_DECREF(callback_args);
    }

    ////////////////////////////////////////////////////////////////////////////
    // Free memory
    ////////////////////////////////////////////////////////////////////////////

    free(dsmaxs);
    //
    i = 0;
    while (i < bodyCount) {
        free(forcing[i]);
        free(wghtlow[i]);
        free(wghthigh[i]);
        i++;
    }
    free(forcing);
    free(wghtlow);
    free(wghthigh);

    return Py_BuildValue("d", n + 1);
}

static PyObject*
prange(PyObject* self, PyObject* args)
{
    double e;
    int kpar, mat;

    if (!PyArg_ParseTuple(args, "dii", &e, &kpar, &mat))
        return NULL;

    return Py_BuildValue("d", prange_(&e, &kpar, &mat));
}

static PyObject*
phmfp(PyObject* self, PyObject* args)
{
    double e;
    int kpar, mat, icol;

    if (!PyArg_ParseTuple(args, "diii", &e, &kpar, &mat, &icol))
        return NULL;

    return Py_BuildValue("d", phmfp_(&e, &kpar, &mat, &icol));
}

static PyMethodDef wrapper_methods[] =
                {
                                {
                                                "peinit",
                                                peinit,
                                                METH_VARARGS,
                                                "Initializes simulation routines." },
                                {
                                                "geomin",
                                                geomin,
                                                METH_VARARGS,
                                                "Initializes geometry. Returns the number of materials and bodies in the geometry." },
                                {
                                                "create_material",
                                                create_material,
                                                METH_VARARGS,
                                                "Creates a material. Arguments: Composition dictionary (key: atomic number, value: weight fraction), density, name and filename." },
                                {
                                                "run",
                                                run,
                                                METH_VARARGS,
                                                "Run a simulation. Arguments: total number of showers, maximum energy, seed1, seed2, list of callbacks. Returns the number of simulated showers." },
                                {
                                                "run_advanced",
                                                run_advanced,
                                                METH_VARARGS,
                                                "Run a detailed simulation. Arguments: total number of showers, maximum energy, seed1, seed2, list of callbacks. Returns the number of simulated showers." },
                                {
                                                "prange",
                                                prange,
                                                METH_VARARGS,
                                                "Returns the range (in cm) of a particle type for a given energy and material." },
                                {
                                                "phmfp",
                                                phmfp,
                                                METH_VARARGS,
                                                "Returns the mean free path (in cm) of a type of collision for a given particle type, energy and material." },
                                { NULL } /* Sentinel */
                };

////////////////////////////////////////////////////////////////////////////////
// Initialize module
////////////////////////////////////////////////////////////////////////////////

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC initwrapper(void)
{
    // Initialize callbacks constants
    TRAJECTORY_END = PyString_FromString("trajectory_end");
    Py_INCREF(TRAJECTORY_END);
    KNOCK = PyString_FromString("knock");
    Py_INCREF(KNOCK);

    BACKSCATTERED_ELECTRON = PyString_FromString("backscattered_electron");
    Py_INCREF(BACKSCATTERED_ELECTRON);
    TRANSMITTED_ELECTRON = PyString_FromString("transmitted_electron");
    Py_INCREF(TRANSMITTED_ELECTRON);
    ABSORBED_ELECTRON = PyString_FromString("absorbed_electron");
    Py_INCREF(ABSORBED_ELECTRON);
    EXIT_PHOTON = PyString_FromString("exit_photon");
    Py_INCREF(EXIT_PHOTON);
    GENERATED_ELECTRON = PyString_FromString("generated_electron");
    Py_INCREF(GENERATED_ELECTRON);

    ABSORBED_PHOTON = PyString_FromString("absorbed_photon");
    Py_INCREF(ABSORBED_PHOTON);
    GENERATED_PHOTON = PyString_FromString("generated_photon");
    Py_INCREF(GENERATED_PHOTON);

    // Initialize types
    wrapper_TrackType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&wrapper_TrackType) < 0)
        return;

    wrapper_RSeedType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&wrapper_RSeedType) < 0)
        return;

    wrapper_SimParType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&wrapper_SimParType) < 0)
        return;

    wrapper_IntForcingType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&wrapper_IntForcingType) < 0)
        return;

    // Initialize module
    PyObject* m;
    m = Py_InitModule3("wrapper", wrapper_methods,
                    "Wrapper of PENELOPE functions.");
    if (m == NULL)
        return;

    // Create object for types
    PyObject *track = PyObject_CallObject((PyObject *) &wrapper_TrackType,
                                          NULL);
    Py_INCREF(track);
    PyModule_AddObject(m, "track", track);

    PyObject *rseed = PyObject_CallObject((PyObject *) &wrapper_RSeedType,
                                          NULL);
    Py_INCREF(rseed);
    PyModule_AddObject(m, "rseed", rseed);

    PyObject *simpar = PyObject_CallObject((PyObject *) &wrapper_SimParType,
                                           NULL);
    Py_INCREF(simpar);
    PyModule_AddObject(m, "simpar", simpar);

    PyObject *intforce = PyObject_CallObject(
                    (PyObject *) &wrapper_IntForcingType, NULL);
    Py_INCREF(intforce);
    PyModule_AddObject(m, "intforce", intforce);
}
