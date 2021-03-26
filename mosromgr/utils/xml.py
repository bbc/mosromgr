# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

def remove_node(parent, node):
    "Remove *node* from *parent*."
    parent.remove(node)


def replace_node(parent, old_node, new_node, index):
    "Replace *old_node* with *new_node* in *parent* at *index*."
    parent.remove(old_node)
    parent.insert(index, new_node)


def insert_node(parent, node, index):
    "Insert *node* in *parent* at *index*."
    parent.insert(index, node)


def append_node(parent, node):
    "Append *node* to *parent*."
    parent.append(node)


def find_child(parent, child_tag, id=None):
    """
    Find an element with *child_tag* in *parent* and return ``(child, index)``
    or ``(None, None)`` if not found. If *id* is provided, it will be searched
    for, otherwise the first child will be returned.
    """
    for i, child in enumerate(list(parent)):
        if child.tag == child_tag:
            if id is None:
                return (child, i)
            child_id = child.find(f'{child_tag}ID').text
            if child_id == id:
                return (child, i)
            if child_id.split(',')[-1] == id.split(',')[-1]:
                return (child, i)
    return (None, None)
