# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

from functools import total_ordering
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
import logging
import warnings
import copy
import itertools
from pathlib import Path
from typing import Optional, Union, List, Tuple
from collections import OrderedDict
from datetime import datetime

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


@total_ordering
class MosFile:
    """
    Base class for all MOS files
    """
    def __init__(self, xml: Element):
        if type(xml) != Element:
            raise TypeError("MosFile objects should be constructed using from_ classmethods")
        self._xml = xml
        self._base_tag = None

    @classmethod
    def from_file(cls, mos_file_path: Union[Path, str]):
        """
        Construct from a path to a MOS file

        :type mos_file_path:
            Union[pathlib.Path, str]
        :param mos_file_path:
            The MOS file path
        """
        try:
            xml = ElementTree.parse(mos_file_path).getroot()
        except ElementTree.ParseError as e:
            raise MosInvalidXML(e) from e
        if cls in (MosFile, ElementAction):
            return cls._classify(xml)
        return cls(xml)

    @classmethod
    def from_string(cls, mos_xml_string: str):
        """
        Construct from an XML string of a MOS document

        :type mos_xml_string:
            str
        :param mos_xml_string:
            The XML string of the MOS document
        """
        try:
            xml = ElementTree.fromstring(mos_xml_string)
        except ElementTree.ParseError as e:
            raise MosInvalidXML(e) from e
        if cls in (MosFile, ElementAction):
            return cls._classify(xml)
        return cls(xml)

    @classmethod
    def from_s3(cls, bucket_name: str, mos_file_key: str):
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
    def _classify(cls, xml: Element):
        """
        Classify the MOS type and return an instance of the relevant class
        """
        tag_class_map = {
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
        }
        for tag, subcls in tag_class_map.items():
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
        """
        The XML string of the MOS file
        """
        return ElementTree.tostring(self.xml, encoding='unicode')

    def __lt__(self, other) -> bool:
        """
        Sort by :attr:`message_id` i.e. ``ro < ss`` or ``sorted([ro, ss])``
        """
        return self.message_id < other.message_id

    @property
    def base_tag_name(self):
        """
        The base tag (:class:`xml.etree.ElementTree.Element`) within the
        :attr:`xml`, as determined by :attr:`base_tag_name`
        """

    @property
    def xml(self) -> Element:
        """
        The XML element of the MOS file
        """
        return self._xml

    @property
    def base_tag(self) -> Element:
        """
        The base tag within the :attr:`xml`, as determined by
        :attr:`base_tag_name`
        """
        return self.xml.find(self.base_tag_name)

    @property
    def message_id(self) -> int:
        """
        The MOS file's message ID
        """
        return int(self.xml.find('messageID').text)

    @property
    def ro_id(self) -> str:
        """
        The running order ID
        """
        return self.base_tag.find('roID').text

    @property
    def dict(self) -> OrderedDict:
        """
        Convert XML to dictionary using ``xmltodict`` library. Useful for
        testing.
        """
        return xmltodict.parse(str(self))

    @property
    def completed(self) -> bool:
        return False

    def merge(self, other):
        raise NotImplementedError("Merge method not implemented")


