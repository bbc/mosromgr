# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from datetime import datetime, timedelta
from typing import Optional, Union, List, Dict

from dateutil.parser import parse


def _get_story_offsets(all_stories: Optional[List[Element]]) -> Optional[Dict[str, float]]:
    """
    Create a dict of {story_id: story_offset}
    """
    story_offsets = {}
    if all_stories:
        t = 0
        for story in all_stories:
            story_offsets[story.find('storyID').text] = t
            t += _get_story_duration(story)
        return story_offsets


def _get_story_duration(story_tag: Element) -> Optional[float]:
    """
    Return the sum of the text time and media time, or return None if not found
    """
    try:
        metadata = story_tag.find('mosExternalMetadata')
        payload = metadata.find('mosPayload')
    except AttributeError:
        return

    try:
        return float(payload.find('StoryDuration').text)
    except AttributeError:
        pass

    text_time = payload.find('TextTime')
    media_time = payload.find('MediaTime')
    if text_time is not None or media_time is not None:
        text_time = float(text_time.text) if text_time is not None else 0
        media_time = float(media_time.text) if media_time is not None else 0
        return text_time + media_time


def _is_technical_note(p: Element) -> bool:
    """
    Return ``True`` if the text in a paragraph element is surrounded by round
    ``()`` or angle ``<>`` brackets.
    """
    text = p.text.strip()
    if text.startswith('(') and text.endswith(')'):
        return True
    if text.startswith('<') and text.endswith('>'):
        return True
    return False

def _get_tag_text(tag: Element) -> str:
    """
    If a ``<p>`` tag contains text, return it, otherwise return an empty string
    (rather than ``None``).
    """
    if tag.text is not None:
        return tag.text
    return ''


class MosElement:
    """
    Abstract base class for MOS elements
    """
    def __init__(self, xml: Element, *, id: Optional[str] = None, slug: Optional[str] = None):
        self._xml = xml
        self._id = id
        self._slug = slug
        self._id_tag = None
        self._slug_tag = None

    def __repr__(self):
        try:
            short_id = self.id.split(',')[-1]
            return f"<{self.__class__.__name__} {short_id}>"
        except AttributeError:
            return f"<{self.__class__.__name__}>"

    def __str__(self):
        """
        The XML string
        """
        return ElementTree.tostring(self.xml, encoding='unicode')

    @property
    def xml(self) -> Element:
        """
        The XML element
        """
        return self._xml

    @property
    def id(self) -> Optional[str]:
        """
        The element ID (if present in the XML)
        """
        if self._id is None:
            try:
                self._id = self.xml.find(self._id_tag).text
            except AttributeError:
                self._id = None
        return self._id

    @property
    def slug(self) -> Optional[str]:
        """
        The element slug (if present in the XML)
        """
        try:
            self._slug = self.xml.find(self._slug_tag).text
        except AttributeError:
            return
        return self._slug


class Item(MosElement):
    """
    This class represents an Item element within any
    :class:`~mosromgr.mostypes.MosFile` object, providing data relating to an
    item within a :class:`Story`. The Item ID and Item slug (and more) are
    exposed as properties, and the XML element is provided for further
    introspection.
    """
    def __init__(self, xml: Element, *, id: Optional[str] = None, slug: Optional[str] = None):
        super().__init__(xml, id=id, slug=slug)
        self._id_tag = 'itemID'
        self._slug_tag = 'itemSlug'

    @property
    def id(self) -> Optional[str]:
        """
        The Item ID (if present in the XML)
        """
        return super().id

    @property
    def slug(self) -> Optional[str]:
        """
        The Item slug (if present in the XML)
        """
        return super().slug

    @property
    def type(self) -> Optional[str]:
        """
        The Item's object type (if present in the XML)
        """
        obj_type = self.xml.find('objType')
        if obj_type is not None:
            return obj_type.text

    @property
    def object_id(self) -> Optional[str]:
        """
        The Item's Object ID (if present in the XML)
        """
        obj_id = self.xml.find('objID')
        if obj_id is not None:
            return obj_id.text

    @property
    def mos_id(self) -> Optional[str]:
        """
        The Item's MOS ID (if present in the XML)
        """
        mos_id = self.xml.find('mosID')
        if mos_id is not None:
            return mos_id.text

    @property
    def note(self) -> Optional[str]:
        """
        The item note text (if present in the XML)
        """
        try:
            metadata = self.xml.find('mosExternalMetadata')
            mos_payload = metadata.find('mosPayload')
            note = mos_payload.find(".//studioCommand[@type='note']")
            return note.find('text').text
        except AttributeError:
            return


