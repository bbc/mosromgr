from xml.etree.ElementTree import Element

from mosromgr.mostypes import *
from mosromgr.moselements import *
from const import *


def test_mos_element_init():
    "Test we can create a MosElement and access its repr"
    e = MosElement(xml=None)
    assert repr(e) == '<MosElement>'

def test_running_order():
    """
    Test we can access the elements of a RunningOrder object created from a
    roCreate file
    """
    ro = RunningOrder(ROCREATE)
    assert isinstance(ro.xml, Element)
    assert str(ro).startswith('<mos>')
    assert str(ro).endswith('</mos>')
    assert isinstance(ro.stories, list)
    assert len(ro.stories) == 3
    assert ro.duration == 31

    story1 = ro.stories[0]
    assert repr(story1) == '<Story STORY1>'
    assert isinstance(story1, Story)
    assert isinstance(story1.xml, Element)
    assert str(story1).startswith('<story>')
    assert str(story1).strip().endswith('</story>')
    assert story1.id == 'STORY1'
    assert story1.slug == 'STORY 1'
    assert story1.duration == 3

    assert isinstance(story1.items, list)
    assert len(story1.items) == 3
    item1 = story1.items[0]
    assert repr(item1) == '<Item ITEM1>'
    assert isinstance(item1, Item)
    assert isinstance(item1.xml, Element)
    assert item1.id == 'ITEM1'
    assert item1.slug == 'ITEM 1'
    assert item1.note is None

    item2 = story1.items[1]
    assert isinstance(item2, Item)
    assert isinstance(item2.xml, Element)
    assert item2.id == 'ITEM2'
    assert item2.slug == 'ITEM 2'
    assert item2.note is None

    story2 = ro.stories[1]
    assert story2.id == 'STORY2'
    assert story2.slug == 'STORY 2'
    assert story2.duration == 8

    assert isinstance(story2.items, list)
    assert len(story2.items) == 3
    item21 = story2.items[0]
    assert isinstance(item21, Item)
    assert isinstance(item21.xml, Element)
    assert item21.id == 'ITEM21'
    assert item21.slug == 'ITEM 21'

def test_running_order_with_note():
    """
    Test we can access the notes in a RunningOrder object created from a
    roCreate file
    """
    ro = RunningOrder(ROCREATE3)
    assert ro.stories[0].items[0].note == 'BB1'
    assert ro.stories[1].items[0].note == 'BB2'

def test_story_send():
    """
    Test we can access the elements of a StorySend object created from a
    roStorySend file
    """
    ss = StorySend(ROSTORYSEND1)
    assert isinstance(ss.xml, Element)
    assert isinstance(ss.story, Story)
    assert isinstance(ss.story.xml, Element)
    assert ss.story.id == 'STORY1'
    assert ss.story.slug == 'STORY 1'
    assert ss.story.duration == 30

    assert isinstance(ss.story.items, list)
    assert len(ss.story.items) == 1
    item1 = ss.story.items[0]
    assert isinstance(item1, Item)
    assert isinstance(item1.xml, Element)
    assert item1.id == 'ITEM1'
    assert item1.slug == 'ITEM 1'

def test_story_append():
    """
    Test we can access the elements of a StoryAppend object created from a
    roStoryAppend file
    """
    sa = StoryAppend(ROAPPENDSTORY)
    assert isinstance(sa.xml, Element)
    assert isinstance(sa.stories, list)
    assert len(sa.stories) == 2
    story1, story2 = sa.stories

    assert isinstance(story1, Story)
    assert isinstance(story1.xml, Element)
    assert story1.id == 'STORYNEW1'
    assert story1.slug == 'STORY NEW 1'
    assert story1.duration == 6
    assert isinstance(story1.items, list)
    assert len(story1.items) == 1
    item11 = story1.items[0]
    assert item11.id == 'ITEMNEW1'
    assert item11.slug == 'ITEM NEW 1'

    assert isinstance(story2, Story)
    assert isinstance(story2.xml, Element)
    assert story2.id == 'STORYNEW2'
    assert story2.slug == 'STORY NEW 2'
    assert story2.duration == 15
    assert isinstance(story2.items, list)
    assert len(story2.items) == 1
    item21 = story2.items[0]
    assert item21.id == 'ITEMNEW21'
    assert item21.slug == 'ITEM NEW 21'


