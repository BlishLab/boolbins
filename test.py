import boolbins
import unittest
import os.path


SIMPLE_OUT = """
Filename,(Ce140)Dd: beads
tests/first9.csv,0.2222222222222222
"""
MULTIPLE_OUT = """
Filename,(Cd110)Dd: HLADR,(Ce140)Dd: beads,(Cd110)Dd: HLADR (Ce140)Dd: beads
tests/first9.csv,0.2222222222222222,0.1111111111111111,0.1111111111111111
"""
MULTIPLE_FILES_OUT = """
Filename,(Cd110)Dd: HLADR,(Ce140)Dd: beads,(Cd110)Dd: HLADR (Ce140)Dd: beads
tests/first5.csv,0.2,0,0.2
tests/first9.csv,0.2222222222222222,0.1111111111111111,0.1111111111111111
"""


class TestBasic(unittest.TestCase):
    output_file = "tests/output.csv"
    def cleanup_files(self):
        for f in [self.output_file]:
            if os.path.exists(f):
                os.remove(f)

    def setUp(self):
        self.cleanup_files()
    def tearDown(self):
        self.cleanup_files()

    def test_one_threshold(self):
        boolbins.run(open("tests/thresholds_simple.csv"), ["tests/first9.csv"], self.output_file)
        self.assertEqual(open(self.output_file, "rU").read().strip(), SIMPLE_OUT.strip())

    def test_multiple_thresholds(self):
        boolbins.run(open("tests/thresholds_multiple.csv"), ["tests/first9.csv"], self.output_file)
        self.assertEqual(open(self.output_file, "rU").read().strip(), MULTIPLE_OUT.strip())

    def test_multiple_thresholds_multiple_files(self):
        boolbins.run(open("tests/thresholds_multiple.csv"), ["tests/first9.csv", "tests/first5.csv"], self.output_file)
        self.assertEqual(open(self.output_file, "rU").read().strip(), MULTIPLE_OUT.strip())
