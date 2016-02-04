class MetadbException(Exception):
    """Base exception for this package."""
    pass

class NoDataFoundException(MetadbException):
    """Should be used when no data has been found."""
    pass

class BadDataException(MetadbException):
    """Should be used when incorrect data is being submitted."""
    pass

class ErrorAddingException(MetadbException):
    """Should be used when incorrect data is being submitted."""
    pass
