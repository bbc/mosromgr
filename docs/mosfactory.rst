===========
MOS Factory
===========

.. module:: mosromgr.mosfactory

This part of the module contains a single function,
:func:`~mosromgr.mosfactory.get_mos_object`, that converts an XML MOS message
into a :class:`~mosromgr.mostypes.MosFile` compatible object that matches the
MOS message type. This function reads the XML and uses simple rules to determine
the MOS message type. If the MOS message type cannot be identified then the
function returns :data:`None`, if this happens a warning is triggered but this
is not considered fatal.

The MOS message type is detected by looking for a "fingerprint" in the structure
of the XML. This is a combination of tags and attributes that uniquely
identifies each MOS type. For most of the types this is simply the presence of a
tag matching the type name as the child of the ``<mos>`` tag. For example the
start of a ``roCreate`` MOS message follows this structure:

.. literalinclude:: examples/exampleRoCreate.xml

So we can identify a ``roCreate`` message by looking for the ``<roCreate>`` tag
in the children of ``<mos>``. This pattern can be followed for all MOS types
except ``roElementAction``. Since ``roElementAction`` can perform multiple
functions its structure is more complex. This can be seen here:

.. literalinclude:: examples/exampleRoElementAction.xml

We can identify that this is a ``roElementAction`` using the previous method,
but then we need to work out what type of ``roElementAction`` this is. The first
step is to look at the ``operation`` attribute of the ``roElementAction`` tag,
here it is set to ``INSERT``. Now we need to work out if we are inserting a
story or an item. To do this we use the combination of tags inside the
``<element_target>`` tag. Since we have both a ``<storyID>`` and an ``<itemID>``
we know this is an item insert operation. This pattern is similar, but not
identical for all ``roElementAction`` messages.

If the XML fails to parse then a :class:`~mosromgr.exc.MosInvalidXML` exception
will be raised.

The function is typically imported like so::

    from mosromgr.mosfactory import get_mos_object

get_mos_object
==============

.. autofunction:: mosromgr.mosfactory.get_mos_object

Example usage
-------------

:func:`~mosromgr.mosfactory.get_mos_object` produces a
:class:`~mosromgr.mostypes.RunningOrder` object from a ``roCreate`` file.

From a file::

    >>> ro = get_mos_object('roCreate.mos.xml')
    >>> ro
    <RunningOrder 1000>

From a string::

    >>> with open('roCreate.mos.xml') as f:
    ...     xml = f.read()
    >>> ro = get_mos_object(mos_file_contents=xml)
    >>> ro
    <RunningOrder 1000>
