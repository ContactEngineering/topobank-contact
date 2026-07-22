Contact Analysis for TopoBank
==============================

Purpose
-------

This plugin adds the following analysis function to Topobank:

- Contact analysis

For more information, see our `paper`_.

Documentation
-------------

- `Conventions <docs/conventions.md>`_ — geometry and sign conventions,
  x/y orientation, definition of the contact modulus E*, units, and how
  to treat the contact of two rough surfaces (composite roughness).
- `Example script <docs/examples/plot_contact_step.py>`_ — reads a
  ``results.nc`` file from the ZIP download and produces correctly
  labeled plots.

Installation
------------

For production:

.. code-block:: bash

    pip install topobank-contact`

For development:

Clone project, enter project directory and run

.. code-block:: bash

    pip install -e .[dev]

.. _paper: https://doi.org/10.1088/2051-672X/ac860a