def test_story_delete():
    """
    Test we can access the elements of a StoryDelete object created from a
    roStoryDelete file
    """
    sd = StoryDelete(RODELSTORY)
    assert isinstance(sd.xml, Element)
    assert isinstance(sd.stories, list)
    assert len(sd.stories) == 2
    story1, story2 = sd.stories

    assert isinstance(story1, Story)
    assert isinstance(story1.xml, Element)
    assert story1.id == 'STORY1'
    assert story1.slug is None
    assert story1.duration is None
    assert isinstance(story1.items, list)
    assert len(story1.items) == 0

    assert isinstance(story2, Story)
    assert isinstance(story2.xml, Element)
    assert story2.id == 'STORY2'
    assert story2.slug is None
    assert story2.duration is None
    assert isinstance(story2.items, list)
    assert len(story2.items) == 0

def test_story_insert():
    """
    Test we can access the elements of a StoryInsert object created from a
    roStoryInsert file
    """
    si = StoryInsert(ROINSERTSTORY)
    assert isinstance(si.xml, Element)
    assert isinstance(si.target_story, Story)
    assert si.target_story.id == 'STORY2'
    assert si.target_story.slug is None
    assert si.target_story.duration is None
    assert isinstance(si.source_stories, list)
    assert len(si.source_stories) == 2
    story1, story2 = si.source_stories

    assert isinstance(story1, Story)
    assert story1.id == 'STORYNEW1'
    assert story1.slug == 'STORY NEW 1'
    assert story1.duration == 6
    assert isinstance(story1.items, list)
    assert len(story1.items) == 1
    item1 = story1.items[0]
    assert item1.id == 'ITEMNEW1'
    assert item1.slug == 'ITEM NEW 1'

    assert isinstance(story2, Story)
    assert story2.id == 'STORYNEW2'
    assert story2.slug == 'STORY NEW 2'
    assert story2.duration == 15
    assert isinstance(story2.items, list)
    assert len(story2.items) == 1
    item2 = story2.items[0]
    assert item2.id == 'ITEMNEW21'
    assert item2.slug == 'ITEM NEW 21'

def test_story_move():
    """
    Test we can access the elements of a StoryMove object created from a
    roStoryMove file
    """
    sm = StoryMove(ROMOVESTORY)
    assert isinstance(sm.target_story, Story)
    assert sm.target_story.id == 'STORY1'
    assert isinstance(sm.target_story.xml, Element)
    assert sm.target_story.items is None

    assert isinstance(sm.source_story, Story)
    assert sm.source_story.id == 'STORY3'
    assert isinstance(sm.source_story.xml, Element)
    assert sm.target_story.items is None

def test_story_replace():
    """
    Test we can access the elements of a StoryReplace object created from a
    roStoryReplace file
    """
    sr = StoryReplace(ROREPSTORY)
    assert isinstance(sr.xml, Element)
    assert isinstance(sr.target_story, Story)
    assert isinstance(sr.target_story.xml, Element)
    assert sr.target_story.id == 'STORY1'
    assert sr.target_story.items is None

    assert isinstance(sr.source_story, Story)
    assert isinstance(sr.source_story.xml, Element)
    assert sr.source_story.id == 'STORY1'
    assert sr.source_story.slug == 'STORY ONE'
    assert isinstance(sr.source_story.items, list)
    assert len(sr.source_story.items) == 1
    item1 = sr.source_story.items[0]
    assert isinstance(item1, Item)
    assert item1.id == 'ITEM1'
    assert item1.slug == 'ITEM ONE'

def test_ro_replace():
    """
    Test we can access the elements of a RunningOrderReplace object created from
    a roReplace file
    """
    ror = RunningOrderReplace(ROREPLACE)
    assert isinstance(ror.xml, Element)
    assert isinstance(ror.stories, list)
    assert len(ror.stories) == 3
    assert ror.duration == 53

    story1 = ror.stories[0]
    assert isinstance(story1, Story)
    assert isinstance(story1.xml, Element)
    assert story1.id == 'STORY1'
    assert story1.slug == 'STORY 1'
    assert story1.duration == 30
    assert isinstance(story1.items, list)
    assert len(story1.items) == 3
    item1 = story1.items[0]
    assert isinstance(item1, Item)
    assert item1.id == 'ITEM1'
    assert item1.slug == 'ITEM 1'

    story2 = ror.stories[1]
    assert story2.id == 'STORY2'
    assert story2.slug == 'STORY 2'
    assert story2.duration == 20
    assert isinstance(story2.items, list)
    assert len(story2.items) == 3
    item21 = story2.items[0]
    assert isinstance(item21, Item)
    assert item21.id == 'ITEM21'
    assert item21.slug == 'ITEM 21'

def test_metadata_replace():
    """
    Test we can access the elements of a MetaDataReplace object created from a
    roMetadataReplace file
    """
    mdr = MetaDataReplace(ROMETADATAREPLACE)
    assert isinstance(mdr.xml, Element)
    assert mdr.ro_slug == 'RO SLUG NEW'

def test_item_insert():
    """
    Test we can access the elements of an ItemInsert object created from a
    roItemInsert file
    """
    ii = ItemInsert(ROINSERTITEM)
    assert isinstance(ii.xml, Element)
    assert isinstance(ii.target_story, Story)
    assert ii.target_story.id == 'STORY1'
    assert ii.target_story.slug is None
    assert ii.target_story.duration is None
    assert ii.target_story.items is None

    assert isinstance(ii.target_item, Item)
    assert ii.target_item.id == 'ITEM2'

    assert isinstance(ii.source_items, list)
    assert len(ii.source_items) == 2

    item1, item2 = ii.source_items
    assert item1.id == 'ITEMNEW1'
    assert item1.slug == 'ITEM NEW 1'
    assert item2.id == 'ITEMNEW2'
    assert item2.slug == 'ITEM NEW 2'

def test_item_delete():
    """
    Test we can access the elements of an ItemDelete object created from a
    roItemDelete file
    """
    id = ItemDelete(RODELITEM)
    assert isinstance(id.xml, Element)
    assert isinstance(id.target_story, Story)
    assert id.target_story.id == 'STORY1'
    assert id.target_story.slug is None
    assert id.target_story.duration is None
    assert id.target_story.items is None

    assert isinstance(id.target_items, set)
    assert len(id.target_items) == 2
    assert {item.id for item in id.target_items} == {'ITEM1', 'ITEM2'}

def test_item_move_multiple():
    """
    Test we can access the elements of an ItemMoveMultiple object created from a
    roItemMoveMultiple file
    """
    imm = ItemMoveMultiple(ROMOVEMULTIPLEITEM)
    assert isinstance(imm.xml, Element)
    assert isinstance(imm.target_story, Story)
    assert imm.target_story.id == 'STORY1'
    assert imm.target_story.slug is None
    assert imm.target_story.duration is None
    assert imm.target_story.items is None

    assert isinstance(imm.target_item, Item)
    assert imm.target_item.id == 'ITEM1'
    assert imm.target_item.slug is None

    assert isinstance(imm.source_items, list)
    assert len(imm.source_items) == 2
    item1, item2 = imm.source_items
    assert item1.id == 'ITEM2'
    assert item1.slug is None
    assert item2.id == 'ITEM3'
    assert item2.slug is None

