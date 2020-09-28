import pytest

from mosromgr.mostypes import *
from mosromgr.exc import *
from const import *


def test_running_order_init():
    "Test we can create a RunningOrder object from a roCreate file"
    ro = RunningOrder(ROCREATE)
    assert repr(ro) == '<RunningOrder 1000>'

def test_running_order_init_str():
    "Test we can create a RunningOrder object from a string representation of a roCreate file"
    with open(ROCREATE) as f:
        rocreate_str = f.read()
    ro = RunningOrder(mos_file_contents=rocreate_str)
    assert repr(ro) == '<RunningOrder 1000>'

def test_story_send_init():
    "Test we can create a StorySend object from a roStorySend file"
    ss = StorySend(ROSTORYSEND1)
    assert repr(ss) == '<StorySend 1001>'

def test_story_send():
    """
    GIVEN: Running order and StorySend message (Add contents to STORY 1)
    EXPECT: Running order with storyBody present in STORY 1
    """
    ro = RunningOrder(ROCREATE)
    ss1 = StorySend(ROSTORYSEND1)
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 3
    ro += ss1
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 3
    body1 = d['mos']['roCreate']['story'][0]['p']
    assert body1 == '(BONG+PRES)'

def test_running_order_ro_id():
    "Test we can retrieve the RO ID of a MOS message"
    ro = RunningOrder(ROCREATE)
    assert ro.ro_id == 'RO ID'
    ss = StorySend(ROSTORYSEND1)
    assert ss.ro_id == 'RO ID'

def test_running_order_notes():
    "Test we can retrieve the 'best bits' from a roCreate"
    ro = RunningOrder(ROCREATE)
    assert ro.notes == []

    ro = RunningOrder(ROCREATE3)
    assert ro.notes == [
        {'item_id': 'ITEM1', 'story_slug': 'STORY 1', 'text': 'BB1'},
        {'item_id': 'ITEM21', 'story_slug': 'STORY 2', 'text': 'BB2'},
    ]

def test_element_action_replace_story_init():
    "Test we can create an EAReplaceStory object from a roElementAction file"
    ea = EAReplaceStory(ROELEMENTACTIONREPSTORY)
    assert repr(ea) == '<EAReplaceStory 1003>'

def test_element_action_replace_story():
    """
    GIVEN: Running order and EAReplaceStory message (STORY 1 for STORY ONE)
    EXPECT: Running order with STORY ONE and no STORY 1
    """
    ro = RunningOrder(ROCREATE)
    ea = EAReplaceStory(ROELEMENTACTIONREPSTORY)
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug == 'STORY 1'
    item_slug = d['mos']['roCreate']['story'][0]['item'][0]['itemSlug']
    assert item_slug == 'ITEM 1'

    ro += ea
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug == 'STORY ONE'
    item_slug = d['mos']['roCreate']['story'][0]['item']['itemSlug']
    assert item_slug == 'ITEM ONE'

def test_element_action_replace_item_init():
    "Test we can create an EAReplaceItem object from a roElementAction file"
    ea = EAReplaceItem(ROELEMENTACTIONREPITEM)
    assert repr(ea) == '<EAReplaceItem 1004>'

def test_element_action_replace_item():
    """
    GIVEN: Running order and EAReplaceItem message (ITEM 21 for NEW ITEM 21)
    EXPECT: Running order with NEW ITEM 21 in STORY 2
    """
    ro = RunningOrder(ROCREATE)
    ea = EAReplaceItem(ROELEMENTACTIONREPITEM)
    ro += ea
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug = d['mos']['roCreate']['story'][1]['storySlug']
    assert story_slug == 'STORY 2'
    item_slug = d['mos']['roCreate']['story'][1]['item'][0]['itemSlug']
    assert item_slug == 'NEW ITEM 21'

def test_element_action_delete_story_init():
    "Test we can create an EADeleteStory object from a roElementAction file"
    ea = EADeleteStory(ROELEMENTACTIONDELSTORY)
    assert repr(ea) == '<EADeleteStory 1005>'

def test_element_action_delete_story():
    """
    GIVEN: Running order and EADeleteStory message (delete STORY 1)
    EXPECT: Running order with no STORY 1
    """
    ro = RunningOrder(ROCREATE)
    ea = EADeleteStory(ROELEMENTACTIONDELSTORY)
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug1 = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug1 == 'STORY 1'
    story_slug2 = d['mos']['roCreate']['story'][1]['storySlug']
    assert story_slug2 == 'STORY 2'

    ro += ea
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 2
    story_slug = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug == 'STORY 2'

