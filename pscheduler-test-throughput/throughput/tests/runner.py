#!/usr/bin/python

import unittest
import os
from os import listdir
from os.path import isfile, join

path = os.path.dirname(os.path.realpath(__file__))

test_files = [f for f in listdir(path) if isfile(join(path, f)) and f.startswith("test") and f.endswith('.py')]

suite = unittest.TestSuite()

for f in test_files:
    suite.addTest(unittest.defaultTestLoader.loadTestsFromName(f[:-3]))

unittest.TextTestRunner().run(suite)
