import unittest
from nose.tools import *
import cancer_api as ca


class TestStructuralVariation(unittest.TestCase):

    def setUp(self):
        """Create a list of structural variations"""
        # Inter-chromosomal SV
        self.sv1 = ca.StructuralVariation(chrom1="1", pos1=1000, strand1="+",
                                          chrom2="2", pos2=2000, strand2="-",
                                          sv_type="translocation")
        # Intra-chromosomal SV
        self.sv2 = ca.StructuralVariation(chrom1="3", pos1=1000, strand1="+",
                                          chrom2="3", pos2=2000, strand2="+",
                                          sv_type="inversion")

    def test_is_overlap(self):
        """Test the is_overlap method for structural variations
        """
        # Test one position without margin
        self.assertFalse(self.sv1.is_overlap("1", 995))
        self.assertTrue(self.sv1.is_overlap("1", 1000))
        # Test one position with margin
        self.assertTrue(self.sv1.is_overlap("1", 995, margin=5))
        self.assertTrue(self.sv1.is_overlap("1", 1000, margin=5))
        # Test two positions without margin
        self.assertFalse(self.sv1.is_overlap("1", 995, 999))
        self.assertTrue(self.sv1.is_overlap("1", 995, 1001))
        # Test two positions with margin
        self.assertTrue(self.sv1.is_overlap("1", 995, 999, margin=5))
        self.assertTrue(self.sv1.is_overlap("1", 995, 1001, margin=5))
        # Test one position in middle of intra-chromosomal event
        self.assertTrue(self.sv2.is_overlap("3", 1500))
        # Test two positions in middle of intra-chromosomal event
        self.assertTrue(self.sv2.is_overlap("3", 1400, 1600))
        # Test two positions overlapping with intra-chromosomal event
        self.assertTrue(self.sv2.is_overlap("3", 500, 1500))
        self.assertTrue(self.sv2.is_overlap("3", 1500, 2500))
        self.assertFalse(self.sv2.is_overlap("3", 500, 990))
        self.assertFalse(self.sv2.is_overlap("3", 500, 990, margin=9))
        self.assertTrue(self.sv2.is_overlap("3", 500, 990, margin=10))
