import xml.etree.ElementTree as ET
from datetime import timedelta


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
        return
    text_time = int(payload.find('TextTime').text)
    media_time = int(payload.find('MediaTime').text)
    return text_time + media_time


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
            return f'<{self.__class__.__name__} {short_id}>'
        except AttributeError:
            return f'<{self.__class__.__name__}>'

    def __str__(self):
        "The XML string"
        return ET.tostring(self.xml, encoding='unicode')

    @property
    def xml(self):
        "The parent XML element (:class:`xml.etree.ElementTree.Element`)"
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
    story. The Story ID, Story slug and duration are exposed as properties, and
    the parent XML element is provided for further introspection.
    """
    def __init__(self, xml, *, id=None, slug=None, duration=None,
                 unknown_items=False, all_stories=None, prog_tx_time=None):
        super().__init__(xml, id=id, slug=slug)
        self._id_tag = 'storyID'
        self._slug_tag = 'storySlug'
        self._duration = duration
        self._unknown_items = unknown_items
        self._prog_tx_time = prog_tx_time
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
        within ``mosExternalMetadata->mosPayload``), in seconds (:class:`int`)
        """
        return _get_story_duration(self.xml)

    @property
    def offset(self):
        """
        The time offset of the story in seconds (:class:`int` or ``None`` if not
        available in the XML)
        """
        return self._story_offsets.get(self.id)

    @property
    def tx_time(self):
        """
        The transmission time of the story (:class:`datetime.datetime` or
        ``None`` if not available in the XML)
        """
        return self._prog_tx_time + timedelta(seconds=self.offset)


class Item(MosElement):
    """
    This class represents an Item element within any
    :class:`~mosromgr.mostypes.MosFile` object, providing data relating to the
    item within a :class:`Story`. The Item ID and Item slug are exposed as
    properties, and the parent XML element is provided for further
    introspection.
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
    def note(self):
        "The item note text (:class:`str` or ``None`` if not found)"
        try:
            metadata = self.xml.find('mosExternalMetadata')
            mos_payload = metadata.find('mosPayload')
            note = mos_payload.find(".//studioCommand[@type='note']")
            return note.find('text').text
        except AttributeError:
            return
