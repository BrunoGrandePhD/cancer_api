"""
files.py
========
This submodules contains all classes representing file
types/formats, which in turn employ the parsers submodule.
"""

import gzip
import os.path
import gc
import parsers
import mutations
import misc
from exceptions import CancerApiException, IllegalVariableDefinition


class BaseFile(object):
    """Base class for file classes"""

    DEFAULT_HEADER = ""
    HEADER_PREFIX = "#"
    FILE_EXTENSIONS = []

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
        obj.is_new_file = False
        return obj

    @classmethod
    def convert(cls, other_file):
        """Instantiate a BaseFile object from another
        BaseFile object.
        """
        obj = cls.__new__(cls)
        obj._source = other_file._source
        obj.is_new_file = True
        return obj

    @classmethod
    def new(cls, filepath=None):
        """Instantiate a BaseFile object from scratch.
        Useful for adding objects and write them out to disk.
        """
        obj = cls.__new__(cls)
        obj.filepath = filepath
        obj._source = obj
        obj.is_new_file = True
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
    def filename(self):
        if self._source == self:
            full_filename = os.path.basename(self.filepath)
            for ext in self.FILE_EXTENSIONS:
                if full_filename.lower().endswith("." + ext.lower()):
                    ext_len = len("." + ext)
                    return full_filename[:-ext_len]
            return full_filename
        else:
            return None

    @filename.setter
    def filename(self, value):
        raise IllegalVariableDefinition("Cannot directly edit filename.")

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

    @property
    def storelist(self):
        if not getattr(self, "_storelist", None):
            self._storelist = []
        return self._storelist

    @storelist.setter
    def storelist(self, value):
        raise IllegalVariableDefinition("Modify storelist using methods such as "
                                        "`add_obj`, `rm_obj`, `clear_storelist`")

    def add_obj(self, obj):
        """Add object to storelist. Useful to bind objects
        to files created with the `new` constructor.
        Returns whether the object was added
        (always True for now).
        """
        # Ensure that storelist is defined
        self.storelist
        self._storelist.append(obj)
        return True

    def rm_obj(self, obj):
        raise NotImplementedError("`BaseFile.rm_obj` is not implemented yet.")

    def clear_storelist(self):
        """Empty storelist"""
        self._storelist = []
        # Force garbage collection
        gc.collect()

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

    @classmethod
    def obj_to_str(cls, obj):
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

    def write(self, outfilepath=None):
        """Write BaseFile instance out to disk.
        If not outfilepath specified, appends objects
        stored in self.storelist to current filepath.
        Will iterate over source's file and any objects
        stored in self.storelist.
        If instance is a converted file, update
        filepath and parser attributes accordingly.
        """
        # If outfilepath is specified, write every object in
        # self.source and self.storelist to disk.
        # Clear self.storelist afterwards.
        if outfilepath:
            with self._open(outfilepath, "w") as outfile:
                header = self.create_header()
                outfile.write(header)
                for obj in self.source:
                    line = self.obj_to_str(obj)
                    outfile.write(line)
                for obj in self.source.storelist:
                    line = self.obj_to_str(obj)
                    outfile.write(line)
            if self._source is not self:
                self._source = self
                self.filepath = outfilepath
                self.has_written
                self.parser = self.DEFAULT_PARSER_CLS
            self.clear_storelist()
        # If outfilepath is not specified, it is assumed that the
        # file instance already has self.filepath and the purpose
        # is to append any objects stored in self.storelist to the
        # file on disk.
        # Clear self.storelist afterwards.
        else:
            if self._source is not self or not self.filepath:
                raise CancerApiException("This file has never been written out to disk. "
                                         "Please specify an outfilepath at first.")
            # Check if this is a new file and if self.filepath exists
            if self.is_new_file and os.path.exists(self.filepath):
                raise CancerApiException("The specified filepath already exists. If you wish "
                                         "to overwrite the file, delete it or explicitly "
                                         "specify an outfilepath for the `write` method.")
            with self._open(self.filepath, "a+") as outfile:
                for obj in self.storelist:
                    line = self.obj_to_str(obj)
                    outfile.write(line)
            self.clear_storelist()

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
    FILE_EXTENSIONS = ["vcf"]


class BedpeFile(BaseFile):
    """Class for representing BEDPE files."""

    @classmethod
    def obj_to_str(cls, obj):
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
    FILE_EXTENSIONS = ["fastq", "fq", "fastq.gz", "fq.gz"]

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
                obj = source.parser.parse(current_quartet)
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
