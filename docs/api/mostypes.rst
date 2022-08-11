.. mosromgr: Python library for managing MOS running orders
.. Copyright 2021 BBC
.. SPDX-License-Identifier: Apache-2.0

=========
MOS Types
=========

.. module:: mosromgr.mostypes

This part of the module provides the classes required for classifying and
managing MOS files.

MOS Type classes are typically imported like so::

    from mosromgr.mostypes import MosFile

MOS objects are constructed using one of three classmethods. Either from a file
path::

    ro = RunningOrder.from_file('roCreate.mos.xml')

from an XML string::

    with open('roCreate.mos.xml') as f:
        xml = f.read()

    ro = RunningOrder.from_string(xml)

or from an S3 file key::

    ro = RunningOrder.from_s3(bucket_name='newsnight', mos_file_key='20200101/roCreate.mos.xml')

Similarly, objects constructed using these classmethods on the :class:`MosFile`
base class will be automatically classified and an instance of the relevant
class will be created::

    >>> ro = MosFile.from_file('roCreate.mos.xml')
    >>> ro
    <RunningOrder 1000>
    >>> ss = MosFile.from_file('roStorySend.mos.xml')
    >>> ss
    <StorySend 1001>
    >>> ro = MosFile.from_string(xml1)
    >>> ro
    <RunningOrder 1000>
    >>> ss = MosFile.from_string(xml2)
    >>> ss
    <StorySend 1001>

Even ``roElementAction`` files, which require a number of different subclasses,
can be classified this way::

    >>> ea1 = MosFile.from_file('roElementAction1.mos.xml')
    >>> ea1
    <EAStorySwap 1012>
    >>> ea2 = MosFile.from_string(xml)
    >>> ea2
    <EAItemMove 1013>

.. note::

    Your AWS credentials must be configured to construct using the :meth:`~MosFile.from_s3`
    classmethod. See https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

MOS message classes
===================

The following classes are used to parse and manage specific types of MOS
messages.

RunningOrder
------------

.. autoclass:: RunningOrder()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

StorySend
---------

.. autoclass:: StorySend()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

StoryReplace
------------

.. autoclass:: StoryReplace()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

StoryInsert
-----------

.. autoclass:: StoryInsert()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

StoryAppend
-----------

.. autoclass:: StoryAppend()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

StoryMove
---------

.. autoclass:: StoryMove()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

StoryDelete
-----------

.. autoclass:: StoryDelete()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

MetaDataReplace
---------------

.. autoclass:: MetaDataReplace()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

ItemDelete
----------

.. autoclass:: ItemDelete()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

ItemInsert
----------

.. autoclass:: ItemInsert()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

ItemMoveMultiple
----------------

.. autoclass:: ItemMoveMultiple()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

ItemReplace
-----------

.. autoclass:: ItemReplace()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

ReadyToAir
----------

.. autoclass:: ReadyToAir()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

EAStoryReplace
--------------

.. autoclass:: EAStoryReplace()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

EAItemReplace
-------------

.. autoclass:: EAItemReplace()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

EAStoryDelete
-------------

.. autoclass:: EAStoryDelete()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

EAItemDelete
------------

.. autoclass:: EAItemDelete()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

EAStoryInsert
-------------

.. autoclass:: EAStoryInsert()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

EAItemInsert
------------

.. autoclass:: EAItemInsert()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

EAStorySwap
-----------

.. autoclass:: EAStorySwap()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

EAItemSwap
----------

.. autoclass:: EAItemSwap()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

EAStoryMove
-----------

.. autoclass:: EAStoryMove()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

EAItemMove
----------

.. autoclass:: EAItemMove()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

RunningOrderReplace
-------------------

.. autoclass:: RunningOrderReplace()
    :show-inheritance:
    :members:
    :inherited-members:
    :exclude-members: completed
    :special-members: __add__, __lt__, __str__

RunningOrderEnd
---------------

.. autoclass:: RunningOrderEnd()
    :show-inheritance:
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __str__

Base classes
============

Since some logic is shared between MOS file management, some inheritance is used
in the implementation:

.. image:: ../images/class_hierarchy.*
    :align: center

MosFile
-------

.. autoclass:: MosFile()
    :members:
    :inherited-members:

ElementAction
-------------

.. autoclass:: ElementAction()
    :members:
    :inherited-members:
