"""
files.py
========
This submodules contains all classes representing file
types/formats, which in turn employ the parsers submodule.
"""

import gzip
import parsers
import mutations
import misc
from exceptions import CancerApiException


class BaseFile(object):
    """Base class for file classes"""

    DEFAULT_HEADER = ""
    HEADER_PREFIX = "#"

    def __init__(self, *args, **kwargs):
        """Provide more informative error message.
        Redirect users to open and convert methods.
        """
        raise CancerApiException("Cannot instantiate file directly. "
                                 "Please use `open` and `convert` methods instead.")

    @classmethod
    def open(cls, filepath, parser_cls=None):
        """Instantiate a BaseFile object from an
        existing file on disk.
        """
        obj = cls.__new__(cls)
        obj.filepath = filepath
        if not parser_cls:
            parser_cls = cls.DEFAULT_PARSER_CLS
        obj.parser = parser_cls(obj)
        obj._source = obj
        return obj

    @classmethod
    def convert(cls, other_file):
        """Instantiate a BaseFile object from another
        BaseFile object.
        """
        obj = cls.__new__(cls)
        obj._source = other_file._source
        return obj

    @property
    def header(self):
        """Return header if already stored in instance.
        Otherwise, parse file on disk if filepath is specified.
        If not, return default header for current file type.
        """
        if getattr(self, "_header", None):
            header = self._header
        elif getattr(self, "filepath", None):
            with self._open(self.filepath) as infile:
                header = ""
                for line in infile:
                    if self.is_header_line(line):
                        header += line
        else:
            header = self.DEFAULT_HEADER
        return header

    @header.setter
    def header(self, value):
        self._header = value

    @property
    def col_names(self):
        if getattr(self, "_col_names", None):
            col_names = self._col_names
        else:
            header = self.header
            # Assume that the column names are the
            # last line in the header
            last_header_line = header.rstrip("\n").split("\n")[-1]
            col_names = last_header_line.lstrip(self.HEADER_PREFIX).split("\t")
            self._col_names = col_names
        return col_names

    @col_names.setter
    def col_names(self, value):
        self._col_names = list(value)

    @property
    def filepath(self):
        return self._source._filepath

    @filepath.setter
    def filepath(self, value):
        self._filepath = value

    @property
    def parser(self):
        return self._source._parser

    @parser.setter
    def parser(self, value):
        self._parser = value

    @classmethod
    def is_header_line(cls, line):
        """Return whether or not a line is a header line
        according to the current file type.
        Defaults to lines starting with '#'.
        """
        is_header_line = False
        # If HEADER_PREFIX is None, always return false
        if cls.HEADER_PREFIX is not None and line.startswith(cls.HEADER_PREFIX):
            is_header_line = True
        return is_header_line

    def _open(self, filepath, mode="r", *args, **kwargs):
        """Wrapper for file open() function.
        Purpose: to catch gzipped files and handle them
        accordingly by using the gzip module.
        """
        opened_file = None
        if filepath.endswith(".gz"):
            # Ensure that "b" is in the mode
            if "b" not in mode:
                mode += "b"
            # Override compression level default (9 -> 6)
            # if not specified
            if "compresslevel" not in kwargs:
                kwargs["compresslevel"] = 6
            opened_file = gzip.open(filepath, mode, *args, **kwargs)
        else:
            opened_file = open(filepath, mode, *args, **kwargs)
        return opened_file

    def obj_to_str(self, obj):
        """Returns string for representing objects
        as lines (one or many) in current file type.
        If object doesn't have a line representation for
        the current file type, return None.
        """
        # Example implementation:
        # if type(obj) is SingleNucleotideVariant:
        #     line = "{chrom}\t{pos}\t{ref_allele}\t{alt_allele}\n".format(**vars(obj))
        # elif type(obj) is StructuralVariation:
        #     line = "{chrom1}\t{pos1}\t...\n".format(**vars(obj))
        # else:
        #     line = None
        # return line
        raise NotImplementedError

    def write(self, outfilepath):
        """Write BaseFile instance out to disk.
        If instance is a converted file, update
        filepath and parser attributes accordingly.
        """
        with self._open(outfilepath, "w") as outfile:
            header = self.create_header()
            outfile.write(header)
            for obj in self.source:
                line = self.obj_to_str(obj)
                outfile.write(line)
        if self._source is not self:
            self._source = self
            self.filepath = outfilepath
            self.parser = self.DEFAULT_PARSER_CLS

    def __iter__(self):
        """Return instances of the objects
        associated with the current file type.
        """
        # Iterate over every non-header line
        source = self._source
        with self._open(source.filepath) as infile:
            for line in infile:
                if source.is_header_line(line):
                    continue
                obj = source.parser.parse(line)
                if obj:
                    yield obj


class VcfFile(BaseFile):
    """Class for representing VCF files."""

    DEFAULT_PARSER_CLS = parsers.VcfParser


class BedpeFile(BaseFile):
    """Class for representing BEDPE files."""

    def obj_to_str(self, obj):
        """Create line from SV objects."""
        if type(obj) is mutations.StructuralVariation:
            template = ("{chrom1}\t{start1}\t{end1}\t{chrom2}\t{start2}\t{end2}\t"
                        "{name}\t{score}\t{strand1}\t{strand2}\n")
            line = template.format(
                chrom1=obj.chrom1,
                start1=obj.pos1,
                end1=obj.pos1,
                chrom2=obj.chrom2,
                start2=obj.pos2,
                end2=obj.pos2,
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


class FastqFile(BaseFile):
    """Class for representing FASTQ raw read files.
    Assumes modern Illumina FASTQ files.
    """

    DEFAULT_PARSER_CLS = parsers.FastqParser
    HEADER_PREFIX = None

    def __iter__(self):
        """Override __iter__ such that it iterates over
        quartets (groups of four lines).
        """
        # Iterate over quartets (non-header lines)
        source = self._source
        with self._open(source.filepath) as infile:
            current_quartet = ""
            for line in infile:
                # Skip header lines
                if source.is_header_line(line):
                    continue
                # Add line to quartet
                current_quartet += line
                # Check if quartet has four lines
                # And continue to next line otherwise
                if len(current_quartet.rstrip("\n").split("\n")) < 4:
                    continue
                # Once the quartet has four lines, it will continue on
                # to being parsed
                obj = source.parser.parse(line)
                if obj:
                    yield obj
                current_quartet = ""

    def obj_to_str(self, obj):
        """Create quartet from RawRead instance."""
        if type(obj) is misc.RawRead:
            template = ("{id}\n{seq}\n{strand}\n{qual}\n")
            line = template.format(
                id=("@" + obj.id),
                seq=obj.seq,
                strand=obj.strand,
                qual=obj.qual
            )
        else:
            line = None
        return line