def test_element_action_delete_item_init():
    "Test we can create an EADeleteItem object from a roElementAction file"
    ea = EADeleteItem(ROELEMENTACTIONDELITEM)
    assert repr(ea) == '<EADeleteItem 1006>'

def test_element_action_delete_item():
    """
    GIVEN: Running order and EADeleteItem message (delete ITEM 1 in STORY 1)
    EXPECT: Running order with no ITEM 1 in STORY 1
    """
    ro = RunningOrder(ROCREATE)
    ea = EADeleteItem(ROELEMENTACTIONDELITEM)
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3

    ro += ea
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story'][0]['item']) == 2
    item_slug_1 = d['mos']['roCreate']['story'][0]['item'][0]['itemSlug']
    assert item_slug_1 == "ITEM 2"
    item_slug_2 = d['mos']['roCreate']['story'][0]['item'][1]['itemSlug']
    assert item_slug_2 == "ITEM 3"

def test_element_action_insert_story_init():
    "Test we can create an EAInsertStory object from a roElementAction file"
    ea = EAInsertStory(ROELEMENTACTIONINSERTSTORY)
    assert repr(ea) == '<EAInsertStory 1007>'

def test_element_action_insert_story():
    """
    GIVEN: Running order and EAInsertStory message (insert STORY NEW)
    EXPECT: Running order with STORY NEW between STORY 1 and 2
    """
    ro = RunningOrder(ROCREATE)
    ea = EAInsertStory(ROELEMENTACTIONINSERTSTORY)
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug1 = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug1 == 'STORY 1'
    story_slug2 = d['mos']['roCreate']['story'][1]['storySlug']
    assert story_slug2 == 'STORY 2'

    ro += ea
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 4
    story_slug1 = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug1 == 'STORY 1'
    story_slug_new = d['mos']['roCreate']['story'][1]['storySlug']
    assert story_slug_new == 'STORY NEW'
    story_slug2 = d['mos']['roCreate']['story'][2]['storySlug']
    assert story_slug2 == 'STORY 2'

def test_element_action_insert_item_init():
    "Test we can create an EAInsertItem object from a roElementAction file"
    ea = EAInsertItem(ROELEMENTACTIONINSERTITEM)
    assert repr(ea) == '<EAInsertItem 1008>'

def test_element_action_insert_item():
    """
    GIVEN: Running order and EAInsertItem message (insert ITEM NEW in STORY 1)
    EXPECT: Running order with ITEM NEW between ITEM 1 and 2 in STORY 1
    """
    ro = RunningOrder(ROCREATE)
    ea = EAInsertItem(ROELEMENTACTIONINSERTITEM)
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    item_slug1 = d['mos']['roCreate']['story'][0]['item'][0]['itemSlug']
    assert item_slug1 == 'ITEM 1'
    item_slug2 = d['mos']['roCreate']['story'][0]['item'][1]['itemSlug']
    assert item_slug2 == 'ITEM 2'

    ro += ea
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story'][0]['item']) == 4
    item_slug1 = d['mos']['roCreate']['story'][0]['item'][0]['itemSlug']
    assert item_slug1 == 'ITEM 1'
    item_slug_new = d['mos']['roCreate']['story'][0]['item'][1]['itemSlug']
    assert item_slug_new == 'ITEM NEW'
    item_slug2 = d['mos']['roCreate']['story'][0]['item'][2]['itemSlug']
    assert item_slug2 == 'ITEM 2'

def test_element_action_swap_story_init():
    "Test we can create an EASwapStory object from a roElementAction file"
    ea = EASwapStory(ROELEMENTACTIONSWAPSTORY)
    assert repr(ea) == '<EASwapStory 1009>'

def test_element_action_swap_story():
    """
    GIVEN: Running order and EASwapStory message (swap STORY 1 STORY 2)
    EXPECT: Running order with positions of STORY 1 and 2 swapped
    """
    ro = RunningOrder(ROCREATE)
    ea = EASwapStory(ROELEMENTACTIONSWAPSTORY)
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    story_slug1 = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug1 == 'STORY 1'
    story_slug2 = d['mos']['roCreate']['story'][1]['storySlug']
    assert story_slug2 == 'STORY 2'

    ro += ea
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    story_slug1 = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug1 == 'STORY 2'
    story_slug2 = d['mos']['roCreate']['story'][1]['storySlug']
    assert story_slug2 == 'STORY 1'

