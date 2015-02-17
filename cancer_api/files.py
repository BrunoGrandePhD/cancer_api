#!/usr/bin/env python


class BaseFile(object):
    """Base class for file classes"""

    DEFAULT_HEADER = ""

    def __init__(self, filepath, parser):
        """Initialize a file"""
        if filepath:
            self.filepath = filepath
            self.parser = parser(self)
            self.header = self.extract_header()
            self.col_names = None  # list
            self.source = self

    @staticmethod
    def is_header_line(line):
        """Return whether or not a line is a header line
        according to the format.
        """
        is_header_line = False
        if line.startswith("#"):
            is_header_line = True
        return is_header_line

    def extract_header(self):
        """Extract header from file"""
        header = ""
        with open(self.filepath) as infile:
            for line in infile:
                if self.is_header_line(line):
                    header += line
                else:
                    break
        return header

    def create_header(self):
        """Returns stored header if it exists.
        If not, it creates a bare-bones header.
        """
        if getattr(self, "header", None):
            return self.header
        else:
            return self.DEFAULT_HEADER

    def create_line(self, obj):
        """Returns string for representing object
        as line in current file type.
        """
        raise NotImplementedError

    def write(self, outfilepath):
        """Write file out to disk."""
        with open(outfilepath, "w") as outfile:
            header = self.create_header()
            outfile.write(header)
            for obj in self.source:
                line = self.create_line(obj)
                outfile.write(line)

    def __iter__(self):
        """Return instances of the objects
        associated with the current file type.
        """
        # Iterate over every non-header line
        source = self.source
        with open(source.filepath) as infile:
            for line in infile:
                if source.is_header_line(line):
                    continue
                obj = source.parser.parse(line)
                if obj:
                    yield obj

    @classmethod
    def convert(cls, other_file):
        """Returns new instance of current file type
        that is linked to the other_file.
        """
        new_file = cls(None, None)
        new_file.source = other_file
        return new_file


class VcfFile(BaseFile):
    """Class for representing VCF files."""

    def __init__(self, filepath, parser):
        super(VcfFile, self).__init__(filepath, parser)
        self.col_names = self.header.split("\n")[-2].lstrip("#").split("\t")


class BedpeFile(BaseFile):
    """Class for representing BEDPE files."""

    def __init__(self, filepath, parser):
        super(BedpeFile, self).__init__(filepath, parser)

    def create_line(self, obj):
        """Create line from SV objects."""
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
        return line
