#
# Validator for "latency" Test
#

from pscheduler import json_validate

def spec_is_valid(json):
    schema = {
            "title": "pScheduler One-way Latency Request Schema",
            "type": "object",
            "local": {
                "packet-interval": {
                    "type": "number",
                    "minimum": 0,
                    "exclusiveMinimum": True
                },
                "bucket-width": {
                    "type": "number",
                    "minimum": 0,
                    "exclusiveMinimum": True,
                    "maximum": 1,
                    "exclusiveMaximum": True,
                    "default": ".001"
                },
            },
            "properties": {
                "schema": {
                    "description": "The version of the schema",
                    "$ref": "#/pScheduler/Cardinal"
                },
                "source": {
                    "description": "The address of the entity sending packets in this test",
                    "$ref": "#/pScheduler/Host"
                },
                "dest": {
                    "description": "The address of the entity receiving packets in this test",
                    "$ref": "#/pScheduler/Host"
                },
                "packet-count": {
                    "description": "The number of packets to send",
                    "$ref": "#/pScheduler/Cardinal"
                },
                "packet-interval": {
                    "description": "The number of seconds to delay between sending packets",
                    "$ref": "#/local/packet-interval"
                    
                },
                "packet-timeout": {
                    "description": "The number of seconds to wait before declaring a packet lost",
                    "$ref": "#/pScheduler/CardinalZero"
                },
                "packet-padding": {
                    "description": "The size of padding to add to the packet in bytes",
                    "$ref": "#/pScheduler/CardinalZero"
                },
                "ctrl-port": {
                    "description": "The control plane port to use for the entity acting as the server (the dest if flip is not set, the source otherwise)",
                    "$ref": "#/pScheduler/IPPort"
                },
                "data-ports": {
                    "description": "The port range to use on the side of the test running the client. At least two ports required.",
                    "$ref": "#/pScheduler/IPPortRange"
                },
                "ip-tos": {
                    "description": "DSCP value for TOS byte in the IP header as an integer",
                    "$ref": "#/pScheduler/IPTOS"
                },
                "ip-version": {
                    "description": "Force a specific IP address type used performing the test. Useful when specifying hostnames as source or dest that may map to both IPv4 and IPv6 addresses.", 
                    "$ref": "#/pScheduler/ip-version" 
                },
                "bucket-width": {
                    "description": "The bin size to use for histogram calculations. This value is divided into the result as reported in seconds and truncated to the nearest 2 decimal places.",
                    "$ref": "#/local/bucket-width" 
                },
                "output-raw": {
                    "description": "Output individual packet statistics. This will substantially increase the size of a successful result.",
                    "$ref": "#/pScheduler/Boolean"
                },
                "flip": {
                    "description": "In multi-participant mode, have the dest start the client and request a reverse test. Useful in some firewall and NAT environments.",
                    "$ref": "#/pScheduler/Boolean"
                },
                "single-participant-mode": {
                    "description": "Do not coordinate with the remote side. Useful for cases where remote side is not running pScheduler but known to have necessary daemon for test.",
                    "$ref": "#/pScheduler/Boolean"
                }
        
            },
            "anyOf": [
                { "required": ["schema", "source", "dest"] },
                { "required": ["schema", "dest"] }
            ]
        }
    return json_validate(json, schema)