def test_element_action_swap_item_init():
    "Test we can create an EASwapItem object from a roElementAction file"
    ea = EASwapItem(ROELEMENTACTIONSWAPITEM)
    assert repr(ea) == '<EASwapItem 1010>'

def test_element_action_swap_item():
    """
    GIVEN: Running order and EASwapItem message (swap ITEM 1 and ITEM 2)
    EXPECT: Running order with positions of ITEM 1 and 2 swapped in STORY 1
    """
    ro = RunningOrder(ROCREATE)
    ea = EASwapItem(ROELEMENTACTIONSWAPITEM)
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    item_slug1 = d['mos']['roCreate']['story'][0]['item'][0]['itemSlug']
    assert item_slug1 == 'ITEM 1'
    item_slug2 = d['mos']['roCreate']['story'][0]['item'][1]['itemSlug']
    assert item_slug2 == 'ITEM 2'

    ro += ea
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    item_slug1 = d['mos']['roCreate']['story'][0]['item'][0]['itemSlug']
    assert item_slug1 == 'ITEM 2'
    item_slug2 = d['mos']['roCreate']['story'][0]['item'][1]['itemSlug']
    assert item_slug2 == 'ITEM 1'

def test_element_action_move_story_init():
    "Test we can create an EAMoveStory object from a roElementAction file"
    ea = EAMoveStory(ROELEMENTACTIONMOVESTORY)
    assert repr(ea) == '<EAMoveStory 1011>'

def test_element_action_move_story():
    """
    GIVEN: Running order and EAMoveStory message (move STORY 3 to top)
    EXPECT: Running order with STORY 3 at top, above STORY 1
    """
    ro = RunningOrder(ROCREATE)
    ea = EAMoveStory(ROELEMENTACTIONMOVESTORY)
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug1 = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug1 == 'STORY 1'
    story_slug2 = d['mos']['roCreate']['story'][1]['storySlug']
    assert story_slug2 == 'STORY 2'
    story_slug3 = d['mos']['roCreate']['story'][2]['storySlug']
    assert story_slug3 == 'STORY 3'

    ro += ea
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug1 = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug1 == 'STORY 3'
    story_slug2 = d['mos']['roCreate']['story'][1]['storySlug']
    assert story_slug2 == 'STORY 1'
    story_slug3 = d['mos']['roCreate']['story'][2]['storySlug']
    assert story_slug3 == 'STORY 2'

def test_element_action_move_item_init():
    "Test we can create an EAMoveItem object from a roElementAction file"
    ea = EAMoveItem(ROELEMENTACTIONMOVEITEM)
    assert repr(ea) == '<EAMoveItem 1012>'

def test_element_action_move_item():
    """
    GIVEN: Running order and EAMoveItem message (move ITEM 3 to top)
    EXPECT: Running order with ITEM 3 at top of STORY 1
    """
    ro = RunningOrder(ROCREATE)
    ea = EAMoveItem(ROELEMENTACTIONMOVEITEM)
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    story_slug1 = d['mos']['roCreate']['story'][0]['item'][0]['itemSlug']
    assert story_slug1 == 'ITEM 1'
    story_slug2 = d['mos']['roCreate']['story'][0]['item'][1]['itemSlug']
    assert story_slug2 == 'ITEM 2'
    story_slug3 = d['mos']['roCreate']['story'][0]['item'][2]['itemSlug']
    assert story_slug3 == 'ITEM 3'

    ro += ea
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug1 = d['mos']['roCreate']['story'][0]['item'][0]['itemSlug']
    assert story_slug1 == 'ITEM 3'
    story_slug2 = d['mos']['roCreate']['story'][0]['item'][1]['itemSlug']
    assert story_slug2 == 'ITEM 1'
    story_slug3 = d['mos']['roCreate']['story'][0]['item'][2]['itemSlug']
    assert story_slug3 == 'ITEM 2'

def test_metadata_replace_init():
    "Test we can create a MetaDataReplace object from a roMetaDataReplace file"
    ea = MetaDataReplace(ROMETADATAREPLACE)
    assert repr(ea) == '<MetaDataReplace 1013>'

