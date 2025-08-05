from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("backend/effects/VintageOverdrive.pyx")
)import numpy
setup(
    ext_modules=cythonize("backend/effects/VintageOverdrive.pyx"),
    include_dirs=[numpy.get_include()]
)