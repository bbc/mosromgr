# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

from xml.etree.ElementTree import Element
from datetime import datetime

from mosromgr.moselements import *


def test_mos_element_init():
    "Test we can create a MosElement and access its repr"
    e = MosElement(xml=None)
    assert repr(e) == "<MosElement>"

def test_story_init(story_xml):
    "Test we can create a Story element and access its repr"
    story = Story(story_xml)
    assert repr(story) == "<Story STORY1>"

def test_story_properties(story_xml):
    "Test we can create a Story element and access its properties"
    story = Story(story_xml)
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
    p = story.script[0]
    assert p == "Welcome"
    assert type(story.body) == list
    assert len(story.body) == 7
    body_part_1 = story.body[0]
    assert body_part_1 == "Welcome"
    body_part_2 = story.body[1]
    assert body_part_2 is None
    body_part_3 = story.body[2]
    assert type(body_part_3) == Item

def test_item_init(item_xml):
    "Test we can create a Item element and access its repr"
    item = Item(item_xml)
    assert repr(item) == "<Item ITEM1>"

def test_item_properties(item_xml):
    "Test we can create a Item element and access its properties"
    item = Item(item_xml)
    assert item.id == 'ITEM1'
    assert item.slug == 'ITEM 1'
    assert item.note is None
