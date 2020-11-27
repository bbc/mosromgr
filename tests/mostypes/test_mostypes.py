from xml.etree.ElementTree import Element
import warnings

import pytest

from mosromgr.mostypes import *
from mosromgr.exc import *
from const import *


def test_running_order_init():
    "Test we can create a RunningOrder object from a roCreate file"
    ro = RunningOrder.from_file(ROCREATE)
    assert repr(ro) == '<RunningOrder 1000>'
    assert ro.ro_id == 'RO ID'
    assert ro.ro_slug == 'RO SLUG'
    assert isinstance(ro.xml, Element)
    assert str(ro).startswith('<mos>')
    assert str(ro).endswith('</mos>')

def test_running_order_init_str():
    "Test we can create a RunningOrder object from a string representation of a roCreate file"
    with open(ROCREATE) as f:
        xml = f.read()
    ro = RunningOrder.from_string(xml)
    assert repr(ro) == '<RunningOrder 1000>'
    assert ro.ro_id == 'RO ID'
    assert ro.ro_slug == 'RO SLUG'
    assert isinstance(ro.xml, Element)
    assert str(ro).startswith('<mos>')
    assert str(ro).endswith('</mos>')

def test_story_send_init():
    "Test we can create a StorySend object from a roStorySend file"
    ss = StorySend.from_file(ROSTORYSEND1)
    assert repr(ss) == '<StorySend 1001>'
    assert ss.ro_id == 'RO ID'
    assert isinstance(ss.xml, Element)
    assert str(ss).startswith('<mos>')
    assert str(ss).endswith('</mos>')

def test_story_send():
    """
    GIVEN: Running order and StorySend message (Add contents to STORY 1)
    EXPECT: Running order with storyBody present in STORY 1
    """
    ro = RunningOrder.from_file(ROCREATE)
    ss = StorySend.from_file(ROSTORYSEND1)
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3
    ro += ss
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3
    body1 = d['mos']['roCreate']['story'][0]['p']
    assert body1 == '(BONG+PRES)'
    assert ro.base_tag.tag == 'roCreate'
    assert ss.base_tag.tag == 'roStorySend'

def test_element_action_replace_story_init():
    "Test we can create an EAStoryReplace object from a roElementAction file"
    ea = EAStoryReplace.from_file(ROELEMENTACTIONREPSTORY)
    assert repr(ea) == '<EAStoryReplace 1003>'
    assert ea.ro_id == 'RO ID'

def test_element_action_replace_story():
    """
    GIVEN: Running order and EAStoryReplace message (STORY 1 for STORY ONE)
    EXPECT: Running order with STORY ONE and no STORY 1
    """
    ro = RunningOrder.from_file(ROCREATE)
    ea = EAStoryReplace.from_file(ROELEMENTACTIONREPSTORY)
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

def test_element_action_replace_item_init():
    "Test we can create an EAItemReplace object from a roElementAction file"
    ea = EAItemReplace.from_file(ROELEMENTACTIONREPITEM)
    assert repr(ea) == '<EAItemReplace 1004>'
    assert ea.ro_id == 'RO ID'

def test_element_action_replace_item():
    """
    GIVEN: Running order and EAItemReplace message (ITEM 21 for NEW ITEM 21)
    EXPECT: Running order with NEW ITEM 21 in STORY 2
    """
    ro = RunningOrder.from_file(ROCREATE)
    ea = EAItemReplace.from_file(ROELEMENTACTIONREPITEM)
    ro += ea
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug = d['mos']['roCreate']['story'][1]['storySlug']
    assert story_slug == 'STORY 2'
    item_slug = d['mos']['roCreate']['story'][1]['item'][0]['itemSlug']
    assert item_slug == 'NEW ITEM 21'
    assert ro.base_tag.tag == 'roCreate'
    assert ea.base_tag.tag == 'roElementAction'

def test_element_action_delete_story_init():
    "Test we can create an EAStoryDelete object from a roElementAction file"
    ea = EAStoryDelete.from_file(ROELEMENTACTIONDELSTORY)
    assert repr(ea) == '<EAStoryDelete 1005>'
    assert ea.ro_id == 'RO ID'

def test_element_action_delete_story():
    """
    GIVEN: Running order and EAStoryDelete message (delete STORY 1)
    EXPECT: Running order with no STORY 1
    """
    ro = RunningOrder.from_file(ROCREATE)
    ea = EAStoryDelete.from_file(ROELEMENTACTIONDELSTORY)
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

