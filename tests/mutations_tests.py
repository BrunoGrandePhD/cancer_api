import unittest
import cancer_api as ca
import tests_setup


class TestSingleNucleotideVariant(unittest.TestCase):

    def setUp(self):
        """Create SNVs for testing
        """
        # Obtain shared db session
        self.session = tests_setup.session
        # Create some SNVs
        self.snv1 = ca.SingleNucleotideVariant(chrom="1", pos=1000, ref_allele="A",
                                               alt_allele="G", ref_count=10, alt_count=10,
                                               library_id=1, status="somatic")
        self.snv2 = ca.SingleNucleotideVariant(chrom="1", pos=1000, ref_allele="A",
                                               alt_allele="C", ref_count=10, alt_count=10,
                                               library_id=1, status="somatic")
        self.snv3 = ca.SingleNucleotideVariant(chrom="1", pos=1001, ref_allele="T",
                                               alt_allele="G", ref_count=10, alt_count=10,
                                               library_id=1, status="somatic")
        self.snv4 = ca.SingleNucleotideVariant(chrom="2", pos=1000, ref_allele="A",
                                               alt_allele="G", ref_count=10, alt_count=10,
                                               library_id=1, status="somatic")

    def test_add_to_db(self):
        """Test adding SNVs to database"""
        # Add instances to db
        session = self.session
        session.add(self.snv1)
        session.add(self.snv2)
        session.add(self.snv3)
        session.add(self.snv4)
        session.commit()
        # Check if db is populated
        self.assertEqual(session.query(ca.SingleNucleotideVariant).count(), 4)

    def test_is_overlap(self):
        """Test is_overlap method"""
        # Test overlap without margin
        self.assertTrue(self.snv1.is_overlap("1", 1000))
        self.assertFalse(self.snv1.is_overlap("1", 1001))
        self.assertTrue(self.snv2.is_overlap("1", 1000))
        self.assertFalse(self.snv2.is_overlap("1", 1001))
        self.assertFalse(self.snv3.is_overlap("1", 1000))
        self.assertTrue(self.snv3.is_overlap("1", 1001))
        # Test overlap with margin
        self.assertTrue(self.snv1.is_overlap("1", 1000, margin=1))
        self.assertTrue(self.snv1.is_overlap("1", 1001, margin=1))
        # Test wit different chromosomes
        self.assertFalse(self.snv1.is_overlap("2", 1000))
        self.assertTrue(self.snv4.is_overlap("2", 1000))


class TestStructuralVariation(unittest.TestCase):

    def setUp(self):
        """Create a list of structural variations"""
        # Set up db
        self.session = tests_setup.session
        # Inter-chromosomal SV
        self.sv1 = ca.StructuralVariation(chrom1="1", pos1=1000, strand1="+",
                                          chrom2="2", pos2=2000, strand2="-",
                                          sv_type="translocation", library_id=1,
                                          status="somatic")
        # Intra-chromosomal SV
        self.sv2 = ca.StructuralVariation(chrom1="3", pos1=1000, strand1="+",
                                          chrom2="3", pos2=2000, strand2="+",
                                          sv_type="inversion", library_id=1,
                                          status="somatic")

    def test_add_to_db(self):
        """Test adding SVs to database"""
        # Add instances to db
        session = self.session
        session.add(self.sv1)
        session.add(self.sv2)
        session.commit()
        # Check if db is populated
        self.assertEqual(session.query(ca.StructuralVariation).count(), 2)

    def test_predict_effects(self):
        """Testing effect prediction for SVs
        """

    def test_is_overlap(self):
        """Test the is_overlap method for structural variations
        """
        # Test proximity with one position without margin
        self.assertFalse(self.sv1.is_overlap("1", 995))
        self.assertTrue(self.sv1.is_overlap("1", 1000))
        # Test proximity with one position with margin
        self.assertTrue(self.sv1.is_overlap("1", 995, margin=5))
        self.assertTrue(self.sv1.is_overlap("1", 1000, margin=5))
        # Test proximity with two positions without margin
        self.assertFalse(self.sv1.is_overlap("1", 995, 999))
        self.assertTrue(self.sv1.is_overlap("1", 995, 1001))
        # Test proximity with two positions with margin
        self.assertTrue(self.sv1.is_overlap("1", 995, 999, margin=5))
        self.assertTrue(self.sv1.is_overlap("1", 995, 1001, margin=5))
        # Test overlap with two position with inter-chromosomal event
        self.assertTrue(self.sv1.is_overlap("1", 500, 1500))
        self.assertFalse(self.sv1.is_overlap("2", 500, 1500))
        self.assertTrue(self.sv1.is_overlap("2", 1500, 2500))
        # Test overlap with one position in middle of intra-chromosomal event
        self.assertTrue(self.sv2.is_overlap("3", 1500))
        # Test overlap with two positions in middle of intra-chromosomal event
        self.assertTrue(self.sv2.is_overlap("3", 1400, 1600))
        # Test overlap with two positions overlapping with intra-chromosomal event
        self.assertTrue(self.sv2.is_overlap("3", 500, 1500))
        self.assertTrue(self.sv2.is_overlap("3", 1500, 2500))
        self.assertFalse(self.sv2.is_overlap("3", 500, 990))
        self.assertFalse(self.sv2.is_overlap("3", 500, 990, margin=9))
        self.assertTrue(self.sv2.is_overlap("3", 500, 990, margin=10))
