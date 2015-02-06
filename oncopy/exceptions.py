#!/usr/bin/env python


class OncoPyException(Exception):
    """Base class for OncoPy exceptions"""
    pass


class UndefinedUniqueOnError(OncoPyException, NameError):
    """The unique_on class attribute isn't defined
    in the used model.
    """
    pass


class MultipleUniqueInstancesError(OncoPyException):
    """When attempting to obtain a unique instance,
    multiple were returned.
    """
    pass


class NotConnectedToDatabase(OncoPyException):
    """A database connection is needed for running
    this method.
    """
    pass
