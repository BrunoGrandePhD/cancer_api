#!/usr/bin/env python

from mutations import SingleNucleotideVariant


class BaseFile(object):
    """Base class for file classes"""

    def __init__(self, filepath, parser):
        """Initialize a file"""
        self.filepath = filepath
        self.parser = parser(self)

    def is_header_line(line):
        """Return whether or not a line is a header line
        according to the format.
        """
        is_header_line = False
        if line.startswith("#"):
            is_header_line = True
        return is_header_line


class VcfFile(BaseFile):
    """Class for representing VCF files"""

    def __init__(self, filepath, vcf_type=SingleNucleotideVariant):
        pass
