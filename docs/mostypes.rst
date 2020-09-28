=========
MOS Types
=========

.. module:: mosromgr.mostypes

.. currentmodule:: mosromgr

This part of the module provides the classes required for managing MOS files.

.. note::

    Note that no detection or validation is applied when using a MOS message
    class directly. To detect the class required for a particular MOS file, the
    :func:`~mosromgr.mosfactory.get_mos_object` function should be used.

MOS message classes are typically imported like so::

    from mosromgr.mostypes import RunningOrder

MOS message classes
===================

The following classes are used to parse and manage specific types of MOS
messages.

RunningOrder
------------

.. autoclass:: mosromgr.mostypes.RunningOrder
    :members: to_dict

StorySend
---------

.. autoclass:: mosromgr.mostypes.StorySend
    :members: merge

EAReplaceStory
--------------

.. autoclass:: mosromgr.mostypes.EAReplaceStory
    :members: merge

EAReplaceItem
-------------

.. autoclass:: mosromgr.mostypes.EAReplaceItem
    :members: merge

EADeleteStory
-------------

.. autoclass:: mosromgr.mostypes.EADeleteStory
    :members: merge

EADeleteItem
------------

.. autoclass:: mosromgr.mostypes.EADeleteItem
    :members: merge

EAInsertStory
-------------

.. autoclass:: mosromgr.mostypes.EAInsertStory
    :members: merge

EAInsertItem
------------

.. autoclass:: mosromgr.mostypes.EAInsertItem
    :members: merge

EASwapStory
-----------

.. autoclass:: mosromgr.mostypes.EASwapStory
    :members: merge

EASwapItem
----------

.. autoclass:: mosromgr.mostypes.EASwapItem
    :members: merge

EAMoveStory
-----------

.. autoclass:: mosromgr.mostypes.EAMoveStory
    :members: merge

EAMoveItem
----------

.. autoclass:: mosromgr.mostypes.EAMoveItem
    :members: merge

MetaDataReplace
---------------

.. autoclass:: mosromgr.mostypes.MetaDataReplace
    :members: merge

StoryAppend
-----------

.. autoclass:: mosromgr.mostypes.StoryAppend
    :members: merge

StoryDelete
-----------

.. autoclass:: mosromgr.mostypes.StoryDelete
    :members: merge

ItemDelete
----------

.. autoclass:: mosromgr.mostypes.ItemDelete
    :members: merge

StoryInsert
-----------

.. autoclass:: mosromgr.mostypes.StoryInsert
    :members: merge

ItemInsert
----------

.. autoclass:: mosromgr.mostypes.ItemInsert
    :members: merge

StoryMove
---------

.. autoclass:: mosromgr.mostypes.StoryMove
    :members: merge

ItemMoveMultiple
----------------

.. autoclass:: mosromgr.mostypes.ItemMoveMultiple
    :members: merge

StoryReplace
------------

.. autoclass:: mosromgr.mostypes.StoryReplace
    :members: merge

ItemReplace
-----------

.. autoclass:: mosromgr.mostypes.ItemReplace
    :members: merge

RunningOrderReplace
-------------------

.. autoclass:: mosromgr.mostypes.RunningOrderReplace
    :members: merge

RunningOrderEnd
---------------

.. autoclass:: mosromgr.mostypes.RunningOrderEnd
    :members: merge

Base classes
============

Since some logic is shared between MOS file management, some inheritance is used
in the implementation:

.. image:: images/class_hierarchy.*
    :align: center

The following classes are abstract and should not be used directly.

MosFile
-------

.. autoclass:: mosromgr.mostypes.MosFile
    :members: to_dict

ElementAction
-------------

.. autoclass:: mosromgr.mostypes.ElementAction
