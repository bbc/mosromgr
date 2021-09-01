# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

HERE = Path(__file__).parent.absolute()
MOCK_MOS = HERE / 'mock_mos'
MOCK_XML = HERE / 'mock_xml'

@pytest.fixture()
def rocreate():
    return MOCK_MOS / 'roCreate.mos.xml'

@pytest.fixture()
def rocreate2():
    return MOCK_MOS / 'roCreate2.mos.xml'

@pytest.fixture()
def rostorysend1():
    return MOCK_MOS / 'roStorySend1.mos.xml'

@pytest.fixture()
def rostorysend2():
    return MOCK_MOS / 'roStorySend2.mos.xml'

@pytest.fixture()
def roelementactionstoryreplace():
    return MOCK_MOS / 'roElementActionStoryReplace.mos.xml'

@pytest.fixture()
def roelementactionitemreplace():
    return MOCK_MOS / 'roElementActionItemReplace.mos.xml'

@pytest.fixture()
def roelementactionstorydelete():
    return MOCK_MOS / 'roElementActionStoryDelete.mos.xml'

@pytest.fixture()
def roelementactionitemdelete():
    return MOCK_MOS / 'roElementActionItemDelete.mos.xml'

@pytest.fixture()
def roelementactionstoryinsert():
    return MOCK_MOS / 'roElementActionStoryInsert.mos.xml'

@pytest.fixture()
def roelementactioniteminsert():
    return MOCK_MOS / 'roElementActionItemInsert.mos.xml'

@pytest.fixture()
def roelementactionstoryswap():
    return MOCK_MOS / 'roElementActionStorySwap.mos.xml'

@pytest.fixture()
def roelementactionitemswap():
    return MOCK_MOS / 'roElementActionItemSwap.mos.xml'

@pytest.fixture()
def roelementactionstorymove():
    return MOCK_MOS / 'roElementActionStoryMove.mos.xml'

@pytest.fixture()
def roelementactionitemmove():
    return MOCK_MOS / 'roElementActionItemMove.mos.xml'

@pytest.fixture()
def rostoryappend():
    return MOCK_MOS / 'roStoryAppend.mos.xml'

@pytest.fixture()
def rostoryreplace():
    return MOCK_MOS / 'roStoryReplace.mos.xml'

@pytest.fixture()
def roitemreplace():
    return MOCK_MOS / 'roItemReplace.mos.xml'

@pytest.fixture()
def rostorydelete():
    return MOCK_MOS / 'roStoryDelete.mos.xml'

@pytest.fixture()
def roitemdelete():
    return MOCK_MOS / 'roItemDelete.mos.xml'

@pytest.fixture()
def rostoryinsert():
    return MOCK_MOS / 'roStoryInsert.mos.xml'

@pytest.fixture()
def rostoryinsert2():
    return MOCK_MOS / 'roStoryInsert2.mos.xml'

@pytest.fixture()
def roiteminsert():
    return MOCK_MOS / 'roItemInsert.mos.xml'

@pytest.fixture()
def rostorymove():
    return MOCK_MOS / 'roStoryMove.mos.xml'

@pytest.fixture()
def roitemmovemultiple():
    return MOCK_MOS / 'roItemMoveMultiple.mos.xml'

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
def ro_all(rocreate, rostorysend1, rostorysend2, roelementactionstoryreplace,
           roelementactionitemreplace, roelementactionstorydelete,
           roelementactionitemdelete, roelementactionstoryinsert,
           roelementactioniteminsert, roelementactionstoryswap,
           roelementactionitemswap, roelementactionstorymove,
           roelementactionitemmove, rometadatareplace, roreadytoair, rodelete):
    return [rocreate, rostorysend1, rostorysend2, roelementactionstoryreplace,
            roelementactionitemreplace, roelementactionstorydelete,
            roelementactionitemdelete, roelementactionstoryinsert,
            roelementactioniteminsert, roelementactionstoryswap,
            roelementactionitemswap, roelementactionstorymove,
            roelementactionitemmove, rometadatareplace, roreadytoair, rodelete]


# roCreate with notes
@pytest.fixture()
def rocreate3():
    return MOCK_MOS / 'roCreate3.mos.xml'

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
    return ET.parse(MOCK_XML / 'story.xml').getroot()

@pytest.fixture()
def item_mosart_xml():
    return ET.parse(MOCK_XML / 'item_mosart.xml').getroot()

@pytest.fixture()
def item_note_xml():
    return ET.parse(MOCK_XML / 'item_note.xml').getroot()
