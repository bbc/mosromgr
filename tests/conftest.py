from pathlib import Path

import pytest

HERE = Path(__file__).parent.absolute()
MOCK_MOS = HERE / 'mock_mos'

@pytest.fixture()
def rocreate():
    return MOCK_MOS / 'roCreate.mos'

@pytest.fixture()
def rocreate2():
    return MOCK_MOS / 'roCreate2.mos'

@pytest.fixture()
def rostorysend1():
    return MOCK_MOS / 'roStorySend1.mos'

@pytest.fixture()
def rostorysend2():
    return MOCK_MOS / 'roStorySend2.mos'

@pytest.fixture()
def roelementactionstoryreplace():
    return MOCK_MOS / 'roElementActionStoryReplace.mos'

@pytest.fixture()
def roelementactionitemreplace():
    return MOCK_MOS / 'roElementActionItemReplace.mos'

@pytest.fixture()
def roelementactionstorydelete():
    return MOCK_MOS / 'roElementActionStoryDelete.mos'

@pytest.fixture()
def roelementactionitemdelete():
    return MOCK_MOS / 'roElementActionItemDelete.mos'

@pytest.fixture()
def roelementactionstoryinsert():
    return MOCK_MOS / 'roElementActionStoryInsert.mos'

@pytest.fixture()
def roelementactioniteminsert():
    return MOCK_MOS / 'roElementActionItemInsert.mos'

@pytest.fixture()
def roelementactionstoryswap():
    return MOCK_MOS / 'roElementActionStorySwap.mos'

@pytest.fixture()
def roelementactionitemswap():
    return MOCK_MOS / 'roElementActionItemSwap.mos'

@pytest.fixture()
def roelementactionstorymove():
    return MOCK_MOS / 'roElementActionStoryMove.mos'

@pytest.fixture()
def roelementactionitemmove():
    return MOCK_MOS / 'roElementActionItemMove.mos'

@pytest.fixture()
def rostoryappend():
    return MOCK_MOS / 'roStoryAppend.mos'

@pytest.fixture()
def rostoryreplace():
    return MOCK_MOS / 'roStoryReplace.mos'

@pytest.fixture()
def roitemreplace():
    return MOCK_MOS / 'roItemReplace.mos'

@pytest.fixture()
def rostorydelete():
    return MOCK_MOS / 'roStoryDelete.mos'

@pytest.fixture()
def roitemdelete():
    return MOCK_MOS / 'roItemDelete.mos'

@pytest.fixture()
def rostoryinsert():
    return MOCK_MOS / 'roStoryInsert.mos'

@pytest.fixture()
def roiteminsert():
    return MOCK_MOS / 'roItemInsert.mos'

@pytest.fixture()
def rostorymove():
    return MOCK_MOS / 'roStoryMove.mos'

@pytest.fixture()
def roitemmovemultiple():
    return MOCK_MOS / 'roItemMoveMultiple.mos'

@pytest.fixture()
def rometadatareplace():
    return MOCK_MOS / 'roMetadataReplace.mos'

@pytest.fixture()
def roreplace():
    return MOCK_MOS / 'roReplace.mos'

@pytest.fixture()
def rodelete():
    return MOCK_MOS / 'roDelete.mos'

@pytest.fixture()
def roreadytoair():
    return MOCK_MOS / 'roReadyToAir.mos'


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
    return MOCK_MOS / 'roCreate3.mos'

# Various invalid MOS files

@pytest.fixture()
def rostorysend3():
    return MOCK_MOS / 'roStorySend3.mos'

@pytest.fixture()
def rostorysend4():
    return MOCK_MOS / 'roStorySend4.mos'

@pytest.fixture()
def roinvalid():
    return MOCK_MOS / 'roInvalidMos.mos'

@pytest.fixture()
def rodelete2():
    return MOCK_MOS / 'roDelete2.mos'
