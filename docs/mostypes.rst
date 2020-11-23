=========
MOS Types
=========

.. module:: mosromgr.mostypes

This part of the module provides the classes required for managing MOS files.

.. note::

    Note that no detection or validation is applied when using a MOS message
    class directly. To detect the class required for a particular MOS file, the
    :func:`~mosromgr.mosfactory.get_mos_object` function should be used.

MOS message objects provide access to certain elements within the message, such
as the list of :attr:`~RunningOrder.stories` within a :class:`RunningOrder`.
The following documentation for each class lists the available properties. Read
more in the :doc:`moselements` page.

MOS message classes are typically imported like so::

    from mosromgr.mostypes import RunningOrder

MOS objects are initialised using one of two classmethods. Either from a file
path::

    ro = RunningOrder.from_file('roCreate.mos.xml')

or from an XML string::

    with open('roCreate.mos.xml') as f:
        xml = f.read()

    ro = RunningOrder.from_string(xml)

The latter example is particularly useful when loading MOS files from S3.

MOS message classes
===================

The following classes are used to parse and manage specific types of MOS
messages.

RunningOrder
------------

.. autoclass:: RunningOrder()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

StorySend
---------

.. autoclass:: StorySend()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

StoryReplace
------------

.. autoclass:: StoryReplace
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

StoryInsert
-----------

.. autoclass:: StoryInsert()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

StoryAppend
-----------

.. autoclass:: StoryAppend()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

StoryMove
---------

.. autoclass:: StoryMove()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

StoryDelete
-----------

.. autoclass:: StoryDelete()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

MetaDataReplace
---------------

.. autoclass:: MetaDataReplace()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

ItemDelete
----------

.. autoclass:: ItemDelete()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

ItemInsert
----------

.. autoclass:: ItemInsert()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

ItemMoveMultiple
----------------

.. autoclass:: ItemMoveMultiple()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

ItemReplace
-----------

.. autoclass:: ItemReplace()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

EAStoryReplace
--------------

.. autoclass:: EAStoryReplace()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

EAItemReplace
-------------

.. autoclass:: EAItemReplace()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

EAStoryDelete
-------------

.. autoclass:: EAStoryDelete()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

EAItemDelete
------------

.. autoclass:: EAItemDelete()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

EAStoryInsert
-------------

.. autoclass:: EAStoryInsert()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

EAItemInsert
------------

.. autoclass:: EAItemInsert()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

EAStorySwap
-----------

.. autoclass:: EAStorySwap()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

EAItemSwap
----------

.. autoclass:: EAItemSwap()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

EAStoryMove
-----------

.. autoclass:: EAStoryMove()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

EAItemMove
----------

.. autoclass:: EAItemMove()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

RunningOrderReplace
-------------------

.. autoclass:: RunningOrderReplace()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

RunningOrderEnd
---------------

.. autoclass:: RunningOrderEnd()
    :members:
    :inherited-members:
    :special-members: __add__, __lt__, __gt__, __str__

Base classes
============

Since some logic is shared between MOS file management, some inheritance is used
in the implementation:

.. image:: images/class_hierarchy.*
    :align: center

The following classes are abstract and should not be used directly.

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