def test_item_replace():
    """
    Test we can access the elements of an ItemReplace object created from a
    roItemReplace file
    """
    ir = ItemReplace(ROREPITEM)
    assert isinstance(ir.xml, Element)
    assert isinstance(ir.target_story, Story)
    assert ir.target_story.id == 'STORY2'
    assert ir.target_story.slug is None
    assert ir.target_story.duration is None
    assert ir.target_story.items is None

    assert isinstance(ir.target_item, Item)
    assert ir.target_item.id == 'ITEM21'
    assert ir.target_item.slug is None

    assert isinstance(ir.source_item, Item)
    assert ir.source_item.id == 'ITEM21'
    assert ir.source_item.slug == 'NEW ITEM 21'

def test_element_action_replace_story():
    """
    Test we can access the elements of an EAStoryReplace object created from a
    roElementAction file
    """
    ea = EAStoryReplace(ROELEMENTACTIONREPSTORY)
    assert isinstance(ea.xml, Element)

    assert isinstance(ea.target_story, Story)
    assert isinstance(ea.target_story.xml, Element)
    assert ea.target_story.id == 'STORY1'
    assert ea.target_story.slug is None
    assert ea.target_story.duration is None
    assert ea.target_story.items is None

    assert isinstance(ea.source_story, Story)
    assert isinstance(ea.source_story.xml, Element)
    assert ea.source_story.id == 'STORY1'
    assert ea.source_story.slug == 'STORY ONE'
    assert ea.source_story.duration == 30
    assert isinstance(ea.source_story.items, list)
    assert len(ea.source_story.items) == 1
    item = ea.source_story.items[0]
    assert item.id == 'ITEM1'
    assert item.slug == 'ITEM ONE'

def test_element_action_delete_story():
    """
    Test we can access the elements of an EAStoryDelete object created from a
    roElementAction file
    """
    ea = EAStoryDelete(ROELEMENTACTIONDELSTORY)
    assert isinstance(ea.xml, Element)
    assert isinstance(ea.story, Story)
    assert isinstance(ea.story.xml, Element)
    assert ea.story.id == 'STORY1'
    assert ea.story.slug is None
    assert ea.story.duration is None
    assert isinstance(ea.story.items, list)
    assert len(ea.story.items) == 0

def test_element_action_insert_story():
    """
    Test we can access the elements of an EAStoryInsert object created from a
    roElementAction file
    """
    ea = EAStoryInsert(ROELEMENTACTIONINSERTSTORY)
    assert isinstance(ea.xml, Element)

    assert isinstance(ea.target_story, Story)
    assert isinstance(ea.target_story.xml, Element)
    assert ea.target_story.id == 'STORY2'
    assert ea.target_story.slug is None
    assert ea.target_story.duration is None
    assert ea.target_story.items is None

    assert isinstance(ea.source_story, Story)
    assert isinstance(ea.source_story.xml, Element)
    assert ea.source_story.id == 'STORYNEW'
    assert ea.source_story.slug == 'STORY NEW'
    assert ea.source_story.duration is None
    assert isinstance(ea.source_story.items, list)
    assert len(ea.source_story.items) == 1
    item = ea.source_story.items[0]
    assert item.id == 'ITEMNEW'
    assert item.slug == 'ITEM NEW'

def test_element_action_swap_story():
    """
    Test we can access the elements of an EAStorySwap object created from a
    roElementAction file
    """
    ea = EAStorySwap(ROELEMENTACTIONSWAPSTORY)

    assert isinstance(ea.stories, set)
    assert {story.id for story in ea.stories} == {'STORY1', 'STORY2'}
    story1, story2 = ea.stories

    assert isinstance(story1, Story)
    assert isinstance(story1.xml, Element)
    assert isinstance(story1.items, list)
    assert len(story1.items) == 0

    assert isinstance(story2, Story)
    assert isinstance(story2.xml, Element)
    assert isinstance(story2.items, list)
    assert len(story2.items) == 0

