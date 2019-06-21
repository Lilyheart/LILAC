"""
Sphinx has manual code documentation in sphinx/source/code/secondary.rst which states the following:

.. py:function:: setup

   Builds the fast_dp_calculator cython file into a c file.  To build the c file, enter the following into the command
   line in the same folder as this file:

   .. code-block:: bash

      python fast_dp_setup.py build_ext --inplace

"""
from setuptools import setup
from setuptools import Extension
from Cython.Distutils import build_ext
import numpy


ext_modules = [Extension("fast_dp_calculator", ["fast_dp_calculator.pyx"], extra_compile_args=["-ffast-math"])]

setup(
  name="fast_dp_calculator",
  cmdclass={"build_ext": build_ext},
  ext_modules=ext_modules,
  include_dirs=[numpy.get_include()], install_requires=['matplotlib', 'PySide', 'scipy', 'peakutils', 'numpy', 'pandas']
)
