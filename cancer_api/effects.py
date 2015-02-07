#!/usr/bin/env python

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from base import Base


class Effect(Base):
    """Base class for all variant effects"""

    id = Column(Integer, primary_key=True)
    mutation_id = Column(Integer, ForeignKey("mutation.id"))
    effect_type = Column(String(50))

    __mapper_args__ = {"polymorphic_on": effect_type}

    mutation = relationship("Mutation", backref="effects")
