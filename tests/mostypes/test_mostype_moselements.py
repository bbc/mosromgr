# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

from xml.etree.ElementTree import Element
from datetime import datetime

from mosromgr.mostypes import *
from mosromgr.moselements import *


def test_running_order(rocreate):
    """
    Test we can access the elements of a RunningOrder object created from a
    roCreate file
    """
    ro = RunningOrder.from_file(rocreate)
    assert isinstance(ro.xml, Element)
    assert str(ro).startswith('<mos>')
    assert str(ro).endswith('</mos>')
    assert isinstance(ro.stories, list)
    assert len(ro.stories) == 3
    assert ro.duration == 31
    assert isinstance(ro.start_time, datetime)
    assert isinstance(ro.end_time, datetime)
    script = ro.script
    assert type(script) is list
    text = script[0]
    assert type(text) is str
    assert text == 'This is story 1'
    body = ro.body
    assert type(body) is list
    text = body[0]
    assert type(text) is str
    assert text == 'This is story 1'
    item = body[1]
    assert type(item) is Item
    assert item.id == 'ITEM1'

    story1 = ro.stories[0]
    assert repr(story1) == '<Story STORY1>'
    assert isinstance(story1, Story)
    assert isinstance(story1.xml, Element)
    assert str(story1).startswith('<story>')
    assert str(story1).strip().endswith('</story>')
    assert story1.id == 'STORY1'
    assert story1.slug == 'STORY 1'
    assert story1.offset == 0
    assert story1.duration == 3
    assert isinstance(story1.start_time, datetime)
    assert story1.start_time == ro.start_time
    assert isinstance(story1.end_time, datetime)
    assert story1.end_time > ro.start_time
    assert type(story1.script) is list
    script = story1.script
    assert type(script) is list
    text = script[0]
    assert type(text) is str
    assert text == 'This is story 1'
    ro.inspect()  # test this?

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
    assert story2.offset == 3
    assert story2.duration == 8
    assert isinstance(story2.start_time, datetime)
    assert story2.start_time > story1.start_time

    assert isinstance(story2.items, list)
    assert len(story2.items) == 3
    item21 = story2.items[0]
    assert isinstance(item21, Item)
    assert isinstance(item21.xml, Element)
    assert item21.id == 'ITEM21'
    assert item21.slug == 'ITEM 21'

def test_running_order_with_note(rocreate3):
    """
    Test we can access the notes in a RunningOrder object created from a
    roCreate file
    """
    ro = RunningOrder.from_file(rocreate3)
    assert ro.stories[0].items[0].note == 'BB1'
    assert ro.stories[1].items[0].note == 'BB2'

def test_running_order_no_roedstart(rocreate4, rocreate5):
    """
    Test we can access the (null) start_time and end_time properties of a
    RunningOrder object created from a roCreate file with an empty or missing
    roEdStart tag
    """
    ro4 = RunningOrder.from_file(rocreate4)
    assert ro4.start_time is None
    assert ro4.end_time is None
    ro5 = RunningOrder.from_file(rocreate5)
    assert ro5.start_time is None
    assert ro5.end_time is None

def test_running_order_no_story_durations(rocreate6):
    """
    Test the RO duration is None when story duration is not given
    """
    ro = RunningOrder.from_file(rocreate6)
    assert ro.duration is None

def test_story_send(rostorysend1):
    """
    Test we can access the elements of a StorySend object created from a
    roStorySend file
    """
    ss = StorySend.from_file(rostorysend1)
    assert isinstance(ss.xml, Element)
    assert isinstance(ss.story, Story)
    assert isinstance(ss.story.xml, Element)
    assert ss.story.id == 'STORY1'
    assert ss.story.slug == 'STORY 1'
    assert ss.story.duration == 30
    ss.inspect()  # test this?

    assert isinstance(ss.story.items, list)
    assert len(ss.story.items) == 1
    item1 = ss.story.items[0]
    assert isinstance(item1, Item)
    assert isinstance(item1.xml, Element)
    assert item1.id == 'ITEM1'
    assert item1.slug == 'ITEM 1'

