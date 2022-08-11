# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

import warnings

import pytest

from mosromgr.mostypes import *
from mosromgr.exc import *


def test_merge_element_action_story_replace(rocreate, eastoryreplace):
    """
    GIVEN: Running order and EAStoryReplace message (STORY1 for STORY5)
    EXPECT: Running order with STORY5 instead of STORY1
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStoryReplace.from_file(eastoryreplace)
    d = ro.dict
    stories = d['mos']['roCreate']['story']
    assert len(stories) == 3
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY1', 'STORY2', 'STORY3']

    ro += ea
    d = ro.dict
    stories = d['mos']['roCreate']['story']
    assert len(stories) == 3
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY5', 'STORY2', 'STORY3']
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_merge_element_action_story_replace_unknown_story(rocreate, eastoryreplace2):
    """
    GIVEN: Running order and EAStoryReplace message with unknown story
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStoryReplace.from_file(eastoryreplace2)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += ea

    d_after = ro.dict
    assert d_before == d_after

def test_merge_element_action_item_replace(rocreate, eaitemreplace):
    """
    GIVEN: Running order and EAItemReplace message (ITEM1 with ITEM21 in STORY1)
    EXPECT: Running order with ITEM21 in place of ITEM1 In STORY1
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemReplace.from_file(eaitemreplace)
    
    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 3
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM1', 'ITEM2', 'ITEM3']

    ro += ea

    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 3
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM21', 'ITEM2', 'ITEM3']
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_merge_element_action_item_replace_unknown_story(rocreate, eaitemreplace2):
    """
    GIVEN: Running order and EAItemReplace message with unknown story
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemReplace.from_file(eaitemreplace2)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += ea

    d_after = ro.dict
    assert d_before == d_after

def test_merge_element_action_item_replace_unknown_item(rocreate, eaitemreplace3):
    """
    GIVEN: Running order and EAItemReplace message with unknown item
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemReplace.from_file(eaitemreplace3)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += ea

    d_after = ro.dict
    assert d_before == d_after

def test_merge_element_action_story_delete(rocreate, eastorydelete):
    """
    GIVEN: Running order and EAStoryDelete message (delete STORY1)
    EXPECT: Running order with no STORY1
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStoryDelete.from_file(eastorydelete)
    d = ro.dict
    stories = d['mos']['roCreate']['story']
    assert len(stories) == 3
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY1', 'STORY2', 'STORY3']

    ro += ea
    d = ro.dict
    stories = d['mos']['roCreate']['story']
    assert len(stories) == 2
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY2', 'STORY3']
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_merge_element_action_story_delete_unknown_story(rocreate, eastorydelete2):
    """
    GIVEN: Running order and EAStoryDelete message with an unknown story
    EXPECT: Running order unchanged, with a warning
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStoryDelete.from_file(eastorydelete2)
    d_before = ro.dict

    with warnings.catch_warnings(record=True) as w:
        ro += ea
    assert len(w) == 1
    assert w[0].category == StoryNotFoundWarning

    d_after = ro.dict
    assert d_before == d_after

def test_merge_element_action_item_delete(rocreate, eaitemdelete):
    """
    GIVEN: Running order and EAStoryDelete message (delete STORY1)
    EXPECT: Running order with no STORY1
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemDelete.from_file(eaitemdelete)
    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 3
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM1', 'ITEM2', 'ITEM3']

    ro += ea
    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 2
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM2', 'ITEM3']
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_merge_element_action_item_delete_unknown_story(rocreate, eaitemdelete2):
    """
    GIVEN: Running order and EAStoryDelete message with an unknown story
    EXPECT: Running order unchanged, with a warning
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemDelete.from_file(eaitemdelete2)
    d_before = ro.dict

    with warnings.catch_warnings(record=True) as w:
        ro += ea
    assert len(w) == 1
    assert w[0].category == StoryNotFoundWarning

    d_after = ro.dict
    assert d_before == d_after

def test_merge_element_action_item_delete_unknown_item(rocreate, eaitemdelete3):
    """
    GIVEN: Running order and EAStoryDelete message with an unknown item
    EXPECT: Running order unchanged, with a warning
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemDelete.from_file(eaitemdelete3)
    d_before = ro.dict

    with warnings.catch_warnings(record=True) as w:
        ro += ea
    assert len(w) == 1
    assert w[0].category == ItemNotFoundWarning

    d_after = ro.dict
    assert d_before == d_after

