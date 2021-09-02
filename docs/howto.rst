.. mosromgr: Python library for managing MOS running orders
.. Copyright 2021 BBC
.. SPDX-License-Identifier: Apache-2.0

============
How-to guide
============

This section is a series of helpful recipes for how to do things and solve
particular problems with *mosromgr*.

.. note::

    For simplicity, these examples deal with MOS messages read from local files,
    but :class:`~mosromgr.mostypes.MosFile` and
    :class:`~mosromgr.moscollection.MosCollection` objects can also be
    constructed using :class:`~mosromgr.mostypes.MosFile.from_string` and
    :class:`~mosromgr.mostypes.MosFile.from_s3`. Refer to :doc:`api/mostypes`
    and :doc:`api/moscollection` for more information.

Merging MOS files
=================

When dealing with merging :class:`~mosromgr.mostypes.MosFile` objects, this is
done by "adding" each file to the :class:`~mosromgr.mostypes.RunningOrder`
object by using the ``+`` operator::

    >>> from mosromgr.mostypes import RunningOrder, StoryInsert
    >>> ro = RunningOrder.from_file('123456-roCreate.mos.xml')
    >>> si = StoryInsert.from_file('123457-roStoryInsert.mos.xml')
    >>> len(ro.stories)
    10
    >>> ro += si
    >>> len(ro.stories)
    11

To parse and merge a collection of MOS files, you could create a list of files
(or use :func:`~glob.glob`), let :class:`~mosromgr.mostypes.MosFile` classify
each file, then merge each of them into the
:class:`~mosromgr.mostypes.RunningOrder`::

    from mosromgr.mostypes import MosFile
    from glob import glob

    files = glob('*.mos.xml')

    ro, *mosfiles = sorted(MosFile.from_file(f) for f in files)

    for mf in mosfiles:
        ro += mf

To access the final XML, simply print the
:class:`~mosromgr.mostypes.RunningOrder` object or access the
:attr:`~mosromgr.mostypes.RunningOrder.__str__`::

    >>> print(ro)
    <mos>
      <mosID>MOS ID</mosID>
      <messageID>1234567</messageID>
      ...
    >>> s = str(ro)
    >>> s
    <mos>
      <mosID>MOS ID</mosID>
      <messageID>1234567</messageID>
      ...

Merging MOS files using MOSCollection
=====================================

The :class:`~mosromgr.moscollection.MosCollection` class provides a wrapper for
operations dealing with a collection of MOS files as part of one programme. So
to merge files like in the previous example, you could do the following
instead::

    from mosromgr.moscollection import MosCollection
    from glob import glob

    files = glob('*.mos.xml')
    mc = MosCollection.from_files(files)

    mc.merge()

To access the final XML, simply print the
:class:`~mosromgr.moscollection.MosCollection` object or access the
:attr:`~mosromgr.moscollection.MosCollection.__str__`::

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

Accessing the properties of a running order
===========================================

For example, a :class:`~mosromgr.mostypes.RunningOrder` object could contain
several :class:`~mosromgr.moselements.Story` objects, each containing a number
of :class:`~mosromgr.moselements.Item` objects::

    >>> from mosromgr.mostypes import RunningOrder
    >>> ro = RunningOrder.from_file('roCreate.mos.xml')
    >>> ro.stories
    [<Story 1234>, <Story 1235>, <Story 1236>]
    >>> [story.duration for story in ro.stories]
    [10, 20, 30]
    >>> ro.duration
    60
    >>> story = ro.stories[0]
    >>> story.slug
    'Some story'
    >>> story.items
    [<Item ITEM1>, <Item ITEM2>, <Item ITEM3>]
    >>> item = story.items[0]
    >>> item.slug
    'Some item'

In the case of a :class:`~mosromgr.mostypes.StoryAppend` object, this would
contain a single story::

    >>> from mosromgr.mostypes import StoryAppend
    >>> sa = StoryAppend.from_file('roStoryAppend.mos.xml')
    >>> sa.story
    <Story STORY1>
    >>> sa.duration
    20

If this :class:`~mosromgr.mostypes.StoryAppend` object was merged with a
:class:`~mosromgr.mostypes.RunningOrder` object, the new story would be
accessible in the :class:`~mosromgr.mostypes.RunningOrder`
:attr:`~mosromgr.mostypes.RunningOrder.stories` property::

    >>> from mosromgr.mostypes import RunningOrder, StoryAppend
    >>> ro = RunningOrder.from_file('roCreate.mos.xml')
    >>> sa = StoryAppend.from_file('roStoryAppend.mos.xml')
    >>> len(ro.stories)
    3
    >>> ro += sa
    >>> len(ro.stories)
    4

Additional information may be contained within the XML, and not exposed by
properties the way :attr:`~mosromgr.moselements.Item.slug` and
:attr:`~mosromgr.moselements.Item.object_id` are. In the sprit of
`escape hatches and ejector seats`_, the original XML in which the element was
found is accessible as an :class:`xml.etree.ElementTree.Element` object for
further introspection.

    .. _escape hatches and ejector seats: https://anvil.works/blog/escape-hatches-and-ejector-seats

For example, if you knew some of the ``<item>`` tags in a running order
contained an ``<areaID>`` field, and you wanted to access its value, you could
do so by inspecting the :attr:`~mosromgr.moselements.Item.xml` property::

    tag = item.xml.find('areaID')
    if tag is not None:
        print(tag.text)

Handling Exceptions
===================

This can be useful for handling exceptions in your own code. For example, to
handle any exception generated by the library, you can catch the library's base
exception :class:`~mosromgr.exc.MosRoMgrException`::

    try:
        main()
    except MosRoMgrException as e:
        print(e)

To catch a specific exception known to be raised under certain circumstances,
each exception can be imported and handled separately if required::

    from mosromgr.mostypes import MosFile
    from mosromgr.exc import MosInvalidXML, UnknownMosFileType

    try:
        ro = MosFile.from_file(mosfile)
    except MosInvalidXML as e:
        print("Invalid in", mosfile)
    except UnknownMosFileType as e:
        print("Unknown MOS file type", mosfile)

In some cases, a warning is raised rather than an exception. This means that
execution is continued but a warning is output, which can be suppressed using
the :mod:`warnings` module.

Capturing warnings
==================

If you want to catch warnings and log them (for example, during a merge), you
can use :class:`warnings.catch_warnings`::

    with warnings.catch_warnings(record=True) as warns:
        mc.merge()

    warning_messages = [str(w.message) for w in warns]

Suppressing warnings
====================

If you are not interested in seeing or capturing warnings, you can either use a
`warning filter`_ or use :class:`warnings.catch_warnings`::

    with warnings.catch_warnings() as warns:
        mc.merge()

.. _warning filter: https://docs.python.org/3/library/warnings.html#the-warnings-filter