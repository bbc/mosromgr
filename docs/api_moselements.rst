.. mosromgr: Python library for managing MOS running orders
.. Copyright 2021 BBC
.. SPDX-License-Identifier: Apache-2.0

==================
API - MOS Elements
==================

.. module:: mosromgr.moselements

This part of the module provides a collection of classes used to provide easy
access to certain elements within a :class:`~mosromgr.mostypes.MosFile` object,
such as a list of stories within a running order, and the items within a story.

Although usually not required directly, the MOS Element classes can be imported
as follows::

    from mosromgr.moselements import Story

.. note::
    Note that these classes should not normally be constructed by the user, but
    instances of them can be found within :class:`~mosromgr.mostypes.MosFile`
    objects, so the following documentation is provided as a reference to how
    they can be used.

Element classes
===============

Story
-----

.. autoclass:: Story()
    :members:
    :inherited-members:
    :show-inheritance:
    :special-members: __str__

Item
----

.. autoclass:: Item()
    :members:
    :inherited-members:
    :show-inheritance:
    :special-members: __str__

Base classes
============

MosElement
----------

.. autoclass:: MosElement()
    :members:
    :special-members: __str__
