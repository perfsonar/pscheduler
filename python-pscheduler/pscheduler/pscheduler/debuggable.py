"""
Class to add easy debugging to other classes
"""

class Debuggable(object):
    """
    Class to add easy debugging to other classes

    Example usage:

        def do_a_debug(*args):
            print(*args)

        class Foo(pscheduler.Debuggable):
            def __init__(self, debug=None, label=None):
                super().__init__(debug=debug, label=label)

            def foo(self):
                self.debug("Doing a foo")


        f = Foo(debug=do_a_debug, label="My Foo")
        f.foo()
    """
    def __init__(self, debug=lambda s: None, label=None):
        """
        Create a debuggable.  Args:
          debug - Lambda to call with a single argument to be logged
          label - Prefix to be added; will be nicely formatted.
        """

        if not callable(debug):
            raise ValueError("Debug must be callable with a single argument.")
        self._debug = debug
        self._label = "%s: " % (label) if label else "xxx"

    def debug(self, fmt, *args):
        # No args means don't try formatting the string.
        message = fmt % args if args else fmt
        self._debug("%s%s" % (self._label, message))
