#include <Python.h>
#include "penelope.h"

////////////////////////////////////////////////////////////////////////////////
// Type structure
////////////////////////////////////////////////////////////////////////////////

typedef struct
{
    PyObject_HEAD
} common_TrackObject;

////////////////////////////////////////////////////////////////////////////////
// Type methods
////////////////////////////////////////////////////////////////////////////////

static PyObject *
Track_get_energy(common_TrackObject *self, void *closure)
{
    PyObject * ret = Py_BuildValue("d", track_.e);
    Py_INCREF(ret);
    return ret;
}

static int Track_set_energy(common_TrackObject *self, PyObject *value,
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
Track_get_position(common_TrackObject* self, void *closure)
{
    PyObject * ret = Py_BuildValue("ddd", track_.x / 100.0, track_.y / 100.0,
                                   track_.z / 100.0);
    Py_INCREF(ret);
    return ret;
}

static int Track_set_position(common_TrackObject *self, PyObject *value,
                              void *closure)
{
    double x, y, z;

    if (!PyArg_ParseTuple(value, "ddd", &x, &y, &z)) {
        PyErr_SetString(PyExc_TypeError,
                        "Position must be a tuple of 3 floats");
        return -1;
    }

    track_.x = x * 100.0;
    track_.y = y * 100.0;
    track_.z = z * 100.0;

    return 0;
}

static PyObject*
Track_get_direction(common_TrackObject* self, void *closure)
{
    PyObject * ret = Py_BuildValue("ddd", track_.u, track_.v, track_.w);
    Py_INCREF(ret);
    return ret;
}

static int Track_set_direction(common_TrackObject *self, PyObject *value,
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
Track_get_weight(common_TrackObject* self, void *closure)
{
    PyObject * ret = Py_BuildValue("d", track_.wght);
    Py_INCREF(ret);
    return ret;
}

static int Track_set_weight(common_TrackObject *self, PyObject *value,
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
Track_get_particle(common_TrackObject* self, void *closure)
{
    PyObject * ret = Py_BuildValue("i", track_.kpar);
    Py_INCREF(ret);
    return ret;
}

static int Track_set_particle(common_TrackObject *self, PyObject *value,
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
Track_get_body(common_TrackObject* self, void *closure)
{
    PyObject * ret = Py_BuildValue("i", track_.ibody);
    Py_INCREF(ret);
    return ret;
}

static int Track_set_body(common_TrackObject *self, PyObject *value,
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
Track_get_material(common_TrackObject* self, void *closure)
{
    PyObject * ret = Py_BuildValue("i", track_.mat);
    Py_INCREF(ret);
    return ret;
}

static int Track_set_material(common_TrackObject *self, PyObject *value,
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
Track_get_labels(common_TrackObject* self, void *closure)
{
    PyObject * ret = Py_BuildValue("iiiii", track_.ilb[0], track_.ilb[1],
                                   track_.ilb[2], track_.ilb[3],
                                   track_.ilb[4]);
    Py_INCREF(ret);
    return ret;
}
static int Track_set_labels(common_TrackObject *self, PyObject *value,
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

////////////////////////////////////////////////////////////////////////////////
// Type methods and get/setters
////////////////////////////////////////////////////////////////////////////////

static PyGetSetDef Track_getseters[] =
                {
                                { "energy", (getter) Track_get_energy,
                                                (setter) Track_set_energy,
                                                "Particle's energy in eV", NULL },
                                {
                                                "position",
                                                (getter) Track_get_position,
                                                (setter) Track_set_position,
                                                "Particle's position in meters",
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

////////////////////////////////////////////////////////////////////////////////
// Type definitions
////////////////////////////////////////////////////////////////////////////////

static PyTypeObject common_TrackType =
{ PyObject_HEAD_INIT(NULL) 0, /*ob_size*/
"common.track", /*tp_name*/
sizeof(common_TrackObject), /*tp_basicsize*/
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

////////////////////////////////////////////////////////////////////////////////
// Module functions
////////////////////////////////////////////////////////////////////////////////

static PyMethodDef common_methods[] =
{
{ NULL } /* Sentinel */
};

////////////////////////////////////////////////////////////////////////////////
// Initialize module
////////////////////////////////////////////////////////////////////////////////

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC initcommon(void)
{
    // Initialize types
    common_TrackType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&common_TrackType) < 0)
        return;

    // Initialize module
    PyObject* m;
    m = Py_InitModule3("common", common_methods, "PENELOPE COMMON functions.");
    if (m == NULL)
        return;

    // Create object for types
    PyObject *track = PyObject_CallObject((PyObject *) &common_TrackType,
                                          NULL);
    Py_INCREF(track);
    PyModule_AddObject(m, "track", track);
}
