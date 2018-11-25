#
# Validator for "netreach" Test
#

import ipaddress

from pscheduler import json_validate


def gateway_ip(network, gateway):

    """Calculate the gateway's IP address if it's an integer or
    return what was passed in if it isn't.  Raises ValueError if
    there's a problem."""

    if isinstance(gateway, int):

        if abs(gateway) > (network.num_addresses - 2):
            raise ValueError("Gateway host number is outside the network")

        if gateway < 0:
            gateway -= 1

        return network[gateway]

    elif isinstance(gateway, basestring):

        return ipaddress.ip_address(unicode(gateway))

    else:

        raise ValueError("Unknown gateway type.  Check JSON validation.")




def spec_is_valid(json):
    schema = {
        "local" : {

            "NegativeInteger": {
                "type": "integer",
                "maximum": -1
            },

            "NonzeroInteger": {
                "oneOf": [
                    { "$ref": "#/pScheduler/Cardinal" },
                    { "$ref": "#/local/NegativeInteger" }
                ]
            },

            "GatewayHost": {
                "oneOf": [
                    { "$ref": "#/pScheduler/IPAddress" },
                    { "$ref": "#/local/NonzeroInteger" }
                ]
            },

    "ScanScheme": {
                "type": "string",
                "enum": [ "up", "down", "edges", "random"]
            }
        },

        "type": "object",
        "properties": {
            "schema":            { "$ref": "#/pScheduler/Cardinal" },
            "host":              { "$ref": "#/pScheduler/Host" },
            "host-node":         { "$ref": "#/pScheduler/Host" },
            "network":           { "$ref": "#/pScheduler/IPCIDR" },
            "gateway":           { "$ref": "#/local/GatewayHost" },
            "limit":             { "$ref": "#/pScheduler/Cardinal" },
            "parallel":          { "$ref": "#/pScheduler/Cardinal" },
            "scan":              { "$ref": "#/local/ScanScheme" },
            "timeout":           { "$ref": "#/pScheduler/Duration" }
            },
        "required": [
            "network"
            ]
        }

    (json_valid, message) = json_validate(json, schema)

    if not json_valid and "gateway" not in json:
        return (json_valid, message)

    try:
        network = ipaddress.ip_network(unicode(json["network"]))
        gateway = gateway_ip(network, json["gateway"])
    except ValueError as ex:
        return (False, str(ex))

    if network.num_addresses < 2:
        return (False, "Network must have at least two addresses.")
            
    if network.version != gateway.version:
        return (False, "Network and gateway are not in the same family.")

    if gateway not in network:
        return (False, "Gateway is outside of the network")

    if gateway in [ network[0], network[-1] ]:
        return (False, "Gateway cannot be the network or broadcast address.")


    return (True, "OK")



def result_is_valid(json):
    schema = {
	"type": "object",
        "properties": {
            "schema":       { "$ref": "#/pScheduler/Cardinal" },
            "succeeded":    { "$ref": "#/pScheduler/Boolean" },
            "gateway-up":   { "$ref": "#/pScheduler/Boolean" },
            "network-up":   { "$ref": "#/pScheduler/Boolean" }
            },
        "required": [ "succeeded", "network-up" ]
        }
    return json_validate(json, schema)
