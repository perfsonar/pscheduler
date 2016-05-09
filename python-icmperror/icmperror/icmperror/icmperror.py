"""
Functions for translating ICMP error codes to enumerated values.
"""

import json
import sys

icmp_errors = {
    # Strings produced by traceroute, same as ICMP error code counterparts
    'H': 'host-unreachable',
    'N': 'net-unreachable',
    'P': 'protocol-unreachable',
    'S': 'source-route-failed',
    'F':  'fragmentation-needed-and-df-set',
    'X': 'communication-administratively-prohibited',
    'V': 'host-precedence-violation',
    'C': 'precedence-cutoff-in-effect',
    # ICMP Type 3 Error Codes, from RFC 792
    '0':  'net-unreachable',
    '1':  'host-unreachable',
    '2':  'protocol-unreachable',
    '3':  'port-unreachable',
    '4':  'fragmentation-needed-and-df-set',
    '5':  'source-route-failed',
    # ICMP Type 3 Error Codes, from RFC 1122
    '6':  'destination-network-unknown',
    '7':  'destination-host-unknown',
    '8':  'source-host-isolated',
    '9':  'destination-network-administratively-prohibited',
    '10': 'destination-host-administratively-prohibited',
    '11': 'network-unreachable-for-type-of-service',
    '12': 'icmp-destination-host-unreachable-tos',
    # ICMP Type 3 Error Codes, from RFC 1122
    '13': 'communication-administratively-prohibited',
    '14': 'host-precedence-violation',
    '15': 'precedence-cutoff-in-effect'
    }



def translate(code):
    """
    Translate a code which is either a number or single letter,
    optionally preceded by an exclamation point into a string with a
    standardized enumeration of the error.

    For example, 5 or !5 translates to source-route-failed.

    A ValueError is thrown if the code is not valid.
    """
    code = str(code)
    if len(code) and code[0] == '!':
        code = code[1:]

    try:
        return icmp_errors[code]
    except KeyError:
        raise ValueError("Code is not valid")


