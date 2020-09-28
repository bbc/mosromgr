========
mosromgr
========

Python client for managing `MOS`_ running orders.

.. _MOS: http://mosprotocol.com/

The library provides functionality for detecting MOS file types, merging MOS
files into a running order, and providing a "completed" programme including all
additions and changes made between the first message (``roCreate``) and the last
(``roDelete``).

This can be used as a library, using the utilities provided in the package
``mosromgr``, and the command line command ``mosromgr`` can be used to process
either a directory of MOS files, or a folder within an S3 bucket.

There is also an AWS Lambda function provided which merges MOS files in an S3
bucket.

.. image:: images/mos.*
    :target: http://mosprotocol.com/
    :align: center

Table of Contents
=================

.. toctree::
    :maxdepth: 1
    :numbered:

    mostypes
    mosfactory
    moscontainer
    cli
    utils
    exceptions

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Source code
===========

Source code can be found on GitHub at https://github.com/bbc/mosromgr

Contact
=======

Please contact `BBC News Labs Team`_ if you want to get in touch.

.. _BBC News Labs Team: mailto:BBCNewsLabsTeam@bbc.co.uk
