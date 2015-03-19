"""
files.py
========
This submodules contains all classes representing file
types/formats, which in turn employ the parsers submodule.
"""

import os.path
import gc
import parsers
import mutations
import misc
from base import CancerApiObject
from exceptions import CancerApiException
from utils import open_file


class BaseFile(object):
    """Base class for file classes"""

    DEFAULT_HEADER = ""
    HEADER_PREFIX = "#"
    FILE_EXTENSIONS = ["txt"]

    def __init__(self, *args, **kwargs):
        """Can't initialize directly."""
        raise CancerApiException("Please use `open`, `convert` or `new` methods instead.")

    @classmethod
    def _init(cls, filepath=None, parser_cls=None, other_file=None, is_new=False):
        """Initialize BaseFile. Any instantiation of BaseFile should
        go through this method in an attempt to standardize attributes.
        Meant to be used internally only.
        """
        obj = cls.__new__(cls)
        obj.filepath = filepath
        obj.parser_cls = parser_cls
        obj.parser = parser_cls(obj) if parser_cls else cls.DEFAULT_PARSER_CLS(obj)
        obj.source = obj if not other_file else other_file.source
        obj.is_new = is_new
        obj.storelist = []
        return obj

    @classmethod
    def open(cls, filepath, parser_cls=None):
        """Instantiate a BaseFile object from an
        existing file on disk.
        """
        obj = cls._init(filepath=filepath, parser_cls=parser_cls, other_file=None, is_new=False)
        return obj

    @classmethod
    def convert(cls, filepath, other_file):
        """Instantiate a BaseFile object from another
        BaseFile object.
        """
        if not isinstance(other_file, BaseFile):
            raise CancerApiException("Must pass cancer_api file object as `other_file`.")
        obj = cls._init(filepath=filepath, parser_cls=None, other_file=other_file, is_new=True)
        return obj

    @classmethod
    def new(cls, filepath):
        """Instantiate a BaseFile object from scratch.
        Useful for adding objects and write them out to disk.
        """
        obj = cls._init(filepath=filepath, parser_cls=None, other_file=None, is_new=True)
        return obj

    def get_header(self):
        """Return header if already stored in instance.
        Otherwise, parse file on disk if filepath is specified.
        If not, return default header for current file type.
        """
        if self.is_new and self.source is self:
            # It's a file create with the `new` method
            header = self.DEFAULT_HEADER
        elif (self.is_new and self.source is not self) or not self.is_new:
            # It's a file created with the `convert` or `open` methods
            with self._open() as infile:
                header = ""
                for line in infile:
                    if self.is_header_line(line):
                        header += line
                    else:
                        break
        return header

    @property
    def col_names(self):
        if getattr(self, "_col_names", None):
            col_names = self._col_names
        else:
            header = self.get_header()
            # Assume that the column names are the
            # last line in the header
            last_header_line = header.rstrip("\n").split("\n")[-1]
            col_names = last_header_line.lstrip(self.HEADER_PREFIX).split("\t")
            self._col_names = col_names
        return col_names

    @col_names.setter
    def col_names(self, value):
        self._col_names = list(value)

    def split_filename(self):
        """Returns filename (root, ext) tuple."""
        filename = os.path.basename(self.filepath)
        # Make sure that long extensions go first (to match the longest available extension)
        for ext in ("." + x.lower() for x in sorted(self.FILE_EXTENSIONS, len, reverse=True)):
            if filename.lower().endswith(ext):
                return (filename[:-len(ext)], ext)
        # If none of the class' file extensions match, just use os.path.splitext
        return os.path.splitext(filename)

    @classmethod
    def get_cls_extension(cls):
        """Return first extension from cls.FILE_EXTENSIONS.
        Otherwise, returns an error if not available.
        """
        return cls.FILE_EXTENSIONS[0]

    def add_obj(self, obj):
        """Add object to storelist. Useful to bind objects
        to files created with the `new` constructor.
        Returns whether the object was added
        (always True for now).
        """
        if not isinstance(obj, CancerApiObject):
            raise CancerApiException("`add_obj` only supports cancer_api objects")
        self.storelist.append(obj)
        return True

    def clear_storelist(self):
        """Empty storelist"""
        self.storelist = []
        # Force garbage collection
        gc.collect()

    @classmethod
    def is_header_line(cls, line):
        """Return whether or not a line is a header line
        according to the current file type.
        Defaults to lines starting with '#'
        (see BaseFile.HEADER_PREFIX).
        """
        is_header_line = False
        if line.startswith(cls.HEADER_PREFIX):
            is_header_line = True
        return is_header_line

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

    def _open(self):
        """Use the open_file function on self.source.filepath in 'r' mode"""
        return open_file(self.source.filepath)

    def write(self, outfilepath=None, mode="w"):
        """Write objects in file to disk.
        Either you can write to a new file (if outfilepath is given),
        or you can append what's in storelist to the current filepath.
        """
        # If outfilepath is specified, iterate over every object in self
        # (which might come from something else) and every object in
        # self.storelist and write them out to disk
        if outfilepath:
            with open_file(outfilepath, mode) as outfile:
                outfile.write(self.get_header())
                for obj in self:
                    line = self.obj_to_str(obj)
                    outfile.write(line)
                for obj in self.storelist:
                    line = self.obj_to_str(obj)
                    outfile.write(line)
            # Clear storelist now that they've been written to disk
            self.clear_storelist()
            # Update file attributes (in case of new or converted file)
            self.source = self
            self.filepath = outfilepath
            self.is_new = False

        # If outfilepath is not specified, simply iterate over every
        # object in self.storelist and append them to the file on disk.
        else:
            # If the file is new and the path already exist, do not append
            if self.is_new and os.path.exists(self.filepath):
                raise CancerApiException("Output file already exists: {}".format(self.filepath))
            with open_file(self.filepath, "a+") as outfile:
                # If the file is new, start with header
                if self.is_new:
                    outfile.write(self.get_header())
                # Proceed with iterating over storelist
                for obj in self.storelist:
                    line = self.obj_to_str(obj)
                    outfile.write(line)
            # Clear storelist now that they've been written to disk
            self.clear_storelist()
            # Update file attributes (in case of new or converted file)
            self.source = self
            self.is_new = False

    def __iter__(self):
        """Return instances of the objects
        associated with the current file type.
        """
        # Iterate over every non-header line in self.source
        with self._open() as infile:
            for line in infile:
                if self.source.is_header_line(line):
                    continue
                obj = self.source.parser.parse(line)
                if obj:
                    yield obj


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
        source = self._source
        with self._open() as infile:
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


class FacteraFile(BaseFile):
    """Class for representing Factera's 'fusions.txt' files"""

    DEFAULT_PARSER_CLS = parsers.FacteraParser
    HEADER_PREFIX = "Est_Type"
    FILE_EXTENSIONS = ["fusions.txt"]
