.. mosromgr: Python library for managing MOS running orders
.. Copyright 2021 BBC
.. SPDX-License-Identifier: Apache-2.0

==============
mosromgr merge
==============

Merge the provided MOS files

Synopsis
========

.. code-block:: text

    mosromgr merge [-h] [-f [files [files ...]]] [-b bucket] [-p prefix] [-s suffix]
                   [-o outfile] [-i] [-n]

Description
===========

.. program:: mosromgr-merge

.. option:: -f --files [files ...]

    The MOS files to merge

.. option:: -b --bucket-name bucket

    The name of the S3 bucket containing the MOS files

.. option:: -p --prefix prefix

    The file prefix for MOS files in the S3 bucket

.. option:: -s --suffix suffix

    The file suffix for MOS files in the S3 bucket

.. option:: -o --outfile outfile

    Output to a file

.. option:: -i --incomplete

    Allow an incomplete collection

.. option:: -n --non-strict

    Downgrade MOS merge errors to warnings

.. option:: -h, --help

    Show this help message and exit

Usage
=====

Merge local files and store the result in a new file:

.. code-block:: console

    $ mosromgr merge -f *.mos.xml -o FINAL.xml
    ...
    INFO:mosromgr.moscollection:Merging RunningOrderEnd 123499
    INFO:mosromgr.moscollection:Completed merging 99 mos files
    Writing merged running order to FINAL.xml

Merge files in an S3 bucket folder by prefix and store the result in a new file:

.. code-block:: console

    $ mosromgr merge -b my-bucket -p newsnight/20210101/ -o FINAL.xml
    ...
    INFO:mosromgr.moscollection:Merging RunningOrderEnd 123499
    INFO:mosromgr.moscollection:Completed merging 99 mos files
    Writing merged running order to FINAL.xml

.. note::

    Your AWS credentials must be configured to use the S3 method.
    See https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