def test_merge_element_action_story_insert(rocreate, eastoryinsert):
    """
    GIVEN: Running order and EAStoryInsert message (insert STORY5)
    EXPECT: Running order with STORY5 between STORY1 and STORY2
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStoryInsert.from_file(eastoryinsert)
    d = ro.dict
    stories = d['mos']['roCreate']['story']
    assert len(stories) == 3
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY1', 'STORY2', 'STORY3']
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

    ro += ea

    d = ro.dict
    stories = d['mos']['roCreate']['story']
    assert len(stories) == 4
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY1', 'STORY5', 'STORY2', 'STORY3']
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_merge_element_action_story_insert_at_bottom(rocreate, eastoryinsert2):
    """
    GIVEN: Running order and EAStoryInsert message (insert STORY5)
    EXPECT: Running order with STORY5 at the bottom
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStoryInsert.from_file(eastoryinsert2)
    d = ro.dict
    stories = d['mos']['roCreate']['story']
    assert len(stories) == 3
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY1', 'STORY2', 'STORY3']
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

    ro += ea

    d = ro.dict
    stories = d['mos']['roCreate']['story']
    assert len(stories) == 4
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY1', 'STORY2', 'STORY3', 'STORY5']
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_merge_element_action_story_insert_unknown_story(rocreate, eastoryinsert3):
    """
    GIVEN: Running order and EAStoryInsert message (insert STORY5)
    EXPECT: Running order unchanged, with merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStoryInsert.from_file(eastoryinsert3)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += ea

    d_after = ro.dict
    assert d_before == d_after

def test_merge_element_action_story_insert_duplicate_story(rocreate, eastoryinsert4):
    """
    GIVEN: Running order and EAStoryInsert message (insert STORY5)
    EXPECT: Running order unchanged, with merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStoryInsert.from_file(eastoryinsert4)
    d_before = ro.dict

    with warnings.catch_warnings(record=True) as w:
        ro += ea
    assert len(w) == 1
    assert w[0].category == DuplicateStoryWarning

    d_after = ro.dict
    assert d_before == d_after

def test_merge_element_action_item_insert(rocreate, eaiteminsert):
    """
    GIVEN: Running order and EAItemInsert message (insert ITEM 5 in STORY1)
    EXPECT: Running order with ITEM 5 between ITEM1 and ITEM2 in STORY1
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemInsert.from_file(eaiteminsert)
    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 3
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM1', 'ITEM2', 'ITEM3']

    ro += ea
    
    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 4
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM1', 'ITEM5', 'ITEM2', 'ITEM3']

def test_merge_element_action_item_insert_unknown_story(rocreate, eaiteminsert2):
    """
    GIVEN: Running order and EAItemInsert message with unknown story
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemInsert.from_file(eaiteminsert2)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += ea
    
    d_after = ro.dict
    assert d_before == d_after

def test_merge_element_action_item_insert_at_bottom(rocreate, eaiteminsert3):
    """
    GIVEN: Running order and EAItemInsert message (insert ITEM 5 in STORY1)
    EXPECT: Running order with ITEM 5 at the end
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemInsert.from_file(eaiteminsert3)
    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 3
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM1', 'ITEM2', 'ITEM3']

    ro += ea
    
    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 4
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM1', 'ITEM2', 'ITEM3', 'ITEM5']

def test_merge_element_action_item_insert_unknown_item(rocreate, eaiteminsert4):
    """
    GIVEN: Running order and EAItemInsert message with unknown item
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemInsert.from_file(eaiteminsert4)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += ea
    
    d_after = ro.dict
    assert d_before == d_after

def test_merge_element_action_story_swap_missing_target(rocreate, eastoryswap):
    """
    GIVEN: Running order and EAStorySwap message (swap STORY1 and STORY2)
    EXPECT: Running order with positions of STORY1 and STORY2 swapped
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStorySwap.from_file(eastoryswap)
    d = ro.dict
    stories = d['mos']['roCreate']['story']
    assert len(stories) == 3
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY1', 'STORY2', 'STORY3']

    ro += ea
    d = ro.dict
    stories = d['mos']['roCreate']['story']
    assert len(stories) == 3
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY2', 'STORY1', 'STORY3']
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_merge_element_action_story_swap_blank_target_storyid(rocreate, eastoryswap2):
    """
    GIVEN: Running order and EAStorySwap message (swap STORY1 and STORY2)
    EXPECT: Running order with positions of STORY1 and STORY2 swapped
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStorySwap.from_file(eastoryswap2)
    d = ro.dict
    stories = d['mos']['roCreate']['story']
    assert len(stories) == 3
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY1', 'STORY2', 'STORY3']

    ro += ea
    d = ro.dict
    stories = d['mos']['roCreate']['story']
    assert len(stories) == 3
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY2', 'STORY1', 'STORY3']
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_merge_element_action_story_swap_unknown_story1(rocreate, eastoryswap3):
    """
    GIVEN: Running order and EAStorySwap message with unknown story 1
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStorySwap.from_file(eastoryswap3)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += ea
    d_after = ro.dict

    assert d_before == d_after

def test_merge_element_action_story_swap_unknown_story2(rocreate, eastoryswap4):
    """
    GIVEN: Running order and EAStorySwap message with unknown story 2
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStorySwap.from_file(eastoryswap4)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += ea
    d_after = ro.dict

    assert d_before == d_after

