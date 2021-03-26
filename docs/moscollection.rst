.. mosromgr: Python library for managing MOS running orders
.. Copyright 2021 BBC
.. SPDX-License-Identifier: Apache-2.0

==============
MOS Collection
==============

.. module:: mosromgr.moscollection

This part of the module provides a wrapper class :class:`MosCollection` which
stores references to specified MOS files, strings or S3 object keys so the
:class:`~mosromgr.mostypes.MosFile` objects can be recreated when needed rather
than kept in memory.

.. note::
    Note that creating a :class:`MosCollection` from strings does not benefit
    from memory efficiency as the strings would still be held in memory.

When the collection is created it retrieves the message IDs and running order
IDs for each MOS object, sorts the objects by message ID then validates whether
they are ready to be merged. On construction, the collection is validated,
checking all messages are from the same running order, and that a single
``roCreate`` file is included. Optionally, the ``allow_incomplete`` parameter
can be set, removing the requirement for a ``roDelete`` file to be included.

Once a :class:`MosCollection` object has been created, the
:meth:`~MosCollection.merge` method can be used to apply the effects of the
other MOS messages into the :class:`~mosromgr.mostypes.RunningOrder` object
(:attr:`~MosCollection.ro`). If all MOS messages from a finished programme are
provided, :class:`~mosromgr.mostypes.RunningOrder` will be a complete
representation of the programme as completed.

The :class:`MosCollection` class is typically imported like so::

    from mosromgr.moscollection import MosCollection

MOS collections are constructed using one of three classmethods. Either from a
list of file paths::

    mos_files = ['roCreate.mos.xml', 'roStorySend.mos.xml', 'roDelete.mos.xml']
    mc = MosCollection.from_files(mos_files)

from a list of strings::

    mos_strings = [roCreate, roStorySend, roDelete]
    mc = MosCollection.from_strings(mos_files)

or from an S3 bucket::

    mc = MosCollection.from_s3(bucket_name=bucket_name, prefix=prefix)

Whichever way the collection was constructed, you can then proceed to merge all
MOS files into the running order::

    mc.merge()

To access the final XML, simply print the :class:`MosCollection` object or
access the :attr:`~MosCollection.__str__`

    >>> print(mc)
    <mos>
      <mosID>MOS ID</mosID>
      <messageID>1234567</messageID>
      ...
    >>> s = str(mc)
    >>> s
    <mos>
      <mosID>MOS ID</mosID>
      <messageID>1234567</messageID>
      ...

.. note::

    For merging a small number of files, or running in an environment without a
    tight memory constraint, it may be preferred to avoid using
    :class:`MosCollection` and instead simply construct a list of
    :class:`MOSFile` objects.

MosCollection
=============

.. autoclass:: MosCollection()
    :members:
    :special-members: __str__

MosReader
=========

The :class:`MosReader` class is internal and is not intended to be constructed
by the user. A :class:`MosCollection` object will contain a list of
:class:`MosReader` instances, so users may find it useful to refer to its
members.

.. autoclass:: MosReader()
    :members:
