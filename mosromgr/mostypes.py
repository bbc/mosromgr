# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

import xml.etree.ElementTree as ET
import logging
import warnings
import copy

import xmltodict
from dateutil.parser import parse

from .utils.xml import remove_node, replace_node, insert_node, find_child, append_node
from .utils import s3
from .moselements import Story, Item
from .exc import (
    MosInvalidXML, UnknownMosFileType, MosCompletedMergeError, MosMergeError,
    ItemNotFoundWarning, StoryNotFoundWarning, DuplicateStoryWarning
)


logger = logging.getLogger('mosromgr.mostypes')
logging.basicConfig(level=logging.INFO)


class MosFile:
    "Base class for all MOS files"
    def __init__(self, xml):
        if type(xml) != ET.Element:
            raise TypeError("MosFile objects should be constructed using from_ classmethods")
        self._xml = xml
        self._base_tag = None

    @classmethod
    def from_file(cls, mos_file_path):
        """
        Construct from a path to a MOS file

        :type mos_file_path:
            str
        :param mos_file_path:
            The MOS file path
        """
        try:
            xml = ET.parse(mos_file_path).getroot()
        except ET.ParseError as e:
            raise MosInvalidXML(e) from e
        if cls == MosFile:
            return cls._classify(xml)
        return cls(xml)

    @classmethod
    def from_string(cls, mos_xml_string):
        """
        Construct from an XML string of a MOS document

        :type mos_xml_string:
            str
        :param mos_xml_string:
            The XML string of the MOS document
        """
        try:
            xml = ET.fromstring(mos_xml_string)
        except ET.ParseError as e:
            raise MosInvalidXML(e) from e
        if cls == MosFile:
            return cls._classify(xml)
        return cls(xml)

    @classmethod
    def from_s3(cls, bucket_name, mos_file_key):
        """
        Construct from a MOS file in an S3 bucket

        :type bucket_name:
            str
        :param bucket_name:
            The name of the S3 bucket

        :type mos_file_key:
            str
        :param mos_file_key:
            A MOS file key within the S3 bucket
        """
        xml = s3.get_file_contents(bucket_name, mos_file_key)
        return cls.from_string(xml)

    @classmethod
    def _classify(cls, xml):
        "Classify the MOS type and return an instance of the relevant class"
        for tag, subcls in TAG_CLASS_MAP.items():
            if xml.find(tag):
                if subcls == ElementAction:
                    return ElementAction._classify(xml)
                return subcls(xml)
        raise UnknownMosFileType("Unable to determine MOS file type")

    def __repr__(self):
        if self.completed:
            return f"<{self.__class__.__name__} {self.message_id} completed>"
        return f"<{self.__class__.__name__} {self.message_id}>"

    def __str__(self):
        "The XML string of the MOS file"
        return ET.tostring(self.xml, encoding='unicode')

    def __lt__(self, other):
        "Sort by :attr:`message_id` i.e. ``ro < ss`` or ``sorted([ro, ss])``"
        return self.message_id < other.message_id

    def __gt__(self, other):
        "Sort by :attr:`message_id` i.e. ``ss > ro`` or ``sorted([ro, ss])``"
        return self.message_id > other.message_id

    @property
    def base_tag_name(self):
        """
        The base tag (:class:`xml.etree.ElementTree.Element`) within the
        :attr:`xml`, as determined by :attr:`base_tag_name`
        """
        return

    @property
    def xml(self):
        """
        The XML element of the MOS file
        (:class:`xml.etree.ElementTree.Element`)
        """
        return self._xml

    @property
    def base_tag(self):
        """
        The base tag (:class:`xml.etree.ElementTree.Element`) within the
        :attr:`xml`, as determined by :attr:`base_tag_name`
        """
        if self._base_tag is None:
            self._base_tag = self.xml.find(self.base_tag_name)
        return self._base_tag

    @property
    def message_id(self):
        "The MOS file's message ID (:class:`int`)"
        return int(self.xml.find('messageID').text)

    @property
    def ro_id(self):
        "The running order ID (:class:`str`)"
        return self.base_tag.find('roID').text

    @property
    def dict(self):
        """
        Convert XML to dictionary using ``xmltodict`` library. Useful for
        testing. (:class:`dict`)
        """
        return xmltodict.parse(str(self))

    @property
    def completed(self):
        return False

    def merge(self, ro):
        raise NotImplementedError("Merge method not implemented")


class RunningOrder(MosFile):
    """
    A ``RunningOrder`` object is created from a ``roCreate`` MOS file and can be
    constructed using classmethods :meth:`from_file`, :meth:`from_string` or
    :meth:`from_s3`.

    *Specification: Create Running Order*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-32
    """
    def __add__(self, other):
        """
        ``RunningOrder`` objects can be merged with other MOS files which
        implement a ``merge`` method by using the ``+`` operator, for example::

            ro = RunningOrder.from_file('roCreate.mos.xml')
            ss = StorySend.from_file('roStorySend.mos.xml')
            ro += ss
        """
        if self.xml.find('mosromgrmeta') is None or isinstance(other, RunningOrderControl):
            return other.merge(self)
        raise MosCompletedMergeError("Cannot merge completed MOS file")

    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roCreate'

    @property
    def ro_slug(self):
        "The running order slug (:class:`str`)"
        return self.base_tag.find('roSlug').text

    @property
    def stories(self):
        """
        A list of :class:`~mosromgr.moselements.Story` objects within the
        running order
        """
        story_tags = list(self.base_tag.findall('story'))

        return [
            Story(story_tag, all_stories=story_tags, prog_start_time=self.start_time)
            for story_tag in story_tags
        ]

    @property
    def start_time(self):
        "Transmission start time (:class:`datetime.datetime`)"
        ro_ed_start = self.base_tag.find('roEdStart').text
        return parse(ro_ed_start)

    @property
    def end_time(self):
        "Transmission end time (:class:`datetime.datetime`)"
        final_story = self.stories[-1]
        return final_story.end_time


    @property
    def duration(self):
        "Total running order duration in seconds (:class:`int`)"
        return sum(story.duration for story in self.stories)

    @property
    def completed(self):
        """
        Whether or not the running order has had a :class:`RunningOrderEnd`
        merged (:class:`bool`)
        """
        return self.xml.find('mosromgrmeta') is not None

    def find_story(self, story_id):
        return [
            (story.xml, i)
            for i, story in enumerate(self.stories)
            if story.id == story_id
        ][0]


