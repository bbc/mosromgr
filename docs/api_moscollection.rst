.. mosromgr: Python library for managing MOS running orders
.. Copyright 2021 BBC
.. SPDX-License-Identifier: Apache-2.0

====================
API - MOS Collection
====================

.. module:: mosromgr.moscollection

This part of the module provides a wrapper class :class:`MosCollection` which
stores references to specified MOS files, strings or S3 object keys so the
:class:`~mosromgr.mostypes.MosFile` objects can be recreated when needed rather
than kept in memory.

.. note::
    Note that creating a :class:`MosCollection` from strings does not benefit
    from memory efficiency as the strings would still be held in memory.

The :class:`MosCollection` is typically imported like so::

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