def test_metadata_replace():
    """
    GIVEN: Running order and MetadataReplace message (with updated roSlug field)
    EXPECT: Running order with roSlug field: RO SLUG NEW
    """
    ro = RunningOrder(ROCREATE)
    mdr = MetaDataReplace(ROMETADATAREPLACE)
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    ro_id = d['mos']['roCreate']['roID']
    assert ro_id == "RO ID"
    ro_id = d['mos']['roCreate']['roSlug']
    assert ro_id == "RO SLUG"

    ro += mdr
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    ro_id = d['mos']['roCreate']['roID']
    assert ro_id == "RO ID"
    ro_id = d['mos']['roCreate']['roSlug']
    assert ro_id == "RO SLUG NEW"


def test_story_append_init():
    "Test we can create a StoryAppend object from a StoryAppend file"
    sa = StoryAppend(ROAPPENDSTORY)
    assert repr(sa) == '<StoryAppend 1014>'


def test_story_append_item():
    """
    GIVEN: Running order and storyAppend message (add STORYNEW1 and STORYNEW2)
    EXPECT: Running order with STORYNEW1 and STORYNEW2 added to the end
    """
    ro = RunningOrder(ROCREATE)
    sa = StoryAppend(ROAPPENDSTORY)
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 3

    ro += sa

    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 5
    assert d['mos']['roCreate']['story'][3]['storyID'] == 'STORYNEW1'
    assert d['mos']['roCreate']['story'][4]['storyID'] == 'STORYNEW2'

def test_story_delete_init():
    "Test we can create a StoryDelete object from a StoryDelete file"
    sd = StoryDelete(RODELSTORY)
    assert repr(sd) == '<StoryDelete 1015>'


def test_story_delete():
    """
    GIVEN: Running order and storyDelete message (delete STORY1 and STORY2)
    EXPECT: Running order with just STORY3 in
    """
    ro = RunningOrder(ROCREATE)
    sd = StoryDelete(RODELSTORY)
    d = ro.to_dict()
    assert isinstance(d['mos']['roCreate']['story'], list)
    assert len(d['mos']['roCreate']['story']) == 3

    ro += sd
    d = ro.to_dict()
    assert isinstance(d['mos']['roCreate']['story'], dict)
    assert d['mos']['roCreate']['story']['storyID'] == 'STORY3'


def test_story_insert_init():
    "Test we can create a StoryInsert object from a StoryInsert file"
    si = StoryInsert(ROINSERTSTORY)
    assert repr(si) == '<StoryInsert 1016>'


def test_story_insert():
    """
    GIVEN: Running order and storyDelete message (delete STORY1 and STORY2)
    EXPECT: Running order with just STORY3 in
    """
    ro = RunningOrder(ROCREATE)
    si = StoryInsert(ROINSERTSTORY)
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 3

    ro += si
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 5
    assert d['mos']['roCreate']['story'][0]['storyID'] == 'STORY1'
    assert d['mos']['roCreate']['story'][1]['storyID'] == 'STORYNEW1'
    assert d['mos']['roCreate']['story'][2]['storyID'] == 'STORYNEW2'
    assert d['mos']['roCreate']['story'][3]['storyID'] == 'STORY2'
    assert d['mos']['roCreate']['story'][4]['storyID'] == 'STORY3'


def test_story_move_init():
    "Test we can create a StoryMove object from a StoryMove file"
    sm = StoryMove(ROMOVESTORY)
    assert repr(sm) == '<StoryMove 1017>'


def test_story_move():
    """
    GIVEN: Running order and storyDelete message (delete STORY1 and STORY2)
    EXPECT: Running order with just STORY3 in
    """
    ro = RunningOrder(ROCREATE)
    sm = StoryMove(ROMOVESTORY)
    d = ro.to_dict()
    assert d['mos']['roCreate']['story'][0]['storyID'] == 'STORY1'
    assert d['mos']['roCreate']['story'][2]['storyID'] == 'STORY3'

    ro += sm
    d = ro.to_dict()
    assert d['mos']['roCreate']['story'][0]['storyID'] == 'STORY3'
    assert d['mos']['roCreate']['story'][1]['storyID'] == 'STORY1'


def test_story_replace_init():
    "Test we can create a StoryReplace object from a StoryReplace file"
    sr = StoryReplace(ROREPSTORY)
    assert repr(sr) == '<StoryReplace 1018>'