class RunningOrder(MosFile):
    """
    A ``RunningOrder`` object is created from a ``roCreate`` MOS file and can be
    constructed using classmethods :meth:`from_file`, :meth:`from_string` or
    :meth:`from_s3`.

    *Specification: Create Running Order*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-32
    """
    def __add__(self, other: MosFile):
        """
        ``RunningOrder`` objects can be merged with other MOS files which
        implement a ``merge`` method by using the ``+`` operator, for example::

            ro = RunningOrder.from_file('roCreate.mos.xml')
            ss = StorySend.from_file('roStorySend.mos.xml')
            ro += ss
        """
        if self.xml.find('mosromgrmeta') is None:
            return other.merge(self)
        raise MosCompletedMergeError("Cannot merge completed MOS file")

    @property
    def base_tag_name(self) -> str:
        """
        The name of the base XML tag for this file type
        """
        return 'roCreate'

    @property
    def ro_slug(self) -> str:
        """
        The running order slug
        """
        return self.base_tag.find('roSlug').text

    @property
    def stories(self) -> List[Story]:
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
    def start_time(self) -> Optional[datetime]:
        """
        Transmission start time (if present in the XML)
        """
        try:
            ro_ed_start = self.base_tag.find('roEdStart').text
        except AttributeError:
            return
        if ro_ed_start is not None:
            return parse(ro_ed_start)

    @property
    def end_time(self) -> Optional[datetime]:
        """
        Transmission end time (if present in the XML)
        """
        try:
            final_story = self.stories[-1]
            return final_story.end_time
        except IndexError:
            return

    @property
    def duration(self) -> Optional[float]:
        """
        Total running order duration in seconds
        """
        try:
            return sum(story.duration for story in self.stories)
        except TypeError:
            return

    @property
    def completed(self) -> bool:
        """
        Whether or not the running order has had a :class:`RunningOrderEnd`
        merged
        """
        return self.xml.find('mosromgrmeta') is not None

    @property
    def script(self) -> List[str]:
        """
        A list of strings found in paragraph tags within the story bodies,
        excluding any empty paragraphs or technical notes in brackets.
        """
        return list(
            itertools.chain.from_iterable(story.script for story in self.stories)
        )

    @property
    def body(self) -> List[Union[Item, str]]:
        """
        A list of elements found in the story bodies. Each item in the list is
        either a string (representing a ``<p>`` tag) or an
        :class:`~mosromgr.moselements.Item` object (representing an ``<item>``
        tag). Unlike :attr:`script`, this does not exclude empty paragraph tags.
        """
        return list(
            itertools.chain.from_iterable(story.body for story in self.stories)
        )

    def _find_story(self, story_id: str) -> Tuple[Element, int]:
        """
        Find the story with *story_id* and return a tuple of (element, index)
        """
        for i, story in enumerate(self.stories):
            if story.id == story_id:
                return (story.xml, i)
        raise ValueError("Story not found")

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("RO:", self.ro_slug)
        for story in self.stories:
            print("STORY:", story.id)


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
    def base_tag_name(self) -> str:
        """
        The name of the base XML tag for this file type
        """
        return 'roStorySend'

    @property
    def story(self) -> Story:
        """
        The :class:`~mosromgr.moselements.Story` object being sent
        """
        story_tag = self._convert_story_send_to_story_tag(self.base_tag)
        return Story(story_tag)

    def _convert_story_send_to_story_tag(self, ss_tag_orig: Element) -> Element:
        """
        Converts ``<roStorySend>`` tag from ``roStorySend`` format to a
        ``<story>`` tag to be merged into the roCreate, i.e:
            ``<roStorySend><storyBody><storyItem>...</storyItem></storyBody></roStorySend>``
            to ``<story><item>...</item></story>``
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

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        try:
            story, story_index = ro._find_story(self.story.id)
        except ValueError:
            msg = f"{self.__class__.__name__} error in {self.message_id} - story not found"
            logger.warning(msg)
            warnings.warn(msg, StoryNotFoundWarning)
            return ro

        remove_node(parent=ro.base_tag, node=story)
        insert_node(parent=ro.base_tag, node=self.story.xml, index=story_index)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("SEND STORY:", self.story.id)


class MetaDataReplace(MosFile):
    """
    A ``MetaDataReplace`` object is created from a ``roMetadataReplace`` MOS
    file and can be constructed using classmethods :meth:`from_file`,
    :meth:`from_string` or :meth:`from_s3`.

    ``MetaDataReplace`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    *Specification: Replace RO metadata without deleting the RO structure*

    *If metadata tags in the roMetadataReplace message already exist in the
    target RO, values within the RO will be replaced by the values in the
    roMetadataReplace message.*

    *If the metadata tags do not already exist in the target RO they will be
    added.*

    *If a mosExternalMetadata block is included in the roMetadataReplace message,
    it will replace an existing mosExternalMetadata block only if the values of
    mosSchema in the two blocks match. Otherwise the mosExternalMetadata block
    will be added to the target RO.*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-34
    """
    @property
    def base_tag_name(self) -> str:
        """
        The name of the base XML tag for this file type
        """
        return 'roMetadataReplace'

    @property
    def ro_slug(self) -> str:
        """
        The running order slug
        """
        return self.base_tag.find('roSlug').text

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        for source in self.base_tag:
            target, target_index = find_child(parent=ro.base_tag, child_tag=source.tag)
            if target is None:
                insert_node(parent=ro.base_tag, node=source, index=len(ro.base_tag))
            else:
                replace_node(parent=ro.base_tag, old_node=target, new_node=source, index=target_index)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("NEW METATDATA:")
        for tag in self.base_tag:
            print(f"  {tag.tag}:", tag.text if tag.text else '')


class StoryAppend(MosFile):
    """
    A ``StoryAppend`` object is created from a ``roStoryAppend`` MOS file and
    can be constructed using classmethods :meth:`from_file`, :meth:`from_string`
    or :meth:`from_s3`.

    ``StoryAppend`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Append Stories to Running Order*

    *The roStoryAppend message appends stories and all of their defined items at
    the end of a running order.*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOS_Protocol_Version_2.8.5_Final.htm#roStoryAppend
    """
    @property
    def base_tag_name(self) -> str:
        """
        The name of the base XML tag for this file type
        """
        return 'roStoryAppend'

    @property
    def stories(self) -> List[Story]:
        """
        A list of :class:`~mosromgr.moselements.Story` objects to be appended
        """
        return [
            Story(story_tag)
            for story_tag in self.base_tag.findall('story')
        ]

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        for story in self.stories:
            append_node(ro.base_tag, story.xml)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        for story in self.stories:
            print("ADD STORY:", story.id)


class StoryDelete(MosFile):
    """
    A ``StoryDelete`` object is created from a ``roStoryDelete`` MOS file and
    can be constructed using classmethods :meth:`from_file`, :meth:`from_string`
    or :meth:`from_s3`.

    ``StoryDelete`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Delete Stories from Running Order*

    *The roStoryDelete message deletes the referenced Stories and all associated
    Items from the Running Order.*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOS_Protocol_Version_2.8.5_Final.htm#roStoryDelete
    """
    @property
    def base_tag_name(self) -> str:
        """
        The name of the base XML tag for this file type
        """
        return 'roStoryDelete'

    @property
    def stories(self) -> List[Story]:
        """
        A list of :class:`~mosromgr.moselements.Story` objects to be deleted
        """
        return [
            Story(self.base_tag, id=story_id.text)
            for story_id in self.base_tag.findall('storyID')
        ]

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        for story in self.stories:
            found_node, found_index = find_child(parent=ro.base_tag, child_tag='story', id=story.id)
            if found_node is not None:
                remove_node(parent=ro.base_tag, node=found_node)
            else:
                msg = f"{self.__class__.__name__} error in {self.message_id} - story not found"
                logger.warning(msg)
                warnings.warn(msg, StoryNotFoundWarning)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        for story in self.stories:
            print("DELETE STORY:", story.id)


class ItemDelete(MosFile):
    """
    An ``ItemDelete`` object is created from a ``roItemDelete`` MOS file and
    can be constructed using classmethods :meth:`from_file`, :meth:`from_string`
    or :meth:`from_s3`.

    ``ItemDelete`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Delete Items in Story*

    *The roItemDelete message deletes one or more items in a story.*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOS_Protocol_Version_2.8.5_Final.htm#roItemDelete
    """
    @property
    def base_tag_name(self) -> str:
        """
        The name of the base XML tag for this file type
        """
        return 'roItemDelete'

    @property
    def story(self) -> Story:
        """
        The :class:`~mosromgr.moselements.Story` object containing the items
        being deleted
        """
        return Story(self.base_tag, unknown_items=True)

    @property
    def items(self) -> List[Item]:
        """
        A list of the :class:`~mosromgr.moselements.Item` objects being deleted
        """
        return [
            Item(self.base_tag, id=item_id.text)
            for item_id in self.base_tag.findall('itemID')
        ]

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=self.story.id)
        if story is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - story not found"
            )
        for item in self.items:
            found_node, found_index = find_child(parent=story, child_tag='item', id=item.id)
            if found_node is None:
                msg = f"{self.__class__.__name__} error in {self.message_id} - item not found"
                logger.warning(msg)
                warnings.warn(msg, ItemNotFoundWarning)
            else:
                remove_node(parent=story, node=found_node)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("IN STORY:", self.story.id)
        for item in self.items:
            print("  DELETE ITEM:", item.id)


class StoryInsert(MosFile):
    """
    A ``StoryInsert`` object is created from a ``roStoryInsert`` MOS file and
    can be constructed using classmethods :meth:`from_file`, :meth:`from_string`
    or :meth:`from_s3`.

    ``StoryInsert`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Insert Stories in Running Order*

    *This message inserts stories and all of their defined items before the
    referenced story in a Running Order.*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOS_Protocol_Version_2.8.5_Final.htm#roStoryInsert
    """
    @property
    def base_tag_name(self) -> str:
        """
        The name of the base XML tag for this file type
        """
        return 'roStoryInsert'

    @property
    def target_story(self) -> Story:
        """
        The :class:`~mosromgr.moselements.Story` object above which the source
        stories are to be inserted
        """
        return Story(self.base_tag, unknown_items=True)

    @property
    def source_stories(self) -> List[Story]:
        """
        A list of :class:`~mosromgr.moselements.Story` objects to be inserted
        """
        return [
            Story(story_tag)
            for story_tag in self.base_tag.findall('story')
        ]

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=self.target_story.id)
        if story_index is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - target story not found"
            )
        ro_story_ids = {story.id for story in ro.stories}
        for i, new_story in enumerate(self.source_stories, start=story_index):
            if new_story.id in ro_story_ids:
                msg = f"{self.__class__.__name__} error in {self.message_id} - story already found in running order"
                logger.warning(msg)
                warnings.warn(msg, DuplicateStoryWarning)
                continue
            insert_node(parent=ro.base_tag, node=new_story.xml, index=i)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("AFTER STORY:", self.target_story.id)
        for story in self.source_stories:
            print("  INSERT STORY:", story.id)


class ItemInsert(MosFile):
    """
    An ``ItemInsert`` object is created from a ``roItemInsert`` MOS file and
    can be constructed using classmethods :meth:`from_file`, :meth:`from_string`
    or :meth:`from_s3`.

    ``ItemInsert`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Insert Items in Story*

    *This message allows one or more items to be inserted before a referenced
    item in a story in the playlist. The first itemID is the ID of the item
    before which to insert the new items. If the first itemID is blank, the
    items are inserted at the end of the story.*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOS_Protocol_Version_2.8.5_Final.htm#roItemInsert
    """
    @property
    def base_tag_name(self) -> str:
        """
        The name of the base XML tag for this file type
        """
        return 'roItemInsert'

    @property
    def story(self) -> Story:
        """
        The :class:`~mosromgr.moselements.Story` object into which the items are
        to be inserted
        """
        return Story(self.base_tag, unknown_items=True)

    @property
    def item(self) -> Item:
        """
        The :class:`~mosromgr.moselements.Item` object above which the items
        are to be inserted
        """
        return Item(self.base_tag)

    @property
    def items(self) -> List[Item]:
        """
        A list of :class:`~mosromgr.moselements.Item` objects to be inserted
        """
        return [
            Item(item)
            for item in self.base_tag.findall('item')
        ]

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=self.story.id)
        if story is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - target story not found"
            )
        if self.item.id is None:
            # move to the end
            item_index = len(story)
        else:
            target_item, item_index = find_child(parent=story, child_tag='item', id=self.item.id)
            if target_item is None:
                raise MosMergeError(
                    f"{self.__class__.__name__} error in {self.message_id} - target item not found"
                )
        for i, item in enumerate(self.items, start=item_index):
            insert_node(parent=story, node=item.xml, index=i)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("IN STORY:", self.story.id)
        for item in self.items:
            print("INSERT ITEM:", item.id)


class StoryMove(MosFile):
    """
    A ``StoryMove`` object is created from a ``roStoryMove`` MOS file and can be
    constructed using classmethods :meth:`from_file`, :meth:`from_string` or
    :meth:`from_s3`.

    ``StoryMove`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Move a story to a new position in the Playlist*

    *This message allows a story to be moved to a new location in a playlist.
    The first storyID is the ID of the story to be moved. The second storyID is
    the ID of the story above which the first story is to be moved.*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOS_Protocol_Version_2.8.5_Final.htm#roStoryMove
    """
    @property
    def base_tag_name(self) -> str:
        """
        The name of the base XML tag for this file type
        """
        return 'roStoryMove'

    @property
    def source_story(self) -> Optional[Story]:
        """
        The :class:`~mosromgr.moselements.Story` object to be moved
        """
        stories = self.base_tag.findall('storyID')
        if len(stories) == 0:
            return
        return Story(self.base_tag, id=stories[0].text, unknown_items=True)

    @property
    def target_story(self) -> Optional[Story]:
        """
        The :class:`~mosromgr.moselements.Story` object above which the source
        story is to be moved
        """
        stories = self.base_tag.findall('storyID')
        if len(stories) < 2:
            return
        return Story(self.base_tag, id=stories[1].text, unknown_items=True)

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        if self.source_story is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - no stories given"
            )
        if self.target_story is None:
            target_story_index = len(ro.base_tag)
        else:
            target_story, target_story_index = find_child(parent=ro.base_tag, child_tag='story', id=self.target_story.id)
            if target_story is None:
                raise MosMergeError(
                    f"{self.__class__.__name__} error in {self.message_id} - target story not found"
                )
        source_story, source_index = find_child(parent=ro.base_tag, child_tag='story', id=self.source_story.id)
        if source_story is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - source story not found"
            )
        remove_node(parent=ro.base_tag, node=source_story)
        insert_node(parent=ro.base_tag, node=source_story, index=target_story_index)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("MOVE STORY:", self.source_story.id)


class ItemMoveMultiple(MosFile):
    """
    An ``ItemMoveMultiple`` object is created from a ``roItemMoveMultiple`` MOS
    file and can be constructed using classmethods :meth:`from_file`,
    :meth:`from_string` or :meth:`from_s3`.

    ``ItemMoveMultiple`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    *Specification: Move one or more Items to a specified position within a
    Story*

    *The roItemMoveMultiple message allows one or more items in a story to be
    moved to a new location in the story. The last itemID is the ID of the item
    before which to insert the new items. All remaining itemIDs identify items
    to insert at that location. The resulting story has all the moved items
    appearing before the reference item in the order specified in the command.
    If the last itemID is blank, the items are moved to the end of the story.*

    *There may be no duplicates in the list of itemIDs. This prevents the move
    from being ambiguous; if two itemIDs are the same, it is unclear where in
    the story the item with that ID must be placed.*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOS_Protocol_Version_2.8.5_Final.htm#roItemMoveMultiple
    """
    @property
    def base_tag_name(self) -> str:
        """
        The name of the base XML tag for this file type
        """
        return 'roItemMoveMultiple'

    @property
    def story(self) -> Story:
        """
        The :class:`~mosromgr.moselements.Story` object containing the items
        being moved
        """
        return Story(self.base_tag, unknown_items=True)

    @property
    def item(self) -> Optional[Item]:
        """
        The :class:`~mosromgr.moselements.Item` object above which the items
        will be moved (if the last itemID tag is not empty)
        """
        target = self.base_tag.findall('itemID')[-1].text
        if target is None:
            return
        return Item(self.base_tag, id=target)

    @property
    def items(self) -> List[Item]:
        """
        A list of :class:`~mosromgr.moselements.Item` objects to be moved
        """
        items = self.base_tag.findall('itemID')[:-1]
        return [
            Item(self.base_tag, id=item.text)
            for item in items
        ]

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        if self.story.id is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - no story given"
            )
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=self.story.id)
        if story is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - story not found"
            )

        if self.item is None:
            target_item_index = len(story)
        else:
            target_item, target_item_index = find_child(parent=story, child_tag='item', id=self.item.id)
            if target_item is None:
                raise MosMergeError(
                    f"{self.__class__.__name__} error in {self.message_id} - target item not found"
                )

        for i, item in enumerate(self.items, start=target_item_index):
            source_item, source_item_index = find_child(parent=story, child_tag='item', id=item.id)
            if source_item_index is None:
                raise MosMergeError(
                    f"{self.__class__.__name__} error in {self.message_id} - source item not found"
                )
            remove_node(parent=story, node=source_item)
            insert_node(parent=story, node=source_item, index=i)

        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("IN STORY:", self.story.id)
        for item in self.items:
            print("  MOVE ITEM:", item.id)


class StoryReplace(MosFile):
    """
    A ``StoryReplace`` object is created from a ``roStoryReplace`` MOS file and
    can be constructed using classmethods :meth:`from_file`, :meth:`from_string`
    or :meth:`from_s3`.

    ``StoryReplace`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Replace a Story with Another in a Running Order*

    *The roStoryReplace message replaces the referenced story with another story
    or stories. This messages also replaces all items associated with the
    original story or stories.*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOS_Protocol_Version_2.8.5_Final.htm#roStoryReplace
    """
    @property
    def base_tag_name(self) -> str:
        """
        The name of the base XML tag for this file type
        """
        return 'roStoryReplace'

    @property
    def story(self) -> Story:
        """
        The :class:`~mosromgr.moselements.Story` object being replaced
        """
        return Story(self.base_tag, unknown_items=True)

    @property
    def stories(self) -> List[Story]:
        """
        A list of replacement :class:`~mosromgr.moselements.Story` objects
        """
        return [
            Story(story_tag)
            for story_tag in self.base_tag.findall('story')
        ]

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=self.story.id)
        if story is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - target story not found"
            )
        if len(self.stories) == 0:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - no stories to insert"
            )
        remove_node(parent=ro.base_tag, node=story)
        for i, new_story in enumerate(self.stories, start=story_index):
            insert_node(parent=ro.base_tag, node=new_story.xml, index=i)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("REPLACE STORY:", self.story.id, "WITH:")
        for story in self.stories:
            print("  STORY:", story.id)


class ItemReplace(MosFile):
    """
    An ``ItemReplace`` object is created from a ``roItemReplace`` MOS file and
    can be constructed using classmethods :meth:`from_file`, :meth:`from_string`
    or :meth:`from_s3`.

    ``ItemReplace`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Replace an Item with one or more Items in a Story*

    *The roItemReplace message replaces the referenced item in a story with one
    or more items.*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOS_Protocol_Version_2.8.5_Final.htm#roItemReplace
    """
    @property
    def base_tag_name(self) -> str:
        """
        The name of the base XML tag for this file type
        """
        return 'roItemReplace'

    @property
    def story(self) -> Story:
        """
        The :class:`~mosromgr.moselements.Story` object containing the item
        being replaced
        """
        return Story(self.base_tag, unknown_items=True)

    @property
    def item(self) -> Item:
        """
        The :class:`~mosromgr.moselements.Item` object being replaced
        """
        return Item(self.base_tag)

    @property
    def items(self) -> List[Item]:
        """
        A list of replacement :class:`~mosromgr.moselements.Item` objects
        """
        return [
            Item(item_tag)
            for item_tag in self.base_tag.findall('item')
        ]

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=self.story.id)
        if story is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - story not found"
            )

        item, item_index = find_child(parent=story, child_tag='item', id=self.item.id)
        if item is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - item not found"
            )

        remove_node(parent=story, node=item)
        for i, item in enumerate(self.items, start=item_index):
            insert_node(parent=story, node=item.xml, index=i)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("IN STORY:", self.story.id)
        print("REPLACE ITEM:", self.item.id, "WITH:")
        for item in self.items:
            print("  ITEM:", item.id)


class ReadyToAir(MosFile):
    """
    A ``ReadyToAir`` object is created from a ``roReadyToAir`` MOS file and can
    be constructed using classmethods :meth:`from_file`, :meth:`from_string` or
    :meth:`from_s3`.

    ``ReadyToAir`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Identify a Running Order as Ready to Air*

    *The roReadyToAir message allows the NCS to signal the MOS that a Running
    Order has been editorially approved ready for air.*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-41
    """
    @property
    def base_tag_name(self) -> str:
        """
        The name of the base XML tag for this file type
        """
        return 'roReadyToAir'

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.

        Currently unimplemented - has no effect on the running order.
        TODO: #18
        """
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("READY TO AIR")


class RunningOrderReplace(RunningOrder):
    """
    An ``RunningOrderReplace`` object is created from a ``roReplace`` MOS file
    and can be constructed using classmethods :meth:`from_file`,
    :meth:`from_string` or :meth:`from_s3`.

    ``RunningOrderReplace`` objects can be merged with a :class:`RunningOrder`
    by using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    *Specification: Replace Running Order*

    *Replaces an existing Running Order definition in the MOS with another one
    sent from the NCS.*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-33
    """
    @property
    def base_tag_name(self) -> str:
        """
        The name of the base XML tag for this file type
        """
        return 'roReplace'

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        rc, rc_index = find_child(parent=ro.xml, child_tag='roCreate')
        rr = copy.deepcopy(self.base_tag)
        rr.tag = 'roCreate'
        remove_node(parent=ro.xml, node=ro.base_tag)
        insert_node(parent=ro.xml, node=rr, index=rc_index)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("REPLACE RO:")
        for tag in self.base_tag:
            if tag.text.strip():
                print("", tag.tag + ":", tag.text.strip())


class RunningOrderEnd(MosFile):
    """
    A ``RunningOrderEnd`` object is created from a ``roDelete`` MOS file and can
    be constructed using classmethods :meth:`from_file`, :meth:`from_string` or
    :meth:`from_s3`.

    ``RunningOrderEnd`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class. Once a ``RunningOrderEnd`` object has been merged into
    a :class:`RunningOrder`, the running order is considered "completed" and no
    further messages can be merged.

    *Specification: Delete Running Order*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-35
    """
    @property
    def base_tag_name(self) -> str:
        """
        The name of the base XML tag for this file type
        """
        return 'roDelete'

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.

        Adds a ``mosromgrmeta`` tag containing the ``roDelete`` tag from the
        ``roDelete`` message to the ``roCreate`` tag in the running order.
        """
        mosromgrmeta = SubElement(ro.xml, 'mosromgrmeta')
        mosromgrmeta.append(self.base_tag)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("RO DELETE:", self.ro_id)