class StorySend(MosFile):
    """
    A ``StorySend`` object is created from a ``roStorySend`` MOS file and can be
    constructed using classmethods :meth:`from_file`, :meth:`from_string` or
    :meth:`from_s3`.

    ``StorySend`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Send Story information, including Body of the Story*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-49
    """
    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roStorySend'

    @property
    def story(self):
        "The :class:`~mosromgr.moselements.Story` object being sent"
        story_tag = self._convert_story_send_to_story_tag(self.base_tag)
        return Story(story_tag)

    def _convert_story_send_to_story_tag(self, ss_tag_orig):
        """
        Converts <roStorySend> tag from roStorySend format to a <story> tag to
        be merged into the roCreate, i.e:
            <roStorySend><storyBody><storyItem>...</storyItem></storyBody></roStorySend>
            to <story><item>...</item></story>
        """
        # take a copy to preserve the original
        ss_tag = copy.deepcopy(ss_tag_orig)
        # change <roStorySend> to <story>
        ss_tag.tag = 'story'
        for item in ss_tag.find('storyBody').findall('storyItem'):
            # change <storyItem> to <item>
            item.tag = 'item'
        story_body, story_body_index = find_child(parent=ss_tag, child_tag='storyBody')
        children = list(story_body)
        # move all children of <storyBody> to <story>
        for sb_index, child in enumerate(children, start=story_body_index):
            insert_node(parent=ss_tag, node=child, index=sb_index)
        remove_node(parent=ss_tag, node=story_body)
        return ss_tag

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Replaces the story tag in the running order with the one in the
        ``roStorySend`` message.
        """
        try:
            story, story_index = ro.find_story(self.story.id)
        except IndexError:
            msg = f"{self.__class__.__name__} error in {self.message_id} - story not found"
            logger.warning(msg)
            warnings.warn(msg, StoryNotFoundWarning)
            return ro

        new_story = self._convert_story_send_to_story_tag(self.base_tag)
        remove_node(parent=ro.base_tag, node=story)
        insert_node(parent=ro.base_tag, node=new_story, index=story_index)
        return ro


class MetaDataReplace(MosFile):
    """
    A ``MetaDataReplace`` object is created from a ``roMetadataReplace`` MOS
    file and can be constructed using classmethods :meth:`from_file`,
    :meth:`from_string` or :meth:`from_s3`.

    ``MetaDataReplace`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    *Specification: Replace RO metadata without deleting the RO structure*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-34
    """
    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roMetadataReplace'

    @property
    def ro_slug(self):
        "The running order slug (:class:`str`)"
        return self.base_tag.find('roSlug').text

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Replaces the metadata tags in the running order with the ones in the
        ``MetaDataReplace`` message.
        """
        for source in (tag for tag in list(self.base_tag) if tag.text is not None):
            target, target_index = find_child(parent=ro.base_tag, child_tag=source.tag)
            if target is None:
                raise MosMergeError(
                    f"{self.__class__.__name__} error in {self.message_id} - {source.tag} not found"
                )
            replace_node(parent=ro.base_tag, old_node=target, new_node=source, index=target_index)
        return ro


class StoryAppend(MosFile):
    """
    A ``StoryAppend`` object is created from a ``roStoryAppend`` MOS file and
    can be constructed using classmethods :meth:`from_file`, :meth:`from_string`
    or :meth:`from_s3`.

    ``StoryAppend`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Append Stories to Running Order*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOS_Protocol_Version_2.8.5_Final.htm#roStoryAppend
    """
    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roStoryAppend'

    @property
    def stories(self):
        "A list of :class:`~mosromgr.moselements.Story` objects to be appended"
        return [
            Story(story_tag)
            for story_tag in self.base_tag.findall('story')
        ]

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Adds the story tag in the ``roStoryAppend`` message onto the end of the
        running order.
        """
        stories = self.base_tag.findall('story')
        if not stories:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - no stories to append"
            )
        for story in stories:
            ro.base_tag.append(story)
        return ro