def test_element_action_delete_item_init():
    "Test we can create an EAItemDelete object from a roElementAction file"
    ea = EAItemDelete.from_file(ROELEMENTACTIONDELITEM)
    assert repr(ea) == '<EAItemDelete 1006>'
    assert ea.ro_id == 'RO ID'

def test_element_action_delete_item():
    """
    GIVEN: Running order and EAItemDelete message (delete ITEM 1 in STORY 1)
    EXPECT: Running order with no ITEM 1 in STORY 1
    """
    ro = RunningOrder.from_file(ROCREATE)
    ea = EAItemDelete.from_file(ROELEMENTACTIONDELITEM)
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

def test_element_action_insert_story_init():
    "Test we can create an EAStoryInsert object from a roElementAction file"
    ea = EAStoryInsert.from_file(ROELEMENTACTIONINSERTSTORY)
    assert repr(ea) == '<EAStoryInsert 1007>'
    assert ea.ro_id == 'RO ID'

def test_element_action_insert_story():
    """
    GIVEN: Running order and EAStoryInsert message (insert STORY NEW)
    EXPECT: Running order with STORY NEW between STORY 1 and 2
    """
    ro = RunningOrder.from_file(ROCREATE)
    ea = EAStoryInsert.from_file(ROELEMENTACTIONINSERTSTORY)
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

def test_element_action_insert_item_init():
    "Test we can create an EAItemInsert object from a roElementAction file"
    ea = EAItemInsert.from_file(ROELEMENTACTIONINSERTITEM)
    assert repr(ea) == '<EAItemInsert 1008>'
    assert ea.ro_id == 'RO ID'

def test_element_action_insert_item():
    """
    GIVEN: Running order and EAItemInsert message (insert ITEM NEW in STORY 1)
    EXPECT: Running order with ITEM NEW between ITEM 1 and 2 in STORY 1
    """
    ro = RunningOrder.from_file(ROCREATE)
    ea = EAItemInsert.from_file(ROELEMENTACTIONINSERTITEM)
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

def test_element_action_swap_story_init():
    "Test we can create an EAStorySwap object from a roElementAction file"
    ea = EAStorySwap.from_file(ROELEMENTACTIONSWAPSTORY)
    assert repr(ea) == '<EAStorySwap 1009>'
    assert ea.ro_id == 'RO ID'

def test_element_action_swap_story():
    """
    GIVEN: Running order and EAStorySwap message (swap STORY 1 STORY 2)
    EXPECT: Running order with positions of STORY 1 and 2 swapped
    """
    ro = RunningOrder.from_file(ROCREATE)
    ea = EAStorySwap.from_file(ROELEMENTACTIONSWAPSTORY)
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

def test_element_action_swap_item_init():
    "Test we can create an EAItemSwap object from a roElementAction file"
    ea = EAItemSwap.from_file(ROELEMENTACTIONSWAPITEM)
    assert repr(ea) == '<EAItemSwap 1010>'
    assert ea.ro_id == 'RO ID'

def test_element_action_swap_item():
    """
    GIVEN: Running order and EAItemSwap message (swap ITEM 1 and ITEM 2)
    EXPECT: Running order with positions of ITEM 1 and 2 swapped in STORY 1
    """
    ro = RunningOrder.from_file(ROCREATE)
    ea = EAItemSwap.from_file(ROELEMENTACTIONSWAPITEM)
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

def test_element_action_move_story_init():
    "Test we can create an EAStoryMove object from a roElementAction file"
    ea = EAStoryMove.from_file(ROELEMENTACTIONMOVESTORY)
    assert repr(ea) == '<EAStoryMove 1011>'
    assert ea.ro_id == 'RO ID'

def test_element_action_move_story():
    """
    GIVEN: Running order and EAStoryMove message (move STORY 3 to top)
    EXPECT: Running order with STORY 3 at top, above STORY 1
    """
    ro = RunningOrder.from_file(ROCREATE)
    ea = EAStoryMove.from_file(ROELEMENTACTIONMOVESTORY)
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

def test_element_action_move_item_init():
    "Test we can create an EAItemMove object from a roElementAction file"
    ea = EAItemMove.from_file(ROELEMENTACTIONMOVEITEM)
    assert repr(ea) == '<EAItemMove 1012>'
    assert ea.ro_id == 'RO ID'

def test_element_action_move_item():
    """
    GIVEN: Running order and EAItemMove message (move ITEM 3 to top)
    EXPECT: Running order with ITEM 3 at top of STORY 1
    """
    ro = RunningOrder.from_file(ROCREATE)
    ea = EAItemMove.from_file(ROELEMENTACTIONMOVEITEM)
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