class ElementAction(MosFile):
    """
    Base class for various ``roElementAction`` MOS files.

    *Specification: Performs specific Action on a Running Order*

    https://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @classmethod
    def _classify(cls, xml):
        """
        Classify the MOS type and return an instance of the relevant class
        """
        ea = xml.find('roElementAction')
        operation = ea.attrib['operation']

        # are there any itemID tags in element_target?
        try:
            target_item = len(ea.find('element_target').findall('itemID')) > 0
        except AttributeError:
            target_item = False

        # are there any itemID tags in element_source?
        source_item = len(ea.find('element_source').findall('itemID')) > 0

        # use the combination of operation, target_item and source_item to
        # determine the subclass
        subcls = {
            # (operation, target, item): subcls
            ('REPLACE', False, False): EAStoryReplace,
            ('REPLACE', True, False): EAItemReplace,
            ('DELETE', False, False): EAStoryDelete,
            ('DELETE', False, True): EAItemDelete,
            ('INSERT', False, False): EAStoryInsert,
            ('INSERT', True, False): EAItemInsert,
            ('SWAP', False, False): EAStorySwap,
            ('SWAP', False, True): EAItemSwap,
            ('MOVE', False, False): EAStoryMove,
            ('MOVE', True, True): EAItemMove,
        }[(operation, target_item, source_item)]
        return subcls(xml)

    @property
    def base_tag_name(self) -> str:
        """
        The name of the base XML tag for this file type
        """
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

    *In element_target: A storyID specifying the story to be replaced*

    *In element_source: One or more stories to put in its place*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def story(self) -> Story:
        """
        The :class:`~mosromgr.moselements.Story` object being replaced
        """
        return Story(self.base_tag.find('element_target'), unknown_items=True)

    @property
    def stories(self) -> List[Story]:
        """
        A list of replacement :class:`~mosromgr.moselements.Story` objects
        """
        return [
            Story(story_tag)
            for story_tag in self.base_tag.find('element_source').findall('story')
        ]

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=self.story.id)
        if story is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - story not found"
            )
        remove_node(parent=ro.base_tag, node=story)
        for i, new_story in enumerate(self.stories, start=story_index):
            insert_node(parent=ro.base_tag, node=new_story.xml, index=i)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("REPLACE STORY:", self.story.id, "WITH:")
        for story in self.stories:
            print("  STORY:", story.id)


class EAItemReplace(ElementAction):
    """
    An ``EAItemReplace`` object is created from a ``roElementAction`` MOS file
    containing an item replacement, and can be constructed using classmethods
    :meth:`from_file`, :meth:`from_string` or :meth:`from_s3`.

    ``EAItemReplace`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    *Specification: Replacing an item*

    *In element_target: A storyID and itemID specifying the item to be replaced*

    *In element_source: One or more items to put in its place*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def story(self) -> Story:
        """
        The :class:`~mosromgr.moselements.Story` object containing the item
        being replaced
        """
        return Story(self.base_tag.find('element_target'), unknown_items=True)

    @property
    def item(self) -> Item:
        """
        The :class:`~mosromgr.moselements.Item` object being replaced
        """
        return Item(self.base_tag.find('element_target'))

    @property
    def items(self) -> List[Item]:
        """
        A list of replacement :class:`~mosromgr.moselements.Item` objects
        """
        return [
            Item(item_tag)
            for item_tag in self.base_tag.find('element_source').findall('item')
        ]

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=self.story.id)
        if story is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - story not found"
            )
        item, item_index = find_child(parent=story, child_tag='item', id=self.item.id)
        if item is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - item not found"
            )
        remove_node(parent=story, node=item)
        for i, new_item in enumerate(self.items, start=item_index):
            insert_node(parent=story, node=new_item.xml, index=i)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("IN STORY:", self.story.id)
        print("REPLACE ITEM:", self.item.id, "WITH:")
        for item in self.items:
            print("  ITEM:", item.id)


class EAStoryDelete(ElementAction):
    """
    An ``EAStoryDelete`` object is created from a ``roElementAction`` MOS file
    containing a story deletion, and can be constructed using classmethods
    :meth:`from_file`, :meth:`from_string` or :meth:`from_s3`.

    ``EAStoryDelete`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    *Specification: Deleting stories*

    *In element_target: Not needed, since deletes don't happen relative to
    another story*

    *In element_source: One or more storyIDs specifying the stories to be
    deleted*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def stories(self) -> List[Story]:
        """
        A list of :class:`~mosromgr.moselements.Story` objects to be deleted
        """
        return [
            Story(story_tag)
            for story_tag in self.base_tag.findall('element_source')
        ]

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        for source_story in self.stories:
            story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=source_story.id)
            if story is None:
                msg = f"{self.__class__.__name__} error in {self.message_id} - story not found"
                logger.warning(msg)
                warnings.warn(msg, StoryNotFoundWarning)
            else:
                remove_node(parent=ro.base_tag, node=story)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        for story in self.stories:
            print("DELETE STORY:", story.id)


