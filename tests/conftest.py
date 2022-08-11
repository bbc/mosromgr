# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from xml.etree import ElementTree

import pytest


HERE = Path(__file__).parent.absolute()
MOCK_MOS = HERE / 'mock_mos'
MOCK_XML = HERE / 'mock_xml'


@pytest.fixture()
def invalid_xml():
    return MOCK_XML / 'invalid.xml'

@pytest.fixture()
def rocreate():
    return MOCK_MOS / 'roCreate.mos.xml'

@pytest.fixture()
def rocreate2():
    return MOCK_MOS / 'roCreate2.mos.xml'
    
# roCreate with notes
@pytest.fixture()
def rocreate3():
    return MOCK_MOS / 'roCreate3.mos.xml'
    
# roCreate with no roEdStart
@pytest.fixture()
def rocreate4():
    return MOCK_MOS / 'roCreate4.mos.xml'
    
# roCreate with empty roEdStart
@pytest.fixture()
def rocreate5():
    return MOCK_MOS / 'roCreate5.mos.xml'
    
# roCreate with no roEdStart or story durations
@pytest.fixture()
def rocreate6():
    return MOCK_MOS / 'roCreate6.mos.xml'

@pytest.fixture()
def rostorysend1():
    return MOCK_MOS / 'roStorySend1.mos.xml'

@pytest.fixture()
def rostorysend2():
    return MOCK_MOS / 'roStorySend2.mos.xml'

@pytest.fixture()
def eastoryreplace():
    return MOCK_MOS / 'roElementActionStoryReplace.mos.xml'

# eastoryreplace with unknown story
@pytest.fixture()
def eastoryreplace2():
    return MOCK_MOS / 'roElementActionStoryReplace2.mos.xml'

@pytest.fixture()
def eaitemreplace():
    return MOCK_MOS / 'roElementActionItemReplace.mos.xml'

# eaitemreplace with unknown story
@pytest.fixture()
def eaitemreplace2():
    return MOCK_MOS / 'roElementActionItemReplace2.mos.xml'

# eaitemreplace with unknown item
@pytest.fixture()
def eaitemreplace3():
    return MOCK_MOS / 'roElementActionItemReplace3.mos.xml'

@pytest.fixture()
def eastorydelete():
    return MOCK_MOS / 'roElementActionStoryDelete.mos.xml'

# eastorydelete with unknown story
@pytest.fixture()
def eastorydelete2():
    return MOCK_MOS / 'roElementActionStoryDelete2.mos.xml'

@pytest.fixture()
def eaitemdelete():
    return MOCK_MOS / 'roElementActionItemDelete.mos.xml'

# eaitemdelete with unknown story
@pytest.fixture()
def eaitemdelete2():
    return MOCK_MOS / 'roElementActionItemDelete2.mos.xml'

# eaitemdelete with unknown item
@pytest.fixture()
def eaitemdelete3():
    return MOCK_MOS / 'roElementActionItemDelete3.mos.xml'

@pytest.fixture()
def eastoryinsert():
    return MOCK_MOS / 'roElementActionStoryInsert.mos.xml'

# eastoryinsert with empty story id
@pytest.fixture()
def eastoryinsert2():
    return MOCK_MOS / 'roElementActionStoryInsert2.mos.xml'

# eastoryinsert with unknown story
@pytest.fixture()
def eastoryinsert3():
    return MOCK_MOS / 'roElementActionStoryInsert3.mos.xml'

# eastoryinsert with duplicate story
@pytest.fixture()
def eastoryinsert4():
    return MOCK_MOS / 'roElementActionStoryInsert4.mos.xml'

@pytest.fixture()
def eaiteminsert():
    return MOCK_MOS / 'roElementActionItemInsert.mos.xml'

# eaiteminsert with unknown story
@pytest.fixture()
def eaiteminsert2():
    return MOCK_MOS / 'roElementActionItemInsert2.mos.xml'

# eaiteminsert with no item id
@pytest.fixture()
def eaiteminsert3():
    return MOCK_MOS / 'roElementActionItemInsert3.mos.xml'

# eaiteminsert with unknown item
@pytest.fixture()
def eaiteminsert4():
    return MOCK_MOS / 'roElementActionItemInsert4.mos.xml'

# eastoryswap with empty element_target
@pytest.fixture()
def eastoryswap():
    return MOCK_MOS / 'roElementActionStorySwap.mos.xml'

# eastoryswap with empty storyid in element_target
@pytest.fixture()
def eastoryswap2():
    return MOCK_MOS / 'roElementActionStorySwap2.mos.xml'

# eastoryswap with unknown story 1
@pytest.fixture()
def eastoryswap3():
    return MOCK_MOS / 'roElementActionStorySwap3.mos.xml'

