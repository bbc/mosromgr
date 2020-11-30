import pytest

from mosromgr.mostypes import *
from mosromgr.exc import *


def test_mosfile_detect_invalid_xml():
    "Test we can catch XML parsing errors"
    with pytest.raises(MosInvalidXML):
        not_xml = "hello"
        MosFile.from_string(not_xml)

def test_mosfile_detect_rocreate_contents(rocreate):
    """
    GIVEN: A path to a roCreate MOS file
    EXPECT: An object of type RunningOrder
    """
    with open(rocreate) as f:
        contents = f.read()
    rc = MosFile.from_string(contents)
    assert isinstance(rc, RunningOrder)

def test_mosfile_detect_rocreate(rocreate):
    """
    GIVEN: A path to a roCreate MOS file
    EXPECT: An object of type RunningOrder
    """
    rc = MosFile.from_file(rocreate)
    assert isinstance(rc, RunningOrder)

def test_mosfile_detect_storysend(rostorysend1):
    """
    GIVEN: A path to a storySend MOS file
    EXPECT: An object of type StorySend
    """
    ss = MosFile.from_file(rostorysend1)
    assert isinstance(ss, StorySend)

def test_mosfile_detect_appendstory(rostoryappend):
    """
    GIVEN: A path to a appendStory MOS file
    EXPECT: An object of type StoryAppend
    """
    sa = MosFile.from_file(rostoryappend)
    assert isinstance(sa, StoryAppend)

def test_mosfile_detect_storydelete(rostorydelete):
    """
    GIVEN: A path to a storydelete MOS file
    EXPECT: An object of type StoryDelete
    """
    sd = MosFile.from_file(rostorydelete)
    assert isinstance(sd, StoryDelete)

def test_mosfile_detect_storyinsert(rostoryinsert):
    """
    GIVEN: A path to a storyinsert MOS file
    EXPECT: An object of type StoryInsert
    """
    si = MosFile.from_file(rostoryinsert)
    assert isinstance(si, StoryInsert)

def test_mosfile_detect_storymove(rostorymove):
    """
    GIVEN: A path to a storymove MOS file
    EXPECT: An object of type StoryMove
    """
    sm = MosFile.from_file(rostorymove)
    assert isinstance(sm, StoryMove)

def test_mosfile_detect_storyreplace(rostoryreplace):
    """
    GIVEN: A path to a storyreplace MOS file
    EXPECT: An object of type StoryReplace
    """
    sr = MosFile.from_file(rostoryreplace)
    assert isinstance(sr, StoryReplace)

def test_mosfile_detect_itemdelete(roitemdelete):
    """
    GIVEN: A path to a itemdelete MOS file
    EXPECT: An object of type ItemDelete
    """
    id = MosFile.from_file(roitemdelete)
    assert isinstance(id, ItemDelete)

def test_mosfile_detect_iteminsert(roiteminsert):
    """
    GIVEN: A path to a iteminsert MOS file
    EXPECT: An object of type ItemInsert
    """
    ii = MosFile.from_file(roiteminsert)
    assert isinstance(ii, ItemInsert)

def test_mosfile_detect_movemultipleitem(roitemmovemultiple):
    """
    GIVEN: A path to a itemMoveMultiple MOS file
    EXPECT: An object of type ItemMoveMultiple
    """
    imm = MosFile.from_file(roitemmovemultiple)
    assert isinstance(imm, ItemMoveMultiple)

def test_mosfile_detect_replaceitem(roitemreplace):
    """
    GIVEN: A path to a replaceItem MOS file
    EXPECT: An object of type ItemReplace
    """
    ir = MosFile.from_file(roitemreplace)
    assert isinstance(ir, ItemReplace)

def test_mosfile_detect_roreplace(roreplace):
    """
    GIVEN: A path to a roReplace MOS file
    EXPECT: An object of type RunningOrderReplace
    """
    rr = MosFile.from_file(roreplace)
    assert isinstance(rr, RunningOrderReplace)

