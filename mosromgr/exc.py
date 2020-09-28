class MosRoMgrException(Exception):
    "Base class for all ``mosromgr`` exceptions"


class MosMergeError(MosRoMgrException):
    "Exception raised when MOS merge fails"


class MosClosedMergeError(MosRoMgrException):
    "Exception raised when MOS merge is attempted on a closed :class:`~mosromgr.mostypes.RunningOrder`"


class MosContainerBadInit(MosRoMgrException):
    "Exception raised when MosContainer is created without a ``roCreate`` MOS message"


class MosInvalidXML(MosRoMgrException):
    "Exception raised when :func:`~mosromgr.mosfactory.get_mos_object` cannot parse given XML"


class MosRoMgrWarning(Warning):
    "Base class for all warnings in mosromgr"


class UnknownMosFileTypeWarning(MosRoMgrWarning):
    "Warning raised when :func:`~mosromgr.mosfactory.get_mos_object` cannot detect MOS file type"


class MergeAfterDeleteWarning(MosRoMgrWarning):
    "Warning raised when :class:`~mosromgr.moscontainer.MosContainer` merge finds files after roDelete"


class ItemNotFoundWarning(MosRoMgrWarning):
    "Warning raised when an item cannot be found during a :class:`~mosromgr.mostypes.MosFile merge"


class StoryNotFoundWarning(MosRoMgrWarning):
    "Warning raised when a story cannot be found during a :class:`~mosromgr.mostypes.MosFile merge"
