"""
exceptions.py
=============
This submodule contains custom exceptions to achieve more
informative error messages when something goes wrong.
"""


class CancerApiException(Exception):
    """Base class for Cancer_API exceptions"""
    pass


class NotConnectedToDatabase(CancerApiException):
    """A database connection is needed for running
    this method.
    """
    pass


class IllegalVariableDefinition(CancerApiException):
    """A variable was attempted to be defined in a non-canonical way."""
    pass
