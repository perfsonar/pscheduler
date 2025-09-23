#!/usr/bin/env python3
"""
Test for ClassifierSet
"""

import unittest

from test_base import PschedTestBase

from pscheduler.limitprocessor.classifierset import *


class TestClassifierSet(PschedTestBase):
    """
    Basic tests for classifier set
    """

    def test_classifier_set(self):
        cset = ClassifierSet([
            {
                "name": "neither",
                "description": "Neither odd nor even",
                "identifiers": [ "0" ]
            },
            {
                "name": "odd",
                "description": "Odd",
                "identifiers": [ "1", "3", "5", "7", "9" ],
            },
            {
                "name": "even",
                "description": "Even",
                "identifiers": [ "2", "4", "6", "8", "10" ],
            },
            {
                "name": "small",
                "description": "small numbers",
                "identifiers": [ "1", "2", "3" ],
            },
            {
                "name": "no-small",
                "description": "No small numbers",
                "identifiers": [ "1", "2", "3" ],
                "require": "none"
            },
            {
                "name": "one-small",
                "description": "Small odd numbers.",
                "identifiers": [ "1", "2", "3" ],
                "require": "one"
            },
            {
                "name": "small-odd",
                "description": "Small odd numbers.",
                "identifiers": [ "1", "3" ],
                "require": "any"
            },
            {
                "name": "set-of-three",
                "description": "Some set of three.",
                "identifiers": [ "4", "5", "6" ],
                "require": "all"
            }
            ],
            {
                "0": 0,
                "1": 1,
                "2": 2,
                "3": 3,
                "4": 4,
                "5": 5,
                "6": 6,
                "7": 7,
                "8": 8,
                "9": 9,
                "10": 10
            }
        )

        idents = ["3", "5", "7"]
        self.assertEqual(cset.classifications(idents[0]),["odd", "small", "one-small", "small-odd"])
        self.assertEqual(cset.classifications(idents), ['odd', 'small', 'one-small', 'small-odd'])
        idents.append("4")
        self.assertEqual(cset.classifications(idents), ['odd', 'even', 'small', 'one-small', 'small-odd'])

if __name__ == '__main__':
    unittest.main()
