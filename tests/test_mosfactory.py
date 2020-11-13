from pathlib import Path
import pytest

from mosromgr.mosfactory import *
from mosromgr.mostypes import *
from mosromgr.exc import *
from const import *


def test_get_mos_object_with_invalid_xml():
    "Test we can catch XML parsing errors"
    with pytest.raises(MosInvalidXML):
        not_xml = "hello"
        get_mos_object(mos_file_contents=not_xml)

def test_get_mos_object_with_rocreate_contents():
    """
    GIVEN: A path to a roCreate MOS file
    EXPECT: An object of type RunningOrder
    """
    with open(ROCREATE) as f:
        contents = f.read()
    rc = get_mos_object(mos_file_contents=contents)
    assert isinstance(rc, RunningOrder)
    rc = get_mos_object(mos_file_contents=contents, mos_file_prefix='ROCREATE')
    assert isinstance(rc, RunningOrder)

def test_get_mos_object_with_rocreate():
    """
    GIVEN: A path to a roCreate MOS file
    EXPECT: An object of type RunningOrder
    """
    rc = get_mos_object(ROCREATE)
    assert isinstance(rc, RunningOrder)

def test_get_mos_object_with_storysend():
    """
    GIVEN: A path to a storySend MOS file
    EXPECT: An object of type StorySend
    """
    ss = get_mos_object(ROSTORYSEND1)
    assert isinstance(ss, StorySend)

def test_get_mos_object_with_appendstory():
    """
    GIVEN: A path to a appendStory MOS file
    EXPECT: An object of type StoryAppend
    """
    sa = get_mos_object(ROAPPENDSTORY)
    assert isinstance(sa, StoryAppend)

def test_get_mos_object_with_deletestory():
    """
    GIVEN: A path to a deleteStory MOS file
    EXPECT: An object of type StoryDelete
    """
    sd = get_mos_object(RODELSTORY)
    assert isinstance(sd, StoryDelete)

def test_get_mos_object_with_insertstory():
    """
    GIVEN: A path to a insertStory MOS file
    EXPECT: An object of type StoryInsert
    """
    si = get_mos_object(ROINSERTSTORY)
    assert isinstance(si, StoryInsert)

def test_get_mos_object_with_movestory():
    """
    GIVEN: A path to a moveStory MOS file
    EXPECT: An object of type StoryMove
    """
    sm = get_mos_object(ROMOVESTORY)
    assert isinstance(sm, StoryMove)

def test_get_mos_object_with_replacestory():
    """
    GIVEN: A path to a replaceStory MOS file
    EXPECT: An object of type StoryReplace
    """
    sr = get_mos_object(ROREPSTORY)
    assert isinstance(sr, StoryReplace)

def test_get_mos_object_with_deleteitem():
    """
    GIVEN: A path to a deleteItem MOS file
    EXPECT: An object of type ItemDelete
    """
    id = get_mos_object(RODELITEM)
    assert isinstance(id, ItemDelete)

def test_get_mos_object_with_insertitem():
    """
    GIVEN: A path to a insertItem MOS file
    EXPECT: An object of type ItemInsert
    """
    ii = get_mos_object(ROINSERTITEM)
    assert isinstance(ii, ItemInsert)

def test_get_mos_object_with_movemultipleitem():
    """
    GIVEN: A path to a itemMoveMultiple MOS file
    EXPECT: An object of type ItemMoveMultiple
    """
    imm = get_mos_object(ROMOVEMULTIPLEITEM)
    assert isinstance(imm, ItemMoveMultiple)

def test_get_mos_object_with_replaceitem():
    """
    GIVEN: A path to a replaceItem MOS file
    EXPECT: An object of type ItemReplace
    """
    ir = get_mos_object(ROREPITEM)
    assert isinstance(ir, ItemReplace)

def test_get_mos_object_with_roreplace():
    """
    GIVEN: A path to a roReplace MOS file
    EXPECT: An object of type RunningOrderReplace
    """
    rr = get_mos_object(ROREPLACE)
    assert isinstance(rr, RunningOrderReplace)

def test_get_mos_object_with_elementaction_replace_story():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'REPLACE' and
    no target itemID
    EXPECT: An object of type EAStoryReplace
    """
    ea = get_mos_object(ROELEMENTACTIONREPSTORY)
    assert isinstance(ea, EAStoryReplace)

def test_get_mos_object_with_elementaction_replace_item():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'REPLACE' and
    a target itemID
    EXPECT: An object of type EAItemReplace
    """
    ea = get_mos_object(ROELEMENTACTIONREPITEM)
    assert isinstance(ea, EAItemReplace)

def test_get_mos_object_with_elementaction_delete_story():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'DELETE' and
    no source itemID
    EXPECT: An object of type EAStoryDelete
    """
    ea = get_mos_object(ROELEMENTACTIONDELSTORY)
    assert isinstance(ea, EAStoryDelete)

def test_get_mos_object_with_elementaction_delete_item():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'DELETE' and a
    source itemID
    EXPECT: An object of type EAItemDelete
    """
    ea = get_mos_object(ROELEMENTACTIONDELITEM)
    assert isinstance(ea, EAItemDelete)

def test_get_mos_object_with_elementaction_insert_story():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'INSERT' and
    no target itemID
    EXPECT: An object of type EAStoryInsert
    """
    ea = get_mos_object(ROELEMENTACTIONINSERTSTORY)
    assert isinstance(ea, EAStoryInsert)

def test_get_mos_object_with_elementaction_insert_item():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'INSERT' and a
    target itemID
    EXPECT: An object of type EAItemInsert
    """
    ea = get_mos_object(ROELEMENTACTIONINSERTITEM)
    assert isinstance(ea, EAItemInsert)

def test_get_mos_object_with_elementaction_swap_story():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'SWAP' and no
    source itemID
    EXPECT: An object of type EAStorySwap
    """
    ea = get_mos_object(ROELEMENTACTIONSWAPSTORY)
    assert isinstance(ea, EAStorySwap)

def test_get_mos_object_with_elementaction_swap_item():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'SWAP' and two
    source itemIDs
    EXPECT: An object of type EAItemSwap
    """
    ea = get_mos_object(ROELEMENTACTIONSWAPITEM)
    assert isinstance(ea, EAItemSwap)

def test_get_mos_object_with_elementaction_move_story():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'MOVE' and no
    target itemID
    EXPECT: An object of type EAStoryMove
    """
    ea = get_mos_object(ROELEMENTACTIONMOVESTORY)
    assert isinstance(ea, EAStoryMove)

def test_get_mos_object_with_elementaction_move_item():
    """
    GIVEN: A path to a elementAction MOS file with the operation 'MOVE' and a
    target itemID
    EXPECT: An object of type EAItemMove
    """
    ea = get_mos_object(ROELEMENTACTIONMOVEITEM)
    assert isinstance(ea, EAItemMove)

def test_get_mos_object_with_metadata_replace():
    """
    GIVEN: A path to a metadataReplace MOS file
    EXPECT: An object of type MetaDataReplace
    """
    ea = get_mos_object(ROMETADATAREPLACE)
    assert isinstance(ea, MetaDataReplace)

def test_get_mos_object_with_delete():
    """
    GIVEN: A path to a roDelete MOS file
    EXPECT: An object of type RunningOrderEnd
    """
    rd = get_mos_object(RODELETE)
    assert isinstance(rd, RunningOrderEnd)

def test_get_mos_object_invalid_mos_type():
    with warnings.catch_warnings(record=True) as w:
        im = get_mos_object(ROINVALID)
        assert len(w) == 1
        assert w[0].category == UnknownMosFileTypeWarning
    assert im is None
