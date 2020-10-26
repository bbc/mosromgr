import xml.etree.ElementTree as ET
import logging
import warnings
from datetime import datetime

try:
    import xmltodict
except ImportError:
    xmltodict = None

from .utils.xml import remove_node, replace_node, insert_node, find_child
from .exc import MosClosedMergeError, MosMergeError, ItemNotFoundWarning, StoryNotFoundWarning

logger = logging.getLogger('mos_types')
logging.basicConfig(level=logging.INFO)


class MosFile:
    """
    Base class for all MOS files.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents
    """
    def __init__(self, mos_file_path=None, mos_file_contents=None):
        self._notes = None

        if mos_file_path is not None:
            self.xml = ET.parse(mos_file_path)
            self.mos = self.xml.getroot()
        elif mos_file_contents is not None:
            self.mos = ET.fromstring(mos_file_contents)
        else:
            raise TypeError('Must specify mos_file_path or mos_file_contents')

    def __repr__(self):
        if self.mos.find('mosromgrmeta') is None:
            return f'<{self.__class__.__name__} {self.message_id}>'
        else:
            return f'<{self.__class__.__name__} {self.message_id} ended>'

    def __str__(self):
        return ET.tostring(self.mos, encoding="unicode")

    def __lt__(self, other):
        return self.message_id < other.message_id

    def __gt__(self, other):
        return self.message_id > other.message_id

    @property
    def message_id(self):
        return int(self.mos.find('messageID').text)

    @property
    def ro_id(self):
        tag = class_tag_map[self.__class__.__name__]
        return self.mos.find(tag).find('roID').text

    @property
    def notes(self):
        # This property assumes all notes contain an element called *studioCommand*
        # with type *note*. It also assumes that this element always appears at
        # the same position within a story element. From quick testing these
        # assumptions seem safe.

        if self._notes is None:
            self._notes = []
            for story in self.xml.findall(".//studioCommand[@type='note']/../../../.."):
                for item in story.findall(".//studioCommand[@type='note']/../../.."):
                    self._notes.append({
                        'item_id': item.find('itemID').text,
                        'story_slug': story.find('storySlug').text,
                        'text': item.find(".//studioCommand[@type='note']/text").text,
                    })
        return self._notes

    def to_dict(self):
        "Convert XML to dictionary using ``xmltodict`` library. Useful for testing."
        if xmltodict is None:
            raise RuntimeError('to_dict requires package xmltodict')
        xml_string = ET.tostring(self.mos)
        return xmltodict.parse(xml_string)

    def merge(self, ro):
        raise NotImplementedError('merge method not implemented')


