import pytest
from mock import patch
import warnings

from mosromgr.moscollection import *
from mosromgr.mostypes import *
from mosromgr.exc import *
from const import *


def test_mos_collection_init_path():
    """
    GIVEN: A list containing a filepath to a roCreate and roDelete message
    EXPECT: MosCollection object with 1 file
    """
    mos_files = [ROCREATE, RODELETE]
    mc = MosCollection.from_files(mos_files)
    assert repr(mc) == "<MosCollection RO SLUG>"
    assert isinstance(mc.ro, RunningOrder)
    assert isinstance(mc.mos_readers, list)
    assert len(mc.mos_readers) == 1

def test_mos_collection_bad_init_params():
    "Test MosCollection cannot be created with bad input"
    with pytest.raises(TypeError):
        MosCollection.from_files()
    with pytest.raises(TypeError):
        MosCollection.from_s3(bucket_name='bucket_name')
    with pytest.raises(TypeError):
        MosCollection.from_files(mos_file_keys=['a', 'b', 'c'])

def test_mos_collection_bad_init():
    "Test MosCollection cannot be created without a roCreate message"
    mos_files = [ROSTORYSEND1]
    with pytest.raises(InvalidMosCollection):
        MosCollection.from_files(mos_files)

    mos_files = [ROCREATE]
    with pytest.raises(InvalidMosCollection):
        MosCollection.from_files(mos_files)

    mos_files = [RODELETE]
    with pytest.raises(InvalidMosCollection):
        MosCollection.from_files(mos_files)

    mos_files = [ROCREATE, ROSTORYSEND1]
    with pytest.raises(InvalidMosCollection):
        MosCollection.from_files(mos_files)

    mos_files = [ROCREATE, ROCREATE2, RODELETE]
    with pytest.raises(InvalidMosCollection):
        MosCollection.from_files(mos_files)

    mos_files = [ROCREATE, RODELETE, RODELETE2]
    with pytest.raises(InvalidMosCollection):
        MosCollection.from_files(mos_files)

def test_mos_collection_bad_init_mixed_ids():
    "Test MosCollection cannot be created with messages with mixed RO IDs"
    mos_files = [ROCREATE, RODELETE2]
    with pytest.raises(InvalidMosCollection):
        MosCollection.from_files(mos_files)

def test_mos_collection_init_files_after_rodelete():
    """
    GIVEN: A list of MOS files with messages following roDelete
    EXPECT: MosCollection object with 2 files, plus warning on merge
    """
    mos_files = [ROCREATE, RODELETE, ROSTORYSEND4]
    mc = MosCollection.from_files(mos_files)
    assert repr(mc) == "<MosCollection RO SLUG>"
    assert isinstance(mc.ro, RunningOrder)
    assert isinstance(mc.mos_readers, list)
    assert len(mc.mos_readers) == 2
    with warnings.catch_warnings(record=True) as w:
        mc.merge()
    assert len(w) == 1
    assert w[0].category == MosMergeWarning

@patch('mosromgr.utils.s3.boto3')
@patch('mosromgr.utils.s3.get_file_contents')
@patch('mosromgr.utils.s3.get_mos_files')
def test_mos_collection_init_s3(get_mos_files, get_file_contents, boto3):
    """
    GIVEN: A bucket name and prefix (mocked to contain two files)
    EXPECT: MosCollection object with 1 reader
    """
    with open(ROCREATE) as f:
        rocreate = f.read()
    with open(RODELETE) as f:
        rodelete = f.read()

    get_mos_files.return_value = ['roCreate.mos.xml', 'roDelete.mos.xml']
    get_file_contents.side_effect = [rocreate, rodelete, rocreate, rodelete]

    mc = MosCollection.from_s3(bucket_name='bucket_name', prefix='newsnight')
    assert repr(mc) == "<MosCollection RO SLUG>"
    assert isinstance(mc.ro, RunningOrder)
    assert isinstance(mc.mos_readers, list)
    assert len(mc.mos_readers) == 1

def test_mos_collection_init_multiple_files():
    "Test collection can be created from multiple files"
    mc = MosCollection.from_files(RO_ALL)
    assert repr(mc) == "<MosCollection RO SLUG>"
    assert isinstance(mc.ro, RunningOrder)
    assert isinstance(mc.mos_readers, list)
    assert len(mc.mos_readers) == len(RO_ALL) - 1

def test_mos_collection_init_multiple_files_sorted():
    "Test collection can sort input files by messageID field"
    mos_files = [ROSTORYSEND2, ROCREATE, ROSTORYSEND1, RODELETE]
    mc = MosCollection.from_files(mos_files)
    assert isinstance(mc.ro, RunningOrder)
    assert isinstance(mc.mos_readers, list)
    assert len(mc.mos_readers) == 3
    mf1, mf2, mf3 = mc.mos_readers
    assert mf1.message_id == 1001
    assert mf2.message_id == 1002

def test_mos_collection_unsupported_mos_type():
    """
    GIVEN: Running order and invalid mos message, in list form
    EXPECT: MosCollection object with running order and no other files
    """
    mos_files = [ROCREATE, ROINVALID, RODELETE]
    with warnings.catch_warnings(record=True) as w:
        mc = MosCollection.from_files(mos_files)
    assert len(w) == 1
    assert w[0].category == UnknownMosFileTypeWarning
    assert isinstance(mc.ro, RunningOrder)
    assert isinstance(mc.mos_readers, list)
    assert len(mc.mos_readers) == 1

def test_mos_collection_merge():
    """
    GIVEN: Running order and EAStoryInsert paths
    EXPECT: Running order summary, with story from EAStoryInsert added
    """
    mos_files = [ROCREATE, ROELEMENTACTIONINSERTSTORY, RODELETE]
    mc = MosCollection.from_files(mos_files)
    assert len(mc.mos_readers) == 2
    d = mc.ro.dict
    assert len(d['mos']['roCreate']['story']) == 3

    mc.merge()
    d = mc.ro.dict
    assert len(d['mos']['roCreate']['story']) == 4

@patch('mosromgr.utils.s3.boto3')
@patch('mosromgr.utils.s3.get_file_contents')
@patch('mosromgr.utils.s3.get_mos_files')
def test_mos_collection_s3_merge(get_mos_files, get_file_contents, boto3):
    """
    GIVEN: Bucket prefix matching a roCreate and ElementAction (StoryInsert)
    EXPECT: Running order summary, with story from EAStoryInsert added
    """
    with open(ROCREATE) as f:
        rc = f.read()
    with open(ROELEMENTACTIONINSERTSTORY) as f:
        ea = f.read()
    with open(RODELETE) as f:
        rd = f.read()

    get_mos_files.return_value = [rc, ea, rd]
    get_file_contents.side_effect = [rc, ea, rd, rc, ea, rd]

    mc = MosCollection.from_s3(bucket_name='bucket_name', prefix='newsnight')
    assert len(mc.mos_readers) == 2
    d = mc.ro.dict
    print(d['mos'].keys())
    assert len(d['mos']['roCreate']['story']) == 3

    mc.merge()
    d = mc.ro.dict
    assert len(d['mos']['roCreate']['story']) == 4

def test_mos_collection_merge_warning():
    """
    GIVEN: Running order and invalid StorySend, in list form
    EXPECT: MosMergeError
    """
    mos_files = [ROCREATE, ROSTORYSEND3, RODELETE]
    mc = MosCollection.from_files(mos_files)
    with warnings.catch_warnings(record=True) as w:
        mc.merge()
    assert len(w) == 1
    assert w[0].category == StoryNotFoundWarning
