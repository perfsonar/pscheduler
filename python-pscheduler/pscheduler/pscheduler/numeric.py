"""
Classes for dealing with numeric values.
"""

class HighInteger(object):

    """Integer that maintains its highest-ever value."""

    def __init__(self, initial=None):
        """Construct a high integer."""
        self.__value = initial

    def set(self, new_value):
        """Set the value to new_value if higher than the old one."""

        if type(new_value) != int:
            raise ValueError("Value must be an integer.")

        if self.__value is None or new_value > self.__value:
            self.__value = new_value

    def value(self):
        """Return the current value"""
        return self.__value



# Test program

if __name__ == "__main__":

    high = HighInteger()
    high.set(5)
    high.set(4)
    high.set(3)
    print high.value()
