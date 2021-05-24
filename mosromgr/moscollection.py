# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

import logging
import warnings

from .mostypes import MosFile, RunningOrder, RunningOrderEnd
from .utils import s3
from .exc import MosMergeError, InvalidMosCollection, MosMergeNonStrictWarning


logger = logging.getLogger('mosromgr.moscollection')
logging.basicConfig(level=logging.INFO)


class MosReader:
    """
    Internal construct for opening and inspecting a MOS file for the purposes of
    classifying, sorting and validating a :class:`MosCollection`. Provides the
    means to reconstruct the :class:`~mosromgr.mostypes.MosFile` instance when
    needed in order to preserve memory usage.
    """
    def __init__(self, mo, *, restore_fn, restore_args):
        self._message_id = mo.message_id
        self._ro_id = mo.ro_id
        self._mos_type = mo.__class__
        self._restore_fn = restore_fn
        self._restore_args = restore_args

    @classmethod
    def from_file(cls, mos_file_path):
        mo = MosFile.from_file(mos_file_path)
        # store a method of restoring the mos object from the determined class
        return cls(mo,
                   restore_fn=mo.__class__.from_file,
                   restore_args=(mos_file_path, ))

    @classmethod
    def from_string(cls, mos_file_contents):
        mo = MosFile.from_string(mos_file_contents)
        # store a method of restoring the mos object from the determined class
        return cls(mo,
                   restore_fn=mo.__class__.from_string,
                   restore_args=(mos_file_contents, ))

    @classmethod
    def from_s3(cls, bucket_name, mos_file_key):
        mo = MosFile.from_s3(bucket_name=bucket_name, mos_file_key=mos_file_key)
        # store a method of restoring the mos object from the determined class
        return cls(mo,
                   restore_fn=mo.__class__.from_s3,
                   restore_args=(bucket_name, mos_file_key))

    def __repr__(self):
        return f'<{self.__class__.__name__} type {self.mos_type.__name__}>'

    def __lt__(self, other):
        return self.message_id < other.message_id

    def __gt__(self, other):
        return self.message_id > other.message_id

    @property
    def message_id(self):
        "The message ID of the MOS file (:class:`str`)"
        return self._message_id

    @property
    def ro_id(self):
        "The MOS file's running order ID (:class:`str`)"
        return self._ro_id

    @property
    def mos_type(self):
        """
        The :class:`~mosromgr.mostypes.MosFile` subclass this object was
        classified as (returns the class object, not an instance or a string)
        """
        return self._mos_type

    @property
    def mos_object(self):
        """
        Restore the MOS object and return it
        (:class:`~mosromgr.mostypes.MosFile`)
        """
        return self._restore_fn(*self._restore_args)


