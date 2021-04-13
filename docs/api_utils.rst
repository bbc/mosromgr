.. mosromgr: Python library for managing MOS running orders
.. Copyright 2021 BBC
.. SPDX-License-Identifier: Apache-2.0

===============
API - Utilities
===============

.. module:: mosromgr.utils

This part of the module provides a collection of generic utilities which are
largely for internal use.

The various utilities are typically imported like so::

    from mosromgr.utils import s3

.. warning::
    This part of the module should not be considered part of the stable API and
    is subject to backwards-incompatible changes.

S3
==

AWS S3 utilities

get_mos_files
-------------

.. autofunction:: mosromgr.utils.s3.get_mos_files

get_file_contents
-----------------

.. autofunction:: mosromgr.utils.s3.get_file_contents

XML
===

XML helper functions

remove_node
-----------

.. autofunction:: mosromgr.utils.xml.remove_node

replace_node
------------

.. autofunction:: mosromgr.utils.xml.replace_node

insert_node
-----------

.. autofunction:: mosromgr.utils.xml.insert_node

find_child
----------

.. autofunction:: mosromgr.utils.xml.find_child
