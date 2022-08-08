# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

from mosromgr.mostypes import *
from mosromgr.exc import *


def test_mosfile_detect_element_action_story_replace(eastoryreplace):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'REPLACE' and
    no target itemID
    EXPECT: An object of type EAStoryReplace
    """
    ea = MosFile.from_file(eastoryreplace)
    assert type(ea) == EAStoryReplace

def test_mosfile_detect_element_action_story_replace(eaitemreplace):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'REPLACE' and
    a target itemID
    EXPECT: An object of type EAItemReplace
    """
    ea = MosFile.from_file(eaitemreplace)
    assert type(ea) == EAItemReplace

def test_mosfile_detect_element_action_story_delete(eastorydelete):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'DELETE' and
    no source itemID
    EXPECT: An object of type EAStoryDelete
    """
    ea = MosFile.from_file(eastorydelete)
    assert type(ea) == EAStoryDelete

def test_mosfile_detect_element_action_item_delete(eaitemdelete):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'DELETE' and a
    source itemID
    EXPECT: An object of type EAItemDelete
    """
    ea = MosFile.from_file(eaitemdelete)
    assert type(ea) == EAItemDelete

def test_mosfile_detect_element_action_item_insert(eastoryinsert):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'INSERT' and
    no target itemID
    EXPECT: An object of type EAStoryInsert
    """
    ea = MosFile.from_file(eastoryinsert)
    assert type(ea) == EAStoryInsert

def test_mosfile_detect_element_action_item_insert(eaiteminsert):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'INSERT' and a
    target itemID
    EXPECT: An object of type EAItemInsert
    """
    ea = MosFile.from_file(eaiteminsert)
    assert type(ea) == EAItemInsert

def test_mosfile_detect_element_action_story_swap_missing_target(eastoryswap):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'SWAP' and no
    source itemID
    EXPECT: An object of type EAStorySwap
    """
    ea = MosFile.from_file(eastoryswap)
    assert type(ea) == EAStorySwap

def test_mosfile_detect_element_action_story_swap_blank_target_storyid(eastoryswap2):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'SWAP' and no
    source itemID
    EXPECT: An object of type EAStorySwap
    """
    ea = MosFile.from_file(eastoryswap2)
    assert type(ea) == EAStorySwap

def test_mosfile_detect_element_action_item_swap(eaitemswap):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'SWAP' and two
    source itemIDs
    EXPECT: An object of type EAItemSwap
    """
    ea = MosFile.from_file(eaitemswap)
    assert type(ea) == EAItemSwap

def test_mosfile_detect_element_action_story_move(eastorymove):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'MOVE' and no
    target itemID
    EXPECT: An object of type EAStoryMove
    """
    ea = MosFile.from_file(eastorymove)
    assert type(ea) == EAStoryMove

def test_mosfile_detect_element_action_item_move(eaitemmove):
    """
    GIVEN: A path to a elementAction MOS file with the operation 'MOVE' and a
    target itemID
    EXPECT: An object of type EAItemMove
    """
    ea = MosFile.from_file(eaitemmove)
    assert type(ea) == EAItemMove