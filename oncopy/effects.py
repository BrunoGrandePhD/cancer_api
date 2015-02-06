#!/usr/bin/env python

from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from base import Base


class Effect(Base):
    """Base class for all variant effects"""
    __tablename__ = "effect"

    id = Column(Integer, primary_key=True)
    mutation_id = Column(Integer, ForeignKey("mutation.id"))
    effect_type = Column(String(50))

    __mapper_args__ = {"polymorphic_on": effect_type}

    mutation = relationship("Mutation", backref="effects")
