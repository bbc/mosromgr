.. mosromgr: Python library for managing MOS running orders
.. Copyright 2021 BBC
.. SPDX-License-Identifier: Apache-2.0

============
Introduction
============

This section is a walkthrough of the contents of the module, intended to explain
how *mosromgr* works and introduce the concepts.

MOS Types
=========

The :doc:`api/mostypes` section of the module provides a collection of classes
for dealing with individual MOS messages. The classes provide easy access to
some of the elements within a MOS file, such as a list of stories within a
running order, the transmission time of a programme, or its duration.

For example, you can load a running order from a ``roCreate`` file, print the RO
Slug and access some details::

    >>> from mosromgr.mostypes import RunningOrder
    >>> ro = RunningOrder.from_file('123456-roCreate.mos.xml')
    >>> ro.ro_slug
    '22:45 NEWSNIGHT 54D CORE Thu, 08.04.2021'
    >>> ro.message_id
    123456
    >>> ro.start_time
    datetime.datetime(2021, 4, 8, 21, 46, 30)
    >>> ro.duration
    970.0
    >>> len(ro.stories)
    10

In the case of MOS messages which contain a *change* to a running order, the
relevant details are exposed, for example a
:class:`~mosromgr.mostypes.StoryInsert` includes access to the
:attr:`~mosromgr.mostypes.StoryInsert.source_stories` and
:attr:`~mosromgr.mostypes.StoryInsert.target_story`.

When dealing with merging :class:`~mosromgr.mostypes.MosFile` objects, this is
done by "adding" each file to the :class:`~mosromgr.mostypes.RunningOrder`
object by using the ``+`` operator::

    >>> from mosromgr.mostypes import RunningOrder, StoryInsert
    >>> ro = RunningOrder.from_file('123456-roCreate.mos.xml')
    >>> ss = StoryInsert.from_file('123457-roStoryInsert.mos.xml')
    >>> len(ro.stories)
    10
    >>> ro += ss
    >>> len(ro.stories)
    11

MOS Elements
============

The :doc:`api/moselements` part of the module provides a collection of classes
used to provide easy access to certain elements within a
:class:`~mosromgr.mostypes.MosFile` object, such as a list of stories within a
running order, and the items within a story::

    from mosromgr.mostypes import RunningOrder

    ro = RunningOrder.from_file('123456-roCreate.mos.xml')

    print(ro.ro_slug)
    for story in ro.stories:
        print(story.slug)

Here, ``ro.stories`` is a list of :class:`~mosromgr.moselements.Story` objects.
Each story has its own set of accessible properties, such as the story's
:class:`~mosromgr.moselements.Story.duration`,
:class:`~mosromgr.moselements.Story.start_time`,
:class:`~mosromgr.moselements.Story.end_time`,
:class:`~mosromgr.moselements.Story.offset` and
:class:`~mosromgr.moselements.Story.items`::

    >>> story = ro.stories[0]
    >>> story.duration
    180.0
    >>> story.start_time
    datetime.datetime(2021, 4, 8, 21, 46, 30)
    >>> len(story.items)
    3

Here, the story contains 3 items, each of these is an
:class:`~mosromgr.moselements.Item` object.

MOS Collection
==============

The :doc:`api/moscollection` part of the module provides a wrapper class
:class:`~mosromgr.moscollection.MosCollection` which stores references to
specified MOS files, strings or S3 object keys so the
:class:`~mosromgr.mostypes.MosFile` objects can be recreated when needed rather
than kept in memory. Rather than using the ``+`` operator, a
:meth:`~mosromgr.moscollection.MosCollection.merge` method is provided::

    from mosromgr.moscollection import MosCollection

    mc = MosCollection.from_s3(bucket_name=bucket_name, prefix=prefix)

    mc.merge()

The next page will cover some example problems and solutions to show you how you
can use *mosromgr* in practice.
