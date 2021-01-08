======================
Command line interface
======================

.. _cli-mosromgr:

mosromgr
========

.. code-block:: text

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit

    commands:
      {help,detect,inspect,merge}
        help                Displays help about the specified command
        detect              Detect the MOS type of one or more files
        inspect             Inspect the contents of one or more MOS files
        merge               Merge the given MOS files

mosromgr detect
===============

.. code-block:: text

    Detect the MOS type of one or more files

    positional arguments:
      files       The MOS file to detect

    optional arguments:
      -h, --help  show this help message and exit

mosromgr inspect
================

.. code-block:: text

    Inspect the contents of one or more MOS files

    optional arguments:
      -h, --help            show this help message and exit
      -f file, --file file  The roCreate file to inspect
      -b bucket, --bucket-name bucket
                          S3 bucket name containing the roCreate file
      -p prefix, --prefix prefix
                          The file prefix for the roCreate file in the S3 bucket
      -k key, --key key     The file key for the roCreate file in the S3 bucket
      -t, --start-time      Show programme start time
      -e, --end-time        Show programme end time
      -d, --duration        Show total running order duration
      -s, --stories         Show stories within the running order in the running order
      -i, --items           Show items within stories in the running order
      -n, --notes           Show notes within story items in the running order

mosromgr merge
==============

.. code-block:: text

    Merge the provided MOS files

    optional arguments:
      -h, --help            show this help message and exit
      -f [files [files ...]], --files [files [files ...]]
                            The MOS file to inspect
      -b bucket, --bucket-name bucket
                            S3 bucket name containing MOS files
      -p prefix, --prefix prefix
                            The file prefix for MOS files in the S3 bucket
      -o outfile, --outfile outfile
                            Output to a file
      -i, --incomplete      Allow an incomplete collection
