# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

from typing import Optional, Tuple
from xml.etree.ElementTree import Element


def remove_node(parent: Element, node: Element):
    """
    Remove *node* from *parent*.
    """
    parent.remove(node)


def replace_node(parent: Element, old_node: Element, new_node: Element, index: int):
    """
    Replace *old_node* with *new_node* in *parent* at *index*.
    """
    parent.remove(old_node)
    parent.insert(index, new_node)


def insert_node(parent: Element, node: Element, index: int):
    """
    Insert *node* in *parent* at *index*.
    """
    parent.insert(index, node)


def append_node(parent, node):
    """
    Append *node* to *parent*.
    """
    parent.append(node)


def find_child(
        parent: Element,
        child_tag: str,
        id: Optional[str] = None
    ) -> Tuple[Optional[Element], Optional[int]]:
    """
    Find an element with *child_tag* in *parent* and return ``(child, index)``
    or ``(None, None)`` if not found. If *id* is provided, it will be searched
    for, otherwise the first child will be returned.
    """
    for i, child in enumerate(parent):
        if child.tag == child_tag:
            if id is None:
                return (child, i)
            child_id = child.find(f'{child_tag}ID').text
            if child_id == id:
                return (child, i)
    return (None, None)