class StoryDelete(MosFile):
    """
    A ``StoryDelete`` object is created from a ``roStoryDelete`` MOS file and
    can be constructed using classmethods :meth:`from_file`, :meth:`from_string`
    or :meth:`from_s3`.

    ``StoryDelete`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Delete Stories from Running Order*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOS_Protocol_Version_2.8.5_Final.htm#roStoryDelete
    """
    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roStoryDelete'

    @property
    def stories(self):
        "A list of :class:`~mosromgr.moselements.Story` objects to be deleted"
        return [
            Story(self.base_tag, id=story_id.text)
            for story_id in self.base_tag.findall('storyID')
        ]

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Removes any story tags from the running order which are included in the
        ``roStoryDelete`` message.
        """
        story_ids = self.base_tag.findall('storyID')
        if not story_ids:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - no stories to delete"
            )
        for id in story_ids:
            found_node, found_index = find_child(parent=ro.base_tag, child_tag='story', id=id.text)
            if not found_node:
                msg = f"{self.__class__.__name__} error in {self.message_id} - story not found"
                logger.warning(msg)
                warnings.warn(msg, StoryNotFoundWarning)
            else:
                remove_node(parent=ro.base_tag, node=found_node)
        return ro


class ItemDelete(MosFile):
    """
    An ``ItemDelete`` object is created from a ``roItemDelete`` MOS file and
    can be constructed using classmethods :meth:`from_file`, :meth:`from_string`
    or :meth:`from_s3`.

    ``ItemDelete`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Delete Items in Story*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOS_Protocol_Version_2.8.5_Final.htm#roItemDelete
    """
    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roItemDelete'

    @property
    def target_story(self):
        """
        The :class:`~mosromgr.moselements.Story` object containing the items
        being replaced
        """
        return Story(self.base_tag, unknown_items=True)

    @property
    def target_items(self):
        "The :class:`~mosromgr.moselements.Item` objects being deleted"
        return {
            Item(self.base_tag, id=item_id.text)
            for item_id in self.base_tag.findall('itemID')
        }

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Deletes any item tags with the IDs specified in the ``roItemDelete``
        message from the running order.
        """
        story_id = self.base_tag.find('storyID').text
        if not story_id:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - no story to delete item from"
            )
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=story_id)
        if story is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - story not found"
            )

        item_ids = self.base_tag.findall('itemID')
        if not item_ids:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - no items to delete"
            )
        for id in item_ids:
            found_node, found_index = find_child(parent=story, child_tag='item', id=id.text)
            if found_node is None:
                msg = f"{self.__class__.__name__} error in {self.message_id} - item not found"
                logger.warning(msg)
                warnings.warn(msg, ItemNotFoundWarning)
            else:
                remove_node(parent=story, node=found_node)
        return ro


class StoryInsert(MosFile):
    """
    A ``StoryInsert`` object is created from a ``roStoryInsert`` MOS file and
    can be constructed using classmethods :meth:`from_file`, :meth:`from_string`
    or :meth:`from_s3`.

    ``StoryInsert`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Insert Stories in Running Order*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOS_Protocol_Version_2.8.5_Final.htm#roStoryInsert
    """
    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roStoryInsert'

    @property
    def target_story(self):
        """
        The :class:`~mosromgr.moselements.Story` object above which the source
        stories are to be inserted
        """
        return Story(self.base_tag, unknown_items=True)

    @property
    def source_stories(self):
        "A list of :class:`~mosromgr.moselements.Story` objects to be inserted"
        return [
            Story(story_tag)
            for story_tag in self.base_tag.findall('story')
        ]

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Inserts the story tags from the ``roStoryInsert`` message into the running
        order.
        """
        target_id = self.base_tag.find('storyID').text
        if not target_id:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - no target storyID"
            )
        target_node, target_index = find_child(parent=ro.base_tag, child_tag='story', id=target_id)
        if not target_index:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - target story not found"
            )
        stories = self.base_tag.findall('story')
        if not stories:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - no story to insert"
            )
        for story in stories:
            insert_node(parent=ro.base_tag, node=story, index=target_index)
            target_index += 1
        return ro


