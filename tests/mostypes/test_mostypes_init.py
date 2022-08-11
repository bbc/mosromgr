# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

from xml.etree.ElementTree import Element

from mosromgr.mostypes import *
from mosromgr.exc import *


def test_running_order_init(rocreate):
    "Test we can create a RunningOrder object from a roCreate file"
    ro = RunningOrder.from_file(rocreate)
    assert repr(ro) == '<RunningOrder 1000>'
    assert ro.ro_id == 'RO ID'
    assert ro.ro_slug == 'RO SLUG'
    assert isinstance(ro.xml, Element)
    assert str(ro).startswith('<mos>')
    assert str(ro).endswith('</mos>')

def test_running_order_init_str(rocreate):
    "Test we can create a RunningOrder object from a string representation of a roCreate file"
    xml = rocreate.read_text()
    ro = RunningOrder.from_string(xml)
    assert repr(ro) == '<RunningOrder 1000>'
    assert ro.ro_id == 'RO ID'
    assert ro.ro_slug == 'RO SLUG'
    assert isinstance(ro.xml, Element)
    assert str(ro).startswith('<mos>')
    assert str(ro).endswith('</mos>')

def test_story_send_init(rostorysend1):
    "Test we can create a StorySend object from a roStorySend file"
    ss = StorySend.from_file(rostorysend1)
    assert repr(ss) == '<StorySend 1001>'
    assert ss.ro_id == 'RO ID'
    assert isinstance(ss.xml, Element)
    assert str(ss).startswith('<mos>')
    assert str(ss).endswith('</mos>')

def test_element_action_replace_story_init(eastoryreplace):
    "Test we can create an EAStoryReplace object from a roElementAction file"
    ea = EAStoryReplace.from_file(eastoryreplace)
    assert repr(ea) == '<EAStoryReplace 1003>'
    assert ea.ro_id == 'RO ID'

def test_element_action_replace_item_init(eaitemreplace):
    "Test we can create an EAItemReplace object from a roElementAction file"
    ea = EAItemReplace.from_file(eaitemreplace)
    assert repr(ea) == '<EAItemReplace 1004>'
    assert ea.ro_id == 'RO ID'

def test_element_action_delete_story_init(eastorydelete):
    "Test we can create an EAStoryDelete object from a roElementAction file"
    ea = EAStoryDelete.from_file(eastorydelete)
    assert repr(ea) == '<EAStoryDelete 1005>'
    assert ea.ro_id == 'RO ID'

def test_element_action_delete_item_init(eaitemdelete):
    "Test we can create an EAItemDelete object from a roElementAction file"
    ea = EAItemDelete.from_file(eaitemdelete)
    assert repr(ea) == '<EAItemDelete 1006>'
    assert ea.ro_id == 'RO ID'

def test_element_action_insert_story_init(eastoryinsert):
    "Test we can create an EAStoryInsert object from a roElementAction file"
    ea = EAStoryInsert.from_file(eastoryinsert)
    assert repr(ea) == '<EAStoryInsert 1007>'
    assert ea.ro_id == 'RO ID'

def test_element_action_insert_item_init(eaiteminsert):
    "Test we can create an EAItemInsert object from a roElementAction file"
    ea = EAItemInsert.from_file(eaiteminsert)
    assert repr(ea) == '<EAItemInsert 1008>'
    assert ea.ro_id == 'RO ID'

def test_element_action_swap_story_init(eastoryswap):
    "Test we can create an EAStorySwap object from a roElementAction file"
    ea = EAStorySwap.from_file(eastoryswap)
    assert repr(ea) == '<EAStorySwap 1009>'
    assert ea.ro_id == 'RO ID'

def test_element_action_swap_item_init(eaitemswap):
    "Test we can create an EAItemSwap object from a roElementAction file"
    ea = EAItemSwap.from_file(eaitemswap)
    assert repr(ea) == '<EAItemSwap 1010>'
    assert ea.ro_id == 'RO ID'

def test_element_action_move_story_init(eastorymove):
    "Test we can create an EAStoryMove object from a roElementAction file"
    ea = EAStoryMove.from_file(eastorymove)
    assert repr(ea) == '<EAStoryMove 1011>'
    assert ea.ro_id == 'RO ID'

