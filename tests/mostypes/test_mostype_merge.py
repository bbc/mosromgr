# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

import warnings

import pytest

from mosromgr.mostypes import *
from mosromgr.exc import *


def test_story_send(rocreate, rostorysend1):
    """
    GIVEN: Running order and StorySend message (Add contents to STORY 1)
    EXPECT: Running order with storyBody present in STORY 1
    """
    ro = RunningOrder.from_file(rocreate)
    ss = StorySend.from_file(rostorysend1)
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3
    ro += ss
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3
    body1 = d['mos']['roCreate']['story'][0]['p']
    assert body1 == '(BONG+PRES)'
    assert ro.base_tag.tag == 'roCreate'
    assert ss.base_tag.tag == 'roStorySend'

def test_element_action_replace_story(rocreate, roelementactionstoryreplace):
    """
    GIVEN: Running order and EAStoryReplace message (STORY 1 for STORY ONE)
    EXPECT: Running order with STORY ONE and no STORY 1
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStoryReplace.from_file(roelementactionstoryreplace)
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug == 'STORY 1'
    item_slug = d['mos']['roCreate']['story'][0]['item'][0]['itemSlug']
    assert item_slug == 'ITEM 1'

    ro += ea
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug == 'STORY ONE'
    item_slug = d['mos']['roCreate']['story'][0]['item']['itemSlug']
    assert item_slug == 'ITEM ONE'
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_element_action_replace_item(rocreate, roelementactionitemreplace):
    """
    GIVEN: Running order and EAItemReplace message (ITEM 21 for NEW ITEM 21)
    EXPECT: Running order with NEW ITEM 21 in STORY 2
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemReplace.from_file(roelementactionitemreplace)
    ro += ea
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug = d['mos']['roCreate']['story'][1]['storySlug']
    assert story_slug == 'STORY 2'
    item_slug = d['mos']['roCreate']['story'][1]['item'][0]['itemSlug']
    assert item_slug == 'NEW ITEM 21'
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_element_action_delete_story(rocreate, roelementactionstorydelete):
    """
    GIVEN: Running order and EAStoryDelete message (delete STORY 1)
    EXPECT: Running order with no STORY 1
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStoryDelete.from_file(roelementactionstorydelete)
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug1 = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug1 == 'STORY 1'
    story_slug2 = d['mos']['roCreate']['story'][1]['storySlug']
    assert story_slug2 == 'STORY 2'

    ro += ea
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 2
    story_slug = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug == 'STORY 2'
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_element_action_delete_item(rocreate, roelementactionitemdelete):
    """
    GIVEN: Running order and EAItemDelete message (delete ITEM 1 in STORY 1)
    EXPECT: Running order with no ITEM 1 in STORY 1
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemDelete.from_file(roelementactionitemdelete)
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3

    ro += ea
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 2
    item_slug_1 = d['mos']['roCreate']['story'][0]['item'][0]['itemSlug']
    assert item_slug_1 == "ITEM 2"
    item_slug_2 = d['mos']['roCreate']['story'][0]['item'][1]['itemSlug']
    assert item_slug_2 == "ITEM 3"
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_element_action_insert_story(rocreate, roelementactionstoryinsert):
    """
    GIVEN: Running order and EAStoryInsert message (insert STORY NEW)
    EXPECT: Running order with STORY NEW between STORY 1 and 2
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStoryInsert.from_file(roelementactionstoryinsert)
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug1 = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug1 == 'STORY 1'
    story_slug2 = d['mos']['roCreate']['story'][1]['storySlug']
    assert story_slug2 == 'STORY 2'
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

    ro += ea
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 4
    story_slug1 = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug1 == 'STORY 1'
    story_slug_new = d['mos']['roCreate']['story'][1]['storySlug']
    assert story_slug_new == 'STORY NEW'
    story_slug2 = d['mos']['roCreate']['story'][2]['storySlug']
    assert story_slug2 == 'STORY 2'

def test_element_action_insert_item(rocreate, roelementactioniteminsert):
    """
    GIVEN: Running order and EAItemInsert message (insert ITEM NEW in STORY 1)
    EXPECT: Running order with ITEM NEW between ITEM 1 and 2 in STORY 1
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemInsert.from_file(roelementactioniteminsert)
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    item_slug1 = d['mos']['roCreate']['story'][0]['item'][0]['itemSlug']
    assert item_slug1 == 'ITEM 1'
    item_slug2 = d['mos']['roCreate']['story'][0]['item'][1]['itemSlug']
    assert item_slug2 == 'ITEM 2'

    ro += ea
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 4
    item_slug1 = d['mos']['roCreate']['story'][0]['item'][0]['itemSlug']
    assert item_slug1 == 'ITEM 1'
    item_slug_new = d['mos']['roCreate']['story'][0]['item'][1]['itemSlug']
    assert item_slug_new == 'ITEM NEW'
    item_slug2 = d['mos']['roCreate']['story'][0]['item'][2]['itemSlug']
    assert item_slug2 == 'ITEM 2'
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_element_action_swap_story(rocreate, roelementactionstoryswap):
    """
    GIVEN: Running order and EAStorySwap message (swap STORY 1 STORY 2)
    EXPECT: Running order with positions of STORY 1 and 2 swapped
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStorySwap.from_file(roelementactionstoryswap)
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    story_slug1 = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug1 == 'STORY 1'
    story_slug2 = d['mos']['roCreate']['story'][1]['storySlug']
    assert story_slug2 == 'STORY 2'

    ro += ea
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    story_slug1 = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug1 == 'STORY 2'
    story_slug2 = d['mos']['roCreate']['story'][1]['storySlug']
    assert story_slug2 == 'STORY 1'
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_element_action_swap_item(rocreate, roelementactionitemswap):
    """
    GIVEN: Running order and EAItemSwap message (swap ITEM 1 and ITEM 2)
    EXPECT: Running order with positions of ITEM 1 and 2 swapped in STORY 1
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemSwap.from_file(roelementactionitemswap)
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    item_slug1 = d['mos']['roCreate']['story'][0]['item'][0]['itemSlug']
    assert item_slug1 == 'ITEM 1'
    item_slug2 = d['mos']['roCreate']['story'][0]['item'][1]['itemSlug']
    assert item_slug2 == 'ITEM 2'

    ro += ea
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    item_slug1 = d['mos']['roCreate']['story'][0]['item'][0]['itemSlug']
    assert item_slug1 == 'ITEM 2'
    item_slug2 = d['mos']['roCreate']['story'][0]['item'][1]['itemSlug']
    assert item_slug2 == 'ITEM 1'
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_element_action_move_story(rocreate, roelementactionstorymove):
    """
    GIVEN: Running order and EAStoryMove message (move STORY 3 to top)
    EXPECT: Running order with STORY 3 at top, above STORY 1
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStoryMove.from_file(roelementactionstorymove)
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug1 = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug1 == 'STORY 1'
    story_slug2 = d['mos']['roCreate']['story'][1]['storySlug']
    assert story_slug2 == 'STORY 2'
    story_slug3 = d['mos']['roCreate']['story'][2]['storySlug']
    assert story_slug3 == 'STORY 3'

    ro += ea
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug1 = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug1 == 'STORY 3'
    story_slug2 = d['mos']['roCreate']['story'][1]['storySlug']
    assert story_slug2 == 'STORY 1'
    story_slug3 = d['mos']['roCreate']['story'][2]['storySlug']
    assert story_slug3 == 'STORY 2'
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_element_action_move_story_no_target(rocreate, roelementactionstorymove2):
    """
    GIVEN: Running order and EAStoryMove message (move STORY 1 to bottom)
    EXPECT: Running order with STORY 1 at bottom
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStoryMove.from_file(roelementactionstorymove2)
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug1 = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug1 == 'STORY 1'
    story_slug2 = d['mos']['roCreate']['story'][1]['storySlug']
    assert story_slug2 == 'STORY 2'
    story_slug3 = d['mos']['roCreate']['story'][2]['storySlug']
    assert story_slug3 == 'STORY 3'

    ro += ea
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug1 = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug1 == 'STORY 2'
    story_slug2 = d['mos']['roCreate']['story'][1]['storySlug']
    assert story_slug2 == 'STORY 3'
    story_slug3 = d['mos']['roCreate']['story'][2]['storySlug']
    assert story_slug3 == 'STORY 1'
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_element_action_move_item(rocreate, roelementactionitemmove):
    """
    GIVEN: Running order and EAItemMove message (move ITEM 3 to top)
    EXPECT: Running order with ITEM 3 at top of STORY 1
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemMove.from_file(roelementactionitemmove)
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    story_slug1 = d['mos']['roCreate']['story'][0]['item'][0]['itemSlug']
    assert story_slug1 == 'ITEM 1'
    story_slug2 = d['mos']['roCreate']['story'][0]['item'][1]['itemSlug']
    assert story_slug2 == 'ITEM 2'
    story_slug3 = d['mos']['roCreate']['story'][0]['item'][2]['itemSlug']
    assert story_slug3 == 'ITEM 3'

    ro += ea
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug1 = d['mos']['roCreate']['story'][0]['item'][0]['itemSlug']
    assert story_slug1 == 'ITEM 3'
    story_slug2 = d['mos']['roCreate']['story'][0]['item'][1]['itemSlug']
    assert story_slug2 == 'ITEM 1'
    story_slug3 = d['mos']['roCreate']['story'][0]['item'][2]['itemSlug']
    assert story_slug3 == 'ITEM 2'
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_metadata_replace(rocreate, rometadatareplace):
    """
    GIVEN: Running order and MetadataReplace message (with updated roSlug field)
    EXPECT: Running order with roSlug field: RO SLUG NEW
    """
    ro = RunningOrder.from_file(rocreate)
    mdr = MetaDataReplace.from_file(rometadatareplace)
    d = ro.dict
    assert d['mos']['roCreate']['roEdStart'] == '2020-01-01T12:30:00'
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    ro_id = d['mos']['roCreate']['roID']
    assert ro_id == "RO ID"
    ro_id = d['mos']['roCreate']['roSlug']
    assert ro_id == "RO SLUG"

    ro += mdr
    d = ro.dict
    assert d['mos']['roCreate']['roEdStart'] == '2020-01-01T12:45:00'
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    ro_id = d['mos']['roCreate']['roID']
    assert ro_id == "RO ID"
    ro_id = d['mos']['roCreate']['roSlug']
    assert ro_id == "RO SLUG NEW"
    assert ro.base_tag.tag == 'roCreate'
    assert mdr.base_tag.tag == 'roMetadataReplace'

def test_story_append_item(rocreate, rostoryappend):
    """
    GIVEN: Running order and storyAppend message (add STORYNEW1 and STORYNEW2)
    EXPECT: Running order with STORYNEW1 and STORYNEW2 added to the end
    """
    ro = RunningOrder.from_file(rocreate)
    sa = StoryAppend.from_file(rostoryappend)
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3

    ro += sa
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 5
    assert d['mos']['roCreate']['story'][3]['storyID'] == 'STORYNEW1'
    assert d['mos']['roCreate']['story'][4]['storyID'] == 'STORYNEW2'
    assert ro.base_tag.tag == 'roCreate'
    assert sa.base_tag.tag == 'roStoryAppend'

def test_story_delete(rocreate, rostorydelete):
    """
    GIVEN: Running order and storyDelete message (delete STORY1 and STORY2)
    EXPECT: Running order with just STORY3 in
    """
    ro = RunningOrder.from_file(rocreate)
    sd = StoryDelete.from_file(rostorydelete)
    d = ro.dict
    assert isinstance(d['mos']['roCreate']['story'], list)
    assert len(d['mos']['roCreate']['story']) == 3

    ro += sd
    d = ro.dict
    assert isinstance(d['mos']['roCreate']['story'], dict)
    assert d['mos']['roCreate']['story']['storyID'] == 'STORY3'
    assert ro.base_tag.tag == 'roCreate'
    assert sd.base_tag.tag == 'roStoryDelete'

def test_story_insert(rocreate, rostoryinsert):
    """
    GIVEN: Running order and storyDelete message (delete STORY1 and STORY2)
    EXPECT: Running order with just STORY3 in
    """
    ro = RunningOrder.from_file(rocreate)
    si = StoryInsert.from_file(rostoryinsert)
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3

    ro += si
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 5
    assert d['mos']['roCreate']['story'][0]['storyID'] == 'STORY1'
    assert d['mos']['roCreate']['story'][1]['storyID'] == 'STORYNEW1'
    assert d['mos']['roCreate']['story'][2]['storyID'] == 'STORYNEW2'
    assert d['mos']['roCreate']['story'][3]['storyID'] == 'STORY2'
    assert d['mos']['roCreate']['story'][4]['storyID'] == 'STORY3'
    assert ro.base_tag.tag == 'roCreate'
    assert si.base_tag.tag == 'roStoryInsert'

def test_story_move(rocreate, rostorymove):
    """
    GIVEN: Running order and storyDelete message (delete STORY1 and STORY2)
    EXPECT: Running order with just STORY3 in
    """
    ro = RunningOrder.from_file(rocreate)
    sm = StoryMove.from_file(rostorymove)
    d = ro.dict
    assert d['mos']['roCreate']['story'][0]['storyID'] == 'STORY1'
    assert d['mos']['roCreate']['story'][2]['storyID'] == 'STORY3'

    ro += sm
    d = ro.dict
    assert d['mos']['roCreate']['story'][0]['storyID'] == 'STORY3'
    assert d['mos']['roCreate']['story'][1]['storyID'] == 'STORY1'
    assert ro.base_tag.tag == 'roCreate'
    assert sm.base_tag.tag == 'roStoryMove'

def test_story_replace(rocreate, rostoryreplace):
    """
    GIVEN: Running order and roStoryReplace message (STORY 1 for STORY ONE)
    EXPECT: Running order with STORY ONE and no STORY 1
    """
    ro = RunningOrder.from_file(rocreate)
    sr = StoryReplace.from_file(rostoryreplace)
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug == 'STORY 1'
    item_slug = d['mos']['roCreate']['story'][0]['item'][0]['itemSlug']
    assert item_slug == 'ITEM 1'

    ro += sr
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug == 'STORY ONE'
    item_slug = d['mos']['roCreate']['story'][0]['item']['itemSlug']
    assert item_slug == 'ITEM ONE'
    assert ro.base_tag.tag == 'roCreate'
    assert sr.base_tag.tag == 'roStoryReplace'

def test_item_delete(rocreate, roitemdelete):
    """
    GIVEN: Running order and roItemDelete message (STORY 1 for STORY ONE)
    EXPECT: Running order with STORY ONE and no STORY 1
    """
    ro = RunningOrder.from_file(rocreate)
    id = ItemDelete.from_file(roitemdelete)
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3

    ro += id
    d = ro.dict
    assert isinstance(d['mos']['roCreate']['story'][0]['item'], dict)
    assert d['mos']['roCreate']['story'][0]['item']['itemID'] == 'ITEM3'
    assert ro.base_tag.tag == 'roCreate'
    assert id.base_tag.tag == 'roItemDelete'

def test_item_insert(rocreate, roiteminsert):
    """
    GIVEN: Running order and roItemInsert message (ITEMNEW1 and ITEMNEW2)
    EXPECT: Running order with ITEMNEW1 and ITEMNEW2 above ITEM2
    """
    ro = RunningOrder.from_file(rocreate)
    ii = ItemInsert.from_file(roiteminsert)
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3

    ro += ii
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 5
    item_id1 = d['mos']['roCreate']['story'][0]['item'][1]['itemID']
    assert item_id1 == 'ITEMNEW1'
    item_id2 = d['mos']['roCreate']['story'][0]['item'][2]['itemID']
    assert item_id2 == 'ITEMNEW2'
    assert ro.base_tag.tag == 'roCreate'
    assert ii.base_tag.tag == 'roItemInsert'

def test_item_move_multiple(rocreate, roitemmovemultiple):
    """
    GIVEN: Running order and roItemMoveMultiple message (ITEM2, ITEM3 above ITEM1 in STORY1)
    EXPECT: Running order with STORY1 items in order (ITEM2, ITEM3, ITEM1)
    """
    ro = RunningOrder.from_file(rocreate)
    imm = ItemMoveMultiple.from_file(roitemmovemultiple)
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    assert d['mos']['roCreate']['story'][0]['item'][0]['itemID'] == 'ITEM1'
    assert d['mos']['roCreate']['story'][0]['item'][1]['itemID'] == 'ITEM2'
    assert d['mos']['roCreate']['story'][0]['item'][2]['itemID'] == 'ITEM3'

    ro += imm
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    assert d['mos']['roCreate']['story'][0]['item'][0]['itemID'] == 'ITEM2'
    assert d['mos']['roCreate']['story'][0]['item'][1]['itemID'] == 'ITEM3'
    assert d['mos']['roCreate']['story'][0]['item'][2]['itemID'] == 'ITEM1'
    assert ro.base_tag.tag == 'roCreate'
    assert imm.base_tag.tag == 'roItemMoveMultiple'

def test_item_replace(rocreate, roitemreplace):
    """
    GIVEN: Running order and roItemReplace message (add NEW to ITEM21 slug)
    EXPECT: Running order with STORY2 ITEM21 slug as 'NEW ITEM 21'
    """
    ro = RunningOrder.from_file(rocreate)
    ir = ItemReplace.from_file(roitemreplace)
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][1]['item']) == 3
    assert d['mos']['roCreate']['story'][1]['item'][0]['itemSlug'] == 'ITEM 21'

    ro += ir
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][1]['item']) == 3
    assert d['mos']['roCreate']['story'][1]['item'][0]['itemSlug'] == 'NEW ITEM 21'
    assert ro.base_tag.tag == 'roCreate'
    assert ir.base_tag.tag == 'roItemReplace'

def test_ro_replace(rocreate, roreplace):
    """
    GIVEN: Running order and roReplace message (replace roID's contents)
    EXPECT: Running order with roSlug 'RO SLUG NEW'
    """
    ro = RunningOrder.from_file(rocreate)
    ror = RunningOrderReplace.from_file(roreplace)
    d = ro.dict
    assert d['mos']['roCreate']['roSlug'] == 'RO SLUG'

    ro += ror
    d = ro.dict
    assert d['mos']['roCreate']['roSlug'] == 'RO SLUG NEW'
    assert ro.base_tag.tag == 'roCreate'
    assert ror.base_tag.tag == 'roReplace'

def test_ready_to_air(rocreate, roreadytoair):
    """
    GIVEN: Running order and roReadyToAir message
    EXPECT: Running order with no changes
    """
    ro = RunningOrder.from_file(rocreate)
    rta = ReadyToAir.from_file(roreadytoair)
    d = ro.dict
    assert d['mos']['roCreate']['roSlug'] == 'RO SLUG'

    ro += rta
    d = ro.dict
    assert d['mos']['roCreate']['roSlug'] == 'RO SLUG'
    assert ro.base_tag.tag == 'roCreate'
    assert rta.base_tag.tag == 'roReadyToAir'

def test_running_order_end(rocreate, rodelete):
    """
    GIVEN: Running order and RunningOrderEnd message
    EXPECT: Running order with roDelete tag
    """
    ro = RunningOrder.from_file(rocreate)
    rd = RunningOrderEnd.from_file(rodelete)
    d = ro.dict
    ro_id = d['mos']['roCreate']['roID']
    assert ro_id == 'RO ID'
    assert 'mosromgrmeta' not in d['mos']

    ro += rd
    assert repr(ro) == '<RunningOrder 1000 completed>'
    d = ro.dict
    assert 'mosromgrmeta' in d['mos']
    assert 'roDelete' in d['mos']['mosromgrmeta']
    assert d['mos']['roCreate']['roID'] == ro_id
    assert d['mos']['mosromgrmeta']['roDelete']['roID'] == ro_id
    assert ro.base_tag.tag == 'roCreate'
    assert rd.base_tag.tag == 'roDelete'

def test_merge_after_delete(rocreate, rodelete, rostorysend1):
    """
    GIVEN: A completed RunningOrder and a StorySend
    EXPECT: The RunningOrder should refuse the merge
    """
    ro = RunningOrder.from_file(rocreate)
    rd = RunningOrderEnd.from_file(rodelete)
    ss = StorySend.from_file(rostorysend1)
    ro += rd
    with pytest.raises(MosCompletedMergeError):
        ro += ss

def test_merge_failure(rocreate, rostorysend3):
    """
    GIVEN: A RunningOrder and an invalid StorySend
    EXPECT: The RunningOrder should fail to merge
    """
    ro = RunningOrder.from_file(rocreate)
    ss3 = StorySend.from_file(rostorysend3)
    with warnings.catch_warnings(record=True) as w:
        ro += ss3
    assert len(w) == 1
    assert w[0].category == StoryNotFoundWarning

def test_storysend_merge_failure(rocreate, rostorysend6):
    """
    GIVEN: A RunningOrder and a StorySend with an unknown Story ID
    EXPECT: The RunningOrder should fail to merge
    """
    ro = RunningOrder.from_file(rocreate)
    ss6 = StorySend.from_file(rostorysend6)
    with warnings.catch_warnings(record=True) as w:
        ro += ss6
    assert len(w) == 1
    assert w[0].category == StoryNotFoundWarning
