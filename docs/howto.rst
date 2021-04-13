.. mosromgr: Python library for managing MOS running orders
.. Copyright 2021 BBC
.. SPDX-License-Identifier: Apache-2.0

============
How-to guide
============

This section is a series of helpful recipes for how to do things and solve
particular problems with *mosromgr*.

.. note::
    These examples deal with MOS messages read from local files, but
    :class:`~mosromgr.mostypes.MosFile` and
    :class:`~mosromgr.moscollection.MosCollection` objects can also be
    constructed using :class:`~mosromgr.mostypes.MosFile.from_string` and
    :class:`~mosromgr.mostypes.MosFile.from_s3`. Refer to :doc:`api_mostypes`
    and :doc:`api_moscollection` for more information.

Merging MOS files
=================

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

.. note::
    Note that these classes should not normally be constructed by the user, but
    instances of them can be found within :class:`~mosromgr.mostypes.MosFile`
    objects, so the following documentation is provided as a reference to how
    they can be used.

.. note::
    Note that additional information may be contained within the XML, and these
    elements are simply an abstraction providing easy access to certain
    elements. In the sprit of `escape hatches and ejector seats`_, the original
    XML in which the element was found is accessible as an
    :class:`xml.etree.ElementTree.Element` object for further introspection.

    .. _escape hatches and ejector seats: https://anvil.works/blog/escape-hatches-and-ejector-seats

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

.. _cli_howto:

Using the command line interface
================================

The ``mosromgr`` command provided includes a number of subcommands. Running
``mosromgr`` alone will show the general help message, and running a subcommand
without arguments will show the help message for that subcommand.

Detecting MOS file types
------------------------

To detect the type of a MOS file, use the :ref:`cli_mosromgr_detect` command:

.. code-block:: console

    $ mosromgr detect -f 123456-roCreate.mos.xml
    123456-roCreate.mos.xml: RunningOrder

Multiple files can be provided as arguments:

.. code-block:: console

    $ mosromgr detect -f 123456-roCreate.mos.xml 123457-roStorySend.mos.xml
    123456-roCreate.mos.xml: RunningOrder
    123457-roStorySend.mos.xml: StorySend

Wildcards can also be used:

.. code-block:: console

    $ mosromgr detect *
    123456-roCreate.mos.xml: RunningOrder
    123457-roStorySend.mos.xml: StorySend
    ...
    9148627-roDelete.mos.xml: RunningOrderEnd
    bbcProgrammeMetadata.xml: Unknown MOS file type
    cricket: Invalid
    FINAL.json: Invalid
    FINAL.xml: RunningOrder (completed)

You can also read files from an S3 bucket. Either a specific file by key:

.. code-block:: console

    $ mosromgr detect -b my-bucket -k newsnight/20210101/123456-roCreate.mos.xml
    INFO:botocore.credentials:Found credentials in environment variables.
    OPENMEDIA_NCS.W1.BBC.MOS/OM_10.1253459/5744992-roCreate.mos.xml: RunningOrder

Or a whole folder by prefix:

.. code-block:: console

    $ mosromgr detect -b bbc-newslabs-slicer-mos-message-store -p newsnight/20210101/
    INFO:botocore.credentials:Found credentials in environment variables.
    newsnight/20210101/123456-roCreate.mos.xml: RunningOrder
    newsnight/20210101/123457-roStorySend.mos.xml: StorySend
    newsnight/20210101/123458-roStorySend.mos.xml: StorySend
    newsnight/20210101/123459-roStorySend.mos.xml: StorySend
    ...

Inspecting a running order
--------------------------

To inspect the contents of a ``roCreate`` file, use the
:ref:`cli_mosromgr_inspect` command:

.. code-block:: console

    $ mosromgr inspect -f 123456-roCreate.mos.xml
    22:45 NEWSNIGHT 54D CORE Thu, 08.04.2021

Many options are available which allow for inspecting a file from an S3 bucket
(``-b`` and ``-k``) instead of a local file (``-f``); and others which affect the
output such as ``-t`` (start time), ``-d`` (duration), ``-s`` (stories):

.. code-block:: console

    $ mosromgr inspect -b my-bucket -k newsnight/20210804/123456-roCreate.mos.xml -tds
    22:45 NEWSNIGHT 54D CORE Thu, 08.04.2021
    Start time: 2021-04-08 21:46
    Duration: 0:35:09

    MENU START

    MENU-PRE TITLE TEASE

    MENU-TITLES

    MENU-POST TITLE "ALSO TONIGHT"

    NORTHERN IRELAND-INTRO

    NORTHERN IRELAND-LEWIS PACKAGE

    ...

    END OF PROGRAMME

.. note:
    Note that this command currently only works for ``roCreate`` files,
    but this includes ``roCreate`` files which have had additional files merged
    into it, whether complete or not.

Merging MOS files
-----------------

To merge a set of MOS files for a programme, use the :ref:`cli_mosromgr_merge`
command.

Merging local files:

.. code-block:: console

    $ mosromgr merge -f *.mos.xml -o FINAL.xml
    ...
    INFO:mosromgr.moscollection:Merging RunningOrderEnd 123499
    INFO:mosromgr.moscollection:Completed merging 99 mos files
    Writing merged running order to FINAL.xml

Or files in an S3 bucket folder by prefix:

.. code-block:: console

    $ mosromgr merge -b my-bucket -p newsnight/20210101/ -o
    ...
    INFO:mosromgr.moscollection:Merging RunningOrderEnd 123499
    INFO:mosromgr.moscollection:Completed merging 99 mos files
    Writing merged running order to FINAL.xml
