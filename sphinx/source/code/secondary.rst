Secondary Code
==============

scan module
-----------

.. automodule:: scan
    :members:
    :undoc-members:
    :show-inheritance:

graphs module
-------------

.. automodule:: graphs
    :members:
    :undoc-members:
    :show-inheritance:

helper_functions module
-----------------------

.. automodule:: helper_functions
    :members:
    :undoc-members:
    :show-inheritance:
    :exclude-members: _EmptyClass

fast_dp_calculator module
-------------------------

.. automodule:: fast_dp_calculator
    :members:
    :undoc-members:
    :show-inheritance:
    :exclude-members: rand, randn

fast_dp_setup module
--------------------

.. py:function:: setup

   Builds the fast_dp_calculator cython file into a c file.  To build the c file, enter the following into the command
   line in the same folder as this file:

   .. code-block:: bash

      python fast_dp_setup.py build_ext --inplace