class EAItemDelete(ElementAction):
    """
    An ``EAItemDelete`` object is created from a ``roElementAction`` MOS file
    containing an item deletion, and can be constructed using classmethods
    :meth:`from_file`, :meth:`from_string` or :meth:`from_s3`.

    ``EAItemDelete`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Deleting items*

    *In element_target: A storyID specifying the story containing the items to
    be deleted*

    *In element_source: One or more itemIDs specifying the items in the story to
    be deleted*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def story(self) -> Story:
        """
        The :class:`~mosromgr.moselements.Story` object containing the items
        being deleted
        """
        return Story(self.base_tag.find('element_target'), unknown_items=True)

    @property
    def items(self) -> List[Item]:
        """
        A list of :class:`~mosromgr.moselements.Item` objects being deleted
        """
        return [
            Item(item_tag)
            for item_tag in self.base_tag.findall('element_source')
        ]

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=self.story.id)
        if story is None:
            msg = f"{self.__class__.__name__} error in {self.message_id} - story not found"
            logger.warning(msg)
            warnings.warn(msg, StoryNotFoundWarning)
            return ro

        for source_item in self.items:
            item, item_index = find_child(parent=story, child_tag='item', id=source_item.id)
            if item is None:
                msg = f"{self.__class__.__name__} error in {self.message_id} - item not found"
                logger.warning(msg)
                warnings.warn(msg, ItemNotFoundWarning)
            else:
                remove_node(parent=story, node=item)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("IN STORY:", self.story.id)
        for item in self.items:
            print("  DELETE ITEM:", item.id)


class EAStoryInsert(ElementAction):
    """
    An ``EAStoryInsert`` object is created from a ``roElementAction`` MOS file
    containing a story insertion, and can be constructed using classmethods
    :meth:`from_file`, :meth:`from_string` or :meth:`from_s3`.

    ``EAStoryInsert`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    *Specification: Inserting stories*

    *In element_target: A storyID specifying the story before which the source
    stories are inserted*

    *In element_source: One or more stories to insert*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def story(self) -> Story:
        """
        The :class:`~mosromgr.moselements.Story` object above which the source
        story will be inserted
        """
        return Story(self.base_tag.find('element_target'), unknown_items=True)

    @property
    def stories(self) -> List[Story]:
        """
        The :class:`~mosromgr.moselements.Story` objects to be inserted
        """
        return [
            Story(story_tag)
            for story_tag in self.base_tag.find('element_source').findall('story')
        ]

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        if self.story.id is None:
            # insert at the end
            story_index = len(ro.base_tag)
        else:
            story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=self.story.id)
            if story is None:
                raise MosMergeError(
                    f"{self.__class__.__name__} error in {self.message_id} - target story not found"
                )
        ro_story_ids = {story.id for story in ro.stories}
        for i, new_story in enumerate(self.stories, start=story_index):
            if new_story.id in ro_story_ids:
                msg = f"{self.__class__.__name__} error in {self.message_id} - story already found in running order"
                logger.warning(msg)
                warnings.warn(msg, DuplicateStoryWarning)
            else:
                insert_node(parent=ro.base_tag, node=new_story.xml, index=i)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("AFTER STORY:", self.story.id)
        for story in self.stories:
            print("  INSERT STORY:", story.id)


class EAItemInsert(ElementAction):
    """
    An ``EAItemInsert`` object is created from a ``roElementAction`` MOS file
    containing an item insertion, and can be constructed using classmethods
    :meth:`from_file`, :meth:`from_string` or :meth:`from_s3`.

    ``EAItemInsert`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Inserting items*

    *In element_target: A storyID and itemID specifying the item before which
    the source items are inserted*

    *In element_source: One or more items to insert*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def story(self) -> Story:
        """
        The :class:`~mosromgr.moselements.Story` object into which the item is
        to be inserted
        """
        return Story(self.base_tag.find('element_target'), unknown_items=True)

    @property
    def item(self) -> Item:
        """
        The :class:`~mosromgr.moselements.Item` object above which the source
        item is to be be inserted
        """
        return Item(self.base_tag.find('element_target'))

    @property
    def items(self) -> List[Item]:
        """
        A list of :class:`~mosromgr.moselements.Item` objects to be inserted
        """
        return [
            Item(item_tag)
            for item_tag in self.base_tag.find('element_source').findall('item')
        ]

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=self.story.id)
        if story is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - story not found"
            )
        if self.item.id is None:
            # move to bottom
            item_index = len(story)
        else:
            item, item_index = find_child(parent=story, child_tag='item', id=self.item.id)
            if item is None:
                raise MosMergeError(
                    f"{self.__class__.__name__} error in {self.message_id} - item not found"
                )
        for i, new_item in enumerate(self.items, start=item_index):
            insert_node(parent=story, node=new_item.xml, index=i)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("IN STORY:", self.story.id)
        print("  BEFORE ITEM:", self.story.id)
        for item in self.items:
            print("    INSERT ITEM:", item.id)


