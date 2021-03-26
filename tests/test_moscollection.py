# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

import pytest
from mock import patch
import warnings

from mosromgr.moscollection import *
from mosromgr.mostypes import *
from mosromgr.exc import *


def test_mos_collection_init_path(rocreate, rodelete):
    """
    GIVEN: A list containing a filepath to a roCreate and roDelete message
    EXPECT: MosCollection object with 1 file
    """
    mos_files = [rocreate, rodelete]
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

def test_mos_collection_bad_init(rostorysend1, rocreate, rodelete, rocreate2, rodelete2):
    "Test MosCollection cannot be created without a roCreate message"
    mos_files = [rostorysend1]
    with pytest.raises(InvalidMosCollection):
        MosCollection.from_files(mos_files)

    mos_files = [rocreate]
    with pytest.raises(InvalidMosCollection):
        MosCollection.from_files(mos_files)

    mos_files = [rodelete]
    with pytest.raises(InvalidMosCollection):
        MosCollection.from_files(mos_files)

    mos_files = [rocreate, rostorysend1]
    with pytest.raises(InvalidMosCollection):
        MosCollection.from_files(mos_files)

    mos_files = [rocreate, rocreate2, rodelete]
    with pytest.raises(InvalidMosCollection):
        MosCollection.from_files(mos_files)

    mos_files = [rocreate, rodelete, rodelete2]
    with pytest.raises(InvalidMosCollection):
        MosCollection.from_files(mos_files)

def test_mos_collection_bad_init_mixed_ids(rocreate, rodelete2):
    "Test MosCollection cannot be created with messages with mixed RO IDs"
    mos_files = [rocreate, rodelete2]
    with pytest.raises(InvalidMosCollection):
        MosCollection.from_files(mos_files)

def test_mos_collection_init_files_after_rodelete(rocreate, rodelete, rodelete2, rostorysend4):
    """
    GIVEN: A list of MOS files with messages following roDelete
    EXPECT: MosCollection object with 2 files, plus warning on merge
    """
    mos_files = [rocreate, rodelete, rostorysend4]
    mc = MosCollection.from_files(mos_files)
    assert repr(mc) == "<MosCollection RO SLUG>"
    assert isinstance(mc.ro, RunningOrder)
    assert isinstance(mc.mos_readers, list)
    assert len(mc.mos_readers) == 2
    with pytest.raises(MosMergeError):
        mc.merge()

@patch('mosromgr.utils.s3.boto3')
@patch('mosromgr.utils.s3.get_file_contents')
@patch('mosromgr.utils.s3.get_mos_files')
def test_mos_collection_init_s3(get_mos_files, get_file_contents, boto3, rocreate, rodelete, ro_all):
    """
    GIVEN: A bucket name and prefix (mocked to contain two files)
    EXPECT: MosCollection object with 1 reader
    """
    with open(rocreate) as f:
        rocreate = f.read()
    with open(rodelete) as f:
        rodelete = f.read()

    get_mos_files.return_value = ['roCreate.mos.xml', 'roDelete.mos.xml']
    get_file_contents.side_effect = [rocreate, rodelete, rocreate, rodelete]

    mc = MosCollection.from_s3(bucket_name='bucket_name', prefix='newsnight')
    assert repr(mc) == "<MosCollection RO SLUG>"
    assert isinstance(mc.ro, RunningOrder)
    assert isinstance(mc.mos_readers, list)
    assert len(mc.mos_readers) == 1

def test_mos_collection_init_multiple_files(ro_all):
    "Test collection can be created from multiple files"
    mc = MosCollection.from_files(ro_all)
    assert repr(mc) == "<MosCollection RO SLUG>"
    assert isinstance(mc.ro, RunningOrder)
    assert isinstance(mc.mos_readers, list)
    assert len(mc.mos_readers) == len(ro_all) - 1

def test_mos_collection_init_multiple_files_sorted(rostorysend2, rocreate, rostorysend1, rodelete):
    "Test collection can sort input files by messageID field"
    mos_files = [rostorysend2, rocreate, rostorysend1, rodelete]
    mc = MosCollection.from_files(mos_files)
    assert isinstance(mc.ro, RunningOrder)
    assert isinstance(mc.mos_readers, list)
    assert len(mc.mos_readers) == 3
    mf1, mf2, mf3 = mc.mos_readers
    assert mf1.message_id == 1001
    assert mf2.message_id == 1002

def test_mos_collection_unsupported_mos_type(rocreate, roinvalid, rodelete):
    """
    GIVEN: Running order and invalid mos message, in list form
    EXPECT: MosCollection object with running order and no other files
    """
    mos_files = [rocreate, roinvalid, rodelete]
    with pytest.raises(UnknownMosFileType):
        MosCollection.from_files(mos_files)

def test_mos_collection_merge(rocreate, roelementactionstoryinsert, rodelete):
    """
    GIVEN: Running order and EAStoryInsert paths
    EXPECT: Running order summary, with story from EAStoryInsert added
    """
    mos_files = [rocreate, roelementactionstoryinsert, rodelete]
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
def test_mos_collection_s3_merge(get_mos_files, get_file_contents, boto3,
    rocreate, roelementactionstoryinsert, rodelete):
    """
    GIVEN: Bucket prefix matching a roCreate and ElementAction (StoryInsert)
    EXPECT: Running order summary, with story from EAStoryInsert added
    """
    with open(rocreate) as f:
        rc = f.read()
    with open(roelementactionstoryinsert) as f:
        ea = f.read()
    with open(rodelete) as f:
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

def test_mos_collection_merge_warning(rocreate, rostorysend3, rodelete):
    """
    GIVEN: Running order and invalid StorySend, in list form
    EXPECT: MosMergeError
    """
    mos_files = [rocreate, rostorysend3, rodelete]
    mc = MosCollection.from_files(mos_files)
    with warnings.catch_warnings(record=True) as w:
        mc.merge()
    assert len(w) == 1
    assert w[0].category == StoryNotFoundWarning
