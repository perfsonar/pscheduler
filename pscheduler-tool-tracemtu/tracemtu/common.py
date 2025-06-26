#
# Common functions for the tracemtu tool
#

MAX_HOPS = 30
HOP_TIME = 2

def duration():
    '''
    Return the test duration as seconds
    '''
    return (MAX_HOPS * HOP_TIME) + 3
