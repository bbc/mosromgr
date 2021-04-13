.. mosromgr: Python library for managing MOS running orders
.. Copyright 2021 BBC
.. SPDX-License-Identifier: Apache-2.0

======================
Command line interface
======================

This section lists the module's command line commands and provides a reference
to their arguments. For examples, see the :ref:`cli_howto` section.

.. _cli_mosromgr:

mosromgr
========

.. code-block:: text

    usage: mosromgr [-h] [--version] {help,detect,inspect,merge} ...

    mosromgr is a tool for managing MOS running orders

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit

    commands:
      {help,detect,inspect,merge}
        help                Displays help about the specified command
        detect              Detect the MOS type of one or more files
        inspect             Inspect the contents of a roCreate file
        merge               Merge the provided MOS files

.. _cli_mosromgr_detect:

mosromgr detect
===============

.. code-block:: text

    usage: mosromgr detect [-h] [-f [files [files ...]]] [-b bucket] [-p prefix] [-s suffix] [-k key]

    Detect the MOS type of one or more files

    optional arguments:
      -h, --help            show this help message and exit
      -f [files [files ...]], --files [files [files ...]]
                            The MOS files to detect
      -b bucket, --bucket-name bucket
                            S3 bucket name containing the MOS files
      -p prefix, --prefix prefix
                            The prefix for MOS files in the S3 bucket
      -s suffix, --suffix suffix
                            The suffix for MOS files in the S3 bucket
      -k key, --key key     The file key for a MOS file in the S3 bucket

.. _cli_mosromgr_inspect:

mosromgr inspect
================

.. code-block:: text

    usage: mosromgr inspect [-h] [-f file] [-b bucket] [-k key] [-t] [-e] [-d] [-s] [-i] [-n]

    Inspect the contents of a roCreate file

    optional arguments:
      -h, --help            show this help message and exit
      -f file, --file file  The roCreate file to inspect
      -b bucket, --bucket-name bucket
                            S3 bucket name containing the roCreate file
      -k key, --key key     The file key for the roCreate file in the S3 bucket
      -t, --start-time      Show programme start time
      -e, --end-time        Show programme end time
      -d, --duration        Show total running order duration
      -s, --stories         Show stories within the running order in the running order
      -i, --items           Show items within stories in the running order
      -n, --notes           Show notes within story items in the running order


.. _cli_mosromgr_merge:

mosromgr merge
==============

.. code-block:: text

    usage: mosromgr merge [-h] [-f [files [files ...]]] [-b bucket] [-p prefix] [-s suffix]
                          [-o outfile] [-i]

    Merge the provided MOS files

    optional arguments:
      -h, --help            show this help message and exit
      -f [files [files ...]], --files [files [files ...]]
                            The MOS files to merge
      -b bucket, --bucket-name bucket
                            S3 bucket name containing MOS files
      -p prefix, --prefix prefix
                            The file prefix for MOS files in the S3 bucket
      -s suffix, --suffix suffix
                            The file suffix for MOS files in the S3 bucket
      -o outfile, --outfile outfile
                            Output to a file
      -i, --incomplete      Allow an incomplete collection
