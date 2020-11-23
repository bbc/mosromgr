import xml.etree.ElementTree as ET
import logging
import warnings
from datetime import datetime
import copy

import xmltodict

from .utils.xml import remove_node, replace_node, insert_node, find_child
from .moselements import Story, Item
from .exc import (
    MosClosedMergeError, MosMergeError, ItemNotFoundWarning,
    StoryNotFoundWarning
)

logger = logging.getLogger('mosromgr.mostypes')
logging.basicConfig(level=logging.INFO)


class MosFile:
    """
    Base class for all MOS files.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
    """
    def __init__(self, mos_file_path=None, *, mos_file_contents=None):
        self._base_tag = None

        if mos_file_path is not None:
            self._xml = ET.parse(mos_file_path).getroot()
        elif mos_file_contents is not None:
            self._xml = ET.fromstring(mos_file_contents)
        else:
            raise TypeError("Must specify mos_file_path or mos_file_contents")

    def __repr__(self):
        if self.xml.find('mosromgrmeta') is None:
            return f'<{self.__class__.__name__} {self.message_id}>'
        else:
            return f'<{self.__class__.__name__} {self.message_id} ended>'

    def __str__(self):
        "The XML string"
        return ET.tostring(self.xml, encoding='unicode')

    def __lt__(self, other):
        "Sort by :attr:`message_id` i.e. ``ro < ss`` or ``sorted([ro, ss])``"
        return self.message_id < other.message_id

    def __gt__(self, other):
        "Sort by :attr:`message_id` i.e. ``ss > ro`` or ``sorted([ro, ss])``"
        return self.message_id > other.message_id

    @property
    def base_tag_name(self):
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

    def to_dict(self):
        """
        Convert XML to dictionary using ``xmltodict`` library. Useful for
        testing.
        """
        return xmltodict.parse(str(self))

    def merge(self, ro):
        raise NotImplementedError("merge method not implemented")


class RunningOrder(MosFile):
    """
    A ``RunningOrder`` object is created from a ``roCreate`` MOS file.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
    """
    def __add__(self, other):
        """
        ``RunningOrder`` objects can be merged with other MOS files which
        implement a ``merge`` method by using the ``+`` operator, for example::

            ro = RunningOrder('roCreate.mos.xml')
            ss = StorySend('roStorySend.mos.xml')
            ro += ss
        """
        if self.xml.find('mosromgrmeta') is None:
            return other.merge(self)
        else:
            raise MosClosedMergeError("Cannot merge closed MOS file")

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
        return [
            Story(story_tag)
            for story_tag in self.base_tag.findall('story')
        ]

    @property
    def tx_time(self):
        "Transmission time (:class:`datetime.datetime`)"
        ro_ed_start = self.base_tag.find('roEdStart').text
        return datetime.strptime(ro_ed_start, '%Y-%m-%dT%H:%M:%S')

    @property
    def duration(self):
        "Total running order duration in seconds (:class:`int`)"
        return sum(story.duration for story in self.stories)


class StorySend(MosFile):
    """
    A ``StorySend`` object is created from a ``roStorySend`` MOS file.

    ``StorySend`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
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
            insert_node(parent=ss_tag, node=child, index=story_body_index)
        remove_node(parent=ss_tag, node=story_body)
        return ss_tag

    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=self.story.id)
        if not story:
            msg = f'{self.__class__.__name__} error in {self.message_id} - story not found'
            logger.warning(msg)
            warnings.warn(msg, StoryNotFoundWarning)
        else:
            new_story = self._convert_story_send_to_story_tag(self.base_tag)
            remove_node(parent=ro.base_tag, node=story)
            insert_node(parent=ro.base_tag, node=new_story, index=story_index)
        return ro


class ElementAction(MosFile):
    """
    Base class for various ``roElementAction`` MOS files.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
    """
    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roElementAction'


class EAStoryReplace(ElementAction):
    """
    An ``EAStoryReplace`` object is created from a ``roElementAction`` MOS file
    containing a story replacement.

    ``EAStoryReplace`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
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
        "Merge into the :class:`RunningOrder` object provided"
        target = self.base_tag.find('element_target')
        source = self.base_tag.find('element_source')
        target_story_id = target.find('storyID').text
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)
        if not story:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story not found'
            )
        new_stories = source.findall('story')
        if not new_stories:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story not found'
            )
        remove_node(parent=ro.base_tag, node=story)
        for new_story in new_stories:
            insert_node(parent=ro.base_tag, node=new_story, index=story_index)
            story_index += 1
        return ro


class EAItemReplace(ElementAction):
    """
    An ``EAItemReplace`` object is created from a ``roElementAction`` MOS file
    containing an item replacement.

    ``EAItemReplace`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
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
    def source_item(self):
        "The replacement :class:`~mosromgr.moselements.Item` object"
        return Item(self.base_tag.find('element_source').find('item'))

    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        target = self.base_tag.find('element_target')
        source = self.base_tag.find('element_source')
        target_story_id = target.find('storyID').text
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)
        if not story:
            msg = f'{self.__class__.__name__} error in {self.message_id} - story not found'
            logger.warning(msg)
            warnings.warn(msg, StoryNotFoundWarning)
            return ro
        target_item_id = target.find('itemID').text
        item, item_index = find_child(parent=story, child_tag='item', id=target_item_id)
        if not item:
            msg = f'{self.__class__.__name__} error in {self.message_id} - item not found'
            logger.warning(msg)
            warnings.warn(msg, ItemNotFoundWarning)
            return ro
        new_items = source.findall('item')
        if not new_items:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - item not found'
            )
        remove_node(parent=story, node=item)
        for new_item in new_items:
            insert_node(parent=story, node=new_item, index=item_index)
            item_index += 1
        return ro


