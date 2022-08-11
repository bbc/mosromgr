# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

from xml.etree.ElementTree import Element
from datetime import datetime

from mosromgr.moselements import MosElement, Story, Item, _is_technical_note


def test_mos_element_init():
    "Test we can create a MosElement and access its repr"
    e = MosElement(xml=None)
    assert repr(e) == "<MosElement>"

def test_story_init(story_xml):
    "Test we can create a Story element and access its repr"
    story = Story(story_xml)
    assert repr(story) == "<Story STORY1>"

def test_story_properties(story_xml, story2_xml, story3_xml):
    "Test we can create a Story element and access its properties"
    story = Story(story_xml)
    assert type(story.xml) == Element
    assert story.id == 'STORY1'
    assert story.slug == 'STORY 1'
    assert type(story.items) == list
    assert len(story.items) == 3
    item = story.items[0]
    assert type(item) == Item
    assert story.duration == 3
    assert story.offset is None
    assert story.start_time is None
    assert story.end_time is None
    assert type(story.script) == list
    assert len(story.script) == 3
    for p in story.script:
        assert type(p) == str
    p1 = story.script[0]
    assert p1 == "Welcome"
    p2 = story.script[1]
    assert p2 == "Welcome again"
    assert type(story.body) == list
    assert len(story.body) == 7
    for p in story.body:
        assert type(p) in (str, Item)
    body_part_1 = story.body[0]
    assert body_part_1 == "Welcome"
    body_part_2 = story.body[1]
    assert body_part_2 == ""
    body_part_3 = story.body[2]
    assert type(body_part_3) == Item

    story2 = Story(story2_xml)
    assert story2.duration is None
    assert story2.start_time == datetime(2022, 11, 16, 12, 30)
    assert story2.end_time == datetime(2022, 11, 16, 12, 40)

    story3 = Story(story3_xml)
    assert story3.start_time == datetime(2022, 11, 16, 12, 30)
    assert story3.end_time == datetime(2022, 11, 16, 12, 32)

def test_item_init(item_mosart_xml):
    "Test we can create a Item element and access its repr"
    item = Item(item_mosart_xml)
    assert repr(item) == "<Item ITEM1>"

def test_item_properties(item_mosart_xml):
    "Test we can create a Item element and access its properties"
    item = Item(item_mosart_xml)
    assert type(item.xml) == Element
    assert item.id == 'ITEM1'
    assert item.slug == 'ITEM 1'
    assert item.note is None
    assert item.type == 'MOSART'
    assert item.mos_id == 'MOS ID'
    assert item.object_id == '100'

def test_item_note_properties(item_note_xml):
    "Test we can create a Item element and access its properties"
    item = Item(item_note_xml)
    assert type(item.xml) == Element
    assert item.id == 'ITEM2'
    assert item.slug == 'ITEM 2'
    assert item.note == 'THIS IS A NOTE'
    assert item.type is None
    assert item.mos_id is None
    assert item.object_id is None

def test_is_technical_note():
    "Test we can determine what is and is not a technical note"
    e = Element('p')
    e.text = '(test)'
    assert _is_technical_note(e)
    e.text = '<test>'
    assert _is_technical_note(e)
    e.text = '(test'
    assert not _is_technical_note(e)
    e.text = 'test)'
    assert not _is_technical_note(e)
    e.text = 'test>'
    assert not _is_technical_note(e)
    e.text = 'test'
    assert not _is_technical_note(e)