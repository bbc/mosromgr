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

def test_metadata_replace(rocreate, rometadatareplace):
    """
    GIVEN: Running order and roMetadataReplace message (with updated roSlug field)
    EXPECT: Running order with roSlug field: RO SLUG NEW
    """
    ro = RunningOrder.from_file(rocreate)
    mdr = MetaDataReplace.from_file(rometadatareplace)
    d = ro.dict
    assert d['mos']['roCreate']['roEdStart'] == '2020-01-01T12:30:00'
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    ro_id = d['mos']['roCreate']['roID']
    assert ro_id == 'RO ID'
    ro_id = d['mos']['roCreate']['roSlug']
    assert ro_id == 'RO SLUG'
    assert 'roChannel' not in d['mos']['roCreate']

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
    assert 'roChannel' in d['mos']['roCreate']
    assert d['mos']['roCreate']['roChannel'] == 'bbcnews'

def test_story_append(rocreate, rostoryappend):
    """
    GIVEN: Running order and roStoryAppend message (add STORYNEW1 and STORYNEW2)
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
    GIVEN: Running order and roStoryDelete message (delete STORY1 and STORY2)
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

def test_story_delete_no_matching_stories(rocreate, rostorydelete2):
    """
    GIVEN: Running order and roStoryDelete message with no matching stories
    EXPECT: Running order unaltered, with merge error
    """
    ro = RunningOrder.from_file(rocreate)
    sd = StoryDelete.from_file(rostorydelete2)
    d_before = ro.dict

    with warnings.catch_warnings(record=True) as w:
        ro += sd
    assert len(w) == 1
    assert w[0].category == StoryNotFoundWarning

    d_after = ro.dict
    assert d_before == d_after

def test_story_insert(rocreate, rostoryinsert):
    """
    GIVEN: Running order and roStoryInsert message (insert 2 new stories)
    EXPECT: Running order new stories added
    """
    ro = RunningOrder.from_file(rocreate)
    si = StoryInsert.from_file(rostoryinsert)
    d = ro.dict
    stories = d['mos']['roCreate']['story']
    assert len(stories) == 3
    story_ids = [i['storyID'] for i in stories]
    assert story_ids == ['STORY1', 'STORY2', 'STORY3']

    ro += si
    d = ro.dict
    stories = d['mos']['roCreate']['story']
    assert len(stories) == 5
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY1', 'STORY4', 'STORY5', 'STORY2', 'STORY3']
    assert ro.base_tag.tag == 'roCreate'
    assert si.base_tag.tag == 'roStoryInsert'

def test_story_insert_with_no_target_story(rocreate, rostoryinsert2):
    """
    GIVEN: Running order and roStoryInsert message with no target story
    EXPECT: Running order unchanged, and a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    si = StoryInsert.from_file(rostoryinsert2)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += si
    
    d_after = ro.dict
    assert d_before == d_after

def test_story_insert_with_known_target_story(rocreate, rostoryinsert3):
    """
    GIVEN: Running order and roStoryInsert message with already known source story
    EXPECT: Running order unchanged, and a warning
    """
    ro = RunningOrder.from_file(rocreate)
    si = StoryInsert.from_file(rostoryinsert3)
    d_before = ro.dict

    with warnings.catch_warnings(record=True) as w:
        ro += si
    assert len(w) == 1
    assert w[0].category == DuplicateStoryWarning

    d_after = ro.dict
    assert d_before == d_after

def test_story_move(rocreate, rostorymove):
    """
    GIVEN: Running order and roStoryMove message (move STORY1 above STORY3)
    EXPECT: Running order with STORY3 at the top
    """
    ro = RunningOrder.from_file(rocreate)
    sm = StoryMove.from_file(rostorymove)
    d = ro.dict
    stories = d['mos']['roCreate']['story']
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY1', 'STORY2', 'STORY3']

    ro += sm
    d = ro.dict
    stories = d['mos']['roCreate']['story']
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY3', 'STORY1', 'STORY2']
    assert ro.base_tag.tag == 'roCreate'
    assert sm.base_tag.tag == 'roStoryMove'

def test_story_move_to_bottom(rocreate, rostorymove2):
    """
    GIVEN: Running order and roStoryMove message (move STORY1 above STORY3)
    EXPECT: Running order with STORY1 at the bottom
    """
    ro = RunningOrder.from_file(rocreate)
    sm = StoryMove.from_file(rostorymove2)
    d = ro.dict
    stories = d['mos']['roCreate']['story']
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY1', 'STORY2', 'STORY3']

    ro += sm
    d = ro.dict
    stories = d['mos']['roCreate']['story']
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY2', 'STORY3', 'STORY1']

