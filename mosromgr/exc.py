class MosRoMgrException(Exception):
    "Base class for all ``mosromgr`` exceptions"


class UnknownMosFileType(MosRoMgrException):
    "Exception raised when a MOS file type cannot be determined"


class MosMergeError(MosRoMgrException):
    "Exception raised when MOS merge fails"


class MosCompletedMergeError(MosMergeError):
    "Exception raised when MOS merge is attempted on a completed :class:`~mosromgr.mostypes.RunningOrder`"


class InvalidMosCollection(MosRoMgrException):
    "Exception raised when MosCollection fails validation"


class MosInvalidXML(MosRoMgrException):
    "Exception raised when :class:`~mosromgr.mostypes.MosFile` cannot parse given XML"


class MosRoMgrWarning(Warning):
    "Base class for all warnings in mosromgr"


class ItemNotFoundWarning(MosRoMgrWarning):
    "Warning raised when an item cannot be found during a :class:`~mosromgr.mostypes.MosFile` merge"


class StoryNotFoundWarning(MosRoMgrWarning):
    "Warning raised when a story cannot be found during a :class:`~mosromgr.mostypes.MosFile` merge"
