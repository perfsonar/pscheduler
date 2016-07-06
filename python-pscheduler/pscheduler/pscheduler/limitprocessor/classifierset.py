"""
Set of Classifiers
"""

class ClassifierSet():

    """
    Class that holds and processes identifiers
    """

    def __init__(self,
                 fodder,           # Set of classifiers as read from a limit file
                 identifiers=None, # Identifier set
                 ):

        # This works the reverse of how you might think it would.
        # We're going to be handed a list of identifiers and need to
        # produce a list of the classifications that they fall into.
        # To that end, this builds a hash of lists of classifications
        # keyed by identifier.

        self.iclasses = {}
        self.names = {}

        for classifier in fodder:

            name = classifier['name']

            # Weed out dupes
            if name in self.names:
                raise ValueError("Duplicate classifier '%s'" % name)
            self.names[name] = 1

            for identifier in classifier['identifiers']:
                if identifiers is not None and identifier not in identifiers:
                    raise ValueError("Unknown identifier '%s' in classifier '%s'" \
                                     % (identifier, name))
                if identifier not in self.iclasses:
                    self.iclasses[identifier] = []
                self.iclasses[identifier].append(name)


    def __contains__(self, name):
        return name in self.names


    def classifications(self,
                 identifiers  # List of identifiers to classify
                 ):

        """Given a set of identifiers, return a list of the classifications
        they fall into.

        """

        result = {}

        for candidate in identifiers:
            if candidate in self.iclasses:
                for classification in self.iclasses[candidate]:
                    # Doesn't matter what the value is.
                    result[classification] = 0

        # TODO: Is there any reason to sort this for consistency?
        return result.keys()



# A short test program

if __name__ == "__main__":

    iset = IdentifierSet(
        )

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
        }
        ])

    list = []
    for num in range(0,12):
        print list, '->', cset.classifications(list)
        list.append(str(num))

    while len(list):
        del list[0]
        print list, '->', cset.classifications(list)
