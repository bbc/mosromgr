.. mosromgr: Python library for managing MOS running orders
.. Copyright 2021 BBC
.. SPDX-License-Identifier: Apache-2.0

===============
Getting started
===============

This section shows you how to get started with *mosromgr*.

Installing
==========

Install with pip:

.. code-block:: console

    $ pip install mosromgr

Command line interface check
============================

After installing the module, a simple way to verify it's working is by using the
:doc:`cli/index`. First of all, open a terminal and run the command ``mosromgr``
to be sure it's installed. You should see output like so:

.. code-block:: console

    $ mosromgr
    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit

    commands:
      {help,detect,inspect,merge}
        help                Displays help about the specified command
        detect              Detect the MOS type of one or more files
        inspect             Inspect the contents of a roCreate file
        merge               Merge the given MOS files

Now start by obtaining the MOS files for a single complete programme. In a
terminal window, enter the directory containing the MOS files and run the
command ``mosromgr detect`` on a single roCreate file, for example:

.. code-block:: console

    $ mosromgr detect 123456-roCreate.mos.xml
    123456-roCreate.mos.xml: RunningOrder

The output shows that it's identified the ``roCreate`` file as a
:class:`~mosromgr.mostypes.RunningOrder`. Try it with some other files to check
it can correctly identify a :class:`~mosromgr.mostypes.MosFile` subclass to
represent the file.

Using the module in Python code
===============================

Now you've tested the ready-made command line program is working with your MOS
file, try using the module in some custom Python code.

Open a Python shell and try creating a MOS object from your ``roCreate`` file:

.. code-block:: pycon

    >>> from mosromgr.mostypes import RunningOrder
    >>> ro = RunningOrder.from_file('123456-roCreate.mos.xml')
    >>> ro
    <RunningOrder 123456>

This shows you've successfully loaded a MOS file and created a
:class:`~mosromgr.mostypes.RunningOrder` from it. The output shows the object
representation (``__repr__``) which includes the class name and message ID (this
is from the XML contents, not the filename).

The next page will walk through the functionality provided by the module.
