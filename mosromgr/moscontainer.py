from collections import namedtuple
import logging
import warnings

from .mosfactory import get_mos_object
from .mostypes import RunningOrder
from .utils import s3
from .exc import MosContainerBadInit, MosClosedMergeError, MergeAfterDeleteWarning


MosReader = namedtuple(
    'MosReader',
    ['message_id', 'ro_id', 'bucket_name', 'mos_file', 'mos_type']
)


class MosContainer:
    """
    Wrapper for a complete programme

    :type mos_file_paths: list
    :param mos_file_paths:
        List of mos_file_paths from the given directory

    :type bucket_name: str
    :param bucket_name:
        S3 bucket name string

    :type mos_file_keys: list
    :param mos_file_keys:
        List of keys of mos files from the S3 bucket

    :type sns: :class:`~mosromgr.utils.sns.SNS` or None
    :param sns:
        SNS object used for lambda notifications
    """
    def __init__(self, mos_file_paths=None, *, bucket_name=None, mos_file_keys=None, sns=None):
        self.logger = logging.getLogger('mos_container')
        self.sns = sns
        if mos_file_paths is None:
            if mos_file_keys is None or bucket_name is None:
                raise TypeError('If mos_file_paths is not used, mos_file_keys and bucket_name must be passed')
            self.logger.info('containerising %s mos_files from S3', len(mos_file_keys))
            self.mos_readers = self._process_mos_file_keys(bucket_name=bucket_name, mos_file_keys=mos_file_keys)
        else:
            self.logger.info('containerising %s mos_files from directory', len(mos_file_paths))
            self.mos_readers = self._process_mos_file_paths(mos_file_paths=mos_file_paths)
        self._validate()
        self.ro_slug = self.ro.ro_slug
        self.ro_id = self.ro.ro_id

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.ro_slug}>'

    def __str__(self):
        return str(self.ro)

    def _process_mos_file_paths(self, mos_file_paths):
        """
        Get message IDs and RO IDs from objects in directory, sorted by message
        ID
        """
        self.ro = None
        mos_readers = []
        for mos_file_path in mos_file_paths:
            mo = get_mos_object(mos_file_path=mos_file_path, sns=self.sns)
            if isinstance(mo, RunningOrder):
                self._save_ro(mo)
            elif mo is not None:
                mos_type = mo.__class__.__name__
                mr = MosReader(mo.message_id, mo.ro_id, None, mos_file_path, mos_type)
                mos_readers.append(mr)
                del mo
        return sorted(mos_readers)

    def _process_mos_file_keys(self, bucket_name, mos_file_keys, sns=None):
        """
        Get message IDs and RO IDs from objects in S3 bucket, sorted by message
        ID
        """
        self.ro = None
        mos_readers = []
        for mos_file_key in mos_file_keys:
            contents = s3.get_file_contents(bucket_name, mos_file_key)
            mo = get_mos_object(mos_file_contents=contents, mos_file_prefix=mos_file_key, sns=self.sns)
            if isinstance(mo, RunningOrder):
                self._save_ro(mo)
            elif mo is not None:
                mos_type = mo.__class__.__name__
                mr = MosReader(mo.message_id, mo.ro_id, bucket_name, mos_file_key, mos_type)
                mos_readers.append(mr)
                del mo
        return sorted(mos_readers)

    def _save_ro(self, mo):
        if self.ro is None:
            self.ro = mo
        else:
            raise MosContainerBadInit('Multiple roCreate files found')

    def _validate(self):
        """
        Check a single :class:`~mosromgr.mostypes.RunningOrder` object, and a
        single :class:`~mosromgr.mostypes.RunningOrderEnd` object is present
        (i.e. ``roCreate`` and ``roDelete``).
        """
        self._check_ro_create()
        ro_deletes = 0
        for mr in self.mos_readers:
            self._check_ro_ids(mr)
            ro_deletes = self._check_ro_delete(mr, ro_deletes)
        self._check_ro_deletes(ro_deletes)

    def _check_ro_create(self):
        if self.ro is None:
            self.logger.error('No roCreate message found')
            if self.sns:
                prefix = '/'.join(self.mos_readers[0].mos_file.split('/')[:-1])
                self.sns.send_sns_notification(self.sns.ERRORLVL, f'No roCreate Message found in bucket: {prefix}')
            raise MosContainerBadInit('No roCreate message found')

    def _check_ro_ids(self, mr):
        if mr.ro_id != self.ro.ro_id:
            self.logger.error(
                'found MOS message with wrong RO ID: %s has RO ID %s, expected %s',
                mr.message_id, mr.ro_id, self.ro.ro_id
            )
            if self.sns:
                self.sns.send_sns_notification(self.sns.ERRORLVL, f'Wrong roID found in file: {mr.mos_file}\nExpected: {self.ro.ro_id}\nFound: {mr.ro_id}')
            raise MosContainerBadInit('Unmatched RO ID')

    def _check_ro_delete(self, mr, ro_deletes):
        if mr.mos_type == 'RunningOrderEnd':
            ro_deletes += 1
        if ro_deletes > 1:
            raise MosContainerBadInit('Multiple roDelete files found')
        return ro_deletes

    def _check_ro_deletes(self, ro_deletes):
        if ro_deletes == 0:
            raise MosContainerBadInit('No roDelete files found')

    def merge(self):
        """
        Merge all MOS files into the :class:`~mosromgr.mostypes.RunningOrder`
        object provided.
        """
        self.logger.info('merging %s mos files', len(self.mos_readers))
        for mr in self.mos_readers:
            if mr.bucket_name is not None:
                contents = s3.get_file_contents(mr.bucket_name, mr.mos_file)
                mo = get_mos_object(mos_file_contents=contents, mos_file_prefix=mr.mos_file, sns=self.sns)
            else:
                mo = get_mos_object(mos_file_path=mr.mos_file, sns=self.sns)
            self.logger.info('merging %s %s', mo.__class__.__name__, mo.message_id)
            try:
                self.ro += mo
            except MosClosedMergeError as e:
                warnings.warn(str(e), MergeAfterDeleteWarning)
            del mo
        self.logger.info('successfully merged %s mos files', len(self.mos_readers))
