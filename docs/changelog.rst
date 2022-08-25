.. mosromgr: Python library for managing MOS running orders
.. Copyright 2021 BBC
.. SPDX-License-Identifier: Apache-2.0

=========
Changelog
=========

.. warning::

    Note that the library is currently in beta. The API and CLI are not yet
    stable and may change. Once the library reaches v1.0, it will be considered
    stable. Please consider giving :doc:`feedback` to help stabilise the API.

Release 0.10.0 (2022-08-25)
===========================

- Add type hints
- Remove ``RunningOrderControl`` class
- Add support for various edge cases in ``merge`` methods, fixing several bugs
- Increase test coverage for :ref:`xml`, :doc:`api/moscollection`,
  :doc:`api/moselements` and :doc:`api/mostypes` to 100%

Release 0.9.1 (2021-09-02)
==========================

- Add :attr:`~mosromgr.moselements.Item.type`,
  :attr:`~mosromgr.moselements.Item.object_id`,  and
  :attr:`~mosromgr.moselements.Item.mos_id` properties to the
  :class:`~mosromgr.moselements.Item` class

Release 0.9.0 (2021-06-21)
==========================

- Updated :doc:`cli/inspect` CLI command to work for all file types
- Corrected some singular :class:`~mosromgr.mostypes.MosFile`
  :doc:`MOS element <api/moselements>` properties that should have been lists
  (e.g. ``source_story`` should have been ``source_stories``)
- Improved validation and error handling when merging various
  :class:`~mosromgr.mostypes.MosFile` objects
- Added :attr:`~mosromgr.moselements.Story.script` and
  :attr:`~mosromgr.moselements.Story.body` to
  :class:`~mosromgr.moselements.Story`
- Added :attr:`~mosromgr.mostypes.RunningOrder.script` and
  :attr:`~mosromgr.mostypes.RunningOrder.body` to
  :class:`~mosromgr.mostypes.RunningOrder`
- Added non-strict mode to the :class:`~mosromgr.moscollection.MosCollection`
  :meth:`~mosromgr.moscollection.MosCollection.merge` method and the
  :doc:`cli/merge` CLI command
- Corrected some edge cases in :class:`~mosromgr.mostypes.MosFile` subclass
  merge implementations (e.g. empty ``storyID`` tag means move to bottom)

Release 0.8.1 (2021-04-14)
==========================

- Fixup release

Release 0.8.0 (2021-04-13)
==========================

- Improved validation and error handling when merging various
  :class:`~mosromgr.mostypes.MosFile` objects
- Added more arguments to CLI commands
- Corrected some singular :class:`~mosromgr.mostypes.MosFile`
  :doc:`api/moselements` properties that should have been lists (e.g.
  ``source_story`` should have been ``source_stories``)

Release 0.7.0 (2021-01-08)
==========================

- Ensured exceptions are raised when story IDs are not found when merging
- Ensured tags aren't overwritten when they are empty in
  :class:`~mosromgr.mostypes.MetaDataReplace`
- Ensured target story is found when merging
  :class:`~mosromgr.mostypes.StoryInsert` and
  :class:`~mosromgr.mostypes.StoryReplace`
- Added ``RunningOrderControl`` class (for ``roCtrl`` messages)
- Changed ``tx_time`` to :attr:`~mosromgr.mostypes.RunningOrder.start_time`

Release 0.6.0 (2020-12-01)
==========================

- Added support for ``<StoryDuration>`` as an alternative to ``<MediaTime>`` and
  ``<TextTime>``

Release 0.5.0 (2020-11-30)
==========================

- Added :class:`~mosromgr.mostypes.ReadyToAir` MOS Type
- Improved error message on invalid
  :class:`~mosromgr.moscollection.MosCollection`

Release 0.4.0 (2020-11-30)
==========================

- Changed ``closed`` property to
  :attr:`~mosromgr.mostypes.RunningOrder.completed`
- Added transmission time and offset to :class:`~mosromgr.moselements.Story`
  class
- New :doc:`cli/index` with separate commands for :doc:`cli/detect`,
  :doc:`cli/inspect` and :doc:`cli/merge`
- Make :class:`~mosromgr.moscollection.MosCollection` raise exceptions on
  failure, not just warnings

Release 0.3.0 (2020-11-24)
==========================

- Switched from complicated ``__init__`` constructors to multiple ``from_``
  classmethods e.g. :meth:`~mosromgr.mostypes.RunningOrder.from_file()`
- Replaced ``get_mos_object`` function with detection logic in the
  :class:`~mosromgr.mostypes.MosFile` and
  :class:`~mosromgr.mostypes.ElementAction` base classes
- Replaced ``MosContainer`` class with
  :class:`~mosromgr.moscollection.MosCollection`

Release 0.2.0 (2020-11-24)
==========================

- Added :doc:`api/moselements` - a collection of classes used to provide easy
  access to certain elements within a :class:`~mosromgr.mostypes.MosFile` object

Release 0.1.0 (2020-11-24)
==========================

- Implemented most standard MOS message types as
  :class:`~mosromgr.mostypes.MosFile` subclasses, supporting merging subsequent
  messages into the original running order
- Implemented a MOS file detection function (``get_mos_object``)
- Added a ``MOSContainer`` class as a wrapper for a complete programme
- Added a :doc:`cli/index` for merging MOS files
