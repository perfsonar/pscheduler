#
# Validator for "netreach" Test
#

# IMPORTANT:
#
# When making changes to the JSON schemas in this file, corresponding
# changes MUST be made in 'spec-format' and 'result-format' to make
# them capable of formatting the new specifications and results.

import ipaddress

from pscheduler import json_validate

def check_spec_semantics(proposed):

    def gateway_ip(network, gateway):

        '''Calculate the gateway's IP address if it's an integer or
        return what was passed in if it isn't.  Raises ValueError if
        there's a problem.'''
        
        if isinstance(gateway, int):

            if abs(gateway) > (network.num_addresses - 2):
                raise ValueError('Gateway host number is outside the network')

            if gateway < 0:
                gateway -= 1

            return network[gateway]

        elif isinstance(gateway, str):

            return ipaddress.ip_address(str(gateway))

        else:

            raise ValueError('Unknown gateway type.  Check JSON validation.')


    try:
        network = ipaddress.ip_network(str(proposed['network']))
    except ValueError as ex:
        return (False, 'Invalid network: %s' % (str(ex)))

    if network.num_addresses <= 2:
        return (False, 'Network must have at least two host addresses.')

    try:
        gateway = gateway_ip(network, proposed['gateway'])
    except KeyError:
        gateway = network[1]  # Use first host to make other tests pass
    except ValueError as ex:
        return (False, str(ex))
            
    if network.version != gateway.version:
        return (False, 'Network and gateway are not in the same family.')

    if gateway not in network:
        return (False, 'Gateway is outside of the network')

    if gateway in [ network[0], network[-1] ]:
        return (False, 'Gateway cannot be the network or broadcast address.')

    return (True, 'OK')




def result_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":       { "$ref": "#/pScheduler/Cardinal" },
            "succeeded":    { "$ref": "#/pScheduler/Boolean" },
            "error":        { "$ref": "#/pScheduler/String" },
            "diags":        { "$ref": "#/pScheduler/String" },
            "gateway-up":   { "$ref": "#/pScheduler/Boolean" },
            "network-up":   { "$ref": "#/pScheduler/Boolean" }
            },
        "required": [ "succeeded", "network-up" ]
        }
    return json_validate(json, schema)
