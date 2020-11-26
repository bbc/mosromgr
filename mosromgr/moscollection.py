from collections import namedtuple
import logging
import warnings

from .mostypes import MosFile, RunningOrder, RunningOrderEnd
from .exc import (
    InvalidMosCollection, MosMergeError, MosInvalidXML, UnknownMosFileType,
    UnknownMosFileTypeWarning, MosInvalidXMLWarning, MosMergeWarning
)


logger = logging.getLogger('mosromgr.moscollection')
logging.basicConfig(level=logging.INFO)


class MosReader:
    def __init__(self, mo, *, restore_fn, restore_args):
        self.message_id = mo.message_id
        self.ro_id = mo.ro_id
        self.mos_type = mo.__class__
        self._restore_fn = restore_fn
        self._restore_args = restore_args

    @classmethod
    def from_file(cls, mos_file_path):
        try:
            mo = MosFile.from_file(mos_file_path)
            # store a method of restoring the mos object from the determined class
            return cls(mo,
                       restore_fn=mo.__class__.from_file,
                       restore_args=(mos_file_path, )
            )
        except MosInvalidXML as e:
            warnings.warn(str(e), MosInvalidXMLWarning)
        except UnknownMosFileType as e:
            warnings.warn(str(e), UnknownMosFileTypeWarning)

    @classmethod
    def from_string(cls, mos_file_contents):
        try:
            mo = MosFile.from_string(mos_file_contents)
            # store a method of restoring the mos object from the determined class
            return cls(mo,
                        restore_fn=mo.__class__.from_string,
                        restore_args=(mos_file_contents, )
            )
        except MosInvalidXML as e:
            warnings.warn(e, MosInvalidXMLWarning)
        except UnknownMosFileType as e:
            warnings.warn(e, UnknownMosFileTypeWarning)

    @classmethod
    def from_s3(cls, bucket_name, mos_file_key):
        try:
            mo = MosFile.from_s3(bucket_name=bucket_name, mos_file_key=mos_file_key)
            # store a method of restoring the mos object from the determined class
            return cls(mo,
                       restore_fn=mo.__class__.from_s3,
                       restore_args=(bucket_name, mos_file_key)
            )
        except MosInvalidXML as e:
            warnings.warn(e, MosInvalidXMLWarning)
        except UnknownMosFileType as e:
            warnings.warn(e, UnknownMosFileTypeWarning)

    def __repr__(self):
        return f'<{self.__class__.__name__} type {self.mos_type.__name__}>'

    def __lt__(self, other):
        return self.message_id < other.message_id

    def __gt__(self, other):
        return self.message_id > other.message_id

    @property
    def mos_object(self):
        return self._restore_fn(*self._restore_args)


class MosCollection:
    """
    Wrapper for a collection of MOS files representing a partial or complete
    programme
    """
    def __init__(self, mos_readers, *, allow_incomplete=False):
        logger.info("Making MosCollection from %s MosReaders", len(mos_readers))
        self.mos_readers = mos_readers
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
    def from_s3(cls, *, bucket_name, mos_file_keys, allow_incomplete=False):
        """
        Construct from a list of MOS files in an S3 bucket

        :type bucket_name:
            str
        :param bucket_name:
            The name of the S3 bucket (keyword-only argument)

        :type mos_file_keys:
            list
        :param mos_file_keys:
            A list of file keys within the S3 bucket (keyword-only argument)

        :type allow_incomplete:
            bool
        :param allow_incomplete:
            If ``False`` (the default), the collection is permitted to be
            constructed without a ``roDelete``. If ``True``, a
            :class:`~mosromgr.exc.InvalidMosCollection` will be raised if one is
            not present. (keyword-only argument)
        """
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

    def _validate(self, allow_incomplete=False):
        """
        Check a single roCreate is present, and if *allow_incomplete* is True,
        also check a single roDelete is present.
        """
        ro_id = self.mos_readers[0].ro_id
        assert all(mr.ro_id == ro_id for mr in self.mos_readers)
        ro_creates = [
            mr for mr in self.mos_readers if mr.mos_type == RunningOrder
        ]
        assert len(ro_creates) == 1, len(ro_creates)
        self._ro = ro_creates[0].mos_object
        ro_deletes = [
            mr for mr in self.mos_readers if mr.mos_type == RunningOrderEnd
        ]
        assert len(ro_deletes) < 2
        if not allow_incomplete:
            assert len(ro_deletes) == 1, len(ro_deletes)
        self.mos_readers = [
            mr for mr in self.mos_readers if mr.mos_type != RunningOrder
        ]

    def merge(self):
        "Merge all MOS files into the collection's running order (:attr:`ro`)"
        logger.info("Merging %s MosReaders into RunningOrder", len(self.mos_readers))
        errors = 0
        for mr in self.mos_readers:
            mo = mr.mos_object
            logger.info("Merging %s %s", mr.mos_type, mr.message_id)
            try:
                self._ro += mo
            except MosMergeError as e:
                errors += 1
                warnings.warn(str(e), MosMergeWarning)
        logger.info("Completed merging %s mos files with %s errors",
                    len(self.mos_readers), errors)
