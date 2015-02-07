#!/usr/bin/env python


class Cancer_APIException(Exception):
    """Base class for Cancer_API exceptions"""
    pass


class NotConnectedToDatabase(Cancer_APIException):
    """A database connection is needed for running
    this method.
    """
    pass


class IllegalVariableDefinition(Cancer_APIException):
    """A variable was attempted to be defined in a non-canonical way."""
    pass