def test_story_send_with_storyduration(rostorysend5):
    """
    Test we can access the elements of a StorySend object created from a
    roStorySend file with a <StoryDuration> tag instead of MediaTime and
    TextTime
    """
    ss = StorySend.from_file(rostorysend5)
    assert isinstance(ss.xml, Element)
    assert isinstance(ss.story, Story)
    assert isinstance(ss.story.xml, Element)
    assert ss.story.id == 'STORY1'
    assert ss.story.slug == 'STORY 1'
    assert ss.story.duration == 45

    assert isinstance(ss.story.items, list)
    assert len(ss.story.items) == 1
    item1 = ss.story.items[0]
    assert isinstance(item1, Item)
    assert isinstance(item1.xml, Element)
    assert item1.id == 'ITEM1'
    assert item1.slug == 'ITEM 1'

def test_story_append(rostoryappend):
    """
    Test we can access the elements of a StoryAppend object created from a
    roStoryAppend file
    """
    sa = StoryAppend.from_file(rostoryappend)
    assert isinstance(sa.xml, Element)
    assert isinstance(sa.stories, list)
    assert len(sa.stories) == 2
    story1, story2 = sa.stories
    sa.inspect()  # test this?

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


def test_story_delete(rostorydelete):
    """
    Test we can access the elements of a StoryDelete object created from a
    roStoryDelete file
    """
    sd = StoryDelete.from_file(rostorydelete)
    sd.inspect()  # test this?
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

def test_story_insert(rostoryinsert):
    """
    Test we can access the elements of a StoryInsert object created from a
    roStoryInsert file
    """
    si = StoryInsert.from_file(rostoryinsert)
    si.inspect()  # test this?
    assert isinstance(si.xml, Element)
    assert isinstance(si.target_story, Story)
    assert si.target_story.id == 'STORY2'
    assert si.target_story.slug is None
    assert si.target_story.duration is None
    assert isinstance(si.source_stories, list)
    assert len(si.source_stories) == 2
    story1, story2 = si.source_stories

    assert isinstance(story1, Story)
    assert story1.id == 'STORY4'
    assert story1.slug == 'STORY 4'
    assert story1.duration == 6
    assert isinstance(story1.items, list)
    assert len(story1.items) == 1
    item1 = story1.items[0]
    assert item1.id == 'ITEM4'
    assert item1.slug == 'ITEM 4'

    assert isinstance(story2, Story)
    assert story2.id == 'STORY5'
    assert story2.slug == 'STORY 5'
    assert story2.duration == 15
    assert isinstance(story2.items, list)
    assert len(story2.items) == 1
    item2 = story2.items[0]
    assert item2.id == 'ITEM5'
    assert item2.slug == 'ITEM 5'

def test_story_move(rostorymove):
    """
    Test we can access the elements of a StoryMove object created from a
    roStoryMove file
    """
    sm = StoryMove.from_file(rostorymove)
    assert isinstance(sm.target_story, Story)
    assert sm.target_story.id == 'STORY1'
    assert isinstance(sm.target_story.xml, Element)
    assert sm.target_story.items is None
    sm.inspect()  # test this?

    assert isinstance(sm.source_story, Story)
    assert sm.source_story.id == 'STORY3'
    assert isinstance(sm.source_story.xml, Element)
    assert sm.target_story.items is None

def test_story_replace(rostoryreplace):
    """
    Test we can access the elements of a StoryReplace object created from a
    roStoryReplace file
    """
    sr = StoryReplace.from_file(rostoryreplace)
    assert isinstance(sr.xml, Element)
    assert isinstance(sr.story, Story)
    assert isinstance(sr.story.xml, Element)
    assert sr.story.id == 'STORY1'
    assert sr.story.items is None
    sr.inspect()  # test this?

    assert isinstance(sr.stories, list)
    story = sr.stories[0]
    assert isinstance(story, Story)
    assert isinstance(story.xml, Element)
    assert story.id == 'STORY1'
    assert story.slug == 'STORY ONE'
    assert isinstance(story.items, list)
    assert len(story.items) == 1
    item1 = story.items[0]
    assert isinstance(item1, Item)
    assert item1.id == 'ITEM1'
    assert item1.slug == 'ITEM ONE'

def test_ro_replace(roreplace):
    """
    Test we can access the elements of a RunningOrderReplace object created from
    a roReplace file
    """
    ror = RunningOrderReplace.from_file(roreplace)
    assert isinstance(ror.xml, Element)
    assert isinstance(ror.stories, list)
    assert len(ror.stories) == 3
    assert ror.duration == 53
    ror.inspect()  # test this?

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

