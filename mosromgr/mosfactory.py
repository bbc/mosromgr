import xml.etree.ElementTree as ET
import logging
import warnings

from .mostypes import (
    RunningOrder, StorySend, EAReplaceStory, EAReplaceItem, EADeleteStory,
    EADeleteItem, EAInsertStory, EAInsertItem, EASwapStory, EASwapItem,
    EAMoveStory, EAMoveItem, MetaDataReplace, RunningOrderEnd, StoryAppend,
    StoryDelete, StoryInsert, StoryMove, StoryReplace, ItemDelete, ItemInsert,
    ItemMoveMultiple, ItemReplace, RunningOrderReplace, MosFile
)
from .exc import MosInvalidXML, UnknownMosFileTypeWarning

logger = logging.getLogger('mos_factory')
logging.basicConfig(level=logging.INFO)

ignored_types = (
    'roItemStat',
    'roReadyToAir',
    'roList',
)

tags = (
    'roCreate',
    'roStorySend',
    'roCreate',
    'roStorySend',
    'roStoryAppend',
    'roStoryDelete',
    'roStoryInsert',
    'roStoryMove',
    'roStoryReplace',
    'roItemDelete',
    'roItemInsert',
    'roItemMoveMultiple',
    'roItemReplace',
    'roReplace',
    'roMetadataReplace',
    'roDelete',
    'roElementAction',
)

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
    'roDelete': RunningOrderEnd,
}

ea_class_map = {
    'REPLACE': lambda ea: EAReplaceStory if ea.find('element_target').find('itemID') is None else EAReplaceItem,
    'DELETE': lambda ea: EADeleteStory if ea.find('element_target') is None else EADeleteItem,
    'INSERT': lambda ea: EAInsertStory if ea.find('element_target').find('itemID') is None else EAInsertItem,
    'SWAP': lambda ea: EASwapStory if ea.find('element_target') is None else EASwapItem,
    'MOVE': lambda ea: EAMoveStory if ea.find('element_target').find('itemID') is None else EAMoveItem,
}


def get_mos_object(mos_file_path=None, mos_file_contents=None, mos_file_prefix=None, sns=None):
    """
    Factory function that detects the MOS file type, selects the appropriate class
    based on the given MOS file, and constructs and returns an object.

    The MOS file can be passed either as a file path using ``mos_file_path`` or
    as a string using ``mos_file_contents``. ``mos_file_prefix`` should be used
    when working with MOS files stored in an AWS S3 bucket, it is used to make
    logging errors and warnings clearer.

    :type mos_file_path: str or None
    :param mos_file_path:
        Path to MOS file

    :type mos_file_contents: str or None
    :param mos_file_contents:
        XML string of MOS file contents

    :type mos_file_prefix: str or None
    :param mos_file_prefix:
        AWS S3 file prefix

    :type sns: :class:`~mosromgr.utils.sns.SNS` or None
    :param sns:
        SNS object used for lambda notifications
    """
    mo = None
    if mos_file_prefix is not None:
        mos_file_name = mos_file_prefix.split('/')[-1]
    else:
        mos_file_name = str(mos_file_path).split('/')[-1]
    try:
        if mos_file_path is not None:
            logger.info('detecting file %s', mos_file_name)
            xml = ET.parse(mos_file_path)
            mos = xml.getroot()
        elif mos_file_contents is not None:
            logger.info('detecting file %s', mos_file_name)
            mos = ET.fromstring(mos_file_contents)
        else:
            raise TypeError('Must specify mos_file_path or mos_file_contents')
    except ET.ParseError:
        logger.error('Invalid XML: %s', mos_file_name)
        msg = f'Error processing "{mos_file_prefix}": Invalid XML'
        if sns:
            sns.send_sns_notification(sns.ERRORLVL, msg)
        raise MosInvalidXML(msg)

    for tag in tags:
        if mos.find(tag) is not None:
            if tag in tag_class_map:
                ClassName = tag_class_map[tag]
                mo = ClassName(mos_file_path, mos_file_contents)
            elif tag == 'roElementAction':
                if mos.find('roElementAction') is not None:
                    ea = mos.find('roElementAction')
                    ClassName = ea_class_map[ea.attrib['operation']](ea)
                    mo = ClassName(mos_file_path, mos_file_contents)

    if isinstance(mo, MosFile):
        logger.info('created %s from message %s', mo.__class__.__name__, mo.message_id)
    else:
        ignore = False
        for type in ignored_types:
            if mos.find(type) is not None:
                ignore = True
        if not ignore:
            logger.warning('failed to detect mosfile type: %s', mos_file_name)
            msg = f'Failed to detect mosfile type: {mos_file_prefix}'
            warnings.warn(msg, UnknownMosFileTypeWarning)
            if sns:
                sns.send_sns_notification(sns.WARNLVL, msg)

    return mo