class EAStoryDelete(ElementAction):
    """
    An ``EAStoryDelete`` object is created from a ``roElementAction`` MOS file
    containing a story deletion.

    ``EAStoryDelete`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
    """
    @property
    def story(self):
        "The :class:`~mosromgr.moselements.Story` object to be deleted"
        return Story(self.base_tag.find('element_source'))

    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        target = self.base_tag.find('element_target')
        source = self.base_tag.find('element_source')
        source_story_ids = source.findall('storyID')
        for source_story_id in source_story_ids:
            story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=source_story_id.text)
            if not story:
                msg = f'{self.__class__.__name__} error in {self.message_id} - story not found'
                logger.warning(msg)
                warnings.warn(msg, StoryNotFoundWarning)
            else:
                remove_node(parent=ro.base_tag, node=story)
        return ro


class EAItemDelete(ElementAction):
    """
    An ``EAItemDelete`` object is created from a ``roElementAction`` MOS file
    containing an item deletion.

    ``EAItemDelete`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
    """
    @property
    def target_story(self):
        """
        The :class:`~mosromgr.moselements.Story` object containing the item
        being deleted
        """
        return Story(self.base_tag.find('element_target'), unknown_items=True)

    @property
    def source_item(self):
        "The :class:`~mosromgr.moselements.Item` object being deleted"
        return Item(self.base_tag.find('element_source'))

    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        target = self.base_tag.find('element_target')
        source = self.base_tag.find('element_source')
        target_story_id = target.find('storyID').text
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)
        if not story:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story not found'
            )
        item_ids = source.findall('itemID')
        for item_id in item_ids:
            item, item_index = find_child(parent=story, child_tag='item', id=item_id.text)
            if not item:
                msg = f'{self.__class__.__name__} error in {self.message_id} - item not found'
                logger.warning(msg)
                warnings.warn(msg, ItemNotFoundWarning)
            else:
                remove_node(parent=story, node=item)
        return ro


class EAStoryInsert(ElementAction):
    """
    An ``EAStoryInsert`` object is created from a ``roElementAction`` MOS file
    containing a story insertion.

    ``EAStoryInsert`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
    """
    @property
    def target_story(self):
        """
        The :class:`~mosromgr.moselements.Story` object above which the source
        story will be inserted
        """
        return Story(self.base_tag.find('element_target'), unknown_items=True)

    @property
    def source_story(self):
        "The :class:`~mosromgr.moselements.Story` object to be inserted"
        return Story(self.base_tag.find('element_source').find('story'))

    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        target = self.base_tag.find('element_target')
        source = self.base_tag.find('element_source')
        new_stories = source.findall('story')
        target_story_id = target.find('storyID').text
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)
        if not story:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story not found'
            )
        if not new_stories:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story not found'
            )
        for new_story in new_stories:
            insert_node(parent=ro.base_tag, node=new_story, index=story_index)
            story_index += 1
        return ro


