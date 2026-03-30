#
# Validator for "latency" Test
#

# IMPORTANT:
#
# When making changes to the JSON schemas in this file, corresponding
# changes MUST be made in 'spec-format' and 'result-format' to make
# them capable of formatting the new specifications and results.

from pscheduler import json_validate


RESPONSE_SCHEMA = {
        "title": "pScheduler One-way Latency Response Schema",
        "type": "object",
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
        "required": ["succeeded"]
    }


def spec_is_valid(json):

    # Build a temporary structure with a reference that points
    # directly at the validator for the specified version of the
    # schema.  Using oneOf or anyOf results in error messages that are
    # difficult to decipher.

    temp_schema = {
        "local": SPEC_SCHEMA["local"],
        "$ref":"#/local/v%s" % json.get("schema", 1)
    }

    return json_validate(json, temp_schema, max_schema=MAX_SCHEMA)


def result_is_valid(json):
    return json_validate(json, RESPONSE_SCHEMA)
