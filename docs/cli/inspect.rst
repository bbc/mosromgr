.. mosromgr: Python library for managing MOS running orders
.. Copyright 2021 BBC
.. SPDX-License-Identifier: Apache-2.0

================
mosromgr inspect
================

View the high-level the contents of a MOS file

Synopsis
========

.. code-block:: text

    mosromgr inspect [-h] [-f [files [files ...]]] [-b bucket] [-p prefix] [-s suffix] [-k key]

Description
===========

.. program:: mosromgr-inspect

.. option:: -f --files [files ...]

    The MOS files to inspect

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

View the contents of a local MOS file:

.. code-block:: console

    $ mosromgr inspect -f 123456-roCreate.mos.xml
    RO: 22:45 NEWSNIGHT 54D CORE Thu, 08.04.2021
    STORY: OPENMEDIA_NCS.W1.BBC.MOS;OM_4.15529413;OM_4.15529414,4.15529413.1
    STORY: OPENMEDIA_NCS.W1.BBC.MOS;OM_4.15529413;OM_4.15529416,4.15529413.3
    STORY: OPENMEDIA_NCS.W1.BBC.MOS;OM_4.15529413;OM_4.15529418,4.15529413.5
    ...

View the contents of a MOS file in S3:

.. code-block:: console

    $ mosromgr inspect -b my-bucket -k newsnight/20210804/123456-roCreate.mos.xml
    RO: 22:45 NEWSNIGHT 54D CORE Thu, 08.04.2021
    STORY: OPENMEDIA_NCS.W1.BBC.MOS;OM_4.15529413;OM_4.15529414,4.15529413.1
    STORY: OPENMEDIA_NCS.W1.BBC.MOS;OM_4.15529413;OM_4.15529416,4.15529413.3
    STORY: OPENMEDIA_NCS.W1.BBC.MOS;OM_4.15529413;OM_4.15529418,4.15529413.5

.. note::

    Your AWS credentials must be configured to use the S3 method.
    See https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