def test_story_move_no_stories(rocreate, rostorymove3):
    """
    GIVEN: Running order and roStoryMove message with no stories
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    sm = StoryMove.from_file(rostorymove3)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += sm

    d_after = ro.dict
    assert d_before == d_after

def test_story_move_with_unknown_source_story(rocreate, rostorymove4):
    """
    GIVEN: Running order and roStoryMove message with an unknown source story
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    sm = StoryMove.from_file(rostorymove4)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += sm

    d_after = ro.dict
    assert d_before == d_after

def test_story_move_with_unknown_target_story(rocreate, rostorymove5):
    """
    GIVEN: Running order and roStoryMove message with an unknown target story
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    sm = StoryMove.from_file(rostorymove5)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += sm

    d_after = ro.dict
    assert d_before == d_after

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

def test_story_replace_unknown_story(rocreate, rostoryreplace2):
    """
    GIVEN: Running order and roStoryReplace message with an unknown story
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    sr = StoryReplace.from_file(rostoryreplace2)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
       ro += sr

    d_after = ro.dict
    assert d_before == d_after

def test_story_replace_no_stories(rocreate, rostoryreplace3):
    """
    GIVEN: Running order and roStoryReplace message with no stories
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    sr = StoryReplace.from_file(rostoryreplace3)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
       ro += sr

    d_after = ro.dict
    assert d_before == d_after

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

def test_item_delete_no_story(rocreate, roitemdelete2):
    """
    GIVEN: Running order and roItemDelete message (STORY 1 for STORY ONE)
    EXPECT: Running order unchanged, and a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    id = ItemDelete.from_file(roitemdelete2)
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3

    with pytest.raises(MosMergeError):
        ro += id
    d = ro.dict
    
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3

def test_item_delete_item_not_found(rocreate, roitemdelete3):
    """
    GIVEN: Running order and roItemDelete message (STORY 1 for STORY ONE)
    EXPECT: Running order unchanged, with a warning
    """
    ro = RunningOrder.from_file(rocreate)
    id = ItemDelete.from_file(roitemdelete3)
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3

    with warnings.catch_warnings(record=True) as w:
        ro += id
    assert len(w) == 1
    assert w[0].category == ItemNotFoundWarning

    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3

def test_item_insert(rocreate, roiteminsert):
    """
    GIVEN: Running order and roItemInsert message (ITEM4 and ITEM5)
    EXPECT: Running order with ITEM4 and ITEM5 above ITEM2
    """
    ro = RunningOrder.from_file(rocreate)
    ii = ItemInsert.from_file(roiteminsert)
    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 3
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM1', 'ITEM2', 'ITEM3']

    ro += ii
    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 5
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM1', 'ITEM4', 'ITEM5', 'ITEM2', 'ITEM3']
    assert ro.base_tag.tag == 'roCreate'
    assert ii.base_tag.tag == 'roItemInsert'

def test_item_insert_with_unknown_story(rocreate, roiteminsert2):
    """
    GIVEN: Running order and roItemInsert message with unknown story
    EXPECT: Running order unchanged, an a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ii = ItemInsert.from_file(roiteminsert2)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += ii
    
    d_after = ro.dict
    assert d_before == d_after

def test_item_insert_with_unknown_item(rocreate, roiteminsert3):
    """
    GIVEN: Running order and roItemInsert message with an unknown item
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ii = ItemInsert.from_file(roiteminsert3)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += ii

    d_after = ro.dict
    assert d_before == d_after

def test_item_insert_move_to_bottom(rocreate, roiteminsert4):
    """
    GIVEN: Running order and roItemInsert message with no target item ID
    EXPECT: Running order with ITEM4 and ITEM5 at the bottom
    """
    ro = RunningOrder.from_file(rocreate)
    ii = ItemInsert.from_file(roiteminsert4)
    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 3
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM1', 'ITEM2', 'ITEM3']

    ro += ii
    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 5
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM1', 'ITEM2', 'ITEM3', 'ITEM4', 'ITEM5']

def test_item_move_multiple(rocreate, roitemmovemultiple):
    """
    GIVEN: Running order and roItemMoveMultiple message (ITEM2, ITEM3 above ITEM1 in STORY1)
    EXPECT: Running order with STORY1 items in order (ITEM2, ITEM3, ITEM1)
    """
    ro = RunningOrder.from_file(rocreate)
    imm = ItemMoveMultiple.from_file(roitemmovemultiple)
    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 3
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM1', 'ITEM2', 'ITEM3']

    ro += imm
    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 3
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM2', 'ITEM3', 'ITEM1']
    assert ro.base_tag.tag == 'roCreate'
    assert imm.base_tag.tag == 'roItemMoveMultiple'

