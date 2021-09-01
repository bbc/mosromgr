# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

import xml.etree.ElementTree as ET
from datetime import timedelta

from dateutil.parser import parse


def _get_story_offsets(all_stories):
    "Create a dict of {story_id: story_offset}"
    story_offsets = {}
    if all_stories:
        t = 0
        for story in all_stories:
            story_offsets[story.find('storyID').text] = t
            t += _get_story_duration(story)
        return story_offsets


def _get_story_duration(story_tag):
    """
    Return the sum of the text time and media time, or return None if not found
    """
    try:
        metadata = story_tag.find('mosExternalMetadata')
        payload = metadata.find('mosPayload')
    except AttributeError:
        return 0

    try:
        return float(payload.find('StoryDuration').text)
    except AttributeError:
        pass

    try:
        text_time = float(payload.find('TextTime').text)
        media_time = float(payload.find('MediaTime').text)
        return text_time + media_time
    except AttributeError:
        return 0


def _is_technical_note(p):
    """
    Return True if the text in a paragraph element is surrounded by round () or
    angle <> brackets.
    """
    text = p.text.strip()
    if text.startswith('(') and text.endswith(')'):
        return True
    if text.startswith('<') and text.endswith('>'):
        return True
    return False

def _get_tag_text(tag):
    """
    If a <p> tag contains text, return it, otherwise return an empty string
    (rather than None).
    """
    if tag.text is not None:
        return tag.text
    return ''


class MosElement:
    "Abstract base class for MOS elements"
    def __init__(self, xml, *, id=None, slug=None):
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
        "The XML string"
        return ET.tostring(self.xml, encoding='unicode')

    @property
    def xml(self):
        "The XML element (:class:`xml.etree.ElementTree.Element`)"
        return self._xml

    @property
    def id(self):
        "The element ID (:class:`str`)"
        if self._id is None:
            self._id = self.xml.find(self._id_tag).text
        return self._id

    @property
    def slug(self):
        """
        The element slug (:class:`str` or ``None`` if not available in the
        XML)
        """
        try:
            self._slug = self.xml.find(self._slug_tag).text
        except AttributeError:
            return
        return self._slug


class Story(MosElement):
    """
    This class represents a Story element within any
    :class:`~mosromgr.mostypes.MosFile` object, providing data relating to the
    story. The Story ID, Story slug, duration and more are exposed as
    properties, and the XML element is provided for further introspection.
    """
    def __init__(self, xml, *, id=None, slug=None, duration=None,
                 unknown_items=False, all_stories=None, prog_start_time=None):
        super().__init__(xml, id=id, slug=slug)
        self._id_tag = 'storyID'
        self._slug_tag = 'storySlug'
        self._duration = duration
        self._unknown_items = unknown_items
        self._prog_start_time = prog_start_time
        self._story_offsets = _get_story_offsets(all_stories)

    @property
    def id(self):
        """
        The Story ID (:class:`str`)
        """
        return super().id

    @property
    def slug(self):
        "The Story slug (:class:`str` or ``None`` if not available in the XML)"
        return super().slug

    @property
    def items(self):
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
    def duration(self):
        """
        The story duration (the sum of the text time and media time found
        within ``mosExternalMetadata->mosPayload``), in seconds (:class:`float`)
        """
        return _get_story_duration(self.xml)

    @property
    def offset(self):
        """
        The time offset of the story in seconds (:class:`float` or ``None`` if
        not available in the XML)
        """
        try:
            return self._story_offsets.get(self.id)
        except AttributeError:
            return

    @property
    def start_time(self):
        """
        The transmission start time of the story (:class:`datetime.datetime` or
        ``None`` if not available in the XML)
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
    def end_time(self):
        """
        The transmission end time of the story (:class:`datetime.datetime` or
        ``None`` if not available in the XML)
        """
        try:
            metadata = self.xml.find('mosExternalMetadata')
            mos_payload = metadata.find('mosPayload')
            end_time = mos_payload.find('StoryEnded').text
            return parse(end_time)
        except AttributeError:
            pass

        start_time = self.start_time
        duration = self.duration
        if start_time is None or duration is None:
            return
        return self.start_time + timedelta(seconds=self.duration)

    @property
    def script(self):
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
    def body(self):
        """
        A list of elements found in the story body. Each item in the list is
        either a string (representing a ``<p>`` tag) or an :class:`Item` object
        (representing an ``<item>`` tag). Unlike :attr:`script`, this does not
        exclude empty paragraph tags.
        """
        return [
            Item(tag) if tag.tag == 'item' else _get_tag_text(tag)
            for tag in self.xml
            if tag.tag in ('item', 'p')
        ]


class Item(MosElement):
    """
    This class represents an Item element within any
    :class:`~mosromgr.mostypes.MosFile` object, providing data relating to an
    item within a :class:`Story`. The Item ID and Item slug are exposed as
    properties, and the XML element is provided for further introspection.
    """
    def __init__(self, xml, *, id=None, slug=None):
        super().__init__(xml, id=id, slug=slug)
        self._id_tag = 'itemID'
        self._slug_tag = 'itemSlug'

    @property
    def id(self):
        "The Item ID (:class:`str`)"
        return super().id

    @property
    def slug(self):
        "The Item slug (:class:`str` or ``None`` if not available in the XML)"
        return super().slug

    @property
    def type(self):
        """
        The Item's object type (:class:`str` or ``None`` if not available in the
        XML)
        """
        obj_type = self.xml.find('objType')
        if obj_type is not None:
            return obj_type.text

    @property
    def object_id(self):
        """
        The Item's Object ID (:class:`str` or ``None`` if not available in the
        XML)
        """
        obj_id = self.xml.find('objID')
        if obj_id is not None:
            return obj_id.text

    @property
    def mos_id(self):
        """
        The Item's MOS ID (:class:`str` or ``None`` if not available in the XML)
        """
        mos_id = self.xml.find('mosID')
        if mos_id is not None:
            return mos_id.text

    @property
    def note(self):
        "The item note text (:class:`str` or ``None`` if not found)"
        try:
            metadata = self.xml.find('mosExternalMetadata')
            mos_payload = metadata.find('mosPayload')
            note = mos_payload.find(".//studioCommand[@type='note']")
            return note.find('text').text
        except AttributeError:
            return