# eastoryswap with unknown story 2
@pytest.fixture()
def eastoryswap4():
    return MOCK_MOS / 'roElementActionStorySwap4.mos.xml'

@pytest.fixture()
def eaitemswap():
    return MOCK_MOS / 'roElementActionItemSwap.mos.xml'

# eaitemswap with unknown story
@pytest.fixture()
def eaitemswap2():
    return MOCK_MOS / 'roElementActionItemSwap2.mos.xml'

# eaitemswap with unknown item 1
@pytest.fixture()
def eaitemswap3():
    return MOCK_MOS / 'roElementActionItemSwap3.mos.xml'

# eaitemswap with unknown item 2
@pytest.fixture()
def eaitemswap4():
    return MOCK_MOS / 'roElementActionItemSwap4.mos.xml'

@pytest.fixture()
def eastorymove():
    return MOCK_MOS / 'roElementActionStoryMove.mos.xml'

# eastorymove with no target story
@pytest.fixture()
def eastorymove2():
    return MOCK_MOS / 'roElementActionStoryMove2.mos.xml'

# eastorymove with unknown target story
@pytest.fixture()
def eastorymove3():
    return MOCK_MOS / 'roElementActionStoryMove3.mos.xml'

# eastorymove with unknown source story
@pytest.fixture()
def eastorymove4():
    return MOCK_MOS / 'roElementActionStoryMove4.mos.xml'

@pytest.fixture()
def eaitemmove():
    return MOCK_MOS / 'roElementActionItemMove.mos.xml'

# eaitemmove with unknown story
@pytest.fixture()
def eaitemmove2():
    return MOCK_MOS / 'roElementActionItemMove2.mos.xml'

# eaitemmove with unknown target item
@pytest.fixture()
def eaitemmove3():
    return MOCK_MOS / 'roElementActionItemMove3.mos.xml'

# eaitemmove with unknown source item
@pytest.fixture()
def eaitemmove4():
    return MOCK_MOS / 'roElementActionItemMove4.mos.xml'

@pytest.fixture()
def rostoryappend():
    return MOCK_MOS / 'roStoryAppend.mos.xml'

@pytest.fixture()
def rostoryreplace():
    return MOCK_MOS / 'roStoryReplace.mos.xml'

# storyreplace with unknown story
@pytest.fixture()
def rostoryreplace2():
    return MOCK_MOS / 'roStoryReplace2.mos.xml'

# storyreplace with no stories
@pytest.fixture()
def rostoryreplace3():
    return MOCK_MOS / 'roStoryReplace3.mos.xml'

@pytest.fixture()
def roitemreplace():
    return MOCK_MOS / 'roItemReplace.mos.xml'

# itemreplace with unknown story
@pytest.fixture()
def roitemreplace2():
    return MOCK_MOS / 'roItemReplace2.mos.xml'

# itemreplace with unknown item
@pytest.fixture()
def roitemreplace3():
    return MOCK_MOS / 'roItemReplace3.mos.xml'

@pytest.fixture()
def rostorydelete():
    return MOCK_MOS / 'roStoryDelete.mos.xml'

# storydelete with unknown story
@pytest.fixture()
def rostorydelete2():
    return MOCK_MOS / 'roStoryDelete2.mos.xml'

@pytest.fixture()
def roitemdelete():
    return MOCK_MOS / 'roItemDelete.mos.xml'

# itemdelete with unknown story
@pytest.fixture()
def roitemdelete2():
    return MOCK_MOS / 'roItemDelete2.mos.xml'

# itemdelete with unknown item
@pytest.fixture()
def roitemdelete3():
    return MOCK_MOS / 'roItemDelete3.mos.xml'

# itemdelete with no item id
@pytest.fixture()
def roitemdelete4():
    return MOCK_MOS / 'roItemDelete4.mos.xml'

@pytest.fixture()
def rostoryinsert():
    return MOCK_MOS / 'roStoryInsert.mos.xml'

# storyinsert with unknown story
@pytest.fixture()
def rostoryinsert2():
    return MOCK_MOS / 'roStoryInsert2.mos.xml'

# storyinsert with source story which already exists in RO
@pytest.fixture()
def rostoryinsert3():
    return MOCK_MOS / 'roStoryInsert3.mos.xml'

@pytest.fixture()
def roiteminsert():
    return MOCK_MOS / 'roItemInsert.mos.xml'

# iteminsert with unknown story
@pytest.fixture()
def roiteminsert2():
    return MOCK_MOS / 'roItemInsert2.mos.xml'

# iteminsert with unknown item
@pytest.fixture()
def roiteminsert3():
    return MOCK_MOS / 'roItemInsert3.mos.xml'

# iteminsert with no item id
@pytest.fixture()
def roiteminsert4():
    return MOCK_MOS / 'roItemInsert4.mos.xml'