def test_metadata_replace_init():
    "Test we can create a MetaDataReplace object from a roMetaDataReplace file"
    mdr = MetaDataReplace.from_file(ROMETADATAREPLACE)
    assert repr(mdr) == '<MetaDataReplace 1013>'
    assert mdr.ro_id == 'RO ID'

def test_metadata_replace():
    """
    GIVEN: Running order and MetadataReplace message (with updated roSlug field)
    EXPECT: Running order with roSlug field: RO SLUG NEW
    """
    ro = RunningOrder.from_file(ROCREATE)
    mdr = MetaDataReplace.from_file(ROMETADATAREPLACE)
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    ro_id = d['mos']['roCreate']['roID']
    assert ro_id == "RO ID"
    ro_id = d['mos']['roCreate']['roSlug']
    assert ro_id == "RO SLUG"

    ro += mdr
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    ro_id = d['mos']['roCreate']['roID']
    assert ro_id == "RO ID"
    ro_id = d['mos']['roCreate']['roSlug']
    assert ro_id == "RO SLUG NEW"
    assert ro.base_tag.tag == 'roCreate'
    assert mdr.base_tag.tag == 'roMetadataReplace'

def test_story_append_init():
    "Test we can create a StoryAppend object from a StoryAppend file"
    sa = StoryAppend.from_file(ROAPPENDSTORY)
    assert repr(sa) == '<StoryAppend 1014>'
    assert sa.ro_id == 'RO ID'

def test_story_append_item():
    """
    GIVEN: Running order and storyAppend message (add STORYNEW1 and STORYNEW2)
    EXPECT: Running order with STORYNEW1 and STORYNEW2 added to the end
    """
    ro = RunningOrder.from_file(ROCREATE)
    sa = StoryAppend.from_file(ROAPPENDSTORY)
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 3

    ro += sa
    d = ro.dict
    assert len(d['mos']['roCreate']['story']) == 5
    assert d['mos']['roCreate']['story'][3]['storyID'] == 'STORYNEW1'
    assert d['mos']['roCreate']['story'][4]['storyID'] == 'STORYNEW2'
    assert ro.base_tag.tag == 'roCreate'
    assert sa.base_tag.tag == 'roStoryAppend'

def test_story_delete_init():
    "Test we can create a StoryDelete object from a StoryDelete file"
    sd = StoryDelete.from_file(RODELSTORY)
    assert repr(sd) == '<StoryDelete 1015>'
    assert sd.ro_id == 'RO ID'

def test_story_delete():
    """
    GIVEN: Running order and storyDelete message (delete STORY1 and STORY2)
    EXPECT: Running order with just STORY3 in
    """
    ro = RunningOrder.from_file(ROCREATE)
    sd = StoryDelete.from_file(RODELSTORY)
    d = ro.dict
    assert isinstance(d['mos']['roCreate']['story'], list)
    assert len(d['mos']['roCreate']['story']) == 3

    ro += sd
    d = ro.dict
    assert isinstance(d['mos']['roCreate']['story'], dict)
    assert d['mos']['roCreate']['story']['storyID'] == 'STORY3'
    assert ro.base_tag.tag == 'roCreate'
    assert sd.base_tag.tag == 'roStoryDelete'

def test_story_insert_init():
    "Test we can create a StoryInsert object from a StoryInsert file"
    si = StoryInsert.from_file(ROINSERTSTORY)
    assert repr(si) == '<StoryInsert 1016>'
    assert si.ro_id == 'RO ID'

def test_story_insert():
    """
    GIVEN: Running order and storyDelete message (delete STORY1 and STORY2)
    EXPECT: Running order with just STORY3 in
    """
    ro = RunningOrder.from_file(ROCREATE)
    si = StoryInsert.from_file(ROINSERTSTORY)
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

def test_story_move_init():
    "Test we can create a StoryMove object from a StoryMove file"
    sm = StoryMove.from_file(ROMOVESTORY)
    assert repr(sm) == '<StoryMove 1017>'
    assert sm.ro_id == 'RO ID'

