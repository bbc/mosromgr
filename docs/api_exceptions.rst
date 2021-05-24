.. mosromgr: Python library for managing MOS running orders
.. Copyright 2021 BBC
.. SPDX-License-Identifier: Apache-2.0

================
API - Exceptions
================

.. module:: mosromgr.exc

The module's exceptions and warnings are typically imported like so::

    from mosromgr.exc import MosRoMgrException

The library's base warning is :class:`MosRoMgrWarning` and others are detailed
below.

Errors
======

MosRoMgrException
-----------------

.. autoexception:: mosromgr.exc.MosRoMgrException
    :show-inheritance:

UnknownMosFileType
------------------

.. autoexception:: mosromgr.exc.UnknownMosFileType
    :show-inheritance:

MosMergeError
-------------

.. autoexception:: mosromgr.exc.MosMergeError
    :show-inheritance:

MosCompletedMergeError
----------------------

.. autoexception:: mosromgr.exc.MosCompletedMergeError
    :show-inheritance:

InvalidMosCollection
--------------------

.. autoexception:: mosromgr.exc.InvalidMosCollection
    :show-inheritance:

MosInvalidXML
-------------

.. autoexception:: mosromgr.exc.MosInvalidXML
    :show-inheritance:

Warnings
========

MosRoMgrWarning
---------------

.. autoexception:: mosromgr.exc.MosRoMgrWarning
    :show-inheritance:

MosMergeNonStrictWarning
------------------------

.. autoexception:: mosromgr.exc.MosMergeNonStrictWarning
    :show-inheritance:

ItemNotFoundWarning
-------------------

.. autoexception:: mosromgr.exc.ItemNotFoundWarning
    :show-inheritance:

StoryNotFoundWarning
--------------------

.. autoexception:: mosromgr.exc.StoryNotFoundWarning
    :show-inheritance:

DuplicateStoryWarning
---------------------

.. autoexception:: mosromgr.exc.DuplicateStoryWarning
    :show-inheritance:
