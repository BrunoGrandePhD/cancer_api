#!/usr/bin/env python


class CancergenException(Exception):
    """Base class for cancergen exceptions"""
    pass


class UndefinedUniqueOnError(CancergenException, NameError):
    """The unique_on class attribute isn't defined
    in the used model.
    """
    pass


class MultipleUniqueInstancesError(CancergenException):
    """When attempting to obtain a unique instance,
    multiple were returned.
    """
    pass