class EAItemInsert(ElementAction):
    """
    An ``EAItemInsert`` object is created from a ``roElementAction`` MOS file
    containing an item insertion.

    ``EAItemInsert`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
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
    def source_item(self):
        "The :class:`~mosromgr.moselements.Item` object to be inserted"
        return Item(self.base_tag.find('element_source').find('item'))

    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        target = self.base_tag.find('element_target')
        source = self.base_tag.find('element_source')
        target_story_id = target.find('storyID').text
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)
        if not story:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story not found'
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
    containing a story swap.

    ``EAStorySwap`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
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
        "Merge into the :class:`RunningOrder` object provided"
        target = self.base_tag.find('element_target')
        source = self.base_tag.find('element_source')
        source_story_ids = source.findall('storyID')
        story1, story1_index = find_child(parent=ro.base_tag, child_tag='story', id=source_story_ids[0].text)
        if not story1:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story 1 not found'
            )
        story2, story2_index = find_child(parent=ro.base_tag, child_tag='story', id=source_story_ids[1].text)
        if not story2:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story 2 not found'
            )
        remove_node(parent=ro.base_tag, node=story1)
        remove_node(parent=ro.base_tag, node=story2)
        insert_node(parent=ro.base_tag, node=story2, index=story1_index)
        insert_node(parent=ro.base_tag, node=story1, index=story2_index)
        return ro


class EAItemSwap(ElementAction):
    """
    An ``EAItemSwap`` object is created from a ``roElementAction`` MOS file
    containing an item swap.

    ``EAItemSwap`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
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
        "Merge into the :class:`RunningOrder` object provided"
        target = self.base_tag.find('element_target')
        source = self.base_tag.find('element_source')
        target_story_id = target.find('storyID').text
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)
        if not story:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story not found'
            )
        source_item_ids = source.findall('itemID')
        item1, item1_index = find_child(parent=story, child_tag='item', id=source_item_ids[0].text)
        if not item1:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - item 1 not found'
            )
        item2, item2_index = find_child(parent=story, child_tag='item', id=source_item_ids[1].text)
        if not item2:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - item 2 not found'
            )
        remove_node(parent=story, node=item1)
        remove_node(parent=story, node=item2)
        insert_node(parent=story, node=item2, index=item1_index)
        insert_node(parent=story, node=item1, index=item2_index)
        return ro


class EAStoryMove(ElementAction):
    """
    An ``EAStoryMove`` object is created from a ``roElementAction`` MOS file
    containing a story move.

    ``EAStoryMove`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
    """
    @property
    def target_story(self):
        "The :class:`~mosromgr.moselements.Story` object being replaced"
        return Story(self.base_tag.find('element_target'), unknown_items=True)

    @property
    def source_story(self):
        "The replacement :class:`~mosromgr.moselements.Story` object"
        return Story(self.base_tag.find('element_source'))

    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        target = self.base_tag.find('element_target')
        source = self.base_tag.find('element_source')
        target_story_id = target.find('storyID').text
        target_story, target_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)
        if not target_story:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - target story not found'
            )

        source_story_ids = source.findall('storyID')
        for source_story_id in source_story_ids:
            source_story, source_index = find_child(parent=ro.base_tag, child_tag='story', id=source_story_id.text)
            if not source_story:
                raise MosMergeError(
                    f'{self.__class__.__name__} error in {self.message_id} - source story not found'
                )
            remove_node(parent=ro.base_tag, node=source_story)
            insert_node(parent=ro.base_tag, node=source_story, index=target_index)
        return ro


class EAItemMove(ElementAction):
    """
    An ``EAItemMove`` object is created from a ``roElementAction`` MOS file
    containing an item move.

    ``EAItemMove`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
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
        """
        The :class:`~mosromgr.moselements.Item` object above which the source
        items will be moved
        """
        return Item(self.base_tag.find('element_target'))

    @property
    def source_item(self):
        "The :class:`~mosromgr.moselements.Item` object to be moved"
        return Item(self.base_tag.find('element_source'))

    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        target = self.base_tag.find('element_target')
        source = self.base_tag.find('element_source')
        target_story_id = target.find('storyID').text
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)
        if not story:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story not found'
            )
        target_item_id = target.find('itemID').text
        target_item, target_item_index = find_child(parent=story, child_tag='item', id=target_item_id)
        if not target_item:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - target item not found'
            )
        source_item_ids = source.findall('itemID')
        for source_item_id in source_item_ids:
            source_item, source_item_index = find_child(parent=story, child_tag='item', id=source_item_id.text)
            if not source_item:
                raise MosMergeError(
                    f'{self.__class__.__name__} error in {self.message_id} - source item not found'
                )
            remove_node(parent=story, node=source_item)
            insert_node(parent=story, node=source_item, index=target_item_index)
        return ro


class MetaDataReplace(MosFile):
    """
    A ``MetaDataReplace`` object is created from a ``roMetadataReplace`` MOS
    file.

    ``MetaDataReplace`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
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
        "Merge into the :class:`RunningOrder` object provided"
        for source in list(self.base_tag):
            target, target_index = find_child(parent=ro.base_tag, child_tag=source.tag)
            if target is None:
                raise MosMergeError(
                    f'{self.__class__.__name__} error in {self.message_id} - {source.tag} not found'
                )
            replace_node(parent=ro.base_tag, old_node=target, new_node=source, index=target_index)
        return ro


