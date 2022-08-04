.. mosromgr: Python library for managing MOS running orders
.. Copyright 2021 BBC
.. SPDX-License-Identifier: Apache-2.0

===========
Development
===========

This page contains reference material for those interested in developing and
contributing to the **mosromgr** module.

The project source code is hosted on GitHub at https://github.com/bbc/mosromgr
which also includes the `issue tracker`_.

.. _issue tracker: https://github.com/bbc/mosromgr/issues

Setting up for Development
==========================

1. Clone the repository and enter the directory:

    .. code-block:: console

        $ git clone https://github.com/bbc/mosromgr
        $ cd mosromgr

2. Create a virtual environment e.g. using `virtualenvwrapper`_:

    .. code-block:: console

        $ mkvirtualenv mosromgr

    .. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/

3. Install the project for development:

    .. code-block:: console

        $ make develop

After completing these steps, the library and command line interface will be
available to use within your environment. Any modifications made to the source
code will be automatically reflected within the environment.

Tests
=====

The test suite uses `pytest`_. Tests are organised mirroring the source code.

.. _pytest: https://docs.pytest.org

Running the tests
-----------------

To run the linter, test suite and coverage analysis, activate the environment
and run:

.. code-block:: console

    $ make test

For more control when running tests, run ``pytest`` directly, for example
``pytest -vvxk story`` will run tests with ``story`` in the name (``-k story``)
with verbose output (``-vv``), and stop at the first failure (``-x``).

To run tests on multiple versions of Python, run ``tox`` which will invoke
``make test`` for all versions of Python (included in ``tox.ini``) that you have
installed.

Tests are also automatically run against pull requests using GitHub Actions.

Documentation
=============

The documentation is built using `sphinx`_ using the `diataxis`_ framework.

.. _sphinx: https://www.sphinx-doc.org/
.. _diataxis: https://diataxis.fr/

Building the documentation
--------------------------

To build the documentation, activate the environment and run:

.. code-block:: console

    $ make doc

This will generate the required diagrams and build the HTML docs which will be
located in ``docs/build/html``. Serve them with the command:

.. code-block:: console

    $ make doc-serve

You'll now be able to open the docs on your browser at
``http://localhost:8000/``.