def test_metadata_replace(rometadatareplace):
    """
    Test we can access the elements of a MetaDataReplace object created from a
    roMetadataReplace file
    """
    mdr = MetaDataReplace.from_file(rometadatareplace)
    assert isinstance(mdr.xml, Element)
    assert mdr.ro_slug == 'RO SLUG NEW'
    mdr.inspect()  # test this?

def test_item_insert(roiteminsert):
    """
    Test we can access the elements of an ItemInsert object created from a
    roItemInsert file
    """
    ii = ItemInsert.from_file(roiteminsert)
    assert isinstance(ii.xml, Element)
    assert isinstance(ii.story, Story)
    assert ii.story.id == 'STORY1'
    assert ii.story.slug is None
    assert ii.story.duration is None
    assert ii.story.items is None
    ii.inspect()  # test this?

    assert isinstance(ii.item, Item)
    assert ii.item.id == 'ITEM2'

    assert isinstance(ii.items, list)
    assert len(ii.items) == 2

    item1, item2 = ii.items
    assert item1.id == 'ITEM4'
    assert item1.slug == 'ITEM 4'
    assert item2.id == 'ITEM5'
    assert item2.slug == 'ITEM 5'

def test_item_delete(roitemdelete):
    """
    Test we can access the elements of an ItemDelete object created from a
    roItemDelete file
    """
    id = ItemDelete.from_file(roitemdelete)
    assert isinstance(id.xml, Element)
    assert isinstance(id.story, Story)
    assert id.story.id == 'STORY1'
    assert id.story.slug is None
    assert id.story.duration is None
    assert id.story.items is None
    id.inspect()  # test this?

    assert isinstance(id.items, list)
    assert len(id.items) == 2
    assert [item.id for item in id.items] == ['ITEM1', 'ITEM2']

def test_item_move_multiple(roitemmovemultiple):
    """
    Test we can access the elements of an ItemMoveMultiple object created from a
    roItemMoveMultiple file
    """
    imm = ItemMoveMultiple.from_file(roitemmovemultiple)
    assert isinstance(imm.xml, Element)
    assert isinstance(imm.story, Story)
    assert imm.story.id == 'STORY1'
    assert imm.story.slug is None
    assert imm.story.duration is None
    assert imm.story.items is None
    imm.inspect()  # test this?

    assert isinstance(imm.item, Item)
    assert imm.item.id == 'ITEM1'
    assert imm.item.slug is None

    assert isinstance(imm.items, list)
    assert len(imm.items) == 2
    item1, item2 = imm.items
    assert item1.id == 'ITEM2'
    assert item1.slug is None
    assert item2.id == 'ITEM3'
    assert item2.slug is None

def test_item_replace(roitemreplace):
    """
    Test we can access the elements of an ItemReplace object created from a
    roItemReplace file
    """
    ir = ItemReplace.from_file(roitemreplace)
    ir.inspect()  # test this?
    assert isinstance(ir.xml, Element)
    assert isinstance(ir.story, Story)
    assert ir.story.id == 'STORY2'
    assert ir.story.slug is None
    assert ir.story.duration is None
    assert ir.story.items is None

    assert isinstance(ir.item, Item)
    assert ir.item.id == 'ITEM21'
    assert ir.item.slug is None

    assert isinstance(ir.items, list)
    assert len(ir.items) == 2
    item1, item2 = ir.items

    assert isinstance(item1, Item)
    assert item1.id == 'ITEM24'
    assert item1.slug == 'NEW ITEM 24'

    assert isinstance(item2, Item)
    assert item2.id == 'ITEM25'
    assert item2.slug == 'NEW ITEM 25'

def test_ready_to_air(roreadytoair):
    """
    Test we can access the elements of a ReadyToAir object created from a
    roReadyToAir file
    """
    rta = ReadyToAir.from_file(roreadytoair)
    rta.inspect()  # test this?
    assert isinstance(rta.xml, Element)

def test_rodelete(rodelete):
    """
    Test we can access the elements of a RunningOrderAir object created from a
    roDelete file
    """
    rd = RunningOrderEnd.from_file(rodelete)
    rd.inspect()  # test this?
    assert isinstance(rd.xml, Element)