def test_merge_element_action_item_swap(rocreate, eaitemswap):
    """
    GIVEN: Running order and EAItemSwap message (swap ITEM1 and ITEM2)
    EXPECT: Running order with positions of ITEM1 and ITEM2 swapped in STORY 1
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemSwap.from_file(eaitemswap)
    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 3
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM1', 'ITEM2', 'ITEM3']

    ro += ea

    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 3
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM2', 'ITEM1', 'ITEM3']
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_merge_element_action_item_swap_unknown_story(rocreate, eaitemswap2):
    """
    GIVEN: Running order and EAItemSwap message with an unknown story
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemSwap.from_file(eaitemswap2)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += ea

    d_after = ro.dict
    assert d_before == d_after

def test_merge_element_action_item_swap_unknown_item1(rocreate, eaitemswap3):
    """
    GIVEN: Running order and EAItemSwap message with an unknown item
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemSwap.from_file(eaitemswap3)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += ea

    d_after = ro.dict
    assert d_before == d_after

def test_merge_element_action_item_swap_unknown_item2(rocreate, eaitemswap4):
    """
    GIVEN: Running order and EAItemSwap message with an unknown item
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemSwap.from_file(eaitemswap4)
    d_before = ro.dict

    with pytest.raises(MosMergeError):
        ro += ea

    d_after = ro.dict
    assert d_before == d_after

def test_merge_element_action_story_move(rocreate, eastorymove):
    """
    GIVEN: Running order and EAStoryMove message (move STORY 3 to top)
    EXPECT: Running order with STORY 3 at top, above STORY 1
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStoryMove.from_file(eastorymove)
    d = ro.dict
    stories = d['mos']['roCreate']['story']
    assert len(stories) == 3
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY1', 'STORY2', 'STORY3']

    ro += ea
    d = ro.dict
    stories = d['mos']['roCreate']['story']
    assert len(stories) == 3
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY3', 'STORY1', 'STORY2']
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_merge_element_action_story_move_no_target(rocreate, eastorymove2):
    """
    GIVEN: Running order and EAStoryMove message (move STORY 1 to bottom)
    EXPECT: Running order with STORY 1 at bottom
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStoryMove.from_file(eastorymove2)
    d = ro.dict
    stories = d['mos']['roCreate']['story']
    assert len(stories) == 3
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY1', 'STORY2', 'STORY3']

    ro += ea

    d = ro.dict
    stories = d['mos']['roCreate']['story']
    assert len(stories) == 3
    story_ids = [s['storyID'] for s in stories]
    assert story_ids == ['STORY2', 'STORY3', 'STORY1']
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_merge_element_action_story_move_unknown_target_story(rocreate, eastorymove3):
    """
    GIVEN: Running order and EAStoryMove message with unknown target story
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStoryMove.from_file(eastorymove3)
    d_before = ro.dict
    
    with pytest.raises(MosMergeError):
        ro += ea

    d_after = ro.dict
    assert d_before == d_after

def test_merge_element_action_story_move_unknown_source_story(rocreate, eastorymove4):
    """
    GIVEN: Running order and EAStoryMove message with unknown source story
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAStoryMove.from_file(eastorymove4)
    d_before = ro.dict
    
    with pytest.raises(MosMergeError):
        ro += ea

    d_after = ro.dict
    assert d_before == d_after

def test_merge_element_action_item_move(rocreate, eaitemmove):
    """
    GIVEN: Running order and EAItemMove message (move ITEM3 to top)
    EXPECT: Running order with ITEM3 at top of STORY 1
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemMove.from_file(eaitemmove)
    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 3
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM1', 'ITEM2', 'ITEM3']

    ro += ea

    d = ro.dict
    items = d['mos']['roCreate']['story'][0]['item']
    assert len(items) == 3
    item_ids = [i['itemID'] for i in items]
    assert item_ids == ['ITEM3', 'ITEM1', 'ITEM2']
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_merge_element_action_item_move_with_unknown_story(rocreate, eaitemmove2):
    """
    GIVEN: Running order and EAItemMove message with unknown story
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemMove.from_file(eaitemmove2)

    d_before = ro.dict
    
    with pytest.raises(MosMergeError):
        ro += ea

    d_after = ro.dict
    assert d_before == d_after

def test_merge_element_action_item_move_with_unknown_target_item(rocreate, eaitemmove3):
    """
    GIVEN: Running order and EAItemMove message with unknown target item
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemMove.from_file(eaitemmove3)

    d_before = ro.dict
    
    with pytest.raises(MosMergeError):
        ro += ea

    d_after = ro.dict
    assert d_before == d_after

def test_merge_element_action_item_move_with_unknown_source_item(rocreate, eaitemmove4):
    """
    GIVEN: Running order and EAItemMove message with unknown source item
    EXPECT: Running order unchanged, with a merge error
    """
    ro = RunningOrder.from_file(rocreate)
    ea = EAItemMove.from_file(eaitemmove4)

    d_before = ro.dict
    
    with pytest.raises(MosMergeError):
        ro += ea

    d_after = ro.dict
    assert d_before == d_after