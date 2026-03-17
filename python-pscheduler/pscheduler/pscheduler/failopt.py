"""
Option parser that fails with minimal output when help is requested
"""

import argparse
import optparse
import sys

from .exitstatus import fail


# TODO: This isn't really needed
class FailingArgumentParser(argparse.ArgumentParser):
    '''
    A subclass of argparse that conforms to the expected
    spec-to-cli behavior when '--help' or '-h' is present in the
    arguments::

     - Sends help to the standard error
     - Exits 1

    Don't use this for regular command-line programs.  The epilog
    can be formatted verbatim with
    formatter_class=argparse.RawTextHelpFormatter,
    '''

    def __init__(self, *args, **kwargs):
        '''
        Initialize an instance of the class.
        '''
        super().__init__(*args, **kwargs)

    def parse_args(self, args):
        '''
        Parse the arguments, but behave correctly when asked for
        help.
        '''
        if '--help' in args or '-h' in args:
            help_lines = []
            if self.usage is not None:
                help_lines.append(super().format_usage())
            help_lines.append('Options:\n')
            # TODO: This doesn't work when there are positionals.
            help_lines.extend(super().format_help().split('\n\n', maxsplit=2)[1].split('\n')[1:])

            print('\n'.join(help_lines), file=sys.stderr)
            if self.epilog is not None:
                print(self.epilog, file=sys.stderr)
                exit(1)

        return super().parse_args(args)


class FailingOptionParser(optparse.OptionParser):

    def error(self, error):
        fail(error)

    # This is lifted from OptionParser but doesn't print "Options:"
    # TODO: See about not printing or at least indenting the "--help" line
    def format_option_help(self, formatter=None):
        if formatter is None:
            formatter = self.formatter
        formatter.store_option_strings(self)
        result = []
        formatter.indent()
        if self.option_list:
            result.append(optparse.OptionContainer.format_option_help(self, formatter))
            result.append("\n")
        for group in self.option_groups:
            result.append(group.format_help(formatter))
            result.append("\n")
        formatter.dedent()
        # Drop the last "\n", or the header if no options or option groups:
        return "".join(result[:-1])

    # Format the epilog verbatim
    def format_epilog(self, formatter):
        return self.epilog

    def print_help(self):
        result = [self.format_option_help()]
        if self.epilog is not None:
            result.append(self.format_epilog(None))
        fail("\n".join(result))


if __name__ == "__main__":

    import sys

    opt_parser = FailingOptionParser(epilog="""This is the epilog.
    """)

    opt_parser.add_option("--foo",
                          help="foo",
                          action="store", type="string",
                          dest="foo")

    (options, remaining_args) = opt_parser.parse_args(sys.argv)
    if len(remaining_args) > 1:
        fail("Found extra arguments: %s" % remaining_args)
