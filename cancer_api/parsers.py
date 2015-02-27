"""
parsers.py
==========
This submodule contains all parsers used by the file classes
in the files submodule.
"""

from mutations import SingleNucleotideVariant, Indel, StructuralVariation
from misc import GenomicInterval, RawRead


class BaseParser(object):
    """Base file parser for defining necessary methods."""

    def __init__(self, file):
        """Store related file internally."""
        self.file = file

    def basic_parse(self, line):
        """The basic_parse method serves to create
        a dictionary of (column name, value) pairs.
        This is to provide a common base for all
        derivative parsers.

        Returns a dict of (column name, value) pairs.
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

    def basic_parse(self, line):
        """Parse VCF file.
        Returns dict of attribute-value pairs.
        """
        attrs = {}
        # Parse columns
        split_line = line.rstrip("\n").split("\t")
        if len(split_line) <= len(self.BASE_COLUMNS):
            # If there are only the base columns or less
            attrs.update(dict(zip(self.BASE_COLUMNS, split_line)))
        else:
            # If there are more columns (format and sample columns)
            extra_cols = self.file.col_names[len(self.BASE_COLUMNS):]
            extra_cols[0] = "format"  # ensure lowercase for format
            cols = self.BASE_COLUMNS + extra_cols
            attrs.update(dict(zip(cols, split_line)))
        # Parse info column
        info_cols = attrs["info"].split(";")
        info_dict = {}
        for col in info_cols:
            key, sep, value = col.partition("=")
            if sep == "=":
                info_dict[key] = value
            else:
                info_dict[key] = True
        attrs["info_dict"] = info_dict
        return attrs

    def parse(self, line):
        """Parse line from VCF file.
        Returns SingleNucleotideVariant or Indel instance.
        """
        attrs = self._parse(line)
        mutation_dict = {
            "chrom": attrs["chrom"],
            "pos": attrs["pos"],
            "ref_allele": attrs["ref"],
            "alt_allele": attrs["alt"],
            "ref_count": None,
            "alt_count": None
        }
        if (len(mutation_dict["ref_allele"]) == 1 and
                len(mutation_dict["alt_allele"]) == 1):
            mutation = SingleNucleotideVariant(**mutation_dict)
        else:
            mutation = Indel(**mutation_dict)
        return mutation


class DellyVcfParser(VcfParser):
    """Parser for DELLY VCF files."""

    SV_TYPE_MAP = {
        "DEL": "deletion",
        "DUP": "duplication",
        "INV": "inversion",
        "TRA": "translocation",
        "INS": "insertion"
    }

    STRAND_MAP = {
        "5": "+",
        "3": "-"
    }

    def parse(self, line):
        """Parse line from DELLY VCF file.
        Returns StructuralVariant instance.
        """
        attrs = self.basic_parse(line)
        info_dict = attrs["info_dict"]
        # Calculate SV strands, which are encoded are 5' or 3'
        strand1, strand2 = (self.STRAND_MAP[strand] for strand in
                            info_dict["CT"].split("to"))
        # Obtain SV type
        sv_type = self.SV_TYPE_MAP[info_dict["SVTYPE"]]
        # Construct SV object
        sv_dict = {
            "chrom1": attrs["chrom"],
            "pos1": attrs["pos"],
            "strand1": strand1,
            "chrom2": info_dict["CHR2"],
            "pos2": info_dict["END"],
            "strand2": strand2,
            "sv_type": sv_type
        }
        sv = StructuralVariation(**sv_dict)
        return sv


class BedParser(BaseParser):
    """Basic parser for BED interval files"""

    BASE_COLUMNS = ["chrom", "start_pos", "end_pos"]

    def basic_parse(self, line):
        """Parse basic columns for BED file.
        Returns dictionary of attributes.
        """
        attrs = {}
        split_line = line.rstrip("\n").split("\t")
        attrs = dict(zip(self.BASE_COLUMNS, split_line))
        return attrs

    def parse(self, line):
        """Parse BED file line.
        Returns Interval instances.
        """
        attrs = self.basic_parse(line)
        return GenomicInterval(**attrs)


class FastqParser(BaseParser):
    """Basic parser for FASTQ raw read files.
    Assumes quartets (i.e., string of four lines).
    """

    BASE_COLUMNS = ["id", "seq", "strand", "qual"]

    def basic_parse(self, quartet):
        """Parse basic quartet for FASTQ file.
        Returns dictionary of basic attributes.
        """
        attrs = {}
        split_quartet = quartet.rstrip("\n").split("\n")
        attrs = dict(zip(self.BASE_COLUMNS, split_quartet))
        return attrs

    def parse(self, quartet):
        """Parse quartet for FASTQ file.
        Return RawRead instances.
        """
        attrs = self.basic_parse(quartet)
        # Remove @ prefix in id
        attrs["id"] = attrs["id"].lstrip("@")
        # Only keep first character in strand
        attrs["strand"] = attrs["strand"][0]
        return RawRead(**attrs)
