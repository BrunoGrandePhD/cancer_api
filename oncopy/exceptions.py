#!/usr/bin/env python


class OncoPyException(Exception):
    """Base class for OncoPy exceptions"""
    pass


class NotConnectedToDatabase(OncoPyException):
    """A database connection is needed for running
    this method.
    """
    pass


class IllegalVariableDefinition(OncoPyException):
    """A variable was attempted to be defined in a non-canonical way."""
    pass