def test_story_move():
    """
    GIVEN: Running order and storyDelete message (delete STORY1 and STORY2)
    EXPECT: Running order with just STORY3 in
    """
    ro = RunningOrder.from_file(ROCREATE)
    sm = StoryMove.from_file(ROMOVESTORY)
    d = ro.dict
    assert d['mos']['roCreate']['story'][0]['storyID'] == 'STORY1'
    assert d['mos']['roCreate']['story'][2]['storyID'] == 'STORY3'

    ro += sm
    d = ro.dict
    assert d['mos']['roCreate']['story'][0]['storyID'] == 'STORY3'
    assert d['mos']['roCreate']['story'][1]['storyID'] == 'STORY1'
    assert ro.base_tag.tag == 'roCreate'
    assert sm.base_tag.tag == 'roStoryMove'

def test_story_replace_init():
    "Test we can create a StoryReplace object from a StoryReplace file"
    sr = StoryReplace.from_file(ROREPSTORY)
    assert repr(sr) == '<StoryReplace 1018>'
    assert sr.ro_id == 'RO ID'

def test_story_replace():
    """
    GIVEN: Running order and roStoryReplace message (STORY 1 for STORY ONE)
    EXPECT: Running order with STORY ONE and no STORY 1
    """
    ro = RunningOrder.from_file(ROCREATE)
    sr = StoryReplace.from_file(ROREPSTORY)
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

def test_item_delete_init():
    "Test we can create a ItemDelete object from a roItemDelete file"
    id = ItemDelete.from_file(RODELITEM)
    assert repr(id) == '<ItemDelete 1019>'
    assert id.ro_id == 'RO ID'

def test_item_delete():
    """
    GIVEN: Running order and roItemDelete message (STORY 1 for STORY ONE)
    EXPECT: Running order with STORY ONE and no STORY 1
    """
    ro = RunningOrder.from_file(ROCREATE)
    id = ItemDelete.from_file(RODELITEM)
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3

    ro += id
    d = ro.dict
    assert isinstance(d['mos']['roCreate']['story'][0]['item'], dict)
    assert d['mos']['roCreate']['story'][0]['item']['itemID'] == 'ITEM3'
    assert ro.base_tag.tag == 'roCreate'
    assert id.base_tag.tag == 'roItemDelete'

def test_item_insert_init():
    "Test we can create a ItemInsert object from a roItemInsert file"
    ii = ItemInsert.from_file(ROINSERTITEM)
    assert repr(ii) == '<ItemInsert 1020>'
    assert ii.ro_id == 'RO ID'

def test_item_insert():
    """
    GIVEN: Running order and roItemInsert message (ITEMNEW1 and ITEMNEW2)
    EXPECT: Running order with ITEMNEW1 and ITEMNEW2 above ITEM2
    """
    ro = RunningOrder.from_file(ROCREATE)
    ii = ItemInsert.from_file(ROINSERTITEM)
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

def test_item_move_multiple_init():
    "Test we can create a ItemMoveMultiple object from a roItemMoveMultiple file"
    imm = ItemMoveMultiple.from_file(ROMOVEMULTIPLEITEM)
    assert repr(imm) == '<ItemMoveMultiple 1021>'
    assert imm.ro_id == 'RO ID'

def test_item_move_multiple():
    """
    GIVEN: Running order and roItemMoveMultiple message (ITEM2, ITEM3 above ITEM1 in STORY1)
    EXPECT: Running order with STORY1 items in order (ITEM2, ITEM3, ITEM1)
    """
    ro = RunningOrder.from_file(ROCREATE)
    imm = ItemMoveMultiple.from_file(ROMOVEMULTIPLEITEM)
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

def test_item_replace_init():
    "Test we can create a ItemReplace object from a roItemReplace file"
    ir = ItemReplace.from_file(ROREPITEM)
    assert repr(ir) == '<ItemReplace 1022>'
    assert ir.ro_id == 'RO ID'

def test_item_replace():
    """
    GIVEN: Running order and roItemReplace message (add NEW to ITEM21 slug)
    EXPECT: Running order with STORY2 ITEM21 slug as 'NEW ITEM 21'
    """
    ro = RunningOrder.from_file(ROCREATE)
    ir = ItemReplace.from_file(ROREPITEM)
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][1]['item']) == 3
    assert d['mos']['roCreate']['story'][1]['item'][0]['itemSlug'] == 'ITEM 21'

    ro += ir
    d = ro.dict
    assert len(d['mos']['roCreate']['story'][1]['item']) == 3
    assert d['mos']['roCreate']['story'][1]['item'][0]['itemSlug'] == 'NEW ITEM 21'
    assert ro.base_tag.tag == 'roCreate'
    assert ir.base_tag.tag == 'roItemReplace'