class StoryAppend(MosFile):
    """
    A ``StoryAppend`` object is created from a ``roStoryAppend`` MOS file.

    ``StoryAppend`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
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
        "Merge into the :class:`RunningOrder` object provided"
        stories = self.base_tag.findall('story')
        if not stories:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no stories to append'
            )
        for story in stories:
            ro.base_tag.append(story)
        return ro


class StoryDelete(MosFile):
    """
    A ``StoryDelete`` object is created from a ``roStoryDelete`` MOS file.

    ``StoryDelete`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
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
        "Merge into the :class:`RunningOrder` object provided"
        story_ids = self.base_tag.findall('storyID')
        if not story_ids:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no stories to delete'
            )
        for id in story_ids:
            found_node, found_index = find_child(parent=ro.base_tag, child_tag='story', id=id.text)
            if not found_node:
                msg = f'{self.__class__.__name__} error in {self.message_id} - story not found'
                logger.warning(msg)
                warnings.warn(msg, StoryNotFoundWarning)
            else:
                remove_node(parent=ro.base_tag, node=found_node)
        return ro


class ItemDelete(MosFile):
    """
    An ``ItemDelete`` object is created from a ``roItemDelete`` MOS file.

    ``ItemDelete`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
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
        "Merge into the :class:`RunningOrder` object provided"
        story_id = self.base_tag.find('storyID').text
        if not story_id:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no story to delete item from'
            )
        story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=story_id)
        if story is None:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story not found'
            )

        item_ids = self.base_tag.findall('itemID')
        if not item_ids:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no items to delete'
            )
        for id in item_ids:
            found_node, found_index = find_child(parent=story, child_tag='item', id=id.text)
            if found_node is None:
                msg = f'{self.__class__.__name__} error in {self.message_id} - item not found'
                logger.warning(msg)
                warnings.warn(msg, ItemNotFoundWarning)
            else:
                remove_node(parent=story, node=found_node)
        return ro


class StoryInsert(MosFile):
    """
    A ``StoryInsert`` object is created from a ``roStoryInsert`` MOS file.

    ``StoryInsert`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
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
        "Merge into the :class:`RunningOrder` object provided"
        target_id = self.base_tag.find('storyID').text
        if not target_id:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no target storyID'
            )
        target_node, target_index = find_child(parent=ro.base_tag, child_tag='story', id=target_id)
        stories = self.base_tag.findall('story')
        if not stories:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no story to insert'
            )
        for story in stories:
            insert_node(parent=ro.base_tag, node=story, index=target_index)
            target_index += 1
        return ro


class ItemInsert(MosFile):
    """
    An ``ItemInsert`` object is created from a ``roItemInsert`` MOS file.

    ``ItemInsert`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
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
        "Merge into the :class:`RunningOrder` object provided"
        target_story_id = self.base_tag.find('storyID').text
        if not target_story_id:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no target storyID'
            )
        target_story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)
        if not target_story:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no target story not found'
            )
        target_item_id = self.base_tag.find('itemID').text
        if target_item_id:
            target_item, item_index = find_child(parent=target_story, child_tag='item', id=target_item_id)
        else:
            item_index = len(target_story.findall('item)'))
        items = self.base_tag.findall('item')
        if not items:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no item to insert'
            )
        for item in items:
            insert_node(parent=target_story, node=item, index=item_index)
            item_index += 1
        return ro


class StoryMove(MosFile):
    """
    A ``StoryMove`` object is created from a ``roStoryMove`` MOS file.

    ``StoryMove`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
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
        "Merge into the :class:`RunningOrder` object provided"
        story_ids = self.base_tag.findall('storyID')
        if not story_ids:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no storyIDs in MOS message'
            )
        target_id = story_ids[1].text
        target_node, target_index = find_child(parent=ro.base_tag, child_tag='story', id=target_id)
        if not target_node:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - traget storyID not found'
            )
        source_id = story_ids[0].text
        source_node, source_index = find_child(parent=ro.base_tag, child_tag='story', id=source_id)
        if not source_node:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - storyID not found'
            )

        remove_node(parent=ro.base_tag, node=source_node)
        insert_node(parent=ro.base_tag, node=source_node, index=target_index)

        return ro