class ItemInsert(MosFile):
    """
    An ``ItemInsert`` object is created from a ``roItemInsert`` MOS file and
    can be constructed using classmethods :meth:`from_file`, :meth:`from_string`
    or :meth:`from_s3`.

    ``ItemInsert`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Insert Items in Story*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOS_Protocol_Version_2.8.5_Final.htm#roItemInsert
    """
    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roItemInsert'

    @property
    def target_story(self):
        """
        The :class:`~mosromgr.moselements.Story` object into which the items are
        to be inserted
        """
        return Story(self.base_tag, unknown_items=True)

    @property
    def target_item(self):
        """
        The :class:`~mosromgr.moselements.Item` object above which the source
        items will be inserted
        """
        return Item(self.base_tag)

    @property
    def source_items(self):
        "A list of :class:`~mosromgr.moselements.Item` objects to be inserted"
        return [
            Item(item)
            for item in self.base_tag.findall('item')
        ]

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Inserts the item tags from the ``roItemInsert`` message into the
        relevant story in the running order.
        """
        target_story_id = self.base_tag.find('storyID').text
        if not target_story_id:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - no target storyID"
            )
        target_story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)
        if not target_story:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - target story not found"
            )
        target_item_id = self.base_tag.find('itemID').text
        item_index = None
        if target_item_id:
            target_item, item_index = find_child(parent=target_story, child_tag='item', id=target_item_id)
        if item_index is None:
            item_index = len(target_story.findall('item'))
        items = self.base_tag.findall('item')
        if not items:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - no item to insert"
            )
        for item in items:
            insert_node(parent=target_story, node=item, index=item_index)
            item_index += 1
        return ro


class StoryMove(MosFile):
    """
    A ``StoryMove`` object is created from a ``roStoryMove`` MOS file and can be
    constructed using classmethods :meth:`from_file`, :meth:`from_string` or
    :meth:`from_s3`.

    ``StoryMove`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Move a story to a new position in the Playlist*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOS_Protocol_Version_2.8.5_Final.htm#roStoryMove
    """
    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roStoryMove'

    @property
    def target_story(self):
        """
        The :class:`~mosromgr.moselements.Story` object above which the source
        story is to be moved
        """
        source, target = self.base_tag.findall('storyID')
        return Story(self.base_tag, id=target.text, unknown_items=True)

    @property
    def source_story(self):
        "The :class:`~mosromgr.moselements.Story` object to be moved"
        source, target = self.base_tag.findall('storyID')
        return Story(self.base_tag, id=source.text)

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Moves the story given in the ``roStoryMove`` message to a new position
        in the running order.
        """
        story_ids = self.base_tag.findall('storyID')
        if not story_ids:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - no storyIDs in MOS message"
            )
        target_id = story_ids[1].text
        target_node, target_index = find_child(parent=ro.base_tag, child_tag='story', id=target_id)
        if not target_node:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - target storyID not found"
            )
        source_id = story_ids[0].text
        source_node, source_index = find_child(parent=ro.base_tag, child_tag='story', id=source_id)
        if not source_node:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - storyID not found"
            )

        remove_node(parent=ro.base_tag, node=source_node)
        insert_node(parent=ro.base_tag, node=source_node, index=target_index)

        return ro


class ItemMoveMultiple(MosFile):
    """
    An ``ItemMoveMultiple`` object is created from a ``roItemMoveMultiple`` MOS
    file and can be constructed using classmethods :meth:`from_file`,
    :meth:`from_string` or :meth:`from_s3`.

    ``ItemMoveMultiple`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    *Specification: Move one or more Items to a specified position within a Story*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOS_Protocol_Version_2.8.5_Final.htm#roItemMoveMultiple
    """
    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roItemMoveMultiple'

    @property
    def target_story(self):
        """
        The :class:`~mosromgr.moselements.Story` object containing the items
        being moved
        """
        return Story(self.base_tag, unknown_items=True)

    @property
    def target_item(self):
        """
        The :class:`~mosromgr.moselements.Item` object above which the source
        items will be moved
        """
        target = self.base_tag.findall('itemID')[-1]
        return Item(self.base_tag, id=target.text)

    @property
    def source_items(self):
        "A list of :class:`~mosromgr.moselements.Item` objects to be moved"
        items = self.base_tag.findall('itemID')[:-1]
        return [
            Item(self.base_tag, id=item.text)
            for item in items
        ]

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Moves item tags in the ``roItemMove`` message to a new position within
        the story.
        """
        target_story_id = self.base_tag.find('storyID').text
        if not target_story_id:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - no target storyID"
            )
        target_story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)
        if target_story is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - target story not found"
            )

        item_ids = self.base_tag.findall('itemID')
        target_item_id = item_ids[-1].text
        target_item_node, target_item_index = find_child(parent=target_story, child_tag='item', id=target_item_id)
        if target_item_node is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - target item not found"
            )
        source_item_ids = [item.text for item in item_ids[:-1]]

        for item_id in source_item_ids:
            source_item_node, source_item_index = find_child(parent=target_story, child_tag='item', id=item_id)
            if source_item_index is None:
                raise MosMergeError(
                    f"{self.__class__.__name__} error in {self.message_id} - source item not found"
                )
            remove_node(parent=target_story, node=source_item_node)
            insert_node(parent=target_story, node=source_item_node, index=target_item_index)
            target_item_index += 1

        return ro


class StoryReplace(MosFile):
    """
    A ``StoryReplace`` object is created from a ``roStoryReplace`` MOS file and
    can be constructed using classmethods :meth:`from_file`, :meth:`from_string`
    or :meth:`from_s3`.

    ``StoryReplace`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Replace a Story with Another in a Running Order*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOS_Protocol_Version_2.8.5_Final.htm#roStoryReplace
    """
    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roStoryReplace'

    @property
    def target_story(self):
        "The :class:`~mosromgr.moselements.Story` object being replaced"
        return Story(self.base_tag, unknown_items=True)

    @property
    def source_story(self):
        "The replacement :class:`~mosromgr.moselements.Story` object"
        return Story(self.base_tag.find('story'))

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Replaces the story tag in the running order with the one in the
        ``roStoryReplace`` message.
        """
        target_id = self.base_tag.find('storyID').text
        if not target_id:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - no target storyID"
            )
        target_node, target_index = find_child(parent=ro.base_tag, child_tag='story', id=target_id)
        if not target_node:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - target story not found"
            )
        remove_node(parent=ro.base_tag, node=target_node)
        stories = self.base_tag.findall('story')
        if not stories:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - no story to insert"
            )
        for story in stories:
            insert_node(parent=ro.base_tag, node=story, index=target_index)
            target_index += 1
        return ro


class ItemReplace(MosFile):
    """
    An ``ItemReplace`` object is created from a ``roItemReplace`` MOS file and
    can be constructed using classmethods :meth:`from_file`, :meth:`from_string`
    or :meth:`from_s3`.

    ``ItemReplace`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Replace an Item with one or more Items in a Story*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOS_Protocol_Version_2.8.5_Final.htm#roItemReplace
    """
    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roItemReplace'

    @property
    def target_story(self):
        """
        The :class:`~mosromgr.moselements.Story` object containing the item
        being replaced
        """
        return Story(self.base_tag, unknown_items=True)

    @property
    def target_item(self):
        "The :class:`~mosromgr.moselements.Item` object being replaced"
        return Item(self.base_tag)

    @property
    def source_items(self):
        "A list of replacement :class:`~mosromgr.moselements.Item` objects"
        return [
            Item(item_tag)
            for item_tag in self.base_tag.findall('item')
        ]

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Replaces the story tag in the running order with the one in the
        ``roStorySend`` message
        """
        story_id = self.base_tag.find('storyID').text
        if not story_id:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - no target storyID"
            )
        story_node, story_index = find_child(parent=ro.base_tag, child_tag='story', id=story_id)
        if story_node is None:
            msg = f"{self.__class__.__name__} error in {self.message_id} - story not found"
            logger.warning(msg)
            warnings.warn(msg, ItemNotFoundWarning)
            return ro
        item_id = self.base_tag.find('itemID').text
        if item_id is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - no target itemID"
            )
        item_node, item_index = find_child(parent=story_node, child_tag='item', id=item_id)
        if item_node is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - item not found"
            )
        remove_node(parent=story_node, node=item_node)
        items = self.base_tag.findall('item')
        for i, item in enumerate(items, start=item_index):
            insert_node(parent=story_node, node=item, index=i)
        return ro


class ReadyToAir(MosFile):
    """
    A ``ReadyToAir`` object is created from a ``roReadyToAir`` MOS file and can
    be constructed using classmethods :meth:`from_file`, :meth:`from_string` or
    :meth:`from_s3`.

    ``ReadyToAir`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Identify a Running Order as Ready to Air*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-41
    """
    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roReadyToAir'

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Currently unimplemented - has no effect on the running order.
        TODO: #18
        """
        return ro


