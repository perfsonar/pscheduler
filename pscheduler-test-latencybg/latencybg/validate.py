#
# Validator for "latency" Test
#

# IMPORTANT:
#
# When making changes to the JSON schemas in this file, corresponding
# changes MUST be made in 'spec-format' and 'result-format' to make
# them capable of formatting the new specifications and results.

from pscheduler import json_validate
from pscheduler import json_validate_from_standard_template
from pscheduler import json_standard_template_max_schema



#
# Specification
#

SPEC_SCHEMA = {

    "local": {
        "packet-interval": {
            "type": "number",
            "exclusiveMinimum": 0.0
        },
        "bucket-width": {
            "type": "number",
            "exclusiveMinimum": 0.0,
        "exclusiveMaximum": 1.0,
            "default": ".001"
        }
    },

    "versions": {
        "1": {
            "type": "object",
            "properties": {
                "schema": {
                    "description": "The version of the schema",
                    "$ref": "#/pScheduler/Cardinal"
                },
                "source": {
                    "description": "The address of the entity sending packets in this test",
                    "$ref": "#/pScheduler/Host"
                },
                "source-node": {
                    "description": "The address of the source pScheduler node, if different",
                    "$ref": "#/pScheduler/URLHostPort"
                },
                "dest": {
                    "description": "The address of the entity receiving packets in this test",
                    "$ref": "#/pScheduler/Host"
                },
                "dest-node": {
                    "description": "The address of the destination pScheduler node, if different",
                    "$ref": "#/pScheduler/URLHostPort"
                },
                "duration": {
                    "description": "The length of time to run the test",
                    "$ref": "#/pScheduler/Duration"
                },
                "packet-count": {
                    "description": "The number of packets to send before reporting a result",
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
                }

            },
            "required": ["dest"]
        },
        "2": {
            "type": "object",
            "properties": {
                "schema": {
                    "description": "The version of the schema",
                    "$ref": "#/pScheduler/Cardinal"
                },
                "source": {
                    "description": "The address of the entity sending packets in this test",
                    "$ref": "#/pScheduler/Host"
                },
                "source-node": {
                    "description": "The address of the source pScheduler node, if different",
                    "$ref": "#/pScheduler/URLHostPort"
                },
                "dest": {
                    "description": "The address of the entity receiving packets in this test",
                    "$ref": "#/pScheduler/Host"
                },
                "dest-node": {
                    "description": "The address of the destination pScheduler node, if different",
                    "$ref": "#/pScheduler/URLHostPort"
                },
                "protocol": {
                    "description": "The protocol to use in making the measurement",
                    "$ref": "#/pScheduler/String"
                },
                "duration": {
                    "description": "The length of time to run the test",
                    "$ref": "#/pScheduler/Duration"
                },
                "packet-count": {
                    "description": "The number of packets to send before reporting a result",
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
                }

            },
            "required": ["dest"]
        }

    }
}


def spec_max_schema():
    return json_standard_template_max_schema(SPEC_SCHEMA)

def spec_is_valid(json):
    return json_validate_from_standard_template(json, SPEC_SCHEMA)


#
# Result
#

RESULT_SCHEMA = {

    "local": {
        "histogram-number-integer": {
            "type": "object",
            "patternProperties": {
                "^[-+]?([0-9]+(\\.[0-9]+)?|\\.[0-9]+)$": { "type": "integer" }
            },
            "additionalProperties": False
        },
        "histogram-integer-integer": {
            "type": "object",
            "patternProperties": {
                "^\\d+$": { "type": "integer" }
            },
            "additionalProperties": False
        },
        "ip-ttl": {
            "type": "integer",
            "minimum": 0,
            "maximum": 255
        }
    },

    "versions": {
        "1": {
            "type": "object",
            "properties": {
                "schema": {
                    "description": "The version of the schema",
                    "$ref": "#/pScheduler/Cardinal"
                },
                "succeeded": {
                    "description": "Indicates if the test ran successfully",
                    "$ref": "#/pScheduler/Boolean"
                },
                "error": {
                    "description": "Errors that occurred",
                    "$ref": "#/pScheduler/String"
                },
                "diags": {
                    "description": "Diagnostic information",
                    "$ref": "#/pScheduler/String"
                },
                "packets-sent": {
                    "description": "The number of packets sent by the sender",
                    "$ref": "#/pScheduler/CardinalZero"
                },
                "packets-received": {
                    "description": "The number of packets received by the receiver",
                    "$ref": "#/pScheduler/CardinalZero"
                },
                "packets-lost": {
                    "description": "The difference between the number of packets sent and received",
                    "$ref": "#/pScheduler/CardinalZero"
                },
                "packets-duplicated": {
                    "description": "The number of duplicate packets seen by the receiver",
                    "$ref": "#/pScheduler/CardinalZero"
                },
                "packets-reordered": {
                    "description": "The number of packets received out of order seen by the receiver",
                    "$ref": "#/pScheduler/CardinalZero"
                },
                "max-clock-error": {
                    "description": "As the maximum estimate of difference between sender and receiver clocks in milliseconds",
                    "$ref": "#/pScheduler/Number"
                },
                "histogram-latency": {
                    "description": "A histogram where the key is observed one-way latency values divided by bucket-width rounded to the nearest two decimal places, and the value is the number of packets that observed that value.",
                    "$ref": "#/local/histogram-number-integer"
                },
                "histogram-ttl": {
                    "description": "A histogram where the key is the IP time-to-live of the packet when it reached the receiver and the value is the number of packets that observed that value",
                    "$ref": "#/local/histogram-integer-integer"
                },
                "raw-packets": {
                    "description": "List of individual packet measurements collected during test",
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "seq-num": {
                                "description": "A monotonically increasing number starting a 0 indicating when the packet was sent in relation to otehr packets ",
                                "$ref": "#/pScheduler/CardinalZero"
                            },
                            "src-ts": {
                                "description": "The timestamp when the packet was sent. Note this is a RFC1305 64-bit timestamp",
                                "$ref": "#/pScheduler/CardinalZero"
                            },
                            "src-clock-sync": {
                                "description": "Indicates if the clock on the sender is synced with NTP",
                                "$ref": "#/pScheduler/Boolean"
                            },
                            "src-clock-err": {
                                "description": "The estimates NTP error of the sender's clock",
                                "$ref": "#/pScheduler/Number"
                            },
                            "dst-ts": {
                                "description": "The timestamp when the packet was received. Note this is a RFC1305 64-bit timestamp",
                                "$ref": "#/pScheduler/CardinalZero"
                            },
                            "dst-clock-sync": {
                                "description": "Indicates if the clock on the receiver is synced with NTP",
                                "$ref": "#/pScheduler/Boolean"
                            },
                            "dst-clock-err": {
                                "description": "The estimates NTP error of the receiver's clock",
                                "$ref": "#/pScheduler/Number"
                            },
                            "ip-ttl": {
                                "description": "The time-to-live value in teh IP header when the packet reached the receiver",
                                "$ref": "#/local/ip-ttl"
                            }
                        },
                        "required": ["seq-num", "src-ts", "src-clock-sync", "dst-ts", "dst-clock-sync", "ip-ttl"]
                    }
                }
            },
            "required": [ "succeeded" ]
        }
    }
}


def result_max_schema():
    return json_standard_template_max_schema(RESULT_SCHEMA)

def result_is_valid(json):
    return json_validate_from_standard_template(json, RESULT_SCHEMA)
