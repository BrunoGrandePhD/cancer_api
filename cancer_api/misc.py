"""
misc.py
=======
This submodule contains all classes that don't belong
elsewhere for the moment. Eventually, another submodule
might be added and classes herein moved there.
"""

from base import CancerApiObject


class GenomicInterval(CancerApiObject):
    """Simple class for representing genomic intervals."""

    unique_on = ["chrom", "start_pos", "end_pos"]

    def __init__(self, chrom, start_pos, end_pos):
        self.chrom = str(chrom)
        self.start_pos = int(start_pos)
        self.end_pos = int(end_pos)

    @property
    def length(self):
        return self.end_pos - self.start_pos + 1


class RawRead(CancerApiObject):
    """Simple class for representing raw sequence reads"""

    unique_on = ["id", "seq", "strand", "qual"]

    def __init__(self, id, seq, strand, qual):
        self.id = id
        self.seq = seq
        self.strand = strand
        self.qual = qual