class Story(MosElement):
    """
    This class represents a Story element within any
    :class:`~mosromgr.mostypes.MosFile` object, providing data relating to the
    story. The Story ID, Story slug, duration and more are exposed as
    properties, and the XML element is provided for further introspection.
    """
    def __init__(self,
        xml: Element,
        *,
        id: Optional[str] = None,
        slug: Optional[str] = None,
        duration: Optional[float] = None,
        unknown_items: bool = False,
        all_stories: Optional[List[Element]] = None,
        prog_start_time: Optional[datetime] = None
    ):
        super().__init__(xml, id=id, slug=slug)
        self._id_tag = 'storyID'
        self._slug_tag = 'storySlug'
        self._duration = duration
        self._unknown_items = unknown_items
        self._prog_start_time = prog_start_time
        self._story_offsets = _get_story_offsets(all_stories)

    @property
    def id(self) -> Optional[str]:
        """
        The Story ID (if present in the XML)
        """
        return super().id

    @property
    def slug(self) -> Optional[str]:
        """
        The Story slug (if present in the XML)
        """
        return super().slug

    @property
    def items(self) -> Optional[List[Item]]:
        """
        List of :class:`Item` elements found within the story (can be ``None``
        if not available in the XML)
        """
        if self._unknown_items:
            return
        return [
            Item(item_tag)
            for item_tag in self.xml.findall('item')
        ]

    @property
    def duration(self) -> float:
        """
        The story duration (the sum of the text time and media time found
        within ``mosExternalMetadata->mosPayload``), in seconds
        """
        return _get_story_duration(self.xml)

    @property
    def offset(self) -> Optional[float]:
        """
        The time offset of the story in seconds (if available in the XML)
        """
        try:
            return self._story_offsets.get(self.id)
        except AttributeError:
            return

    @property
    def start_time(self) -> Optional[datetime]:
        """
        The transmission start time of the story (if present in the XML)
        """
        try:
            metadata = self.xml.find('mosExternalMetadata')
            mos_payload = metadata.find('mosPayload')
            start_time = mos_payload.find('StoryStarted').text
            return parse(start_time)
        except AttributeError:
            pass

        prog_start_time = self._prog_start_time
        offset = self.offset
        if prog_start_time is None or offset is None:
            return
        return self._prog_start_time + timedelta(seconds=self.offset)

    @property
    def end_time(self) -> Optional[datetime]:
        """
        The transmission end time of the story (if present in the XML)
        """
        try:
            metadata = self.xml.find('mosExternalMetadata')
            mos_payload = metadata.find('mosPayload')
            end_time = mos_payload.find('StoryEnded').text
            return parse(end_time)
        except AttributeError:
            pass

        if self.start_time is not None and self.duration is not None:
            return self.start_time + timedelta(seconds=self.duration)

    @property
    def script(self) -> List[str]:
        """
        A list of strings found in paragraph tags within the story body,
        excluding any empty paragraphs or technical notes in brackets.
        """
        return [
            p.text.strip()
            for p in self.xml.findall('p')
            if p.text and p.text.strip() and not _is_technical_note(p)
        ]

    @property
    def body(self) -> List[Union[Item, str]]:
        """
        A list of elements found in the story body. Each item in the list is
        either a string (representing a ``<p>`` tag) or an :class:`Item` object
        (representing an ``<item>`` tag). Unlike :attr:`script`, this does not
        exclude empty paragraph tags, which will be represented by empty strings.
        """
        return [
            Item(tag) if tag.tag == 'item' else _get_tag_text(tag)
            for tag in self.xml
            if tag.tag in ('item', 'p')
        ]
