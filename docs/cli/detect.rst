.. mosromgr: Python library for managing MOS running orders
.. Copyright 2021 BBC
.. SPDX-License-Identifier: Apache-2.0

===============
mosromgr detect
===============

Detect the MOS type of one or more files

Synopsis
========

.. code-block:: text

    mosromgr detect [-h] [-f [files [files ...]]] [-b bucket] [-p prefix] [-s suffix] [-k key]

Description
===========

.. program:: mosromgr-detect

.. option:: -f --files [files ...]

    The MOS files to detect

.. option:: -b --bucket-name bucket

    The name of the S3 bucket containing the MOS files

.. option:: -p --prefix prefix

    The prefix for MOS files in the S3 bucket

.. option:: -s --suffix suffix

    The suffix for MOS files in the S3 bucket

.. option:: -k --key key

    The file key for a MOS file in the S3 bucket

.. option:: -h, --help

    Show this help message and exit

Usage
=====

Detect the type of a MOS file:

.. code-block:: console

    $ mosromgr detect -f 123456-roCreate.mos.xml
    123456-roCreate.mos.xml: RunningOrder

Multiple files can be provided as arguments:

.. code-block:: console

    $ mosromgr detect -f 123456-roCreate.mos.xml 123457-roStorySend.mos.xml
    123456-roCreate.mos.xml: RunningOrder
    123457-roStorySend.mos.xml: StorySend

Wildcards can also be used:

.. code-block:: console

    $ mosromgr detect *
    123456-roCreate.mos.xml: RunningOrder
    123457-roStorySend.mos.xml: StorySend
    ...
    9148627-roDelete.mos.xml: RunningOrderEnd
    bbcProgrammeMetadata.xml: Unknown MOS file type
    cricket: Invalid
    FINAL.json: Invalid
    FINAL.xml: RunningOrder (completed)

You can also read files from an S3 bucket. Either a specific file by key:

.. code-block:: console

    $ mosromgr detect -b my-bucket -k newsnight/20210101/123456-roCreate.mos.xml
    OPENMEDIA_NCS.W1.BBC.MOS/OM_10.1253459/5744992-roCreate.mos.xml: RunningOrder

Or a whole folder by prefix:

.. code-block:: console

    $ mosromgr detect -b bbc-newslabs-slicer-mos-message-store -p newsnight/20210101/
    newsnight/20210101/123456-roCreate.mos.xml: RunningOrder
    newsnight/20210101/123457-roStorySend.mos.xml: StorySend
    newsnight/20210101/123458-roStorySend.mos.xml: StorySend
    newsnight/20210101/123459-roStorySend.mos.xml: StorySend
    ...

.. note::

    Your AWS credentials must be configured to use the S3 method.
    See https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
