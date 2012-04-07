
void _strcopyfill(const char * str, int strLength, char * array,
                         int arrayLength, char pad);

int _check_filepath_length(const char * filepath);

int _open_fortran_file(const char * filepath, int unit);

int _close_fortran_file(int unit);
