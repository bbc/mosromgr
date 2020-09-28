========
mosromgr
========

Python library for managing `MOS`_ running orders, developed by `BBC News
Labs`_.

.. _MOS: http://mosprotocol.com/
.. _BBC News Labs: https://bbcnewslabs.co.uk

The library provides functionality for detecting MOS file types, merging MOS
files into a running order, and providing a "completed" programme including all
additions and changes made between the first message (``roCreate``) and the last
(``roDelete``).

This can be used as a library, using the utilities provided in the module
**mosromgr**, and the command line command ``mosromgr`` can be used to process
either a directory of MOS files, or a folder within an S3 bucket.

Usage
=====

Command line
------------

Merge all MOS files in directory ``dirname``::

    mosromgr -d dirname

Merge all MOS files in S3 folder ``prefix`` in bucket ``bucketname``::

    mosromgr -b bucketname -p prefix

The final running order is output to stdout, so to save to a file use ``>``
e.g::

    mosromgr -d dirname > FINAL.xml

Library
-------

Simple example merging a single ``roStorySend`` into a ``roCreate`` and
outputting the file to a new file::

    from mosromgr.mostypes import RunningOrder, StorySend

    ro = RunningOrder('roCreate.mos.xml')
    ss = StorySend('roStorySend.mos.xml')

    ro += ss

    with open('final.mos.xml', 'w') as f:
        f.write(ro)

Alternatively, use ``MosContainer`` which will sort and classify MOS types of
all given files::

    from mosromgr.moscontainer import MosContainer

    mos_files = ['roCreate.mos.xml', 'roStorySend.mos.xml', 'roDelete.mos.xml']
    mc = MosContainer(mos_files)

    mc.merge()
    with open('final.mos.xml', 'w') as f:
        f.write(mc)

Contributing
============

Source code can be found on GitHub at https://github.com/bbc/mosromgr which
also hosts the `issue tracker`_ and `contributing guidelines`_.

.. _issue tracker: https://github.com/bbc/mosromgr/issues
.. _contributing guidelines: https://github.com/bbc/mosromgr/blob/main/CONTRIBUTING.md

Contributors
============

- `Ben Nuttall`_
- `Owen Tourlamain`_
- `Rob French`_

.. _Ben Nuttall: https://github.com/bennuttall
.. _Owen Tourlamain: https://github.com/OwenTourlamain
.. _Rob French: https://github.com/FrencR

Licence
=======

TBC

Contact
=======

Please contact the BBC News Labs team (``BBCNewsLabsTeam@bbc.co.uk``) if you
want to get in touch.
