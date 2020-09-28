import pytest
from mock import patch
import warnings

from mosromgr.moscontainer import *
from mosromgr.mostypes import *
from mosromgr.exc import *
from const import *


def test_mos_container_init_path():
    """
    GIVEN: A list containing a filepath to a roCreate and roDelete message
    EXPECT: MosContainer object with 1 file
    """
    mos_files = [ROCREATE, RODELETE]
    mc = MosContainer(mos_files)
    assert repr(mc) == "<MosContainer RO SLUG>"
    assert isinstance(mc.ro, RunningOrder)
    assert isinstance(mc.mos_readers, list)
    assert len(mc.mos_readers) == 1

def test_mos_container_bad_init_params():
    "Test MosContainer cannot be created with bad input"
    with pytest.raises(TypeError):
        MosContainer()
    with pytest.raises(TypeError):
        MosContainer(bucket_name='bucket_name')
    with pytest.raises(TypeError):
        MosContainer(mos_file_keys=['a', 'b', 'c'])

def test_mos_container_bad_init():
    "Test MosContainer cannot be created without a roCreate message"
    mos_files = [ROSTORYSEND1]
    with pytest.raises(MosContainerBadInit):
        MosContainer(mos_files)

    mos_files = [ROCREATE]
    with pytest.raises(MosContainerBadInit):
        MosContainer(mos_files)

    mos_files = [RODELETE]
    with pytest.raises(MosContainerBadInit):
        MosContainer(mos_files)

    mos_files = [ROCREATE, ROSTORYSEND1]
    with pytest.raises(MosContainerBadInit):
        MosContainer(mos_files)

    mos_files = [ROCREATE, ROCREATE2, RODELETE]
    with pytest.raises(MosContainerBadInit):
        MosContainer(mos_files)

    mos_files = [ROCREATE, RODELETE, RODELETE2]
    with pytest.raises(MosContainerBadInit):
        MosContainer(mos_files)

def test_mos_container_bad_init_mixed_ids():
    "Test MosContainer cannot be created with messages with mixed IDs"
    mos_files = [ROCREATE, RODELETE2]
    with pytest.raises(MosContainerBadInit):
        MosContainer(mos_files)

def test_mos_container_init_files_after_rodelete():
    """
    GIVEN: A list of MOS files with messages following roDelete
    EXPECT: MosContainer object with 2 file, plus warning on merge
    """
    mos_files = [ROCREATE, RODELETE, ROSTORYSEND4]
    mc = MosContainer(mos_files)
    assert repr(mc) == "<MosContainer RO SLUG>"
    assert isinstance(mc.ro, RunningOrder)
    assert isinstance(mc.mos_readers, list)
    assert len(mc.mos_readers) == 2
    with warnings.catch_warnings(record=True) as w:
        mc.merge()
    assert len(w) == 1
    assert w[0].category == MergeAfterDeleteWarning

@patch('mosromgr.utils.s3.boto3')
@patch('mosromgr.utils.s3.get_file_contents')
def test_mos_container_init_s3(get_file_contents, boto3):
    """
    GIVEN: A list containing the contents of a roCreate as a string
    EXPECT: MosContainer object
    """
    with open(ROCREATE) as f:
        rocreate = f.read()
    with open(RODELETE) as f:
        rodelete = f.read()

    get_file_contents.side_effect = [rocreate, rodelete]

    bucket_name = 'bucket_name'
    mos_file_keys = ['key', 'key']
    mc = MosContainer(bucket_name=bucket_name, mos_file_keys=mos_file_keys)
    assert repr(mc) == "<MosContainer RO SLUG>"
    assert isinstance(mc.ro, RunningOrder)
    assert isinstance(mc.mos_readers, list)
    assert len(mc.mos_readers) == 1

def test_mos_container_init_multiple_files():
    "Test container can be created from multiple files"
    mc = MosContainer(RO_ALL)
    assert repr(mc) == "<MosContainer RO SLUG>"
    assert isinstance(mc.ro, RunningOrder)
    assert isinstance(mc.mos_readers, list)
    assert len(mc.mos_readers) == len(RO_ALL) - 1

def test_mos_container_init_multiple_files_sorted():
    "Test container can sort input files by messageID field"
    mos_files = [ROSTORYSEND2, ROCREATE, ROSTORYSEND1, RODELETE]
    mc = MosContainer(mos_files)
    assert isinstance(mc.ro, RunningOrder)
    assert isinstance(mc.mos_readers, list)
    assert len(mc.mos_readers) == 3
    mf1, mf2, mf3 = mc.mos_readers
    assert mf1.message_id == 1001
    assert mf2.message_id == 1002

def test_mos_container_unsupported_mos_type():
    """
    GIVEN: Running order and invalid mos message, in list form
    EXPECT: MosContainer object with running order and no other files
    """
    mos_files = [ROCREATE, ROINVALID, RODELETE]
    with warnings.catch_warnings(record=True) as w:
        mc = MosContainer(mos_files)
    assert len(w) == 1
    assert w[0].category == UnknownMosFileTypeWarning
    assert isinstance(mc.ro, RunningOrder)
    assert isinstance(mc.mos_readers, list)
    assert len(mc.mos_readers) == 1

def test_mos_container_merge():
    """
    GIVEN: Running order and EAInsertStory paths
    EXPECT: Running order summary, with story from EAInsertStory added
    """
    mos_files = [ROCREATE, ROELEMENTACTIONINSERTSTORY, RODELETE]
    mc = MosContainer(mos_files)
    assert len(mc.mos_readers) == 2
    d = mc.ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 3

    mc.merge()
    d = mc.ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 4

@patch('mosromgr.utils.s3.boto3')
@patch('mosromgr.utils.s3.get_file_contents')
def test_mos_container_s3_merge(get_file_contents, boto3):
    """
    GIVEN: Running order and EAInsertStory s3 keys
    EXPECT: Running order summary, with story from EAInsertStory added
    """
    with open(ROCREATE) as f:
        rc = f.read()
    with open(ROELEMENTACTIONINSERTSTORY) as f:
        ea = f.read()
    with open(RODELETE) as f:
        rd = f.read()
    # we call get_file_contents on rc once, and ea/rd twice
    get_file_contents.side_effect = [rc, ea, rd, ea, rd]

    # contents of these vars are ignored
    # but len of mos_file_keys needs to be correct
    bucket_name = 'bucket_name'
    mos_file_keys = ['rc', 'ea', 'rd']
    mc = MosContainer(bucket_name=bucket_name, mos_file_keys=mos_file_keys)
    assert len(mc.mos_readers) == 2
    d = mc.ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 3

    mc.merge()
    d = mc.ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 4

def test_mos_container_merge_warning():
    """
    GIVEN: Running order and invalid StorySend, in list form
    EXPECT: MosMergeError
    """
    mos_files = [ROCREATE, ROSTORYSEND3, RODELETE]
    mc = MosContainer(mos_files)
    with warnings.catch_warnings(record=True) as w:
        mc.merge()
    assert len(w) == 1
    assert w[0].category == StoryNotFoundWarning
