#!/usr/bin/env python

import parsers
import mutations


class BaseFile(object):
    """Base class for file classes"""

    DEFAULT_HEADER = ""
    HEADER_PREFIX = "#"

    @classmethod
    def open(cls, filepath, parser_cls=None):
        """Instantiate a BaseFile object from an
        existing file on disk.
        """
        obj = cls()
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
        obj = cls()
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
            with open(self.filepath) as infile:
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
        if line.startswith(cls.HEADER_PREFIX):
            is_header_line = True
        return is_header_line

    def create_line(self, obj):
        """Returns string for representing objects
        as lines in current file type.
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
        with open(outfilepath, "w") as outfile:
            header = self.create_header()
            outfile.write(header)
            for obj in self.source:
                line = self.create_line(obj)
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
        with open(source.filepath) as infile:
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

    def create_line(self, obj):
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
