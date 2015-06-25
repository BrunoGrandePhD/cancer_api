"""
effects.py
==========
This submodule contains classes representing effects that
mutations may have, such as amino acid changes in proteins.
"""

from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from base import Base


class GeneEffect(Base):
    """Base class for all variant effects"""

    id = Column(Integer, primary_key=True)
    mutation_id = Column(Integer, ForeignKey("mutation.id"))
    gene_id = Column(Integer, ForeignKey("gene.id"))
    effect_type = Column(String(50))

    __mapper_args__ = {"polymorphic_on": effect_type}

    mutation = relationship("Mutation", backref="effects")
    gene = relationship("Gene", backref="effects")


class ProteinEffect(GeneEffect):
    """Any consequence that alters the protein sequence.
    For instance: missense, nonsense, nonstop and splice-site
    variants as well as indels.
    """

    id = Column(Integer, ForeignKey("geneeffect.id"), primary_key=True)
    type = Column(Enum("missense", "nonsense", "nonstop", "splice-site", "frameshift"))

    __mapper_args__ = {'polymorphic_identity': 'protein'}


class CopyNumberEffect(GeneEffect):
    """Any consequence that alters allele copy number.
    For instance: amplifications, deletions and LOH.
    """

    id = Column(Integer, ForeignKey("geneeffect.id"), primary_key=True)
    cn_type = Column(Enum("gain", "loss", "loh"))
    num_copies = Column(Integer)

    __mapper_args__ = {'polymorphic_identity': 'copy_number'}


class StructuralEffect(GeneEffect):
    """Any consequence that alters gene structure.
    For instance: translocations and inversions.
    """

    id = Column(Integer, ForeignKey("geneeffect.id"), primary_key=True)

    __mapper_args__ = {'polymorphic_identity': 'structural'}
