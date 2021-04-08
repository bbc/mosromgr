# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

import re
from pathlib import Path

from graphviz import Digraph


CLASS_RE = re.compile(
    r'^class\s+(?P<name>\w+)\s*(?:\((?P<base>.*)\))?:',
    re.MULTILINE
)

ABSTRACT_CLASSES = {'MosFile', 'ElementAction'}


class ClassHierarchy:
    def __init__(self, py_file_path):
        self.classes = {
            name: base
            for name, base in self.find_classes(py_file_path)
        }

    def find_classes(self, py_file_path):
        with py_file_path.open() as f:
            for match in CLASS_RE.finditer(f.read()):
                yield (match.group('name'), match.group('base'))

    def create_graph(self, filename):
        graph_attr = {'rankdir': 'RL'}
        node_attr = {
            'shape': 'rect',
            'style': 'filled',
            'fontname': 'Sans',
            'fontsize': '10',
        }
        abstract_node_attr = {
            'color': '#9ec6e0',
            'fontcolor': '#000000',
        }
        concrete_node_attr = {
            'color': '#2980b9',
            'fontcolor': '#ffffff',
        }
        dot = Digraph(format='svg', graph_attr=graph_attr, node_attr=node_attr)
        for cls in self.classes:
            this_node_attr = abstract_node_attr if cls in ABSTRACT_CLASSES else concrete_node_attr
            dot.node(cls, **this_node_attr)
        for subcls, cls in self.classes.items():
            if cls:
                dot.edge(subcls, cls)
        dot.render(filename, format='svg')
        dot.render(filename, format='png')


if __name__ == '__main__':
    here = Path(__file__).parent
    py_file_path = here / '..' / '..' / 'mosromgr' / 'mostypes.py'
    main = ClassHierarchy(py_file_path)
    main.create_graph(here / 'class_hierarchy')
