'''
Functions for determining assistance servers
'''

def assist(option, args=[], parameters={}):
    '''Determine what server to use for pScheduler assistance based
    on an assist string, command-line arguments and a hash of test parameters.

    Parameters:

      option - String value of option from the command line.  This
               will be returned verbatim if it looks valid and doesn't
               begin with a period.  If it begins with a period, the
               remainder will be split on commas and the arguments and
               parameters will be searched for something that matches
               (e.g., '.host,source' will match the --host or --source
               arguments in --host x or --host=x format or an item in
               the paramters named 'host' or 'source').

      args - Array of unprocessed command-line arguments

      parameters - Hash of test parameters.

    Returns a string with the assist value or raises a ValueError if
    something is wrong.

    '''

    assert isinstance(option, str) or option is None
    assert isinstance(args, list)
    assert isinstance(parameters, dict)

    if option is None:
        return None

    if len(option) == 0:
        raise ValueError('Invalid assist string.')

    if option == 'auto':
        option = '.host-node,source-node,host,source'

    if option[0] != '.':
        return option

    for search_name in map(lambda s: s.strip(), option[1:].split(',')):

        # Command Line

        # Pre-formatted options
        search_opt = f'--{search_name}'
        search_assign = f'{search_opt}='

        for index, item in enumerate(args):

            if item == search_assign:
                # --xxx= alone doesn't contain anything useful.
                raise ValueError(f'Invalid option {item} for assist')
            elif item.startswith(search_assign):
                # Use what's beyond the =
                return item[len(search_assign):]
            elif item == search_opt:
                # --xxx means use the next argument if it exists.
                try:
                    return args[index+1]
                except IndexError:
                    raise ValueError(f'No argument present for {search_opt}.')

        # Test Parameters

        try:
            value = parameters[search_name]
            if not isinstance(value, str):
                raise ValueError(f'''Parameter 'search_name' in test parameters is not a string''')
            return value
        except KeyError:
            pass

    raise ValueError('Nothing found in test parameters for assist.')
