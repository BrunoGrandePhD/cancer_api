"""
files.py
========
This submodules contains all classes representing file
types/formats, which in turn employ the parsers submodule.
"""

from base import BaseFile
import parsers
import mutations
import misc


class VcfFile(BaseFile):
    """Class for representing VCF files."""

    DEFAULT_PARSER_CLS = parsers.VcfParser
    FILE_EXTENSIONS = ["vcf"]


class BedpeFile(BaseFile):
    """Class for representing BEDPE files."""

    FILE_EXTENSIONS = ["bedpe"]
    DEFAULT_HEADER = "#chrom1\tstart1\tend1\tchrom2\tstart2\tend2\tname\tscore\tstrand1\tstrand2\n"
    DEFAULT_PARSER_CLS = parsers.BaseParser  # A BEDPE parser need to be implemented

    @classmethod
    def obj_to_str(cls, obj):
        """Create line from SV objects."""
        if type(obj) is mutations.StructuralVariation:
            template = ("{chrom1}\t{start1}\t{end1}\t{chrom2}\t{start2}\t{end2}\t"
                        "{name}\t{score}\t{strand1}\t{strand2}\n")
            line = template.format(
                chrom1=obj.chrom1,
                start1=obj.pos1,
                end1=int(obj.pos1) + 1,
                chrom2=obj.chrom2,
                start2=obj.pos2,
                end2=int(obj.pos2) + 1,
                name="{}_{}_{}_{}".format(obj.chrom1, obj.pos1, obj.chrom2, obj.pos2),
                score="",
                strand1=obj.strand1,
                strand2=obj.strand2
            )
        else:
            line = None
        return line


class BedFile(BaseFile):
    """Class for representing BED interval files."""

    DEFAULT_PARSER_CLS = parsers.BedParser
    FILE_EXTENSIONS = ["bed"]


class FastqFile(BaseFile):
    """Class for representing FASTQ raw read files.
    Assumes modern Illumina FASTQ files.
    """

    DEFAULT_PARSER_CLS = parsers.FastqParser
    HEADER_PREFIX = None
    FILE_EXTENSIONS = ["fastq", "fq", "fastq.gz", "fq.gz"]

    def __iter__(self):
        """Override __iter__ such that it iterates over
        quartets (groups of four lines).
        """
        # Iterate over quartets (non-header lines)
        with self._open() as infile:
            current_quartet = ""
            for line in infile:
                # Skip header lines
                if self.source.is_header_line(line):
                    continue
                # Add line to quartet
                current_quartet += line
                # Check if quartet has four lines
                # And continue to next line otherwise
                if len(current_quartet.rstrip("\n").split("\n")) < 4:
                    continue
                # Once the quartet has four lines, it will continue on
                # to being parsed
                obj = self.source.parser.parse(current_quartet)
                if obj:
                    yield obj
                current_quartet = ""

    @classmethod
    def obj_to_str(cls, obj):
        """Create quartet from RawRead instance."""
        if type(obj) is misc.RawRead:
            template = ("{id}\n{seq}\n{strand}\n{qual}\n")
            quartet = template.format(
                id=("@" + obj.id),
                seq=obj.seq,
                strand=obj.strand,
                qual=obj.qual
            )
        else:
            quartet = None
        return quartet


class FacteraFile(BaseFile):
    """Class for representing Factera's 'fusions.txt' files"""

    DEFAULT_PARSER_CLS = parsers.FacteraParser
    HEADER_PREFIX = "Est_Type"
    FILE_EXTENSIONS = ["fusions.txt"]
