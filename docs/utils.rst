=========
Utilities
=========

.. module:: mosromgr.utils

.. currentmodule:: mosromgr

The various utilities are typically imported like so::

    from mosromgr.utils import s3

or::

    from mosromgr.utils.sns import SNS

S3
==

AWS S3 utilities

get_mos_files
-------------

.. autofunction:: mosromgr.utils.s3.get_mos_files

get_file_contents
-----------------

.. autofunction:: mosromgr.utils.s3.get_file_contents

SNS
===

.. autoclass:: mosromgr.utils.sns.SNS
    :members: send_sns_notification

.. autoattribute:: mosromgr.utils.sns.SNS.INFOLVL
.. autoattribute:: mosromgr.utils.sns.SNS.DEBUGLVL
.. autoattribute:: mosromgr.utils.sns.SNS.WARNLVL
.. autoattribute:: mosromgr.utils.sns.SNS.ERRORLVL

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
