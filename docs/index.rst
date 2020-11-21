========
mosromgr
========

Python client for managing `MOS`_ running orders. Pronounced *mos-ro-manager*.

.. _MOS: http://mosprotocol.com/

.. image:: images/mos.*
    :target: http://mosprotocol.com/
    :align: center

The library provides functionality for detecting MOS file types, processing and
inspecting MOS message files, as well as merging MOS files into a running order,
and providing a "completed" programme including all additions and changes made
between the first message (``roCreate``) and the last (``roDelete``).

This can be used as a library, using the utilities provided in the *mosromgr*
module, and the command line command :ref:`cli-mosromgr` can be used to process
either a directory of MOS files, or a folder within an S3 bucket.

This library was developed by the `BBC News Labs`_ team.

.. _BBC News Labs: https://bbcnewslabs.co.uk/

Usage
=====

Command line
------------

Merge all MOS files in directory `dirname`::

    mosromgr -d dirname

Merge all MOS files in S3 folder `prefix` in bucket `bucketname`::

    mosromgr -b bucketname -p prefix

The final running order is output to stdout, so to save to a file use `>` e.g::

    mosromgr -d dirname > FINAL.xml

Library
-------

Load a ``roCreate`` file and view its stories::

    from mosromgr.mostypes import RunningOrder

    ro = RunningOrder('roCreate.mos.xml')

    for story in ro.stories:
        print(story.slug)

Merge a single ``roStorySend`` (:class:`~mosromgr.mostypes.StorySend`) into a
``roCreate`` (:class:`~mosromgr.mostypes.RunningOrder`) and output the file to a
new file::

    from mosromgr.mostypes import RunningOrder, StorySend

    ro = RunningOrder('roCreate.mos.xml')
    ss = StorySend('roStorySend.mos.xml')

    ro += ss

    with open('final.mos.xml', 'w') as f:
        f.write(ro)

Alternatively, use :class:`~mosromgr.moscontainer.MosContainer` which will sort
and classify MOS types of all given files::

    from mosromgr.moscontainer import MosContainer

    mos_files = ['roCreate.mos.xml', 'roStorySend.mos.xml', 'roDelete.mos.xml']
    mc = MosContainer(mos_files)

    mc.merge()
    with open('final.mos.xml', 'w') as f:
        f.write(mc)

Table of Contents
=================

.. toctree::
    :maxdepth: 1
    :numbered:

    mostypes
    moselements
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

Contributing
============

Source code can be found on GitHub at `github.com/bbc/mosromgr`_ which also
hosts the `issue tracker`_ and `contributing guidelines`_.

.. _github.com/bbc/mosromgr: https://github.com/bbc/mosromgr
.. _issue tracker: https://github.com/bbc/mosromgr/issues
.. _contributing guidelines: https://github.com/bbc/mosromgr/blob/main/.github/CONTRIBUTING.md

Contributors
============

* `Ben Nuttall`_
* `Owen Tourlamain`_
* `Rob French`_
* `Lucy MacGlashan`_

.. _Ben Nuttall: https://github.com/bennuttall
.. _Owen Tourlamain: https://github.com/OwenTourlamain
.. _Rob French: https://github.com/FrencR
.. _Lucy MacGlashan: https://github.com/lannem

Licence
=======

TBC

Contact
=======

Please contact `BBC News Labs team`_ if you want to get in touch.

.. _BBC News Labs team: mailto:BBCNewsLabsTeam@bbc.co.uk

.. image:: images/bbcnewslabs.*
    :target: https://bbcnewslabs.co.uk/
    :align: center
