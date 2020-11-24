==============
MOS Collection
==============

.. module:: mosromgr.moscollection

This part of the module provides a wrapper class
:class:`MosCollection` which stores references to specified MOS
files, strings or S3 object keys so the :class:`~mosromgr.mostypes.MosFile`
objects can be recreated when needed rather than kept in memory.

.. note::
    Note that creating a :class:`MosCollection` from strings does not benefit
    from memory efficiency as the strings would still be held in memory.

When the collection is created it retrieves the message IDs and running order
IDs for each MOS object, sorts the objects by message ID then validates whether
they are ready to be merged. If no ``roCreate`` file is found or any of the
objects are from a different running order to the ``roCreate`` file, a
:class:`~exc.InvalidMosCollection` exception will be raised and the
:class:`MosCollection` object will not be created. Optionally, the
``allow_incomplete`` flag can be set to determine whether the object should be
allowed to be created without a ``roDelete`` file. Setting this to ``True``
ensures that incomplete programmes cannot be processed, but ``False`` (the
default) allows partial programmes to be analysed as soon as as each message
arrives.

Once a :class:`MosCollection` object has been created, the
:meth:`MosCollection.merge` method can be used to apply the effects of the other
MOS messages into the :class:`~mostypes.RunningOrder` object. If all MOS
messages from a finished programme are provided, :class:`~mostypes.RunningOrder`
will be a complete representation of the programme as completed.

The :class:`MOSCollection` class is typically imported like so::

    from mosromgr.moscollection import MosCollection

MOS collections are initialised using one of three classmethods. Either from a
list of file paths::

    mos_files = ['roCreate.mos.xml', 'roStorySend.mos.xml', 'roDelete.mos.xml']
    mc = MosCollection.from_files(mos_files)

from a list of strings::

    mos_strings = [roCreate, roStorySend, roDelete]
    mc = MosCollection.from_strings(mos_files)

or (using :func:`~mosromgr.utils.s3.get_mos_files`) from a list of S3 file
keys::

    mos_file_keys = s3.get_mos_files(bucket_name, bucket_prefix)
    mc = MosCollection.from_s3(bucket_name=bucket_name, mos_file_keys=mos_file_keys)

Whichever way the collection was initialised, you can then proceed to merge all
MOS files into the running order::

    mc.merge()

To access the final XML, simply print the
:class:`~mosromgr.moscollection.MosCollection` object or access the :attr:``

    >>> print(mc)
    <mos>
      <mosID>"MOS ID"</mosID>
      <messageID>1234567</messageID>
      ...


MosCollection
=============

.. autoclass:: MosCollection
    :members:
