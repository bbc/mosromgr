import re
from pathlib import Path


ABSTRACT_CLASSES = {
    'MosFile',
}

OMIT_CLASSES = {
    'Runner',
    'MosContainer',
    'MosRoMgrException',
    'MosRoMgrWarning',
}


def main():
    """
    A simple application for generating a class diagram for mosromgr. Output is
    in a format suitable for feeding to graphviz's dot application.
    """
    my_path = Path(__file__).parent
    path = my_path / '..' / '..' / 'mosromgr'
    path = str(path.resolve())

    m = make_class_map([path], OMIT_CLASSES)
    with open('docs/images/class_hierarchy.dot', 'w') as f:
        f.write(render_map(m, ABSTRACT_CLASSES))


def make_class_map(search_paths, omit):
    """
    Find all Python source files under *search_paths*, extract (via a crude
    regex) all class definitions and return a mapping of class-name to the list
    of base classes.

    All classes listed in *omit* will be excluded from the result, but not
    their descendents (useful for excluding "object" etc.)
    """
    def find_classes():
        class_re = re.compile(
            r'^class\s+(?P<name>\w+)\s*(?:\((?P<bases>.*)\))?:', re.MULTILINE)
        for path in search_paths:
            for py_file in Path(path).rglob('*.py'):
                with py_file.open() as f:
                    for match in class_re.finditer(f.read()):
                        if match.group('name') not in omit:
                            yield match.group('name'), {
                                base.strip()
                                for base in (match.group('bases') or '').split(',')
                                if base.strip() and base.strip() not in omit
                            }
    return {
        name: bases
        for name, bases in find_classes()
    }


def filter_map(class_map, include_roots, exclude_roots):
    """
    Returns *class_map* (which is a mapping such as that returned by
    :func:`make_class_map`), with only those classes which have at least one
    of the *include_roots* in their ancestry, and none of the *exclude_roots*.
    """
    def has_parent(cls, parent):
        return cls == parent or any(
            has_parent(base, parent) for base in class_map.get(cls, ()))

    filtered = {
        name: bases
        for name, bases in class_map.items()
        if (not include_roots or any(has_parent(name, root) for root in include_roots))
        and not any(has_parent(name, root) for root in exclude_roots)
    }
    pure_bases = {
        base for name, bases in filtered.items() for base in bases
    } - set(filtered)
    # Make a second pass to fill in missing links between classes that are
    # only included as bases of other classes
    for base in pure_bases:
        filtered[base] = pure_bases & class_map[base]
    return filtered


def render_map(class_map, abstract):
    """
    Renders *class_map* (which is a mapping such as that returned by
    :func:`make_class_map`) to graphviz's dot language.

    The *abstract* sequence determines which classes will be rendered lighter
    to indicate their abstract nature. All classes with names ending "Mixin"
    will be implicitly rendered in a different style.
    """
    def all_names(class_map):
        for name, bases in class_map.items():
            yield name
            for base in bases:
                yield base

    template = """\
digraph classes {{
    graph [rankdir=RL];
    node [shape=rect, style=filled, fontname=Sans, fontsize=10];
    edge [];

    /* Abstract classes */
    node [color="#9ec6e0", fontcolor="#000000"]

    {abstract_nodes}

    /* Concrete classes */
    node [color="#2980b9", fontcolor="#ffffff"];

    {edges}
}}
"""

    return template.format(
        abstract_nodes='\n    '.join(
            '{name};'.format(name=name)
            for name in sorted(abstract & set(all_names(class_map)))
        ),
        edges='\n    '.join(
            '{name}->{base};'.format(name=name, base=base)
            for name, bases in sorted(class_map.items())
            for base in sorted(bases)
        ),
    )


if __name__ == '__main__':
    main()
