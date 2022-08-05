# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

from mosromgr.mostypes import *
from mosromgr.exc import *


def test_sort_two(rocreate, rodelete):
    """
    GIVEN: Two MOS objects
    EXPECT: The MOS objects sorted by their message ID
    """
    ro = RunningOrder.from_file(rocreate)
    rd = RunningOrderEnd.from_file(rodelete)
    assert sorted([ro, rd]) == [ro, rd]
    assert sorted([rd, ro]) == [ro, rd]

def test_sort_all(rocreate, rostorysend1, rostorysend2, roelementactionstoryreplace,
    roelementactionitemreplace, roelementactionstorydelete, roelementactionitemdelete,
    roelementactionstoryinsert, roelementactioniteminsert,
    roelementactionstoryswap, roelementactionitemswap, roelementactionstorymove,
    roelementactionitemmove, rometadatareplace, rodelete):
    """
    GIVEN: A list of MOS objects
    EXPECT: The MOS objects sorted by their message ID
    """
    ro = RunningOrder.from_file(rocreate)
    ss1 = StorySend.from_file(rostorysend1)
    ss2 = StorySend.from_file(rostorysend2)
    ea1 = EAStoryReplace.from_file(roelementactionstoryreplace)
    ea2 = EAItemReplace.from_file(roelementactionitemreplace)
    ea3 = EAStoryDelete.from_file(roelementactionstorydelete)
    ea4 = EAItemDelete.from_file(roelementactionitemdelete)
    ea5 = EAStoryInsert.from_file(roelementactionstoryinsert)
    ea6 = EAItemInsert.from_file(roelementactioniteminsert)
    ea7 = EAStorySwap.from_file(roelementactionstoryswap)
    ea8 = EAItemSwap.from_file(roelementactionitemswap)
    ea9 = EAStoryMove.from_file(roelementactionstorymove)
    ea10 = EAItemMove.from_file(roelementactionitemmove)
    mdr = MetaDataReplace.from_file(rometadatareplace)
    rd = RunningOrderEnd.from_file(rodelete)

    all_objs_rand = [ss1, ea1, ea4, mdr, ss2, ea9, ea8, ea2, rd, ea7, ea5, ro, ea3, ea6, ea10]
    all_objs_in_order = [ro, ss1, ss2, ea1, ea2, ea3, ea4, ea5, ea6, ea7, ea8, ea9, ea10, mdr, rd]

    assert sorted(all_objs_rand) == all_objs_in_order