class RunningOrderReplace(RunningOrder):
    """
    An ``RunningOrderReplace`` object is created from a ``roReplace`` MOS file
    and can be constructed using classmethods :meth:`from_file`,
    :meth:`from_string` or :meth:`from_s3`.

    ``RunningOrderReplace`` objects can be merged with a :class:`RunningOrder`
    by using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    *Specification: Replace Running Order*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-33
    """
    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roReplace'

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Replaces the entire ``roCreate`` tag in the running order with the one
        in the ``roReplace`` message.
        """
        rc, rc_index = find_child(parent=ro.xml, child_tag='roCreate')
        if rc is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - roCreate not found"
            )
        rr = copy.deepcopy(self.xml.find('roReplace'))
        rr.tag = 'roCreate'
        remove_node(parent=ro.xml, node=ro.base_tag)
        insert_node(parent=ro.xml, node=rr, index=rc_index)
        return ro


class RunningOrderEnd(MosFile):
    """
    A ``RunningOrderEnd`` object is created from a ``roDelete`` MOS file and can
    be constructed using classmethods :meth:`from_file`, :meth:`from_string` or
    :meth:`from_s3`.

    ``RunningOrderEnd`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class. Once a ``RunningOrderEnd`` object has been merged into
    a :class:`RunningOrder`, the running order is considered "completed" and no
    further messages can be merged (with the exception of
    :class:`RunningOrderControl`).

    *Specification: Delete Running Order*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-35
    """
    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roDelete'

    @property
    def completed(self):
        return False

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Adds a ``mosromgrmeta`` tag containing the ``roDelete`` tag from the
        ``roDelete`` message to the ``roCreate`` tag in the running order.
        """
        mosromgrmeta = ET.SubElement(ro.xml, 'mosromgrmeta')
        mosromgrmeta.append(self.base_tag)
        return ro


class ElementAction(MosFile):
    "Base class for various ``roElementAction`` MOS files"
    @classmethod
    def _classify(cls, xml):
        "Classify the MOS type and return an instance of the relevant class"
        ea = xml.find('roElementAction')
        subcls = EA_CLASS_MAP[ea.attrib['operation']](ea)
        return subcls(xml)

    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roElementAction'


class EAStoryReplace(ElementAction):
    """
    An ``EAStoryReplace`` object is created from a ``roElementAction`` MOS file
    containing a story replacement, and can be constructed using classmethods
    :meth:`from_file`, :meth:`from_string` or :meth:`from_s3`.

    ``EAStoryReplace`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    *Specification: Replacing a story*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def target_story(self):
        "The :class:`~mosromgr.moselements.Story` object being replaced"
        return Story(self.base_tag.find('element_target'), unknown_items=True)

    @property
    def source_story(self):
        "The replacement :class:`~mosromgr.moselements.Story` object"
        return Story(self.base_tag.find('element_source').find('story'))

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Replaces the ``element_target`` story tag in the running order with any
        story tags found in the ``element_source`` in the ``roElementAction``
        message.
        """
        target = self.base_tag.find('element_target')
        source = self.base_tag.find('element_source')
        target_story_id = target.find('storyID').text
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)
        if not story:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - story not found"
            )
        new_stories = source.findall('story')
        if not new_stories:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - story not found"
            )
        remove_node(parent=ro.base_tag, node=story)
        for new_story in new_stories:
            insert_node(parent=ro.base_tag, node=new_story, index=story_index)
            story_index += 1
        return ro


class EAItemReplace(ElementAction):
    """
    An ``EAItemReplace`` object is created from a ``roElementAction`` MOS file
    containing an item replacement, and can be constructed using classmethods
    :meth:`from_file`, :meth:`from_string` or :meth:`from_s3`.

    ``EAItemReplace`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    *Specification: Replacing an item*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def target_story(self):
        """
        The :class:`~mosromgr.moselements.Story` object containing the item
        being replaced
        """
        return Story(self.base_tag.find('element_target'), unknown_items=True)

    @property
    def target_item(self):
        "The :class:`~mosromgr.moselements.Item` object being replaced"
        return Item(self.base_tag.find('element_target'))

    @property
    def source_items(self):
        "A list of replacement :class:`~mosromgr.moselements.Item` objects"
        return [
            Item(item_tag)
            for item_tag in self.base_tag.find('element_source').findall('item')
        ]

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Replaces the target item tag in the target story in the running order
        with any item tags found in the ``element_source`` in the
        ``roElementAction`` message.
        """
        target = self.base_tag.find('element_target')
        source = self.base_tag.find('element_source')
        target_story_id = target.find('storyID').text
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)
        if not story:
            msg = f"{self.__class__.__name__} error in {self.message_id} - story not found"
            logger.warning(msg)
            warnings.warn(msg, StoryNotFoundWarning)
            return ro
        target_item_id = target.find('itemID').text
        item, item_index = find_child(parent=story, child_tag='item', id=target_item_id)
        if not item:
            msg = f"{self.__class__.__name__} error in {self.message_id} - item not found"
            logger.warning(msg)
            warnings.warn(msg, ItemNotFoundWarning)
            return ro
        new_items = source.findall('item')
        if not new_items:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - item not found"
            )
        remove_node(parent=story, node=item)
        for new_item in new_items:
            insert_node(parent=story, node=new_item, index=item_index)
            item_index += 1
        return ro


class EAStoryDelete(ElementAction):
    """
    An ``EAStoryDelete`` object is created from a ``roElementAction`` MOS file
    containing a story deletion, and can be constructed using classmethods
    :meth:`from_file`, :meth:`from_string` or :meth:`from_s3`.

    ``EAStoryDelete`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    *Specification: Deleting stories*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def stories(self):
        "A list of :class:`~mosromgr.moselements.Story` objects to be deleted"
        return [
            Story(story_tag)
            for story_tag in self.base_tag.findall('element_source')
        ]

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Removes any stories specified in ``element_source`` in the
        ``roElementAction`` message from the running order.
        """
        source = self.base_tag.find('element_source')
        source_story_ids = source.findall('storyID')
        for source_story_id in source_story_ids:
            story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=source_story_id.text)
            if not story:
                msg = f"{self.__class__.__name__} error in {self.message_id} - story not found"
                logger.warning(msg)
                warnings.warn(msg, StoryNotFoundWarning)
            else:
                remove_node(parent=ro.base_tag, node=story)
        return ro


class EAItemDelete(ElementAction):
    """
    An ``EAItemDelete`` object is created from a ``roElementAction`` MOS file
    containing an item deletion, and can be constructed using classmethods
    :meth:`from_file`, :meth:`from_string` or :meth:`from_s3`.

    ``EAItemDelete`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Deleting items*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def target_story(self):
        """
        The :class:`~mosromgr.moselements.Story` object containing the items
        being deleted
        """
        return Story(self.base_tag.find('element_target'), unknown_items=True)

    @property
    def source_items(self):
        "A list of :class:`~mosromgr.moselements.Item` objects being deleted"
        return [
            Item(item_tag)
            for item_tag in self.base_tag.findall('element_source')
        ]

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Deletes any items specified in the ``element_target`` in the
        ``roStorySend`` message from the specified story in the running order.
        """
        target = self.base_tag.find('element_target')
        source = self.base_tag.find('element_source')
        target_story_id = target.find('storyID').text
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)
        if not story:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - story not found"
            )
        item_ids = source.findall('itemID')
        for item_id in item_ids:
            item, item_index = find_child(parent=story, child_tag='item', id=item_id.text)
            if not item:
                msg = f"{self.__class__.__name__} error in {self.message_id} - item not found"
                logger.warning(msg)
                warnings.warn(msg, ItemNotFoundWarning)
            else:
                remove_node(parent=story, node=item)
        return ro


class EAStoryInsert(ElementAction):
    """
    An ``EAStoryInsert`` object is created from a ``roElementAction`` MOS file
    containing a story insertion, and can be constructed using classmethods
    :meth:`from_file`, :meth:`from_string` or :meth:`from_s3`.

    ``EAStoryInsert`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    *Specification: Inserting stories*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def target_story(self):
        """
        The :class:`~mosromgr.moselements.Story` object above which the source
        story will be inserted
        """
        return Story(self.base_tag.find('element_target'), unknown_items=True)

    @property
    def source_stories(self):
        "The :class:`~mosromgr.moselements.Story` objects to be inserted"
        return [
            Story(story_tag)
            for story_tag in self.base_tag.find('element_source').findall('story')
        ]

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Inserts any story tags found in the ``element_source`` in the
        ``roElementAction`` message into the running order.
        """
        target = self.base_tag.find('element_target')
        source = self.base_tag.find('element_source')
        new_stories = source.findall('story')
        target_story_id = target.find('storyID').text
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)
        if not story:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - target story not found"
            )
        if not new_stories:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - no source stories found"
            )
        ro_story_ids = {story.id for story in ro.stories}
        for new_story in new_stories:
            new_story_id = new_story.find('storyID').text
            if new_story_id in ro_story_ids:
                msg = f"{self.__class__.__name__} error in {self.message_id} - story already found in running order"
                logger.warning(msg)
                warnings.warn(msg, DuplicateStoryWarning)
                continue
            insert_node(parent=ro.base_tag, node=new_story, index=story_index)
            story_index += 1
        return ro


class EAItemInsert(ElementAction):
    """
    An ``EAItemInsert`` object is created from a ``roElementAction`` MOS file
    containing an item insertion, and can be constructed using classmethods
    :meth:`from_file`, :meth:`from_string` or :meth:`from_s3`.

    ``EAItemInsert`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Inserting items*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def target_story(self):
        """
        The :class:`~mosromgr.moselements.Story` object into which the item is
        to be inserted
        """
        return Story(self.base_tag.find('element_target'), unknown_items=True)

    @property
    def target_item(self):
        """
        The :class:`~mosromgr.moselements.Item` object above which the source
        item is to be be inserted
        """
        return Item(self.base_tag.find('element_target'))

    @property
    def source_items(self):
        "A list of :class:`~mosromgr.moselements.Item` objects to be inserted"
        return [
            Item(item_tag)
            for item_tag in self.base_tag.find('element_source').findall('item')
        ]

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Inserts any item tags found in the ``element_source`` in the
        ``roElementAction`` message into the relevant story in the running
        order.
        """
        target = self.base_tag.find('element_target')
        source = self.base_tag.find('element_source')
        target_story_id = target.find('storyID').text
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)
        if not story:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - story not found"
            )
        target_item_id = target.find('itemID').text
        item_index = None
        if target_item_id:
            item, item_index = find_child(parent=story, child_tag='item', id=target_item_id)
        if not item_index:
            item_index = len(story.findall('item)'))
        new_items = source.findall('item')
        for new_item in new_items:
            insert_node(parent=story, node=new_item, index=item_index)
            item_index += 1
        return ro


class EAStorySwap(ElementAction):
    """
    An ``EAStorySwap`` object is created from a ``roElementAction`` MOS file
    containing a story swap, and can be constructed using classmethods
    :meth:`from_file`, :meth:`from_string` or :meth:`from_s3`.

    ``EAStorySwap`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Swapping stories*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def stories(self):
        """
        A set of the two :class:`~mosromgr.moselements.Story` objects to be
        swapped
        """
        source = self.base_tag.find('element_source')
        return {
            Story(source, id=story_id.text)
            for story_id in source.findall('storyID')
        }

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Swaps the order of the two story tags specified in ``element_source`` in
        the ``roElementAction`` message in the running order.
        """
        source = self.base_tag.find('element_source')
        source_story_ids = source.findall('storyID')
        story1, story1_index = find_child(parent=ro.base_tag, child_tag='story', id=source_story_ids[0].text)
        if not story1:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - story 1 not found"
            )
        story2, story2_index = find_child(parent=ro.base_tag, child_tag='story', id=source_story_ids[1].text)
        if not story2:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - story 2 not found"
            )
        remove_node(parent=ro.base_tag, node=story1)
        remove_node(parent=ro.base_tag, node=story2)
        insert_node(parent=ro.base_tag, node=story2, index=story1_index)
        insert_node(parent=ro.base_tag, node=story1, index=story2_index)
        return ro


class EAItemSwap(ElementAction):
    """
    An ``EAItemSwap`` object is created from a ``roElementAction`` MOS file
    containing an item swap, and can be constructed using classmethods
    :meth:`from_file`, :meth:`from_string` or :meth:`from_s3`.

    ``EAItemSwap`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Swapping items*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def target_story(self):
        """
        The :class:`~mosromgr.moselements.Story` object containing the items
        being swapped
        """
        return Story(self.base_tag.find('element_target'), unknown_items=True)

    @property
    def source_items(self):
        "A set of :class:`~mosromgr.moselements.Item` objects to be swapped"
        source = self.base_tag.find('element_source')
        return {
            Item(source, id=item_id.text)
            for item_id in source.findall('itemID')
        }

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Swaps the order of the two item tags specified in ``element_source`` in
        the ``roElementAction`` message in the relevant story in the running
        order.
        """
        target = self.base_tag.find('element_target')
        source = self.base_tag.find('element_source')
        target_story_id = target.find('storyID').text
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)
        if not story:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - story not found"
            )
        source_item_ids = source.findall('itemID')
        item1, item1_index = find_child(parent=story, child_tag='item', id=source_item_ids[0].text)
        if not item1:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - item 1 not found"
            )
        item2, item2_index = find_child(parent=story, child_tag='item', id=source_item_ids[1].text)
        if not item2:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - item 2 not found"
            )
        remove_node(parent=story, node=item1)
        remove_node(parent=story, node=item2)
        insert_node(parent=story, node=item2, index=item1_index)
        insert_node(parent=story, node=item1, index=item2_index)
        return ro


class EAStoryMove(ElementAction):
    """
    An ``EAStoryMove`` object is created from a ``roElementAction`` MOS file
    containing a story move, and can be constructed using classmethods
    :meth:`from_file`, :meth:`from_string` or :meth:`from_s3`.

    ``EAStoryMove`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Moving stories*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def target_story(self):
        "The :class:`~mosromgr.moselements.Story` object being replaced"
        return Story(self.base_tag.find('element_target'), unknown_items=True)

    @property
    def source_stories(self):
        "A list of replacement :class:`~mosromgr.moselements.Story` objects"
        return [
            Story(story_tag)
            for story_tag in self.base_tag.findall('element_source')
        ]

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Moves story tags in ``element_source`` to the specified location in the
        running order.
        """
        target = self.base_tag.find('element_target')
        source = self.base_tag.find('element_source')
        target_story_id = target.find('storyID').text
        target_story, target_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)
        if not target_story:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - target story not found"
            )

        source_story_ids = source.findall('storyID')
        for source_story_id in source_story_ids:
            source_story, source_index = find_child(parent=ro.base_tag, child_tag='story', id=source_story_id.text)
            if not source_story:
                raise MosMergeError(
                    f"{self.__class__.__name__} error in {self.message_id} - source story not found"
                )
            remove_node(parent=ro.base_tag, node=source_story)
            insert_node(parent=ro.base_tag, node=source_story, index=target_index)
        return ro


class EAItemMove(ElementAction):
    """
    An ``EAItemMove`` object is created from a ``roElementAction`` MOS file
    containing an item move, and can be constructed using classmethods
    :meth:`from_file`, :meth:`from_string` or :meth:`from_s3`.

    ``EAItemMove`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Moving items*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def target_story(self):
        """
        The :class:`~mosromgr.moselements.Story` object containing the item
        being replaced
        """
        return Story(self.base_tag.find('element_target'), unknown_items=True)

    @property
    def target_items(self):
        """
        A list of :class:`~mosromgr.moselements.Item` object above which the
        source items will be moved
        """
        return [
            Item(item_tag)
            for item_tag in self.base_tag.findall('element_target')
        ]

    @property
    def source_item(self):
        "The :class:`~mosromgr.moselements.Item` object to be moved"
        return Item(self.base_tag.find('element_source'))

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Moves item tags in ``element_source`` to the specified location in the
        story in the running order.
        """
        target = self.base_tag.find('element_target')
        source = self.base_tag.find('element_source')
        target_story_id = target.find('storyID').text
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)
        if not story:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - story not found"
            )
        target_item_id = target.find('itemID').text
        target_item, target_item_index = find_child(parent=story, child_tag='item', id=target_item_id)
        if not target_item:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - target item not found"
            )
        source_item_ids = source.findall('itemID')
        for source_item_id in source_item_ids:
            source_item, source_item_index = find_child(parent=story, child_tag='item', id=source_item_id.text)
            if not source_item:
                raise MosMergeError(
                    f"{self.__class__.__name__} error in {self.message_id} - source item not found"
                )
            remove_node(parent=story, node=source_item)
            insert_node(parent=story, node=source_item, index=target_item_index)
        return ro


class RunningOrderControl(MosFile):
    """
    A ``RunningOrderControl`` object is created from a ``roCtrl`` MOS file and
    can be constructed using classmethods :meth:`from_file`, :meth:`from_string`
    or :meth:`from_s3`.

    *Specification: Running Order Control*
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-47

    TODO: generalise this class #20
    """
    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roCtrl'

    @property
    def story(self):
        "The story to which this roCtrl message relates"
        return Story(xml=self.base_tag)

    def merge(self, ro):
        """
        Merge into the :class:`RunningOrder` object provided.

        Replaces the story tag in the running order with the one in the
        ``roStorySend`` message
        """
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=self.story.id)
        if story is None:
            msg = f"{self.__class__.__name__} error in {self.message_id} - story not found"
            logger.warning(msg)
            warnings.warn(msg, StoryNotFoundWarning)
        else:
            ro_story_payload = story.find('mosExternalMetadata').find('mosPayload')
            for new_tag in self.story.xml.find('mosExternalMetadata').find('mosPayload'):
                if new_tag.text:
                    old_tag, old_tag_index = find_child(parent=ro_story_payload, child_tag=new_tag.tag, id=None)
                    if old_tag is None:
                        append_node(parent=ro_story_payload, node=new_tag)
                    else:
                        replace_node(parent=ro_story_payload, old_node=old_tag, new_node=new_tag, index=old_tag_index)
        return ro


TAG_CLASS_MAP = {
    'roCreate': RunningOrder,
    'roStorySend': StorySend,
    'roStoryAppend': StoryAppend,
    'roStoryDelete': StoryDelete,
    'roStoryInsert': StoryInsert,
    'roStoryMove': StoryMove,
    'roStoryReplace': StoryReplace,
    'roItemDelete': ItemDelete,
    'roItemInsert': ItemInsert,
    'roItemMoveMultiple': ItemMoveMultiple,
    'roItemReplace': ItemReplace,
    'roReplace': RunningOrderReplace,
    'roMetadataReplace': MetaDataReplace,
    'roReadyToAir': ReadyToAir,
    'roDelete': RunningOrderEnd,
    'roElementAction': ElementAction,
    'roCtrl': RunningOrderControl,
}

EA_CLASS_MAP = {
    'REPLACE': lambda ea: EAStoryReplace if ea.find('element_target').find('itemID') is None else EAItemReplace,
    'DELETE': lambda ea: EAStoryDelete if ea.find('element_target') is None else EAItemDelete,
    'INSERT': lambda ea: EAStoryInsert if ea.find('element_target').find('itemID') is None else EAItemInsert,
    'SWAP': lambda ea: EAStorySwap if ea.find('element_target') is None else EAItemSwap,
    'MOVE': lambda ea: EAStoryMove if ea.find('element_target').find('itemID') is None else EAItemMove,
}
