import pytest

from mosromgr.mostypes import *
from mosromgr.exc import *
from const import *


def test_get_mos_object_with_invalid_xml():
    "Test we can catch XML parsing errors"
    with pytest.raises(MosInvalidXML):
        not_xml = "hello"
        MosFile.from_string(not_xml)

def test_get_mos_object_with_rocreate_contents():
    """
    GIVEN: A path to a roCreate MOS file
    EXPECT: An object of type RunningOrder
    """
    with open(ROCREATE) as f:
        contents = f.read()
    rc = MosFile.from_string(contents)
    assert isinstance(rc, RunningOrder)

def test_get_mos_object_with_rocreate():
    """
    GIVEN: A path to a roCreate MOS file
    EXPECT: An object of type RunningOrder
    """
    rc = MosFile.from_file(ROCREATE)
    assert isinstance(rc, RunningOrder)

def test_get_mos_object_with_storysend():
    """
    GIVEN: A path to a storySend MOS file
    EXPECT: An object of type StorySend
    """
    ss = MosFile.from_file(ROSTORYSEND1)
    assert isinstance(ss, StorySend)

def test_get_mos_object_with_appendstory():
    """
    GIVEN: A path to a appendStory MOS file
    EXPECT: An object of type StoryAppend
    """
    sa = MosFile.from_file(ROAPPENDSTORY)
    assert isinstance(sa, StoryAppend)

def test_get_mos_object_with_deletestory():
    """
    GIVEN: A path to a deleteStory MOS file
    EXPECT: An object of type StoryDelete
    """
    sd = MosFile.from_file(RODELSTORY)
    assert isinstance(sd, StoryDelete)

def test_get_mos_object_with_insertstory():
    """
    GIVEN: A path to a insertStory MOS file
    EXPECT: An object of type StoryInsert
    """
    si = MosFile.from_file(ROINSERTSTORY)
    assert isinstance(si, StoryInsert)

def test_get_mos_object_with_movestory():
    """
    GIVEN: A path to a moveStory MOS file
    EXPECT: An object of type StoryMove
    """
    sm = MosFile.from_file(ROMOVESTORY)
    assert isinstance(sm, StoryMove)

def test_get_mos_object_with_replacestory():
    """
    GIVEN: A path to a replaceStory MOS file
    EXPECT: An object of type StoryReplace
    """
    sr = MosFile.from_file(ROREPSTORY)
    assert isinstance(sr, StoryReplace)

def test_get_mos_object_with_deleteitem():
    """
    GIVEN: A path to a deleteItem MOS file
    EXPECT: An object of type ItemDelete
    """
    id = MosFile.from_file(RODELITEM)
    assert isinstance(id, ItemDelete)

def test_get_mos_object_with_insertitem():
    """
    GIVEN: A path to a insertItem MOS file
    EXPECT: An object of type ItemInsert
    """
    ii = MosFile.from_file(ROINSERTITEM)
    assert isinstance(ii, ItemInsert)

def test_get_mos_object_with_movemultipleitem():
    """
    GIVEN: A path to a itemMoveMultiple MOS file
    EXPECT: An object of type ItemMoveMultiple
    """
    imm = MosFile.from_file(ROMOVEMULTIPLEITEM)
    assert isinstance(imm, ItemMoveMultiple)

def test_get_mos_object_with_replaceitem():
    """
    GIVEN: A path to a replaceItem MOS file
    EXPECT: An object of type ItemReplace
    """
    ir = MosFile.from_file(ROREPITEM)
    assert isinstance(ir, ItemReplace)

def test_get_mos_object_with_roreplace():
    """
    GIVEN: A path to a roReplace MOS file
    EXPECT: An object of type RunningOrderReplace
    """
    rr = MosFile.from_file(ROREPLACE)
    assert isinstance(rr, RunningOrderReplace)

def test_get_mos_object_with_elementaction_replace_story():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'REPLACE' and
    no target itemID
    EXPECT: An object of type EAStoryReplace
    """
    ea = MosFile.from_file(ROELEMENTACTIONREPSTORY)
    assert isinstance(ea, EAStoryReplace)

def test_get_mos_object_with_elementaction_replace_item():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'REPLACE' and
    a target itemID
    EXPECT: An object of type EAItemReplace
    """
    ea = MosFile.from_file(ROELEMENTACTIONREPITEM)
    assert isinstance(ea, EAItemReplace)

def test_get_mos_object_with_elementaction_delete_story():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'DELETE' and
    no source itemID
    EXPECT: An object of type EAStoryDelete
    """
    ea = MosFile.from_file(ROELEMENTACTIONDELSTORY)
    assert isinstance(ea, EAStoryDelete)

def test_get_mos_object_with_elementaction_delete_item():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'DELETE' and a
    source itemID
    EXPECT: An object of type EAItemDelete
    """
    ea = MosFile.from_file(ROELEMENTACTIONDELITEM)
    assert isinstance(ea, EAItemDelete)

def test_get_mos_object_with_elementaction_insert_story():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'INSERT' and
    no target itemID
    EXPECT: An object of type EAStoryInsert
    """
    ea = MosFile.from_file(ROELEMENTACTIONINSERTSTORY)
    assert isinstance(ea, EAStoryInsert)

def test_get_mos_object_with_elementaction_insert_item():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'INSERT' and a
    target itemID
    EXPECT: An object of type EAItemInsert
    """
    ea = MosFile.from_file(ROELEMENTACTIONINSERTITEM)
    assert isinstance(ea, EAItemInsert)

def test_get_mos_object_with_elementaction_swap_story():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'SWAP' and no
    source itemID
    EXPECT: An object of type EAStorySwap
    """
    ea = MosFile.from_file(ROELEMENTACTIONSWAPSTORY)
    assert isinstance(ea, EAStorySwap)

def test_get_mos_object_with_elementaction_swap_item():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'SWAP' and two
    source itemIDs
    EXPECT: An object of type EAItemSwap
    """
    ea = MosFile.from_file(ROELEMENTACTIONSWAPITEM)
    assert isinstance(ea, EAItemSwap)

def test_get_mos_object_with_elementaction_move_story():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'MOVE' and no
    target itemID
    EXPECT: An object of type EAStoryMove
    """
    ea = MosFile.from_file(ROELEMENTACTIONMOVESTORY)
    assert isinstance(ea, EAStoryMove)

def test_get_mos_object_with_elementaction_move_item():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'MOVE' and a
    target itemID
    EXPECT: An object of type EAItemMove
    """
    ea = MosFile.from_file(ROELEMENTACTIONMOVEITEM)
    assert isinstance(ea, EAItemMove)

def test_get_mos_object_with_metadata_replace():
    """
    GIVEN: A path to a metadataReplace MOS file
    EXPECT: An object of type MetaDataReplace
    """
    ea = MosFile.from_file(ROMETADATAREPLACE)
    assert isinstance(ea, MetaDataReplace)

def test_get_mos_object_with_delete():
    """
    GIVEN: A path to a roDelete MOS file
    EXPECT: An object of type RunningOrderEnd
    """
    rd = MosFile.from_file(RODELETE)
    assert isinstance(rd, RunningOrderEnd)

def test_get_mos_object_invalid_mos_type():
    with pytest.raises(UnknownMosFileType):
        MosFile.from_file(ROINVALID)