def test_item_move_multiple_no_story_id(rocreate, roitemmovemultiple2):
    """
    GIVEN: Running order and roItemMoveMultiple message with no story id
    EXPECT: Running order unchanged, and a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    imm = ItemMoveMultiple.from_file(roitemmovemultiple2)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += imm

    d_after = ro.dict
    assert d_before == d_after

def test_item_move_multiple_no_story(rocreate, roitemmovemultiple3):
    """
    GIVEN: Running order and roItemMoveMultiple message with no story tag
    EXPECT: Running order unchanged, and a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    imm = ItemMoveMultiple.from_file(roitemmovemultiple3)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += imm

    d_after = ro.dict
    assert d_before == d_after

def test_item_move_multiple_unknown_story(rocreate, roitemmovemultiple4):
    """
    GIVEN: Running order and roItemMoveMultiple message with an unknown story
    EXPECT: Running order unchanged, and a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    imm = ItemMoveMultiple.from_file(roitemmovemultiple4)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += imm

    d_after = ro.dict
    assert d_before == d_after

def test_item_move_multiple_unknown_story(rocreate, roitemmovemultiple5):
    """
    GIVEN: Running order and roItemMoveMultiple message (ITEM2 and ITEM3 above
    ITEM1 in STORY1)
    EXPECT: Running order with STORY1 items in order (ITEM2, ITEM3, ITEM1)
    """
    ro = RunningOrder.from_file(rocreate)
    imm = ItemMoveMultiple.from_file(roitemmovemultiple5)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += imm
        
    d_after = ro.dict
    assert d_before == d_after

def test_item_move_multiple_move_to_bottom(rocreate, roitemmovemultiple6):
    """
    GIVEN: Running order and roItemMoveMultiple message (ITEM1 and ITEM2 to
    bottom of STORY1)
    EXPECT: Running order with STORY1 items in order (ITEM3, ITEM1, ITEM2)
    """
    ro = RunningOrder.from_file(rocreate)
    imm = ItemMoveMultiple.from_file(roitemmovemultiple6)
    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 3
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM1', 'ITEM2', 'ITEM3']

    ro += imm
    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 3
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM3', 'ITEM1', 'ITEM2']

def test_item_move_multiple_unknown_target_item(rocreate, roitemmovemultiple7):
    """
    GIVEN: Running order and roItemMoveMultiple message with unknown target item
    EXPECT: Running order unchanged, and a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    imm = ItemMoveMultiple.from_file(roitemmovemultiple7)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += imm
        
    d_after = ro.dict
    assert d_before == d_after

def test_item_move_multiple_unknown_source_item(rocreate, roitemmovemultiple8):
    """
    GIVEN: Running order and roItemMoveMultiple message with unknown source item
    EXPECT: Running order unchanged, and a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    imm = ItemMoveMultiple.from_file(roitemmovemultiple8)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += imm
        
    d_after = ro.dict
    assert d_before == d_after

def test_item_replace(rocreate, roitemreplace):
    """
    GIVEN: Running order and roItemReplace message (add NEW to ITEM21 slug)
    EXPECT: Running order with STORY2 ITEM21 slug as 'NEW ITEM 21'
    """
    ro = RunningOrder.from_file(rocreate)
    ir = ItemReplace.from_file(roitemreplace)
    d = ro.dict
    items = d['mos']['roCreate']['story'][1]['item']
    assert len(items) == 3
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM21', 'ITEM22', 'ITEM23']

    ro += ir
    d = ro.dict
    items = d['mos']['roCreate']['story'][1]['item']
    assert len(items) == 4
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM24', 'ITEM25', 'ITEM22', 'ITEM23']
    assert ro.base_tag.tag == 'roCreate'
    assert ir.base_tag.tag == 'roItemReplace'

def test_item_replace_unknown_story(rocreate, roitemreplace2):
    """
    GIVEN: Running order and roItemReplace message with unknown story
    EXPECT: Running order unchanged, and a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ir = ItemReplace.from_file(roitemreplace2)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += ir
    
    d_after = ro.dict
    assert d_before == d_after

def test_item_replace_unknown_item(rocreate, roitemreplace3):
    """
    GIVEN: Running order and roItemReplace message with unknown story
    EXPECT: Running order unchanged, and a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ir = ItemReplace.from_file(roitemreplace3)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += ir
    
    d_after = ro.dict
    assert d_before == d_after

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
