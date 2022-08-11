# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

from xml.etree.ElementTree import Element

from mosromgr.mostypes import *
from mosromgr.moselements import *


def test_element_action_story_replace(eastoryreplace):
    """
    Test we can access the elements of an EAStoryReplace object created from a
    roElementAction file
    """
    ea = EAStoryReplace.from_file(eastoryreplace)
    ea.inspect()  # test this?
    assert isinstance(ea.xml, Element)

    assert isinstance(ea.story, Story)
    assert isinstance(ea.story.xml, Element)
    assert ea.story.id == 'STORY1'
    assert ea.story.slug is None
    assert ea.story.duration is None
    assert ea.story.items is None

    assert isinstance(ea.stories, list)
    story = ea.stories[0]
    assert isinstance(story, Story)
    assert isinstance(story.xml, Element)
    assert story.id == 'STORY5'
    assert story.slug == 'STORY 5'
    assert story.duration == 30
    assert isinstance(story.items, list)
    assert len(story.items) == 1
    item = story.items[0]
    assert item.id == 'ITEM1'
    assert item.slug == 'ITEM ONE'

def test_element_action_story_delete(eastorydelete):
    """
    Test we can access the elements of an EAStoryDelete object created from a
    roElementAction file
    """
    ea = EAStoryDelete.from_file(eastorydelete)
    ea.inspect()  # test this?
    assert isinstance(ea.xml, Element)
    assert isinstance(ea.stories, list)
    story = ea.stories[0]
    assert isinstance(story, Story)
    assert isinstance(story.xml, Element)
    assert story.id == 'STORY1'
    assert story.slug is None
    assert story.duration is None
    assert isinstance(story.items, list)
    assert len(story.items) == 0

def test_element_action_story_insert(eastoryinsert):
    """
    Test we can access the elements of an EAStoryInsert object created from a
    roElementAction file
    """
    ea = EAStoryInsert.from_file(eastoryinsert)
    ea.inspect()  # test this?
    assert isinstance(ea.xml, Element)

    assert isinstance(ea.story, Story)
    assert isinstance(ea.story.xml, Element)
    assert ea.story.id == 'STORY2'
    assert ea.story.slug is None
    assert ea.story.duration is None
    assert ea.story.items is None

    assert isinstance(ea.stories, list)
    story = ea.stories[0]
    assert isinstance(story, Story)
    assert isinstance(story.xml, Element)
    assert story.id == 'STORY5'
    assert story.slug == 'STORY 5'
    assert story.duration is None
    assert isinstance(story.items, list)
    assert len(story.items) == 1
    item = story.items[0]
    assert item.id == 'ITEM1'
    assert item.slug == 'ITEM 1'

def test_element_action_story_swap(eastoryswap):
    """
    Test we can access the elements of an EAStorySwap object created from a
    roElementAction file
    """
    ea = EAStorySwap.from_file(eastoryswap)
    ea.inspect()  # test this?

    assert isinstance(ea.stories, tuple)
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

def test_element_action_story_move(eastorymove):
    """
    Test we can access the elements of an EAStoryMove object created from a
    roElementAction file
    """
    ea = EAStoryMove.from_file(eastorymove)
    ea.inspect()  # test this?
    assert isinstance(ea.xml, Element)
    assert isinstance(ea.story, Story)
    assert isinstance(ea.story.xml, Element)
    assert ea.story.id == 'STORY1'
    assert ea.story.items is None

    assert isinstance(ea.stories, list)
    story = ea.stories[0]
    assert isinstance(story, Story)
    assert isinstance(story.xml, Element)
    assert story.id == 'STORY3'
    assert isinstance(story.items, list)
    assert len(story.items) == 0

def test_element_action_item_replace(eaitemreplace):
    """
    Test we can access the elements of an EAItemReplace object created from a
    roElementAction file
    """
    ea = EAItemReplace.from_file(eaitemreplace)
    ea.inspect()  # test this?
    assert isinstance(ea.xml, Element)
    assert isinstance(ea.story, Story)
    assert ea.story.id == 'STORY1'
    assert ea.story.slug is None
    assert ea.story.items is None

    assert isinstance(ea.item, Item)
    assert ea.item.id == 'ITEM1'
    assert ea.item.slug is None

    assert isinstance(ea.items, list)
    item = ea.items[0]
    assert isinstance(item, Item)
    assert item.id == 'ITEM21'
    assert item.slug == 'NEW ITEM 21'

def test_element_action_item_delete(eaitemdelete):
    """
    Test we can access the elements of an EAItemDelete object created from a
    roElementAction file
    """
    ea = EAItemDelete.from_file(eaitemdelete)
    ea.inspect()  # test this?
    assert isinstance(ea.xml, Element)
    assert isinstance(ea.story, Story)
    assert ea.story.id == 'STORY1'
    assert ea.story.slug is None
    assert ea.story.items is None

    assert isinstance(ea.items, list)
    source_item = ea.items[0]
    assert isinstance(source_item, Item)
    assert source_item.id == 'ITEM1'
    assert source_item.slug is None

def test_element_action_item_insert(eaiteminsert):
    """
    Test we can access the elements of an EAItemInsert object created from a
    roElementAction file
    """
    ea = EAItemInsert.from_file(eaiteminsert)
    ea.inspect()  # test this?
    assert isinstance(ea.xml, Element)
    assert isinstance(ea.story, Story)
    assert ea.story.id == 'STORY1'
    assert ea.story.slug is None
    assert ea.story.items is None

    assert isinstance(ea.item, Item)
    assert ea.item.id == 'ITEM2'
    assert ea.item.slug is None

    assert isinstance(ea.items, list)
    item = ea.items[0]
    assert isinstance(item, Item)
    assert item.id == 'ITEM5'
    assert item.slug == 'ITEM 5'

def test_element_action_item_swap(eaitemswap):
    """
    Test we can access the elements of an EAItemSwap object created from a
    roElementAction file
    """
    ea = EAItemSwap.from_file(eaitemswap)
    ea.inspect()  # test this?
    assert isinstance(ea.xml, Element)
    assert isinstance(ea.story, Story)
    assert ea.story.items is None
    assert isinstance(ea.items, tuple)
    item1, item2 = ea.items
    assert isinstance(item1, Item)
    assert isinstance(item2, Item)
    assert {item.id for item in ea.items} == {'ITEM1', 'ITEM2'}

def test_element_action_item_move(eaitemmove):
    """
    Test we can access the elements of an EAItemMove object created from a
    roElementAction file
    """
    ea = EAItemMove.from_file(eaitemmove)
    ea.inspect()  # test this?
    assert isinstance(ea.xml, Element)
    assert isinstance(ea.story, Story)
    assert ea.story.id == 'STORY1'
    assert ea.story.slug is None
    assert ea.story.items is None

    assert isinstance(ea.item, Item)
    assert ea.item.id == 'ITEM1'
    assert ea.item.slug is None

    assert isinstance(ea.items, list)
    item = ea.items[0]
    assert isinstance(item, Item)
    assert item.id == 'ITEM3'
    assert item.slug is None