def test_element_action_move_story():
    """
    Test we can access the elements of an EAStoryMove object created from a
    roElementAction file
    """
    ea = EAStoryMove(ROELEMENTACTIONMOVESTORY)
    assert isinstance(ea.xml, Element)
    assert isinstance(ea.target_story, Story)
    assert isinstance(ea.target_story.xml, Element)
    assert ea.target_story.id == 'STORY1'
    assert ea.target_story.items is None

    assert isinstance(ea.source_story, Story)
    assert isinstance(ea.source_story.xml, Element)
    assert ea.source_story.id == 'STORY3'
    assert isinstance(ea.source_story.items, list)
    assert len(ea.source_story.items) == 0

def test_element_action_replace_item():
    """
    Test we can access the elements of an EAItemReplace object created from a
    roElementAction file
    """
    ea = EAItemReplace(ROELEMENTACTIONREPITEM)
    assert isinstance(ea.xml, Element)
    assert isinstance(ea.target_story, Story)
    assert ea.target_story.id == 'STORY2'
    assert ea.target_story.slug is None
    assert ea.target_story.items is None

    assert isinstance(ea.target_item, Item)
    assert ea.target_item.id == 'ITEM21'
    assert ea.target_item.slug is None

    assert isinstance(ea.source_item, Item)
    assert ea.source_item.id == 'ITEM21'
    assert ea.source_item.slug == 'NEW ITEM 21'

def test_element_action_delete_item():
    """
    Test we can access the elements of an EAItemDelete object created from a
    roElementAction file
    """
    ea = EAItemDelete(ROELEMENTACTIONDELITEM)
    assert isinstance(ea.xml, Element)
    assert isinstance(ea.target_story, Story)
    assert ea.target_story.id == 'STORY1'
    assert ea.target_story.slug is None
    assert ea.target_story.items is None

    assert isinstance(ea.source_item, Item)
    assert ea.source_item.id == 'ITEM1'
    assert ea.source_item.slug is None

def test_element_action_insert_item():
    """
    Test we can access the elements of an EAItemInsert object created from a
    roElementAction file
    """
    ea = EAItemInsert(ROELEMENTACTIONINSERTITEM)
    assert isinstance(ea.xml, Element)
    assert isinstance(ea.target_story, Story)
    assert ea.target_story.id == 'STORY1'
    assert ea.target_story.slug is None
    assert ea.target_story.items is None

    assert isinstance(ea.target_item, Item)
    assert ea.target_item.id == 'ITEM2'
    assert ea.target_item.slug is None

    assert isinstance(ea.source_item, Item)
    assert ea.source_item.id == 'ITEMNEW'
    assert ea.source_item.slug == 'ITEM NEW'

def test_element_action_swap_item():
    """
    Test we can access the elements of an EAItemSwap object created from a
    roElementAction file
    """
    ea = EAItemSwap(ROELEMENTACTIONSWAPITEM)
    assert isinstance(ea.xml, Element)
    assert isinstance(ea.target_story, Story)
    assert ea.target_story.items is None
    assert isinstance(ea.source_items, set)
    item1, item2 = ea.source_items
    assert isinstance(item1, Item)
    assert isinstance(item2, Item)
    assert {item.id for item in ea.source_items} == {'ITEM1', 'ITEM2'}

def test_element_action_move_item():
    """
    Test we can access the elements of an EAItemMove object created from a
    roElementAction file
    """
    ea = EAItemMove(ROELEMENTACTIONMOVEITEM)
    assert isinstance(ea.xml, Element)
    assert isinstance(ea.target_story, Story)
    assert ea.target_story.id == 'STORY1'
    assert ea.target_story.slug is None
    assert ea.target_story.items is None

    assert isinstance(ea.target_item, Item)
    assert ea.target_item.id == 'ITEM1'
    assert ea.target_item.slug is None

    assert isinstance(ea.source_item, Item)
    assert ea.source_item.id == 'ITEM3'
    assert ea.source_item.slug is None
