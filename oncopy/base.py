#!/usr/bin/env python

from sqlalchemy.ext.declarative import declarative_base
from exceptions import *


class BaseMixin(object):
    """Provides methods to Base"""

    @classmethod
    def get_or_create(cls, session, **kwargs):
        """If a model's unique_on class attribute is defined,
        get_or_create will first search the database for an
        existing instance based on the attributes listed in
        unique_on. Otherwise, it will create an instance.
        Note that the session still needs to be committed.
        """
        # Check if class' unique_on is defined
        try:
            cls.unique_on
        except AttributeError:
            raise UndefinedUniqueOnError("The {} class doesn't have a defined unique_on "
                                         "class attribute.".format(cls.__name__))
        # Create subset of kwargs according to unique_on
        unique_kwargs = {k: v for k, v in kwargs.iteritems() if k in cls.unique_on}
        # Check if instance already exists based on unique_kwargs
        count = session.query(cls).filter_by(**unique_kwargs).count()
        if count > 1:
            # Ambiguous unique instances
            raise MultipleUniqueInstancesError(
                "More than one instance returned when looking for unique instance.")
        elif count == 1:
            # Instance already exists; obtain it and return it
            instance = session.query(cls).filter_by(**unique_kwargs).first()
        elif count == 0:
            # Instance doesn't already exist, so create a new one
            instance = cls(**kwargs)
            session.add(instance)
        return instance


Base = declarative_base(cls=BaseMixin)
