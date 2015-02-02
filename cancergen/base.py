#!/usr/bin/env python

from sqlalchemy.ext.declarative import declarative_base
from exceptions import *


class BaseMixin(object):
    """Provides methods to Base"""

    def get_or_create(cls, session, **kwargs):
        """If a model's unique_on class attribute is defined,
        get_or_create will first search the database for an
        existing instance based on the attributes listed in
        unique_on. Otherwise, it will create an instance.
        """
        # Check if class' unique_on is defined
        try:
            cls.unique_on
        except NameError:
            raise UndefinedUniqueOn("The {} class doesn't have a defined unique_on "
                                    "class attribute.".format(cls.__name__))
        # Create subset of kwargs according to unique_on
        unique_kwargs = {}
        for key, value in [(k, v) for k, v in kwargs.iteritems() if k in cls.unique_on]:
            unique_kwargs[key] = value
        # Create string for filter
        pass
        # Check if instance already exists based on unique_kwargs
        results = session.query(cls).filter_by(**unique_kwargs)
        if len(results) > 1:
            # Ambiguous unique instances
            raise MultipleUniqueInstancesError(
                "More than one instance returned when looking for unique instance.")
        elif len(results) == 1:
            # Instance already exists, so return it
            instance = results
        elif len(results) == 0:
            # Instance doesn't already exist, so create a new one
            instance = cls(**kwargs)
            session.add(instance)
            session.commit()
        return instance


Base = declarative_base(cls=BaseMixin)
