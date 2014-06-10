#------------------------------------------------------------------------------
# Console.py
#   Initialization script for cx_Freeze which manipulates the path so that the
# directory in which the executable is found is searched for extensions but
# no other directory is searched. It also sets the attribute sys.frozen so that
# the Win32 extensions behave as expected.
#------------------------------------------------------------------------------

import os
import sys
import zipimport
import glob

sys.frozen = True
sys.path = sys.path[:4]

if sys.platform == 'darwin':
    path = os.path.join(DIR_NAME, 'pypenelopelib') #@UndefinedVariable
    if os.environ.get('DYLD_LIBRARY_PATH') != path:
        os.environ["DYLD_LIBRARY_PATH"] = path
        os.execv(sys.executable, sys.argv)
elif sys.platform == 'win32':
    path = os.path.join(DIR_NAME, 'pypenelopelib') #@UndefinedVariable
    if not os.environ.get('PATH').endswith(path):
        os.environ["PATH"] += ';' + path
        os.execv(sys.executable, sys.argv)

#------------------------------------------------------------------------------
# Modification to automatically load programs
sys.path.extend(glob.glob(os.path.join(DIR_NAME, '*.egg'))) #@UndefinedVariable
sys.path.extend(glob.glob(os.path.expanduser('~/.pymontecarlo/*.egg')))
#------------------------------------------------------------------------------

os.environ["TCL_LIBRARY"] = os.path.join(DIR_NAME, "tcl") #@UndefinedVariable
os.environ["TK_LIBRARY"] = os.path.join(DIR_NAME, "tk") #@UndefinedVariable

m = __import__("__main__")
importer = zipimport.zipimporter(INITSCRIPT_ZIP_FILE_NAME) #@UndefinedVariable
if INITSCRIPT_ZIP_FILE_NAME != SHARED_ZIP_FILE_NAME: #@UndefinedVariable
    moduleName = m.__name__
else:
    name, ext = os.path.splitext(os.path.basename(os.path.normcase(FILE_NAME))) #@UndefinedVariable
    moduleName = "%s__main__" % name
code = importer.get_code(moduleName)
exec(code, m.__dict__)