def test_element_action_move_item_init(eaitemmove):
    "Test we can create an EAItemMove object from a roElementAction file"
    ea = EAItemMove.from_file(eaitemmove)
    assert repr(ea) == '<EAItemMove 1012>'
    assert ea.ro_id == 'RO ID'

def test_metadata_replace_init(rometadatareplace):
    "Test we can create a MetaDataReplace object from a roMetaDataReplace file"
    mdr = MetaDataReplace.from_file(rometadatareplace)
    assert repr(mdr) == '<MetaDataReplace 1013>'
    assert mdr.ro_id == 'RO ID'

def test_story_append_init(rostoryappend):
    "Test we can create a StoryAppend object from a StoryAppend file"
    sa = StoryAppend.from_file(rostoryappend)
    assert repr(sa) == '<StoryAppend 1014>'
    assert sa.ro_id == 'RO ID'

def test_story_delete_init(rostorydelete):
    "Test we can create a StoryDelete object from a StoryDelete file"
    sd = StoryDelete.from_file(rostorydelete)
    assert repr(sd) == '<StoryDelete 1015>'
    assert sd.ro_id == 'RO ID'

def test_story_insert_init(rostoryinsert):
    "Test we can create a StoryInsert object from a StoryInsert file"
    si = StoryInsert.from_file(rostoryinsert)
    assert repr(si) == '<StoryInsert 1016>'
    assert si.ro_id == 'RO ID'

def test_story_move_init(rostorymove):
    "Test we can create a StoryMove object from a StoryMove file"
    sm = StoryMove.from_file(rostorymove)
    assert repr(sm) == '<StoryMove 1017>'
    assert sm.ro_id == 'RO ID'

def test_story_replace_init(rostoryreplace):
    "Test we can create a StoryReplace object from a StoryReplace file"
    sr = StoryReplace.from_file(rostoryreplace)
    assert repr(sr) == '<StoryReplace 1018>'
    assert sr.ro_id == 'RO ID'

def test_item_delete_init(roitemdelete):
    "Test we can create a ItemDelete object from a roItemDelete file"
    id = ItemDelete.from_file(roitemdelete)
    assert repr(id) == '<ItemDelete 1019>'
    assert id.ro_id == 'RO ID'

def test_item_insert_init(roiteminsert):
    "Test we can create a ItemInsert object from a roItemInsert file"
    ii = ItemInsert.from_file(roiteminsert)
    assert repr(ii) == '<ItemInsert 1020>'
    assert ii.ro_id == 'RO ID'

def test_item_move_multiple_init(roitemmovemultiple):
    "Test we can create a ItemMoveMultiple object from a roItemMoveMultiple file"
    imm = ItemMoveMultiple.from_file(roitemmovemultiple)
    assert repr(imm) == '<ItemMoveMultiple 1021>'
    assert imm.ro_id == 'RO ID'

def test_item_replace_init(roitemreplace):
    "Test we can create a ItemReplace object from a roItemReplace file"
    ir = ItemReplace.from_file(roitemreplace)
    assert repr(ir) == '<ItemReplace 1022>'
    assert ir.ro_id == 'RO ID'

def test_ro_replace_init(roreplace):
    "Test we can create a roReplace object from a roReplace file"
    rr = RunningOrderReplace.from_file(roreplace)
    assert repr(rr) == '<RunningOrderReplace 1023>'
    assert rr.ro_id == 'RO ID'

def test_ready_to_air_init(roreadytoair):
    "Test we can create a ReadyToAir object from a roReadyToAir file"
    rta = ReadyToAir.from_file(roreadytoair)
    assert repr(rta) == '<ReadyToAir 1024>'
    assert rta.ro_id == 'RO ID'

def test_rodelete_init(rodelete):
    "Test we can create a RunningOrderEnd object from a roDelete file"
    rd = RunningOrderEnd.from_file(rodelete)
    assert repr(rd) == '<RunningOrderEnd 9999>'
    assert rd.ro_id == 'RO ID'