# iteminsert with item id already in RO
@pytest.fixture()
def roiteminsert5():
    return MOCK_MOS / 'roItemInsert5.mos.xml'

# iteminsert with no items
@pytest.fixture()
def roiteminsert6():
    return MOCK_MOS / 'roItemInsert6.mos.xml'

@pytest.fixture()
def rostorymove():
    return MOCK_MOS / 'roStoryMove.mos.xml'

# storymove with no target story
@pytest.fixture()
def rostorymove2():
    return MOCK_MOS / 'roStoryMove2.mos.xml'

# storymove with no stories
@pytest.fixture()
def rostorymove3():
    return MOCK_MOS / 'roStoryMove3.mos.xml'

# storymove with unknown source story
@pytest.fixture()
def rostorymove4():
    return MOCK_MOS / 'roStoryMove4.mos.xml'

# storymove with unknown target story
@pytest.fixture()
def rostorymove5():
    return MOCK_MOS / 'roStoryMove5.mos.xml'

@pytest.fixture()
def roitemmovemultiple():
    return MOCK_MOS / 'roItemMoveMultiple.mos.xml'

# itemmovemultiple with no story id
@pytest.fixture()
def roitemmovemultiple2():
    return MOCK_MOS / 'roItemMoveMultiple2.mos.xml'

# itemmovemultiple with no story tag
@pytest.fixture()
def roitemmovemultiple3():
    return MOCK_MOS / 'roItemMoveMultiple3.mos.xml'

# itemmovemultiple with unknown story
@pytest.fixture()
def roitemmovemultiple4():
    return MOCK_MOS / 'roItemMoveMultiple4.mos.xml'

# itemmovemultiple with unknown story
@pytest.fixture()
def roitemmovemultiple5():
    return MOCK_MOS / 'roItemMoveMultiple5.mos.xml'

# itemmovemultiple with no target item id
@pytest.fixture()
def roitemmovemultiple6():
    return MOCK_MOS / 'roItemMoveMultiple6.mos.xml'

# itemmovemultiple with unknown target item
@pytest.fixture()
def roitemmovemultiple7():
    return MOCK_MOS / 'roItemMoveMultiple7.mos.xml'

# itemmovemultiple with unknown source item
@pytest.fixture()
def roitemmovemultiple8():
    return MOCK_MOS / 'roItemMoveMultiple8.mos.xml'

@pytest.fixture()
def rometadatareplace():
    return MOCK_MOS / 'roMetadataReplace.mos.xml'

@pytest.fixture()
def roreplace():
    return MOCK_MOS / 'roReplace.mos.xml'

@pytest.fixture()
def rodelete():
    return MOCK_MOS / 'roDelete.mos.xml'

@pytest.fixture()
def roreadytoair():
    return MOCK_MOS / 'roReadyToAir.mos.xml'


@pytest.fixture()
def ro_all(rocreate, rostorysend1, rostorysend2, eastoryreplace, eaitemreplace,
    eastorydelete, eaitemdelete, eastoryinsert, eaiteminsert, eastoryswap,
    eaitemswap, eastorymove, eaitemmove, rometadatareplace, roreadytoair,
    rodelete
):
    return [
        rocreate, rostorysend1, rostorysend2, eastoryreplace, eaitemreplace,
        eastorydelete, eaitemdelete, eastoryinsert, eaiteminsert, eastoryswap,
        eaitemswap, eastorymove, eaitemmove, rometadatareplace, roreadytoair,
        rodelete
    ]

# Various invalid MOS files

@pytest.fixture()
def rostorysend3():
    return MOCK_MOS / 'roStorySend3.mos.xml'

@pytest.fixture()
def rostorysend4():
    return MOCK_MOS / 'roStorySend4.mos.xml'

@pytest.fixture()
def rostorysend5():
    return MOCK_MOS / 'roStorySend5.mos.xml'

@pytest.fixture()
def rostorysend6():
    return MOCK_MOS / 'roStorySend6.mos.xml'

@pytest.fixture()
def roinvalid():
    return MOCK_MOS / 'roInvalidMos.mos.xml'

@pytest.fixture()
def rodelete2():
    return MOCK_MOS / 'roDelete2.mos.xml'

@pytest.fixture()
def story_xml():
    return ElementTree.parse(MOCK_XML / 'story.xml').getroot()

@pytest.fixture()
def story2_xml():
    return ElementTree.parse(MOCK_XML / 'story2.xml').getroot()

@pytest.fixture()
def story3_xml():
    return ElementTree.parse(MOCK_XML / 'story3.xml').getroot()

@pytest.fixture()
def item_mosart_xml():
    return ElementTree.parse(MOCK_XML / 'item_mosart.xml').getroot()

@pytest.fixture()
def item_note_xml():
    return ElementTree.parse(MOCK_XML / 'item_note.xml').getroot()
