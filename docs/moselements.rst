============
MOS Elements
============

.. module:: mosromgr.moselements

This part of the module provides a collection of classes used to provide easy
access to certain elements within a :class:`~mosromgr.mostypes.MosFile` object,
such as a list of stories within a running order, and the items within a story.

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

.. note::

    Note that these classes should not normally be initialised by the user, but
    instances of them can be found within :class:`~mosromgr.mostypes.MosFile`
    objects, so the following documentation is provided as a reference to how
    they can be used.

.. note::

    Note that additional information may be contained within the XML, and these
    elements are simply an abstraction providing easy access to certain
    elements. In the sprit of `escape hatches vs ejector seats`_, the original
    XML in which the element was found is accessible as an
    :class:`xml.etree.ElementTree.Element` object for further introspection.

    .. _escape hatches vs ejector seats: https://anvil.works/blog/escape-hatches-and-ejector-seats

Although usually not required directly, the MOS Element classes can be imported
as follows::

    from mosromgr.moselements import Story

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
