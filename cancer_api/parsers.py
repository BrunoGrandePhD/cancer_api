#!/usr/bin/env python

from mutations import SingleNucleotideVariant, StructuralVariant


class BaseParser(object):
    """Base file parser for defining necessary methods."""

    def __init__(self, file):
        """Store related file internally."""
        self.file = file

    def _parse(self, line):
        """The _parse method is internally used by the
        parser classes for generating a dictionary of
        attribute-value pairs. This is useful for
        inheriting parent _parse and updating the
        returned dictionary accordingly.

        Returns a dict of attribute-value pairs
        """
        raise NotImplementedError

    def parse(self, line):
        """The parse method is user-facing and serves
        to return object instances as opposed to the
        dictionaries returned by _parse.

        Returns a cancer_api object instance
        """
        raise NotImplementedError


class VcfParser(BaseParser):
    """Generic parser for VCF files."""

    BASE_COLUMNS = ["chrom", "pos", "id", "ref", "alt", "qual", "filter", "info"]

    def _parse(self, line):
        """Parse line from VCF file.
        Returns dict of attribute-value pairs.
        """
        attrs = {}
        split_line = line.split("\t")
        if len(split_line) <= len(self.BASE_COLUMNS):
            attrs.update(dict(zip(self.BASE_COLUMNS, split_line)))
        else:
            columns = self.BASE_COLUMNS + ["format"]
            columns += ["sample_{}".format(sample_num) for sample_num
                        in range(1, len(split_line) - len(columns) + 1)]
            attrs.update(dict(zip(columns, split_line)))
        return attrs

    def parse(self, line):
        """Parse line from VCF file.
        Returns SingleNucleotideVariant instance.
        """
        attrs = self._parse(line)
        snv_dict = {
            "chrom": attrs["chrom"],
            "pos": attrs["pos"],
            "ref_allele": attrs["ref"],
            "alt_allele": attrs["alt"],
            "ref_count": None,
            "alt_count": None
        }
        snv = SingleNucleotideVariant(**snv_dict)
        return snv


class DellyVcfParser(VcfParser):
    """Parser for DELLY VCF files."""

    def _parse(self, line):
        """Parse line from DELLY VCF file.
        Returns dict of attribute-value pairs.
        """
        attrs = super(DellyVcfParser, self)._parse(line)
        return attrs

    def parse(self, line):
        """Parse line from DELLY VCF file.
        Returns StructuralVariant instance.
        """
        attrs = self._parse(line)
        sv_dict = {
            "chrom1": attrs["chrom"],
            "pos1": attrs["pos"],
            "strand1": None,
            "chrom2": None,
            "pos2": None,
            "strand2": None,
            "sv_type": None
        }
        sv = StructuralVariant(**sv_dict)
        return sv