def test_ro_replace_init():
    "Test we can create a roReplace object from a roReplace file"
    rr = RunningOrderReplace.from_file(ROREPLACE)
    assert repr(rr) == '<RunningOrderReplace 1023>'
    assert rr.ro_id == 'RO ID'

def test_ro_replace():
    """
    GIVEN: Running order and roReplace message (replace roID's contents)
    EXPECT: Running order with roSlug 'RO SLUG NEW'
    """
    ro = RunningOrder.from_file(ROCREATE)
    ror = RunningOrderReplace.from_file(ROREPLACE)
    d = ro.dict
    assert d['mos']['roCreate']['roSlug'] == 'RO SLUG'

    ro += ror
    d = ro.dict
    assert d['mos']['roCreate']['roSlug'] == 'RO SLUG NEW'
    assert ro.base_tag.tag == 'roCreate'
    assert ror.base_tag.tag == 'roReplace'

def test_running_order_end_init():
    "Test we can create a RunningOrderEnd object from a roDelete file"
    rd = RunningOrderEnd.from_file(RODELETE)
    assert repr(rd) == '<RunningOrderEnd 9999>'
    assert rd.ro_id == 'RO ID'

def test_running_order_end():
    """
    GIVEN: Running order and RunningOrderEnd message
    EXPECT: Running order with roDelete tag
    """
    ro = RunningOrder.from_file(ROCREATE)
    rd = RunningOrderEnd.from_file(RODELETE)
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

def test_merge_after_delete():
    """
    GIVEN: A completed RunningOrder and a StorySend
    EXPECT: The RunningOrder should refuse the merge
    """
    ro = RunningOrder.from_file(ROCREATE)
    rd = RunningOrderEnd.from_file(RODELETE)
    ss = StorySend.from_file(ROSTORYSEND1)
    ro += rd
    with pytest.raises(MosClosedMergeError):
        ro += ss

def test_sort_two():
    """
    GIVEN: Two MOS objects
    EXPECT: The MOS objects sorted by their MOS ID
    """
    ro = RunningOrder.from_file(ROCREATE)
    rd = RunningOrderEnd.from_file(RODELETE)
    assert sorted([ro, rd]) == [ro, rd]
    assert sorted([rd, ro]) == [ro, rd]

def test_sort_all():
    """
    GIVEN: A list of MOS objects
    EXPECT: The MOS objects sorted by their MOS ID
    """
    ro = RunningOrder.from_file(ROCREATE)
    ss1 = StorySend.from_file(ROSTORYSEND1)
    ss2 = StorySend.from_file(ROSTORYSEND2)
    ea1 = EAStoryReplace.from_file(ROELEMENTACTIONREPSTORY)
    ea2 = EAItemReplace.from_file(ROELEMENTACTIONREPITEM)
    ea3 = EAStoryDelete.from_file(ROELEMENTACTIONDELSTORY)
    ea4 = EAItemDelete.from_file(ROELEMENTACTIONDELITEM)
    ea5 = EAStoryInsert.from_file(ROELEMENTACTIONINSERTSTORY)
    ea6 = EAItemInsert.from_file(ROELEMENTACTIONINSERTITEM)
    ea7 = EAStorySwap.from_file(ROELEMENTACTIONSWAPSTORY)
    ea8 = EAItemSwap.from_file(ROELEMENTACTIONSWAPITEM)
    ea9 = EAStoryMove.from_file(ROELEMENTACTIONMOVESTORY)
    ea10 = EAItemMove.from_file(ROELEMENTACTIONMOVEITEM)
    mdr = MetaDataReplace.from_file(ROMETADATAREPLACE)
    rd = RunningOrderEnd.from_file(RODELETE)

    all_objs_rand = [ss1, ea1, ea4, mdr, ss2, ea9, ea8, ea2, rd, ea7, ea5, ro, ea3, ea6, ea10]
    all_objs_in_order = [ro, ss1, ss2, ea1, ea2, ea3, ea4, ea5, ea6, ea7, ea8, ea9, ea10, mdr, rd]

    assert sorted(all_objs_rand) == all_objs_in_order

def test_merge_failure():
    """
    GIVEN: A RunningOrder and an invalid StorySend
    EXPECT: The RunningOrder should fail to merge
    """
    ro = RunningOrder.from_file(ROCREATE)
    ss3 = StorySend.from_file(ROSTORYSEND3)
    with warnings.catch_warnings(record=True) as w:
        ro += ss3
    assert len(w) == 1
    assert w[0].category == StoryNotFoundWarning
