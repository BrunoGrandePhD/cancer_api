import unittest
import cancer_api as ca


class TestGenomicInterval(unittest.TestCase):
    """Test genomic interval methods
    """

    def setUp(self):
        """Create some genomic intervals for testing.
        """
        # Single position interval
        self.gi1 = ca.GenomicInterval("1", 1000)
        # Identical single position interval
        self.gi2 = ca.GenomicInterval("1", 1000)
        # Off by one single position interval
        self.gi3 = ca.GenomicInterval("1", 1001)
        # Two-position interval
        self.gi4 = ca.GenomicInterval("1", 1000, 2000)
        # Overlapping two-position interval
        self.gi5 = ca.GenomicInterval("1", 1500, 2500)
        # Overlapping two-position interval (at the edge)
        self.gi6 = ca.GenomicInterval("1", 2000, 3000)
        # Almost overlapping two-position interval
        self.gi7 = ca.GenomicInterval("1", 2010, 3010)
        # Single position interval with same position, but diff chrom
        self.gi8 = ca.GenomicInterval("2", 1000)
        # Overlapping two-position interval, but diff chrom
        self.gi9 = ca.GenomicInterval("2", 1500, 2500)
        # Overlapping single position interval intra to another interval
        self.gi10 = ca.GenomicInterval("1", 1500)
        # Overlapping two-position interval intra to another interval
        self.gi11 = ca.GenomicInterval("1", 1500, 1510)
        # Single position interval nearby a two-position interval
        self.gi12 = ca.GenomicInterval("1", 990)

    def test_is_overlap(self):
        """Test is_overlap method.
        """
        # Check identical single position intervals
        self.assertTrue(self.gi1.is_overlap(self.gi2))
        # Check nearby single position interval with and without margin
        self.assertFalse(self.gi1.is_overlap(self.gi3))
        self.assertTrue(self.gi1.is_overlap(self.gi3, margin=1))
        # Check intervals intra to another
        self.assertTrue(self.gi4.is_overlap(self.gi10))
        self.assertTrue(self.gi4.is_overlap(self.gi11))
        # Check overlapping two-position intervals
        self.assertTrue(self.gi4.is_overlap(self.gi5))
        self.assertTrue(self.gi4.is_overlap(self.gi6))
        # Check nearby intervals with and without margin
        self.assertFalse(self.gi4.is_overlap(self.gi7))
        self.assertFalse(self.gi4.is_overlap(self.gi7, margin=9))
        self.assertTrue(self.gi4.is_overlap(self.gi7, margin=10))
        # Check intervals on different chromosomes
        self.assertFalse(self.gi1.is_overlap(self.gi8))
        self.assertFalse(self.gi4.is_overlap(self.gi9))
        # Check single position interval near two-position interval
        self.assertFalse(self.gi4.is_overlap(self.gi12))
        self.assertFalse(self.gi4.is_overlap(self.gi12, margin=9))
        self.assertTrue(self.gi4.is_overlap(self.gi12, margin=10))
