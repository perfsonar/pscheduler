"""
Set of Classifiers
"""

import copy


require_tests = {
    "none": lambda identified, total: identified == 0,
    "one":  lambda identified, total: identified == 1,
    "any":  lambda identified, total: identified > 0,
    "all":  lambda identified, total: identified == total
}

class ClassifierSet(object):

    """
    Class that holds and processes identifiers
    """

    def __init__(self,
                 fodder,           # Set of classifiers as read from a limit file
                 identifiers       # An IdentifierSet
                 ):

        self.classifiers = {}

        # Create a summary of what the classifiers want

        for classifier in fodder:

            name = classifier["name"]
            if name in self.classifiers:
                raise ValueError("Duplicate classifier '%s'" % name)

            # Make sure all of the identifiers called for 
            class_identifiers = classifier["identifiers"]
            missing = list(filter(
                lambda identifier: identifier not in identifiers,
                list(class_identifiers)
            ))
            if missing:
                raise ValueError("Unknown identifiers: %s" % (", ".join(missing)))

            self.classifiers[name] = {
                "identifiers": class_identifiers,
                "check_count": require_tests[classifier.get("require", "any")]
            }


    def __contains__(self, name):
        return name in self.classifiers


    def classifications(self,
                 identifiers  # List of identifiers to classify
                 ):

        """
        Given a set of identifiers, return a list of the classifications
        they fall into.
        """

        identifier_lookup = dict([ (name, 1) for name in identifiers ])

        classified = []

        for name in self.classifiers:
            classifier = self.classifiers[name]
            met = (list(filter(lambda value: value in identifier_lookup, classifier["identifiers"])))
            if classifier["check_count"](len(met), len(classifier["identifiers"])):
                classified.append(name)

        # TODO: Is there any reason to sort this for consistency?
        return classified



# A short test program

if __name__ == "__main__":

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
    for num in range(0,10):
        print(idents, '->', cset.classifications(idents))
        idents.append(str(num))

    while len(idents):
        del idents[0]
        print(idents, '->', cset.classifications(idents))
