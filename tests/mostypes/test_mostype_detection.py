# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

import pytest

from mosromgr.mostypes import *
from mosromgr.exc import *


def test_mosfile_detect_bad_init(rocreate):
    "Test we can catch consruction using __init__ not _from classmethods"
    with pytest.raises(TypeError):
        MosFile(rocreate)

def test_mosfile_detect_invalid_xml_from_file(invalid_xml):
    "Test we can catch XML parsing errors when constructing from file"
    with pytest.raises(MosInvalidXML):
        MosFile.from_file(invalid_xml)

def test_mosfile_detect_invalid_xml_from_string():
    "Test we can catch XML parsing errors when constructing from string"
    with pytest.raises(MosInvalidXML):
        not_xml = "foo"
        MosFile.from_string(not_xml)

def test_mosfile_detect_rocreate_contents(rocreate):
    """
    GIVEN: A path to a roCreate MOS file
    EXPECT: An object of type RunningOrder
    """
    xml = rocreate.read_text()
    rc = MosFile.from_string(xml)
    assert type(rc) == RunningOrder

def test_mosfile_detect_rocreate(rocreate):
    """
    GIVEN: A path to a roCreate MOS file
    EXPECT: An object of type RunningOrder
    """
    rc = MosFile.from_file(rocreate)
    assert type(rc) == RunningOrder

def test_mosfile_detect_storysend(rostorysend1):
    """
    GIVEN: A path to a storySend MOS file
    EXPECT: An object of type StorySend
    """
    ss = MosFile.from_file(rostorysend1)
    assert type(ss) == StorySend

def test_mosfile_detect_appendstory(rostoryappend):
    """
    GIVEN: A path to a roStoryAppend MOS file
    EXPECT: An object of type StoryAppend
    """
    sa = MosFile.from_file(rostoryappend)
    assert type(sa) == StoryAppend

def test_mosfile_detect_storydelete(rostorydelete):
    """
    GIVEN: A path to a roStoryDelete MOS file
    EXPECT: An object of type StoryDelete
    """
    sd = MosFile.from_file(rostorydelete)
    assert type(sd) == StoryDelete

def test_mosfile_detect_storyinsert(rostoryinsert):
    """
    GIVEN: A path to a RoStoryInsert MOS file
    EXPECT: An object of type StoryInsert
    """
    si = MosFile.from_file(rostoryinsert)
    assert type(si) == StoryInsert

def test_mosfile_detect_storymove(rostorymove):
    """
    GIVEN: A path to a roStoryMove MOS file
    EXPECT: An object of type StoryMove
    """
    sm = MosFile.from_file(rostorymove)
    assert type(sm) == StoryMove

def test_mosfile_detect_storyreplace(rostoryreplace):
    """
    GIVEN: A path to a roStoryReplace MOS file
    EXPECT: An object of type StoryReplace
    """
    sr = MosFile.from_file(rostoryreplace)
    assert type(sr) == StoryReplace

def test_mosfile_detect_itemdelete(roitemdelete):
    """
    GIVEN: A path to a roItemDelete MOS file
    EXPECT: An object of type ItemDelete
    """
    id = MosFile.from_file(roitemdelete)
    assert type(id) == ItemDelete

def test_mosfile_detect_iteminsert(roiteminsert):
    """
    GIVEN: A path to a roItemInsert MOS file
    EXPECT: An object of type ItemInsert
    """
    ii = MosFile.from_file(roiteminsert)
    assert type(ii) == ItemInsert

def test_mosfile_detect_movemultipleitem(roitemmovemultiple):
    """
    GIVEN: A path to a roItemMoveMultiple MOS file
    EXPECT: An object of type ItemMoveMultiple
    """
    imm = MosFile.from_file(roitemmovemultiple)
    assert type(imm) == ItemMoveMultiple

def test_mosfile_detect_replaceitem(roitemreplace):
    """
    GIVEN: A path to a roReplaceItem MOS file
    EXPECT: An object of type ItemReplace
    """
    ir = MosFile.from_file(roitemreplace)
    assert type(ir) == ItemReplace

def test_mosfile_detect_roreplace(roreplace):
    """
    GIVEN: A path to a roReplace MOS file
    EXPECT: An object of type RunningOrderReplace
    """
    rr = MosFile.from_file(roreplace)
    assert type(rr) == RunningOrderReplace

def test_mosfile_detect_metadata_replace(rometadatareplace):
    """
    GIVEN: A path to a roMetadataReplace MOS file
    EXPECT: An object of type MetaDataReplace
    """
    ea = MosFile.from_file(rometadatareplace)
    assert type(ea) == MetaDataReplace

def test_mosfile_detect_delete(rodelete):
    """
    GIVEN: A path to a roDelete MOS file
    EXPECT: An object of type RunningOrderEnd
    """
    rd = MosFile.from_file(rodelete)
    assert type(rd) == RunningOrderEnd

def test_mosfile_detect_readytoair(roreadytoair):
    """
    GIVEN: A path to a roReadyToAir MOS file
    EXPECT: An object of type ReadyToAir
    """
    rta = MosFile.from_file(roreadytoair)
    assert type(rta) == ReadyToAir

def test_get_mos_object_invalid_mos_type(roinvalid):
    """
    GIVEN: A path to a roDelete MOS file
    EXPECT: An object of type RunningOrderEnd
    """
    with pytest.raises(UnknownMosFileType):
        MosFile.from_file(roinvalid)
