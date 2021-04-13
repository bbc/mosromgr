.. mosromgr: Python library for managing MOS running orders
.. Copyright 2021 BBC
.. SPDX-License-Identifier: Apache-2.0

=========
Changelog
=========

.. warning::
    Note that the library is currently in beta. The API and CLI are not yet
    stable and may change. Once the library reaches v1.0, it will be considered
    stable. Please consider giving :doc:`feedback` to help stablise the API.

Release 0.8.0 (TBC)
===================

- Improved validation and error handling when merging various
  :class:`~mosromgr.mostypes.MosFile` objects
- Added more arguments to CLI commands

Release 0.7.0 (2021-01-08)
==========================

- Ensured exceptions are raised when story IDs are not found when merging
- Ensured tags aren't overwritten when they are empty in
  :class:`~mosromgr.mostypes.MetaDataReplace`
- Ensured target story is found when merging
  :class:`~mosromgr.mostypes.StoryInsert` and
  :class:`~mosromgr.mostypes.StoryReplace`
- Added :class:`~mosromgr.mostypes.RunningOrderControl` class (for ``roCtrl``
  messages)
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
- New :doc:`cli` with separate commands for ``detect``, ``inspect`` and
  ``merge``
- Make MosCollection raise exceptions on failure, not just warnings

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

- Added :doc:`api_moselements` - a collection of classes used to provide easy
  access to certain elements within a :class:`~mosromgr.mostypes.MosFile` object

Release 0.1.0 (2020-11-24)
==========================

- Implemented most standard MOS message types as
  :class:`~mosromgr.mostypes.MosFile` subclasses, supporting merging subsequent
  messages into the original running order
- Implemented a MOS file detection function (``get_mos_object``)
- Added a ``MOSContainer`` class as a wrapper for a complete programme
- Added a CLI for merging MOS files