class EAStorySwap(ElementAction):
    """
    An ``EAStorySwap`` object is created from a ``roElementAction`` MOS file
    containing a story swap, and can be constructed using classmethods
    :meth:`from_file`, :meth:`from_string` or :meth:`from_s3`.

    ``EAStorySwap`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Swapping stories*

    *In element_target: An empty storyID tag, or the element_target tag itself
    is absent*

    *In element_source: Exactly two storyIDs specifying the stories to be
    swapped*

    
    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def stories(self) -> Tuple[Story]:
        """
        A tuple of the two :class:`~mosromgr.moselements.Story` objects to be
        swapped
        """
        source = self.base_tag.find('element_source')
        return tuple(
            Story(source, id=story_id.text)
            for story_id in source.findall('storyID')
        )

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        source_story_1, source_story_2 = self.stories
        story1, story1_index = find_child(parent=ro.base_tag, child_tag='story', id=source_story_1.id)
        if story1 is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - story 1 not found"
            )
        story2, story2_index = find_child(parent=ro.base_tag, child_tag='story', id=source_story_2.id)
        if story2 is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - story 2 not found"
            )
        remove_node(parent=ro.base_tag, node=story1)
        remove_node(parent=ro.base_tag, node=story2)
        insert_node(parent=ro.base_tag, node=story2, index=story1_index)
        insert_node(parent=ro.base_tag, node=story1, index=story2_index)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        story1, story2 = self.stories
        print("SWAP STORY:", story1.id)
        print("WITH STORY:", story2.id)


class EAItemSwap(ElementAction):
    """
    An ``EAItemSwap`` object is created from a ``roElementAction`` MOS file
    containing an item swap, and can be constructed using classmethods
    :meth:`from_file`, :meth:`from_string` or :meth:`from_s3`.

    ``EAItemSwap`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Swapping items*

    *In element_target: A storyID specifying the story containing the items to
    be swapped*

    *In element_source: Exactly two itemIDs specifying the items to be swapped*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def story(self) -> Story:
        """
        The :class:`~mosromgr.moselements.Story` object containing the items
        being swapped
        """
        return Story(self.base_tag.find('element_target'), unknown_items=True)

    @property
    def items(self) -> Tuple[Item]:
        """
        A tuple of the two :class:`~mosromgr.moselements.Item` objects to be swapped
        """
        source = self.base_tag.find('element_source')
        return tuple(
            Item(source, id=item_id.text)
            for item_id in source.findall('itemID')
        )

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=self.story.id)
        if story is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - story not found"
            )
        source_item_1, source_item_2 = self.items
        item1, item1_index = find_child(parent=story, child_tag='item', id=source_item_1.id)
        if item1 is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - item 1 not found"
            )
        item2, item2_index = find_child(parent=story, child_tag='item', id=source_item_2.id)
        if item2 is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - item 2 not found"
            )
        remove_node(parent=story, node=item1)
        remove_node(parent=story, node=item2)
        insert_node(parent=story, node=item2, index=item1_index)
        insert_node(parent=story, node=item1, index=item2_index)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("IN STORY:", self.story.id)
        item1, item2 = self.items
        print("  SWAP ITEM:", item1.id)
        print("  WITH ITEM:", item2.id)


class EAStoryMove(ElementAction):
    """
    An ``EAStoryMove`` object is created from a ``roElementAction`` MOS file
    containing a story move, and can be constructed using classmethods
    :meth:`from_file`, :meth:`from_string` or :meth:`from_s3`.

    ``EAStoryMove`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Moving stories*

    *In element_target: A storyID specifying the story before which the source
    stories are moved*

    *In element_source: One or more storyIDs specifying the stories to be moved*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def story(self) -> Story:
        """
        The :class:`~mosromgr.moselements.Story` object above which the other
        stories will be moved
        """
        if self.base_tag.find('element_target') is not None:
            return Story(self.base_tag.find('element_target'), unknown_items=True)

    @property
    def stories(self) -> List[Story]:
        """
        A list of :class:`~mosromgr.moselements.Story` objects being moved
        """
        return [
            Story(story_tag)
            for story_tag in self.base_tag.findall('element_source')
        ]

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        if self.story is None:
            target_story_index = len(ro.base_tag)
        else:
            target_story, target_story_index = find_child(parent=ro.base_tag, child_tag='story', id=self.story.id)
            if target_story is None:
                raise MosMergeError(
                    f"{self.__class__.__name__} error in {self.message_id} - target story not found"
                )

        for source_story in self.stories:
            story, source_index = find_child(parent=ro.base_tag, child_tag='story', id=source_story.id)
            if story is None:
                raise MosMergeError(
                    f"{self.__class__.__name__} error in {self.message_id} - source story not found"
                )
            remove_node(parent=ro.base_tag, node=story)
            insert_node(parent=ro.base_tag, node=story, index=target_story_index)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        for story in self.stories:
            print("MOVE STORY:", story.id)


