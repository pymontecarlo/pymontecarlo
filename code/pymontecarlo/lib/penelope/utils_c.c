#include <Python.h>
#include "utils_c.h"
#include "utils_f.h"

const int FILEPATH_MAX_LENGTH = 4096;

void _strcopyfill(const char * str, int strLength, char * array,
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

int _check_filepath_length(const char * filepath)
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

int _close_fortran_file(int unit)
{
    fclose_(&unit);
    return 0;
}
