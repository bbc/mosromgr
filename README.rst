========
mosromgr
========

Python library for managing `MOS`_ running orders. Pronounced *mos-ro-manager*.

.. _MOS: http://mosprotocol.com/

.. image:: https://mosromgr.readthedocs.io/en/latest/_images/mos.jpg
    :target: http://mosprotocol.com/
    :align: center

The library provides functionality for classifying MOS file types, processing and
inspecting MOS message files, as well as merging MOS files into a running order,
and providing a "completed" programme including all additions and changes made
between the first message (``roCreate``) and the last (``roDelete``).

This can be used as a library, using the utilities provided in the *mosromgr*
module, and the command line command ``mosromgr`` can be used to process either
a directory of MOS files, or a folder within an S3 bucket.

This library was developed by the `BBC News Labs`_ team.

.. _BBC News Labs: https://bbcnewslabs.co.uk/

Usage
=====

Command line
------------

List the stories within a running order:

.. code-block:: console

    $ mosromgr inspect -f roCreate.mos.xml --stories
    0828 MIDLANDS TODAY Wed, 11.11.2020

    INTRODUCTION-READ

    TESTING-OOV

    WEATHER-SHORT

    END OF PROGRAMME

Merge all MOS files in directory `newsnight` and save in ``FINAL.xml``:

.. code-block:: console

    $ mosromgr merge -f newsnight/* -o FINAL.xml

Library
-------

Load a ``roCreate`` file and view its stories::

    from mosromgr.mostypes import RunningOrder

    ro = RunningOrder.from_file('roCreate.mos.xml')

    for story in ro.stories:
        print(story.slug)

Merge a single ``roStorySend`` into a ``roCreate`` and output the file to a new
file::

    from mosromgr.mostypes import RunningOrder, StorySend

    ro = RunningOrder.from_file('roCreate.mos.xml')
    ss = StorySend.from_file('roStorySend.mos.xml')

    ro += ss

    with open('final.mos.xml', 'w') as f:
        f.write(str(ro))

If you're automating this process you won't necessarily know which MOS Type to
use, so you can construct an object from the base class ``MosFile`` which will
automatically classify your file::

    >>> from mosromgr.mostypes import MosFile
    >>> mf1 = MosFile.from_file('roCreate.mos.xml')
    >>> mf1
    <RunningOrder 1000>
    >>> mf2 = MosFile.from_file('roStorySend.mos.xml')
    >>> mf2
    <StorySend 1001>

Using ``MosCollection`` will sort and classify multiple MOS types of all given
files, allowing you to process a collection of MOS files within a complete or
partially complete programme::

    from mosromgr.moscollection import MosCollection

    mos_files = ['roCreate.mos.xml', 'roStorySend.mos.xml', 'roDelete.mos.xml']
    mc = MosCollection.from_files(mos_files)

    mc.merge()
    with open('final.mos.xml', 'w') as f:
        f.write(str(mc))

Documentation
=============

Comprehensive documentation is provided at https://mosromgr.readthedocs.io/

The documentation follows the `Diátaxis`_ system, so is split between four modes
of documentation: tutorials, how-to guides, technical reference and explanation.

.. _Diátaxis: https://diataxis.fr/

Issues and questions
====================

Questions can be asked on the `discussion board`_, and issues can be raised
on the `issue tracker`_.

.. _discussion board: https://github.com/bbc/mosromgr/discussions
.. _issue tracker: https://github.com/bbc/mosromgr/issues

Contributing
============

Source code can be found on GitHub at `github.com/bbc/mosromgr`_.

Contributions are welcome. Please refer to the `contributing guidelines`_.

.. _github.com/bbc/mosromgr: https://github.com/bbc/mosromgr
.. _contributing guidelines: https://github.com/bbc/mosromgr/blob/main/.github/CONTRIBUTING.md

Contributors
============

- `Ben Nuttall`_
- `Owen Tourlamain`_
- `Rob French`_
- `Lucy MacGlashan`_
- `Dave Bevan`_
- `Matthew Sim`_

.. _Ben Nuttall: https://github.com/bennuttall
.. _Owen Tourlamain: https://github.com/OwenTourlamain
.. _Rob French: https://github.com/FrencR
.. _Lucy MacGlashan: https://github.com/lannem
.. _Dave Bevan: https://github.com/bevand10
.. _Matthew Sim: https://github.com/MattSBBC

Licence
=======

Licensed under the `Apache License, Version 2.0`_.

.. _Apache License, Version 2.0: https://opensource.org/licenses/Apache-2.0

Contact
=======

To get in touch with the maintainers, please contact the BBC News Labs team:
bbcnewslabsteam@bbc.co.uk

.. image:: https://mosromgr.readthedocs.io/en/latest/_images/bbcnewslabs.png
    :target: https://bbcnewslabs.co.uk/
    :align: center