class RunningOrder(MosFile):
    """
    A ``RunningOrder`` object is created from a ``roCreate`` MOS file.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents

    ``RunningOrder`` objects can be merged with other MOS files which implement
    a ``merge`` method by using the ``+`` operator, for example::

        ro = RunningOrder('roCreate.mos.xml')
        ss = StorySend('roStorySend.mos.xml')
        ro += ss
    """
    def __init__(self, mos_file_path=None, mos_file_contents=None):
        super().__init__(mos_file_path, mos_file_contents)
        self.slug = self.mos.find('roCreate').find('roSlug').text

    def __add__(self, other):
        if self.mos.find('mosromgrmeta') is None:
            return other.merge(self)
        else:
            raise MosClosedMergeError('Cannot merge closed MOS file')

    @property
    def tx_time(self):
        ro_ed_start = self.mos.find("roCreate").find("roEdStart").text
        tx_time = datetime.strptime(ro_ed_start, '%Y-%m-%dT%H:%M:%S')
        return int(tx_time.timestamp())


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
        XML string of MOS file contents
    """
    def __init__(self, mos_file_path=None, mos_file_contents=None):
        super().__init__(mos_file_path, mos_file_contents)
        self.mos.find('roStorySend').tag = 'story'
        story = self.mos.find('story')
        for item in story.find('storyBody').findall('storyItem'):
            item.tag = 'item'
        sb, sb_index = find_child(parent=story, child_tag='storyBody')
        children = list(sb)
        for child in children:
            insert_node(parent=story, node=child, index=sb_index)
            sb_index += 1
        remove_node(parent=story, node=sb)
        self.id = self.mos.find('story').find('storyID').text

    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        story, story_index = find_child(parent=rc, child_tag='story', id=self.id)
        if not story:
            msg = f'{self.__class__.__name__} error in {self.message_id} - story not found'
            logger.warning(msg)
            warnings.warn(msg, StoryNotFoundWarning)
        else:
            new_story = self.mos.find('story')
            remove_node(parent=rc, node=story)
            insert_node(parent=rc, node=new_story, index=story_index)
        return ro


class ElementAction(MosFile):
    """
    Base class for various ``roElementAction`` MOS files.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents
    """
    def __init__(self, mos_file_path=None, mos_file_contents=None):
        super().__init__(mos_file_path, mos_file_contents)
        self.target = self.mos.find('roElementAction').find('element_target')
        self.source = self.mos.find('roElementAction').find('element_source')


class EAReplaceStory(ElementAction):
    """
    An ``EAReplaceStory`` object is created from a ``roElementAction`` MOS file
    containing a story replacement.

    ``EAReplaceStory`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents
    """
    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        target_story_id = self.target.find('storyID').text
        story, story_index = find_child(parent=rc, child_tag='story', id=target_story_id)
        if not story:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story not found'
            )
        new_stories = self.source.findall('story')
        if not new_stories:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story not found'
            )
        remove_node(parent=rc, node=story)
        for new_story in new_stories:
            insert_node(parent=rc, node=new_story, index=story_index)
            story_index += 1
        return ro


class EAReplaceItem(ElementAction):
    """
    An ``EAReplaceItem`` object is created from a ``roElementAction`` MOS file
    containing an item replacement.

    ``EAReplaceItem`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents
    """
    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        target_story_id = self.target.find('storyID').text
        story, story_index = find_child(parent=rc, child_tag='story', id=target_story_id)
        if not story:
            msg = f'{self.__class__.__name__} error in {self.message_id} - story not found'
            logger.warning(msg)
            warnings.warn(msg, StoryNotFoundWarning)
            return ro
        target_item_id = self.target.find('itemID').text
        item, item_index = find_child(parent=story, child_tag='item', id=target_item_id)
        if not item:
            msg = f'{self.__class__.__name__} error in {self.message_id} - item not found'
            logger.warning(msg)
            warnings.warn(msg, ItemNotFoundWarning)
            return ro
        new_items = self.source.findall('item')
        if not new_items:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - item not found'
            )
        remove_node(parent=story, node=item)
        for new_item in new_items:
            insert_node(parent=story, node=new_item, index=item_index)
            item_index += 1
        return ro


class EADeleteStory(ElementAction):
    """
    An ``EADeleteStory`` object is created from a ``roElementAction`` MOS file
    containing a story deletion.

    ``EADeleteStory`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents
    """
    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        source_story_ids = self.source.findall('storyID')
        for source_story_id in source_story_ids:
            story, story_index = find_child(parent=rc, child_tag='story', id=source_story_id.text)
            if not story:
                msg = f'{self.__class__.__name__} error in {self.message_id} - story not found'
                logger.warning(msg)
                warnings.warn(msg, StoryNotFoundWarning)
            else:
                remove_node(parent=rc, node=story)
        return ro


class EADeleteItem(ElementAction):
    """
    An ``EADeleteItem`` object is created from a ``roElementAction`` MOS file
    containing an item deletion.

    ``EADeleteItem`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents
    """
    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        target_story_id = self.target.find('storyID').text
        story, story_index = find_child(parent=rc, child_tag='story', id=target_story_id)
        if not story:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story not found'
            )
        item_ids = self.source.findall('itemID')
        for item_id in item_ids:
            item, item_index = find_child(parent=story, child_tag='item', id=item_id.text)
            if not item:
                msg = f'{self.__class__.__name__} error in {self.message_id} - item not found'
                logger.warning(msg)
                warnings.warn(msg, ItemNotFoundWarning)
            else:
                remove_node(parent=story, node=item)
        return ro


class EAInsertStory(ElementAction):
    """
    An ``EAInsertStory`` object is created from a ``roElementAction`` MOS file
    containing a story insertion.

    ``EAInsertStory`` objects can be merged with a :class:`RunningOrder` by
    using the ``+`` operator. This behaviour is defined in the :meth:`merge`
    method in this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents
    """
    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        new_stories = self.source.findall('story')
        target_story_id = self.target.find('storyID').text
        story, story_index = find_child(parent=rc, child_tag='story', id=target_story_id)
        if not story:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story not found'
            )
        if not new_stories:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story not found'
            )
        for new_story in new_stories:
            insert_node(parent=rc, node=new_story, index=story_index)
            story_index += 1
        return ro


class EAInsertItem(ElementAction):
    """
    An ``EAInsertItem`` object is created from a ``roElementAction`` MOS file
    containing an item insertion.

    ``EAInsertItem`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents
    """
    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        target_story_id = self.target.find('storyID').text
        story, story_index = find_child(parent=rc, child_tag='story', id=target_story_id)
        if not story:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story not found'
            )
        target_item_id = self.target.find('itemID').text
        item_index = None
        if target_item_id:
            item, item_index = find_child(parent=story, child_tag='item', id=target_item_id)
        if not item_index:
            item_index = len(story.findall('item)'))
        new_items = self.source.findall('item')
        for new_item in new_items:
            insert_node(parent=story, node=new_item, index=item_index)
            item_index += 1
        return ro


class EASwapStory(ElementAction):
    """
    An ``EASwapStory`` object is created from a ``roElementAction`` MOS file
    containing a story swap.

    ``EASwapStory`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents
    """
    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        source_story_ids = self.source.findall('storyID')
        story1, story1_index = find_child(parent=rc, child_tag='story', id=source_story_ids[0].text)
        if not story1:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story 1 not found'
            )
        story2, story2_index = find_child(parent=rc, child_tag='story', id=source_story_ids[1].text)
        if not story2:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story 2 not found'
            )
        remove_node(parent=rc, node=story1)
        remove_node(parent=rc, node=story2)
        insert_node(parent=rc, node=story2, index=story1_index)
        insert_node(parent=rc, node=story1, index=story2_index)
        return ro


class EASwapItem(ElementAction):
    """
    An ``EASwapItem`` object is created from a ``roElementAction`` MOS file
    containing an item swap.

    ``EASwapItem`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents
    """
    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        target_story_id = self.target.find('storyID').text
        story, story_index = find_child(parent=rc, child_tag='story', id=target_story_id)
        if not story:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story not found'
            )
        source_item_ids = self.source.findall('itemID')
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


class EAMoveStory(ElementAction):
    """
    An ``EAMoveStory`` object is created from a ``roElementAction`` MOS file
    containing a story move.

    ``EAMoveStory`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents
    """
    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        target_story_id = self.target.find('storyID').text
        target_story, target_index = find_child(parent=rc, child_tag='story', id=target_story_id)
        if not target_story:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - target story not found'
            )

        source_story_ids = self.source.findall('storyID')
        for source_story_id in source_story_ids:
            source_story, source_index = find_child(parent=rc, child_tag='story', id=source_story_id.text)
            if not source_story:
                raise MosMergeError(
                    f'{self.__class__.__name__} error in {self.message_id} - source story not found'
                )
            remove_node(parent=rc, node=source_story)
            insert_node(parent=rc, node=source_story, index=target_index)
        return ro


class EAMoveItem(ElementAction):
    """
    An ``EAMoveItem`` object is created from a ``roElementAction`` MOS file
    containing an item move.

    ``EAMoveItem`` objects can be merged with a :class:`RunningOrder` by using
    the ``+`` operator. This behaviour is defined in the :meth:`merge` method in
    this class.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents
    """
    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        target_story_id = self.target.find('storyID').text
        story, story_index = find_child(parent=rc, child_tag='story', id=target_story_id)
        if not story:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story not found'
            )
        target_item_id = self.target.find('itemID').text
        target_item, target_item_index = find_child(parent=story, child_tag='item', id=target_item_id)
        if not target_item:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - target item not found'
            )
        source_item_ids = self.source.findall('itemID')
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
        XML string of MOS file contents
    """
    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        for source in list(self.mos.find('roMetadataReplace')):
            target, target_index = find_child(parent=rc, child_tag=source.tag)
            if target is None:
                raise MosMergeError(
                    f'{self.__class__.__name__} error in {self.message_id} - {source.tag} not found'
                )
            replace_node(parent=rc, old_node=target, new_node=source, index=target_index)
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
        XML string of MOS file contents
    """

    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        sa = self.mos.find('roStoryAppend')
        stories = sa.findall('story')
        if not stories:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no stories to append'
            )
        for story in stories:
            rc.append(story)
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
        XML string of MOS file contents
    """

    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        sd = self.mos.find('roStoryDelete')
        story_ids = sd.findall('storyID')
        if not story_ids:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no stories to delete'
            )
        for id in story_ids:
            found_node, found_index = find_child(parent=rc, child_tag='story', id=id.text)
            if not found_node:
                msg = f'{self.__class__.__name__} error in {self.message_id} - story not found'
                logger.warning(msg)
                warnings.warn(msg, StoryNotFoundWarning)
            else:
                remove_node(parent=rc, node=found_node)
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
        XML string of MOS file contents
    """

    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        id = self.mos.find('roItemDelete')

        story_id = id.find('storyID').text
        if not story_id:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no story to delete item from'
            )
        story, story_index = find_child(parent=rc, child_tag='story', id=story_id)
        if story is None:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - story not found'
            )

        item_ids = id.findall('itemID')
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
        XML string of MOS file contents
    """
    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        si = self.mos.find('roStoryInsert')
        target_id = si.find('storyID').text
        if not target_id:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no target storyID'
            )
        target_node, target_index = find_child(parent=rc, child_tag='story', id=target_id)
        stories = si.findall('story')
        if not stories:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no story to insert'
            )
        for story in stories:
            insert_node(parent=rc, node=story, index=target_index)
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
        XML string of MOS file contents
    """
    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        ii = self.mos.find('roItemInsert')
        target_story_id = ii.find('storyID').text
        if not target_story_id:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no target storyID'
            )
        target_story, story_index = find_child(parent=rc, child_tag='story', id=target_story_id)
        if not target_story:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no target story not found'
            )
        target_item_id = ii.find('itemID').text
        if target_item_id:
            target_item, item_index = find_child(parent=target_story, child_tag='item', id=target_item_id)
        else:
            item_index = len(target_story.findall('item)'))
        items = ii.findall('item')
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
        XML string of MOS file contents
    """

    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        sm = self.mos.find('roStoryMove')
        story_ids = sm.findall('storyID')
        if not story_ids:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no storyIDs in MOS message'
            )
        target_id = story_ids[1].text
        target_node, target_index = find_child(parent=rc, child_tag='story', id=target_id)
        if not target_node:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - traget storyID not found'
            )
        source_id = story_ids[0].text
        source_node, source_index = find_child(parent=rc, child_tag='story', id=source_id)
        if not source_node:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - storyID not found'
            )

        remove_node(parent=rc, node=source_node)
        insert_node(parent=rc, node=source_node, index=target_index)

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
        XML string of MOS file contents
    """

    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        imm = self.mos.find('roItemMoveMultiple')

        target_story_id = imm.find('storyID').text
        if not target_story_id:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no target storyID'
            )
        target_story, story_index = find_child(parent=rc, child_tag='story', id=target_story_id)

        item_ids = imm.findall('itemID')
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
        XML string of MOS file contents
    """
    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        sr = self.mos.find('roStoryReplace')
        target_id = sr.find('storyID').text
        if not target_id:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no target storyID'
            )
        target_node, target_index = find_child(parent=rc, child_tag='story', id=target_id)
        remove_node(parent=rc, node=target_node)
        stories = sr.findall('story')
        if not stories:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no story to insert'
            )
        for story in stories:
            insert_node(parent=rc, node=story, index=target_index)
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
        XML string of MOS file contents
    """

    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc = ro.mos.find('roCreate')
        ir = self.mos.find('roItemReplace')
        story_id = ir.find('storyID').text
        if not story_id:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no target storyID'
            )
        story_node, story_index = find_child(parent=rc, child_tag='story', id=story_id)
        if not story_node:
            msg = f'{self.__class__.__name__} error in {self.message_id} - story not found'
            logger.warning(msg)
            warnings.warn(msg, ItemNotFoundWarning)
            return ro
        item_id = ir.find('itemID').text
        if not item_id:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no target itemID'
            )
        item_node, item_index = find_child(parent=story_node, child_tag='item', id=item_id)
        remove_node(parent=story_node, node=item_node)
        items = ir.findall('item')
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
        XML string of MOS file contents
    """
    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rc, rc_index = find_child(parent=ro.mos, child_tag='roCreate')
        rr = self.mos.find('roReplace')
        if not rr:
            raise MosMergeError(
                f'{self.__class__.__name__} error in {self.message_id} - no target storyID'
            )
        rr.tag = 'roCreate'
        remove_node(parent=ro.mos, node=rc)
        insert_node(parent=ro.mos, node=rr, index=rc_index)
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
        XML string of MOS file contents
    """
    def merge(self, ro):
        "Merge into the :class:`RunningOrder` object provided"
        rd = self.mos.find('roDelete')
        mosromgrmeta = ET.SubElement(ro.mos, 'mosromgrmeta')
        mosromgrmeta.append(rd)
        return ro


class_tag_map = {
    'RunningOrder': 'roCreate',
    'StorySend': 'story',  # we change this to story on init
    'EAReplaceStory': 'roElementAction',
    'EAReplaceItem': 'roElementAction',
    'EADeleteStory': 'roElementAction',
    'EADeleteItem': 'roElementAction',
    'EAInsertStory': 'roElementAction',
    'EAInsertItem': 'roElementAction',
    'EASwapStory': 'roElementAction',
    'EASwapItem': 'roElementAction',
    'EAMoveStory': 'roElementAction',
    'EAMoveItem': 'roElementAction',
    'MetaDataReplace': 'roMetadataReplace',
    'RunningOrderEnd': 'roDelete',
    'StoryAppend': 'roStoryAppend',
    'StoryDelete': 'roStoryDelete',
    'StoryInsert': 'roStoryInsert',
    'StoryMove': 'roStoryMove',
    'StoryReplace': 'roStoryReplace',
    'ItemDelete': 'roItemDelete',
    'ItemInsert': 'roItemInsert',
    'ItemMoveMultiple': 'roItemMoveMultiple',
    'ItemReplace': 'roItemReplace',
    'RunningOrderReplace': 'roReplace',
}