def test_mosfile_detect_elementaction_replace_story(roelementactionstoryreplace):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'REPLACE' and
    no target itemID
    EXPECT: An object of type EAStoryReplace
    """
    ea = MosFile.from_file(roelementactionstoryreplace)
    assert isinstance(ea, EAStoryReplace)

def test_mosfile_detect_elementaction_replace_item(roelementactionitemreplace):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'REPLACE' and
    a target itemID
    EXPECT: An object of type EAItemReplace
    """
    ea = MosFile.from_file(roelementactionitemreplace)
    assert isinstance(ea, EAItemReplace)

def test_mosfile_detect_elementaction_delete_story(roelementactionstorydelete):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'DELETE' and
    no source itemID
    EXPECT: An object of type EAStoryDelete
    """
    ea = MosFile.from_file(roelementactionstorydelete)
    assert isinstance(ea, EAStoryDelete)

def test_mosfile_detect_elementaction_delete_item(roelementactionitemdelete):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'DELETE' and a
    source itemID
    EXPECT: An object of type EAItemDelete
    """
    ea = MosFile.from_file(roelementactionitemdelete)
    assert isinstance(ea, EAItemDelete)

def test_mosfile_detect_elementaction_insert_story(roelementactionstoryinsert):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'INSERT' and
    no target itemID
    EXPECT: An object of type EAStoryInsert
    """
    ea = MosFile.from_file(roelementactionstoryinsert)
    assert isinstance(ea, EAStoryInsert)

def test_mosfile_detect_elementaction_insert_item(roelementactioniteminsert):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'INSERT' and a
    target itemID
    EXPECT: An object of type EAItemInsert
    """
    ea = MosFile.from_file(roelementactioniteminsert)
    assert isinstance(ea, EAItemInsert)

def test_mosfile_detect_elementaction_swap_story(roelementactionstoryswap):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'SWAP' and no
    source itemID
    EXPECT: An object of type EAStorySwap
    """
    ea = MosFile.from_file(roelementactionstoryswap)
    assert isinstance(ea, EAStorySwap)

def test_mosfile_detect_elementaction_swap_item(roelementactionitemswap):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'SWAP' and two
    source itemIDs
    EXPECT: An object of type EAItemSwap
    """
    ea = MosFile.from_file(roelementactionitemswap)
    assert isinstance(ea, EAItemSwap)

def test_mosfile_detect_elementaction_move_story(roelementactionstorymove):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'MOVE' and no
    target itemID
    EXPECT: An object of type EAStoryMove
    """
    ea = MosFile.from_file(roelementactionstorymove)
    assert isinstance(ea, EAStoryMove)

def test_mosfile_detect_elementaction_move_item(roelementactionitemmove):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'MOVE' and a
    target itemID
    EXPECT: An object of type EAItemMove
    """
    ea = MosFile.from_file(roelementactionitemmove)
    assert isinstance(ea, EAItemMove)

def test_mosfile_detect_metadata_replace(rometadatareplace):
    """
    GIVEN: A path to a metadataReplace MOS file
    EXPECT: An object of type MetaDataReplace
    """
    ea = MosFile.from_file(rometadatareplace)
    assert isinstance(ea, MetaDataReplace)

def test_mosfile_detect_delete(rodelete):
    """
    GIVEN: A path to a roDelete MOS file
    EXPECT: An object of type RunningOrderEnd
    """
    rd = MosFile.from_file(rodelete)
    assert isinstance(rd, RunningOrderEnd)

def test_mosfile_detect_readytoair(roreadytoair):
    rta = MosFile.from_file(roreadytoair)
    assert isinstance(rta, ReadyToAir)

def test_get_mos_object_invalid_mos_type(roinvalid):
    with pytest.raises(UnknownMosFileType):
        MosFile.from_file(roinvalid)
