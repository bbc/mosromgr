# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

from mosromgr.utils.xml import *
import xml.etree.ElementTree as ET


TESTXMLSTRINGBASE = """
<xml>
    <top>
        <topID>ID1</topID>
        <child>child 1 text</child>
        <child>child 2 text</child>
    </top>
    <top>
        <topID>ID2</topID>
        <child>child 3 text</child>
        <child>child 4 text</child>
    </top>
    <top>
        <topID>ID3</topID>
        <child>child 5 text</child>
        <child>child 6 text</child>
    </top>
    <top>
        <topID>ID4</topID>
        <child>child 7 text</child>
        <child>child 8 text</child>
    </top>
</xml>
"""

TESTXMLSTRINGNEW = """
<xml>
    <top>
        <topID>ID5</topID>
        <child>child 8 text</child>
        <child>child 9 text</child>
    </top>
</xml>
"""

def test_remove_node():
    """
    GIVEN: A node and a parent to remove it from
    EXPECT: The parent without the given node
    """

    root = ET.fromstring(TESTXMLSTRINGBASE)
    assert len(root.findall('top')) == 4

    node_to_remove = root.findall('top')[0]
    remove_node(root, node_to_remove)
    assert len(root.findall('top')) == 3
    assert root.findall('top')[0].find('topID').text == "ID2"
    assert root.findall('top')[1].find('topID').text == "ID3"

def test_replace_node():
    """
    GIVEN: A parent, a node that is a child of that parent and its index, plus a new node
    EXPECT: The parent with the child node replaced by the new node
    """
    root = ET.fromstring(TESTXMLSTRINGBASE)
    node_to_replace = root.findall('top')[0]
    index = 0
    new_root = ET.fromstring(TESTXMLSTRINGNEW)
    new_node = new_root.find('top')
    assert len(root.findall('top')) == 4
    assert root.findall('top')[0].find('topID').text == "ID1"
    assert root.findall('top')[1].find('topID').text == "ID2"
    assert root.findall('top')[2].find('topID').text == "ID3"
    assert root.findall('top')[3].find('topID').text == "ID4"

    replace_node(root, node_to_replace, new_node, index)
    assert len(root.findall('top')) == 4
    assert root.findall('top')[0].find('topID').text == "ID5"
    assert root.findall('top')[1].find('topID').text == "ID2"
    assert root.findall('top')[2].find('topID').text == "ID3"

def test_insert_node():
    """
    GIVEN: A parent, a new node, and an index to insert at
    EXPECT: The parent with the new node inserted at the correct place
    """
    root = ET.fromstring(TESTXMLSTRINGBASE)
    new_root = ET.fromstring(TESTXMLSTRINGNEW)
    node_to_insert = new_root.find('top')
    assert len(root.findall('top')) == 4
    assert root.findall('top')[0].find('topID').text == "ID1"
    assert root.findall('top')[1].find('topID').text == "ID2"
    assert root.findall('top')[2].find('topID').text == "ID3"

    insert_node(root, node_to_insert, 0)
    assert len(root.findall('top')) == 5
    assert root.findall('top')[0].find('topID').text == "ID5"
    assert root.findall('top')[1].find('topID').text == "ID1"
    assert root.findall('top')[2].find('topID').text == "ID2"
    assert root.findall('top')[3].find('topID').text == "ID3"

def test_append_node():
    """
    GIVEN: A parent and a new node to append
    EXPECT: The new node added to the end of the parent
    """
    root = ET.fromstring(TESTXMLSTRINGBASE)
    new_root = ET.fromstring(TESTXMLSTRINGNEW)
    node_to_append = new_root.find('top')
    assert len(root.findall('top')) == 4
    assert root.findall('top')[0].find('topID').text == "ID1"
    assert root.findall('top')[-2].find('topID').text == "ID3"
    assert root.findall('top')[-1].find('topID').text == "ID4"

    append_node(root, node_to_append)
    assert len(root.findall('top')) == 5
    assert root.findall('top')[0].find('topID').text == "ID1"
    assert root.findall('top')[-2].find('topID').text == "ID4"
    assert root.findall('top')[-1].find('topID').text == "ID5"

def test_find_child_with_id():
    """
    GIVEN: A parent, a child to search for, and an id for the child
    EXPECT: The child node and its index within the parent
    """
    root = ET.fromstring(TESTXMLSTRINGBASE)
    child, child_index = find_child(root, 'top', 'ID1')
    assert child_index == 0
    assert child.find('topID').text == 'ID1'

def test_find_child_with_partial_id():
    """
    GIVEN: A parent and a child to search for
    EXPECT: The first instance of the child node and its index within the parent
    """
    root = ET.fromstring(TESTXMLSTRINGBASE)
    child, child_index = find_child(root, 'top', 'ID4')
    assert child_index == 3
    assert child.find('topID').text == 'ID4'

def test_find_child_without_id():
    """
    GIVEN: A parent and a child to search for
    EXPECT: The first instance of the child node and its index within the parent
    """
    root = ET.fromstring(TESTXMLSTRINGBASE)
    child, child_index = find_child(root, 'top')
    assert child_index == 0
    assert child.find('topID').text == 'ID1'

def test_find_child_no_match():
    """
    GIVEN: A parent and a node that is not a child of parent
    EXPECT: A None object
    """
    root = ET.fromstring(TESTXMLSTRINGBASE)
    child = find_child(root, 'notAChild')
    assert child == (None, None)