class EAItemMove(ElementAction):
    """
    An ``EAItemMove`` object is created from a ``roElementAction`` MOS file
    containing an item move, and can be constructed using classmethods
    :meth:`from_file`, :meth:`from_string` or :meth:`from_s3`.

    ``EAItemMove`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    *Specification: Moving items*

    *In element_target: A storyID and itemID specifying the item before which
    the source items are moved*

    *In element_source: One or more itemIDs specifying the items in the story to
    be moved*

    http://mosprotocol.com/wp-content/MOS-Protocol-Documents/MOSProtocolVersion40/index.html#calibre_link-43
    """
    @property
    def story(self) -> Story:
        """
        The :class:`~mosromgr.moselements.Story` object containing the item
        being replaced
        """
        return Story(self.base_tag.find('element_target'), unknown_items=True)

    @property
    def item(self) -> Item:
        """
        The :class:`~mosromgr.moselements.Item` object above which the
        source items will be moved
        """
        return Item(self.base_tag.find('element_target'))

    @property
    def items(self) -> List[Item]:
        "A list of :class:`~mosromgr.moselements.Item` objects to be moved"
        source = self.base_tag.find('element_source')
        return [
            Item(source, id=item.text)
            for item in source.findall('itemID')
        ]

    def merge(self, ro: RunningOrder) -> RunningOrder:
        """
        Merge into the :class:`RunningOrder` object provided.
        """
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=self.story.id)
        if story is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - story not found"
            )
        target_item, target_item_index = find_child(parent=story, child_tag='item', id=self.item.id)
        if target_item is None:
            raise MosMergeError(
                f"{self.__class__.__name__} error in {self.message_id} - target item not found"
            )
        for i, source_item in enumerate(self.items, start=target_item_index):
            item, item_index = find_child(parent=story, child_tag='item', id=source_item.id)
            if item is None:
                raise MosMergeError(
                    f"{self.__class__.__name__} error in {self.message_id} - source item not found"
                )
            remove_node(parent=story, node=item)
            insert_node(parent=story, node=item, index=i)
        return ro

    def inspect(self):
        """
        Print an outline of the key file contents
        """
        print("IN STORY:", self.story.id)
        for item in self.items:
            print("  MOVE ITEM:", item.id)