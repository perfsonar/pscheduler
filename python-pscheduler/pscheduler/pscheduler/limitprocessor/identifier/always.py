"""
Identifier Class for always
"""

import pscheduler


def data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """

    if isinstance(data, dict) and len(data) == 0:
        return True, "OK"

    return False, "Data is not an object or not empty."



class IdentifierAlways(object):


    """
    Identifier that always identifies
    """


    def __init__(self,
                 data   # Data suitable for this class
                 ):

        valid, message = data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)


    def evaluate(self,
                 hints  # Information used for doing identification
                 ):

        """Always return true"""

        return True


# A short test program

if __name__ == "__main__":

    ident = IdentifierAlways({})

    for ip in [ "10.9.8.6", "198.6.1.1", "fd00:dead:beef::1" ]:
        print(ip, ident.evaluate({ "requester": ip }))