class ItemMoveMultiple(MosFile):
    """
    An ``ItemMoveMultiple`` object is created from a ``roItemMoveMultiple`` MOS
    file.

    ``ItemMoveMultiple`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
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
        "Merge into the :class:`RunningOrder` object provided"
        target_story_id = self.base_tag.find('storyID').text
        if not target_story_id:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no target storyID'
            )
        target_story, story_index = find_child(parent=ro.base_tag, child_tag='story', id=target_story_id)

        item_ids = self.base_tag.findall('itemID')
        target_item_id = item_ids[-1].text
        target_item_node, target_item_index = find_child(parent=target_story, child_tag='item', id=target_item_id)
        source_item_ids = item_ids[:-1]

        for item_id in source_item_ids:
            source_item_node, source_item_index = find_child(parent=target_story, child_tag='item', id=item_id.text)
            remove_node(parent=target_story, node=source_item_node)
            insert_node(parent=target_story, node=source_item_node, index=target_item_index)
            target_item_index += 1

        return ro


class StoryReplace(MosFile):
    """
    A ``StoryReplace`` object is created from a ``roStoryReplace`` MOS file.

    ``StoryReplace`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
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
        "Merge into the :class:`RunningOrder` object provided"
        target_id = self.base_tag.find('storyID').text
        if not target_id:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no target storyID'
            )
        target_node, target_index = find_child(parent=ro.base_tag, child_tag='story', id=target_id)
        remove_node(parent=ro.base_tag, node=target_node)
        stories = self.base_tag.findall('story')
        if not stories:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no story to insert'
            )
        for story in stories:
            insert_node(parent=ro.base_tag, node=story, index=target_index)
            target_index += 1
        return ro


class ItemReplace(MosFile):
    """
    An ``ItemReplace`` object is created from a ``roItemReplace`` MOS file.

    ``ItemReplace`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
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
    def source_item(self):
        "The replacement :class:`~mosromgr.moselements.Item` object"
        return Item(self.base_tag.find('item'))

    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        story_id = self.base_tag.find('storyID').text
        if not story_id:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no target storyID'
            )
        story_node, story_index = find_child(parent=ro.base_tag, child_tag='story', id=story_id)
        if not story_node:
            msg = f'{self.__class__.__name__} error in {self.message_id} - story not found'
            logger.warning(msg)
            warnings.warn(msg, ItemNotFoundWarning)
            return ro
        item_id = self.base_tag.find('itemID').text
        if not item_id:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no target itemID'
            )
        item_node, item_index = find_child(parent=story_node, child_tag='item', id=item_id)
        remove_node(parent=story_node, node=item_node)
        items = self.base_tag.findall('item')
        for item in items:
            if not item:
                msg = f'{self.__class__.__name__} error in {self.message_id} - item not found'
                logger.warning(msg)
                warnings.warn(msg, ItemNotFoundWarning)
            else:
                insert_node(parent=story_node, node=item, index=item_index)
                item_index += 1
        return ro


class RunningOrderReplace(MosFile):
    """
    An ``RunningOrderReplace`` object is created from a ``roReplace`` MOS file.

    ``RunningOrderReplace`` objects can be merged with a :class:`RunningOrder`
    by using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
    """
    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roReplace'

    @property
    def stories(self):
        """
        A list of :class:`~mosromgr.moselements.Story` objects within the
        replacement running order
        """
        return [
            Story(story_tag)
            for story_tag in self.base_tag.findall('story')
        ]

    @property
    def duration(self):
        return sum(story.duration for story in self.stories)

    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc, rc_index = find_child(parent=ro.xml, child_tag='roCreate')
        rr = copy.deepcopy(self.xml.find('roReplace'))
        rr.tag = 'roCreate'
        remove_node(parent=ro.xml, node=ro.base_tag)
        insert_node(parent=ro.xml, node=rr, index=rc_index)
        return ro


class RunningOrderEnd(MosFile):
    """
    A ``RunningOrderEnd`` object is created from a ``roDelete`` MOS file.

    ``RunningOrderEnd`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents (keyword-only argument)
    """
    @property
    def base_tag_name(self):
        "The name of the base XML tag for this file type (:class:`str`)"
        return 'roDelete'

    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        mosromgrmeta = ET.SubElement(ro.xml, 'mosromgrmeta')
        mosromgrmeta.append(self.base_tag)
        return ro
