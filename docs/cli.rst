==================
Command line tools
==================

Command line utilities provided by this module:

mosromgr
========

Synopsis
--------

::

    mosromgr [-h] [-d DIRECTORY] [-b BUCKET_NAME] [-p BUCKET_PREFIX]


Description
-----------

A utility for processing MOS messages from a folder or S3 bucket. Running
:program:`mosromgr` providing either a directory or the combination of an S3
bucket name and prefix will read in and process all available MOS files, merge
them and output a "completed" version of the programme running order.

Options
-------

.. program:: mosromgr

.. option:: -h, --help

    show this help message and exit

.. option:: -d DIRECTORY

    The local directory containing MOS files

.. option:: -b BUCKET_NAME

    The name of the S3 bucket containing MOS files

.. option:: -p BUCKET_PREFIX

    The prefix of the location in the S3 bucket which contains the MOS files


Examples
--------

To merge MOS messages in a local directory, and save the output into a new file:

.. code-block:: console

    $ ls newsnight/
    roCreate.mos.xml    roStorySend.mos.xml     roDelete.mos.xml
    $ mosromgr -d newsnight > newsnight/FINAL.xml

To merge MOS messages in a folder within an S3 bucket, and save the output into
a new file:

.. code-block:: console

    $ aws s3 ls s3://news-programmes/
    PRE     newscast/
    PRE     newsnight/
    $ aws s3 ls s3://news-programmes/newsnight/
    roCreate.mos.xml
    roDelete.mos.xml
    roStorySend.mos.xml
    $ mosromgr -b news-programmes -p newsnight > newsnight_FINAL.xml
