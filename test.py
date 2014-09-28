#!/usr/bin/env python

import boolbins
import unittest
import os.path


SIMPLE_OUT = """
,tests/first9.csv
[],0.7777777777777778
beads,0.2222222222222222
"""
SIMPLE_OUT_WITH_LIMIT = """
,tests/first9.csv
[],0.33333333333333337
beads,0.6666666666666666
"""
MULTIPLE_OUT = """
,tests/first9.csv
[],0.5555555555555556
HLADR,0.2222222222222222
beads,0.1111111111111111
HLADR beads,0.1111111111111111
"""
MULTIPLE_FILES_OUT = """
,tests/first5.csv,tests/first9.csv
[],0.6,0.5555555555555556
HLADR,0.2,0.2222222222222222
beads,0,0.1111111111111111
HLADR beads,0.2,0.1111111111111111
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
        boolbins.run("tests/thresholds_simple.csv", ["tests/first9.csv"], self.output_file, 0)
        self.assertEqual(open(self.output_file, "rU").read().strip(), SIMPLE_OUT.strip())

    def test_one_threshold_with_limit(self):
        boolbins.run("tests/thresholds_simple.csv", ["tests/first9.csv"], self.output_file, 3)
        self.assertEqual(open(self.output_file, "rU").read().strip(), SIMPLE_OUT_WITH_LIMIT.strip())

    def test_multiple_thresholds(self):
        boolbins.run("tests/thresholds_multiple.csv", ["tests/first9.csv"], self.output_file, 0)
        self.assertEqual(open(self.output_file, "rU").read().strip(), MULTIPLE_OUT.strip())

    def test_multiple_thresholds_multiple_files(self):
        boolbins.run("tests/thresholds_multiple.csv", ["tests/first9.csv", "tests/first5.csv"], self.output_file, 0)
        self.assertEqual(open(self.output_file, "rU").read().strip(), MULTIPLE_FILES_OUT.strip())
