#!/usr/bin/env python

from sqlalchemy import UniqueConstraint, Index, Column
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.declarative.api import DeclarativeMeta
# from sqlalchemy.ext.declarative.base import _as_declarative, _add_attribute
from exceptions import *
from main import app


class DeclarativeMetaMixin(DeclarativeMeta):
    """A metaclass to intercept the creation of classes inheriting
    from the declarative base in order to perform adjustments
    """

    def __init__(cls, classname, bases, dict_):
        # First, ensure that primary keys aren't nullable
        for name, value in dict_.items():
            if type(value) == Column and value.foreign_keys:
                dict_[name].nullable = False
        # Second, ensure that attributes listed in unique_on aren't nullable either
        if "unique_on" in dict_:
            unique_on = dict_["unique_on"]
            for attribute in unique_on:
                dict_[attribute].nullable = False
        # Then proceed as usual
        super(DeclarativeMetaMixin, cls).__init__(classname, bases, dict_)


# class MyDeclarativeMeta(type):
#     def __init__(cls, classname, bases, dict_):
#         # Intercept class creation and ensure that the unique_on
#         # attributes are nullable=False and unique=True
#         if "unique_on" in dict_:
#             unique_on = dict_["unique_on"]
#             for attribute in unique_on:
#                 dict_[attribute].nullable = False
#                 # dict_[attribute].unique = True
#         # Also ensure that primary keys are not nullable
#         for name, value in dict_.items():
#             if type(value) == Column and value.foreign_keys:
#                 dict_[name].nullable = False
#         # Proceed with the rest
#         if '_decl_class_registry' not in cls.__dict__:
#             _as_declarative(cls, classname, cls.__dict__)
#         type.__init__(cls, classname, bases, dict_)

#     def __setattr__(cls, key, value):
#         _add_attribute(cls, key, value)


class BaseMixin(object):
    """Provides methods to Base"""

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @declared_attr
    def __table_args__(cls):
        addons = []
        if type(cls.unique_on) == list:
            attributes = "_&_".join(cls.unique_on)
            addons.append(UniqueConstraint(*cls.unique_on, name="unique_on_" + attributes))
            addons.append(Index("index_for_" + attributes, *cls.unique_on))
        return tuple(addons)

    @property
    def unique_on(self):
        """List of attributes (as strings) on which each instance should be unique."""
        if not self._unique_on:
            raise NotImplementedError("The unique_on` attribute hasn't been implemented "
                                      "for this class (i.e. {}).".format(cls.__name__))
        return self._unique_on

    @unique_on.setter
    def unique_on(self, value):
        if type(value) == str:
            self._unique_on = [value]
        else:
            self._unique_on = value

    @classmethod
    def get_or_create(cls, **kwargs):
        """If a model's unique_on class attribute is defined,
        get_or_create will first search the database for an
        existing instance based on the attributes listed in
        unique_on. Otherwise, it will create an instance.
        Note that the session still needs to be committed.
        """
        # Get session
        session = app.session
        # Create subset of kwargs according to unique_on
        unique_kwargs = {k: v for k, v in kwargs.iteritems() if k in cls.unique_on}
        # Check if instance already exists based on unique_kwargs
        filter_query = session.query(cls).filter_by(**unique_kwargs)
        is_preexisting = session.query(filter_query.exists()).one()[0]
        if is_preexisting:
            # Instance already exists; obtain it and return it
            instance = filter_query.first()
        else:
            # Instance doesn't already exist, so create a new one
            instance = cls(**kwargs)
            session.add(instance)
        return instance

    def add(self):
        """Add self to session"""
        app.session.add(self)
        return self

    def save(self):
        """Add self to session and commit"""
        self.add()
        app.session.commit()
        return self


Base = declarative_base(cls=BaseMixin, metaclass=DeclarativeMetaMixin)
# Base = declarative_base(cls=BaseMixin)