def test_story_replace():
    """
    GIVEN: Running order and roStoryReplace message (STORY 1 for STORY ONE)
    EXPECT: Running order with STORY ONE and no STORY 1
    """
    ro = RunningOrder(ROCREATE)
    sr = StoryReplace(ROREPSTORY)
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug == 'STORY 1'
    item_slug = d['mos']['roCreate']['story'][0]['item'][0]['itemSlug']
    assert item_slug == 'ITEM 1'

    ro += sr
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story']) == 3
    story_slug = d['mos']['roCreate']['story'][0]['storySlug']
    assert story_slug == 'STORY ONE'
    item_slug = d['mos']['roCreate']['story'][0]['item']['itemSlug']
    assert item_slug == 'ITEM ONE'


def test_item_delete_init():
    "Test we can create a ItemDelete object from a roItemDelete file"
    id = ItemDelete(RODELITEM)
    assert repr(id) == '<ItemDelete 1019>'


def test_item_delete():
    """
    GIVEN: Running order and roItemDelete message (STORY 1 for STORY ONE)
    EXPECT: Running order with STORY ONE and no STORY 1
    """
    ro = RunningOrder(ROCREATE)
    id = ItemDelete(RODELITEM)
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3

    ro += id
    d = ro.to_dict()
    assert isinstance(d['mos']['roCreate']['story'][0]['item'], dict)
    assert d['mos']['roCreate']['story'][0]['item']['itemID'] == 'ITEM3'

def test_item_insert_init():
    "Test we can create a ItemInsert object from a roItemInsert file"
    ii = ItemInsert(ROINSERTITEM)
    assert repr(ii) == '<ItemInsert 1020>'

def test_item_insert():
    """
    GIVEN: Running order and roItemInsert message (ITEMNEW1 and ITEMNEW2)
    EXPECT: Running order with ITEMNEW1 and ITEMNEW2 above ITEM2
    """
    ro = RunningOrder(ROCREATE)
    ii = ItemInsert(ROINSERTITEM)
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3

    ro += ii
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story'][0]['item']) == 5
    item_id1 = d['mos']['roCreate']['story'][0]['item'][1]['itemID']
    assert item_id1 == 'ITEMNEW1'
    item_id2 = d['mos']['roCreate']['story'][0]['item'][2]['itemID']
    assert item_id2 == 'ITEMNEW2'


def test_item_move_multiple_init():
    "Test we can create a ItemMoveMultiple object from a roItemMoveMultiple file"
    imm = ItemMoveMultiple(ROMOVEMULTIPLEITEM)
    assert repr(imm) == '<ItemMoveMultiple 1021>'

def test_item_move_multiple():
    """
    GIVEN: Running order and roItemMoveMultiple message (ITEM2, ITEM3 above ITEM1 in STORY1)
    EXPECT: Running order with STORY1 items in order (ITEM2, ITEM3, ITEM1)
    """
    ro = RunningOrder(ROCREATE)
    imm = ItemMoveMultiple(ROMOVEMULTIPLEITEM)
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    assert d['mos']['roCreate']['story'][0]['item'][0]['itemID'] == 'ITEM1'
    assert d['mos']['roCreate']['story'][0]['item'][1]['itemID'] == 'ITEM2'
    assert d['mos']['roCreate']['story'][0]['item'][2]['itemID'] == 'ITEM3'

    ro += imm
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story'][0]['item']) == 3
    assert d['mos']['roCreate']['story'][0]['item'][0]['itemID'] == 'ITEM2'
    assert d['mos']['roCreate']['story'][0]['item'][1]['itemID'] == 'ITEM3'
    assert d['mos']['roCreate']['story'][0]['item'][2]['itemID'] == 'ITEM1'

def test_item_replace_init():
    "Test we can create a ItemReplace object from a roItemReplace file"
    ir = ItemReplace(ROREPITEM)
    assert repr(ir) == '<ItemReplace 1022>'

def test_item_replace():
    """
    GIVEN: Running order and roItemReplace message (add NEW to ITEM21 slug)
    EXPECT: Running order with STORY2 ITEM21 slug as 'NEW ITEM 21'
    """
    ro = RunningOrder(ROCREATE)
    ir = ItemReplace(ROREPITEM)
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story'][1]['item']) == 3
    assert d['mos']['roCreate']['story'][1]['item'][0]['itemSlug'] == 'ITEM 21'


    ro += ir
    d = ro.to_dict()
    assert len(d['mos']['roCreate']['story'][1]['item']) == 3
    assert d['mos']['roCreate']['story'][1]['item'][0]['itemSlug'] == 'NEW ITEM 21'

def test_ro_replace_init():
    "Test we can create a roReplace object from a roReplace file"
    rr = RunningOrderReplace(ROREPLACE)
    assert repr(rr) == '<RunningOrderReplace 1023>'

