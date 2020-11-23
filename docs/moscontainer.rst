=============
MOS Container
=============

.. module:: mosromgr.moscontainer

This part of the module provides a wrapper class
:class:`~moscontainer.MosContainer` which stores paths to specified MOS objects
in the given directory or S3 bucket. The wrapper can also access the files using
the :func:`~mosfactory.get_mos_object` function.

When the wrapper is created it retrieves the message IDs and RO IDs for each MOS
object, sorts the objects by message ID then validates whether they are ready to
be merged. If no ``roCreate`` file is found or any of the objects are from a
different running order to the ``roCreate`` file, the
:class:`~exc.MosContainerBadInit` exception will be raised and the
:class:`~moscontainer.MosContainer` object will not be created.

Once a :class:`~moscontainer.MosContainer` object has been created, the
:meth:`~moscontainer.MosContainer.merge` method can be used to apply the effects
of the other MOS messages in the bucket/directory to the
:class:`~mostypes.RunningOrder` object. If all MOS messages from a finished
programme are given in ``mos_file_paths``/``mos_file_keys``,
:class:`~mostypes.RunningOrder` will be a complete representation of the
programme as it was completed.

The MOS container class is typically imported like so::

    from mosromgr.moscontainer import MosContainer

MosContainer
============
.. autoclass:: MosContainer
    :members:

Example usage
-------------

Create a :class:`~mosromgr.moscontainer.MosContainer` from a list of file
paths::

    >>> mos_files = ['roCreate.mos.xml', 'roStorySend.mos.xml', 'roDelete.mos.xml']
    >>> mc = MosContainer(mos_files)
    >>> mc
    <MosContainer RO SLUG>

Or (using :func:`~mosromgr.utils.s3.get_mos_files`) from a list of S3 file keys::

    >>> mos_file_keys = s3.get_mos_files(bucket_name, bucket_prefix)
    >>> mc = MosContainer(bucket_name=bucket_name, mos_file_keys=mos_file_keys)
    >>> mc
    <MosContainer RO SLUG>

Merge all MOS files into the running order::

    >>> mc = MosContainer(mos_files)
    >>> mc.merge()

To access the final XML, simply print the
:class:`~mosromgr.moscontainer.MosContainer` object::

    >>> print(mc)
    <mos>
      <mosID>"MOS ID"</mosID>
      <messageID>1234567</messageID>
      ...
