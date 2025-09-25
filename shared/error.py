class AppException(Exception):
    """
    Base application exception class.
    """


class AppInputValueException(AppException, ValueError):
    """
    An exception for input value errors.
    """


class AppInputRangeValueException(AppInputValueException):
    """
    An exception to be raised on invalid range values errors.
    """


class AppOutOfRangeValueException(AppInputRangeValueException):
    """
    An exception to be raised on value out of range errors.
    """


class AppOperationException(AppException):
    """
    An exception to be raised on errors related to operations in the application.
    """


class AppNotFoundError(AppOperationException):
    """
    An exception to raise when something that was searched for was not found.
    """