class MosCollection:
    """
    Wrapper for a collection of MOS files representing a partial or complete
    programme
    """
    def __init__(self, mos_readers, *, allow_incomplete=False):
        logger.info("Making MosCollection from %s MosReaders", len(mos_readers))
        self._mos_readers = mos_readers
        self._ro = None
        try:
            self._validate(allow_incomplete=allow_incomplete)
        except AssertionError as e:
            raise InvalidMosCollection(f"Failed to validate MosCollection: {e}") from e

    @classmethod
    def from_files(cls, mos_file_paths, *, allow_incomplete=False):
        """
        Construct from a list of MOS file paths

        :type mos_file_paths:
            list
        :param mos_file_paths:
            A list of paths to MOS files

        :type allow_incomplete:
            bool
        :param allow_incomplete:
            If ``False`` (the default), the collection is permitted to be
            constructed without a ``roDelete``. If ``True``, a
            :class:`~mosromgr.exc.InvalidMosCollection` will be raised if one is
            not present. (keyword-only argument)
        """
        logger.info("Making MosCollection from %s files", len(mos_file_paths))
        mos_readers = sorted([
            mr
            for mr in [MosReader.from_file(mfp) for mfp in mos_file_paths]
            if mr is not None
        ])
        return cls(mos_readers, allow_incomplete=allow_incomplete)

    @classmethod
    def from_strings(cls, mos_file_strings, *, allow_incomplete=False):
        """
        Construct from a list of MOS document XML strings

        :type mos_file_paths:
            list
        :param mos_file_paths:
            A list of paths to MOS files

        :type allow_incomplete:
            bool
        :param allow_incomplete:
            If ``False`` (the default), the collection is permitted to be
            constructed without a ``roDelete``. If ``True``, a
            :class:`~mosromgr.exc.InvalidMosCollection` will be raised if one is
            not present. (keyword-only argument)
        """
        logger.info("Making MosCollection from %s strings", len(mos_file_strings))
        mos_readers = sorted([
            mr
            for mr in [MosReader.from_string(mfs) for mfs in mos_file_strings]
            if mr is not None
        ])
        return cls(mos_readers, allow_incomplete=allow_incomplete)

    @classmethod
    def from_s3(cls, *, bucket_name, prefix, suffix='.mos.xml', allow_incomplete=False):
        """
        Construct from a list of MOS files in an S3 bucket

        :type bucket_name:
            str
        :param bucket_name:
            The name of the S3 bucket (keyword-only argument)

        :type prefix:
            str
        :param prefix:
            The prefix of the file keys in the S3 bucket (keyword-only argument)

        :type suffix:
            str
        :param suffix:
            The suffix of the file keys in the S3 bucket (keyword-only argument).
            Defaults to '.mos.xml'.

        :type allow_incomplete:
            bool
        :param allow_incomplete:
            If ``True``, the collection is permitted to be constructed without a
            ``roDelete``. If ``False`` (the default), a
            :class:`~mosromgr.exc.InvalidMosCollection` will be raised if one is
            not present. (keyword-only argument)
        """
        mos_file_keys = s3.get_mos_files(
            bucket_name=bucket_name,
            prefix=prefix,
            suffix=suffix,
        )
        logger.info("Making MosCollection from %s S3 files", len(mos_file_keys))
        mos_readers = sorted([
            mr
            for mr in [MosReader.from_s3(bucket_name, key) for key in mos_file_keys]
            if mr is not None
        ])
        return cls(mos_readers, allow_incomplete=allow_incomplete)

    def __repr__(self):
        if self.ro is not None:
            return f'<{self.__class__.__name__} {self.ro_slug}>'
        return f'<{self.__class__.__name__}>'

    def __str__(self):
        "The XML string of the collection's running order"
        return str(self.ro)

    @property
    def mos_readers(self):
        """
        A list of :class:`MosReader` objects representing all MOS files in the
        collection, except the :class:`~mosromgr.mostypes.RunningOrder`
        (``roCreate``) which is held in :attr:`ro`
        """
        return self._mos_readers

    @property
    def ro(self):
        "The collection's :class:`~mosromgr.mostypes.RunningOrder` object"
        return self._ro

    @property
    def ro_id(self):
        "The running order ID"
        return self.ro.ro_id

    @property
    def ro_slug(self):
        "The running order slug"
        return self.ro.ro_slug

    @property
    def completed(self):
        """
        Whether or not the running order has had a
        :class:`~mosromgr.mostypes.RunningOrderEnd` merged (:class:`bool`)
        """
        return self.ro.completed

    def _validate(self, allow_incomplete=False):
        """
        Check a single roCreate is present, and if *allow_incomplete* is True,
        also check a single roDelete is present.
        """
        ro_id = self.mos_readers[0].ro_id
        assert all(mr.ro_id == ro_id for mr in self.mos_readers), "Mixed RO IDs found"
        ro_creates = [
            mr for mr in self.mos_readers if mr.mos_type == RunningOrder
        ]
        assert len(ro_creates) == 1, f"{len(ro_creates)} roCreates found"
        self._ro = ro_creates[0].mos_object
        ro_deletes = [
            mr for mr in self.mos_readers if mr.mos_type == RunningOrderEnd
        ]
        assert len(ro_deletes) < 2, f"{len(ro_deletes)} roDeletes found"
        if not allow_incomplete:
            assert len(ro_deletes) == 1, f"{len(ro_deletes)} roDeletes found"
        self._mos_readers = [
            mr for mr in self.mos_readers if mr.mos_type != RunningOrder
        ]

    def merge(self, *, strict=True):
        """
        Merge all MOS files into the collection's running order (:attr:`ro`). If
        *strict* is ``True`` (the default), then merge errors will be fatal. If
        ``False``, then merge errors will be downgraded to warnings.
        """
        logger.info("Merging %s MosReaders into RunningOrder", len(self.mos_readers))
        for mr in self.mos_readers:
            mo = mr.mos_object
            logger.info("Merging %s %s", mo.__class__.__name__, mr.message_id)
            try:
                self._ro += mo
            except MosMergeError as e:
                if strict:
                    raise
                logger.error(str(e))
                warnings.warn(str(e), MosMergeNonStrictWarning)
        logger.info("Completed merging %s mos files", len(self.mos_readers))