def test_ro_replace():
    """
    GIVEN: Running order and roReplace message (replace roID's contents)
    EXPECT: Running order with roSLug 'RO SLUG NEW'
    """
    ro = RunningOrder(ROCREATE)
    rr = RunningOrderReplace(ROREPLACE)
    d = ro.to_dict()
    assert d['mos']['roCreate']['roSlug'] == 'RO SLUG'

    ro += rr
    d = ro.to_dict()
    assert d['mos']['roCreate']['roSlug'] == 'RO SLUG NEW'


def test_running_order_end_init():
    "Test we can create a RunningOrderEnd object from a roDelete file"
    rd = RunningOrderEnd(RODELETE)
    assert repr(rd) == '<RunningOrderEnd 9999>'

def test_running_order_end():
    """
    GIVEN: Running order and RunningOrderEnd message
    EXPECT: Running order with roDelete tag
    """
    ro = RunningOrder(ROCREATE)
    rd = RunningOrderEnd(RODELETE)
    d = ro.to_dict()
    ro_id = d['mos']['roCreate']['roID']
    assert ro_id == 'RO ID'
    assert 'mosromgrmeta' not in d['mos']

    ro += rd
    assert repr(ro) == '<RunningOrder 1000 ended>'
    d = ro.to_dict()
    assert 'mosromgrmeta' in d['mos']
    assert 'roDelete' in d['mos']['mosromgrmeta']
    assert d['mos']['roCreate']['roID'] == ro_id
    assert d['mos']['mosromgrmeta']['roDelete']['roID'] == ro_id

def test_merge_after_delete():
    """
    GIVEN: A completed RunningOrder and a StorySend
    EXPECT: The RunningOrder should refuse the merge
    """
    ro = RunningOrder(ROCREATE)
    rd = RunningOrderEnd(RODELETE)
    ss = StorySend(ROSTORYSEND1)
    ro += rd
    with pytest.raises(MosClosedMergeError):
        ro += ss

def test_sort_two():
    """
    GIVEN: Two MOS objects
    EXPECT: The MOS objects sorted by their MOS ID
    """
    ro = RunningOrder(ROCREATE)
    rd = RunningOrderEnd(RODELETE)
    assert sorted([ro, rd]) == [ro, rd]
    assert sorted([rd, ro]) == [ro, rd]

def test_sort_all():
    """
    GIVEN: A list of MOS objects
    EXPECT: The MOS objects sorted by their MOS ID
    """
    ro = RunningOrder(ROCREATE)
    ss1 = StorySend(ROSTORYSEND1)
    ss2 = StorySend(ROSTORYSEND2)
    ea1 = EAReplaceStory(ROELEMENTACTIONREPSTORY)
    ea2 = EAReplaceItem(ROELEMENTACTIONREPITEM)
    ea3 = EADeleteStory(ROELEMENTACTIONDELSTORY)
    ea4 = EADeleteItem(ROELEMENTACTIONDELITEM)
    ea5 = EAInsertStory(ROELEMENTACTIONINSERTSTORY)
    ea6 = EAInsertItem(ROELEMENTACTIONINSERTITEM)
    ea7 = EASwapStory(ROELEMENTACTIONSWAPSTORY)
    ea8 = EASwapItem(ROELEMENTACTIONSWAPITEM)
    ea9 = EAMoveStory(ROELEMENTACTIONMOVESTORY)
    ea10 = EAMoveItem(ROELEMENTACTIONMOVEITEM)
    mdr = MetaDataReplace(ROMETADATAREPLACE)
    rd = RunningOrderEnd(RODELETE)

    all_objs_rand = [ss1, ea1, ea4, mdr, ss2, ea9, ea8, ea2, rd, ea7, ea5, ro, ea3, ea6, ea10]
    all_objs_in_order = [ro, ss1, ss2, ea1, ea2, ea3, ea4, ea5, ea6, ea7, ea8, ea9, ea10, mdr, rd]

    assert sorted(all_objs_rand) == all_objs_in_order

def test_merge_failure():
    """
    GIVEN: A RunningOrder and an invalid StorySend
    EXPECT: The RunningOrder should fail to merge
    """
    ro = RunningOrder(ROCREATE)
    ss3 = StorySend(ROSTORYSEND3)
    with warnings.catch_warnings(record=True) as w:
        ro += ss3
    assert len(w) == 1
    assert w[0].category == StoryNotFoundWarning
