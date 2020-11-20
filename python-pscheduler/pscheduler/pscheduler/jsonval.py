"""
Functions for validating JSON against the pScheduler JSON and standard
values dictionaries
"""

import copy
import jsonschema
import sys

# TODO: Consider adding tile/description and maybe "example" (not
# officially supported) as a way to generate the JSON dictionary.


# Note that adding an "x-invalid-message" string to any type will use
# that value for error messages instead of jsonschema's default.  The
# sequence "%s" in that string will be replaced with the invalid value.
#
# See the definition of "Duration" for an example.


#
# Types from the dictionary
#
__dictionary__ = {
    
    #
    # JSON Types
    #

    "AnyJSON": {
        "anyOf": [
            { "type": "array" },
            { "type": "boolean" },
            { "type": "integer" },
            { "type": "null" },
            { "type": "number" },
            { "type": "object" },
            { "type": "string" }
            ]
        },

    "Array": { "type": "array" },

    "AS": {
        "type": "object",
        "properties": {            
            "number": { "$ref": "#/pScheduler/Cardinal" },
            "owner": { "type": "string" },
            },
        "additionalProperties": False,
        "required": [ "number" ]
        },

    "Boolean": { "type": "boolean" },

    "Cardinal": {
        "type": "integer",
        "minimum": 1,
    },

    "CardinalList": {
        "type": "array",
        "items": { "$ref": "#/pScheduler/Cardinal" },
    },

    "CardinalRange": {
        "type": "object",
        "properties": {
            "lower": { "$ref": "#/pScheduler/Cardinal" },
            "upper": { "$ref": "#/pScheduler/Cardinal" }
        },
        "additionalProperties": False,
        "required": [ "lower", "upper" ]
    },

    "CardinalZero": {
        "type": "integer",
        "minimum": 0,
        },

    "CardinalZeroList": {
        "type": "array",
        "items": { "$ref": "#/pScheduler/CardinalZero" },
    },

    "CardinalZeroRange": {
        "type": "object",
        "properties": {
            "lower": { "$ref": "#/pScheduler/CardinalZero" },
            "upper": { "$ref": "#/pScheduler/CardinalZero" }
        },
        "additionalProperties": False,
        "required": [ "lower", "upper" ]
    },

    "ClockState": {
        "type": "object",
        "properties": {
            "time":         { "$ref": "#/pScheduler/Timestamp" },
            "synchronized": { "$ref": "#/pScheduler/Boolean" },
            "source":       { "$ref": "#/pScheduler/String" },
            "reference":    { "$ref": "#/pScheduler/String" },
            "offset":       { "$ref": "#/pScheduler/Number" },
        },
        "additionalProperties": False,
        "required": [ "time", "synchronized" ]
    },

    "Duration": {
        "type": "string",
        # ISO 8601.  Source: https://gist.github.com/philipashlock/8830168
        # Modified not to accept repeats (e.g., R5PT1M), which we don't support.
        # Modified not to accept months or years, which are inexact.
        "pattern": r'^P(?:\d+(?:\.\d+)?W)?(?:\d+(?:\.\d+)?D)?(?:T(?:\d+(?:\.\d+)?H)?(?:\d+(?:\.\d+)?M)?(?:\d+(?:\.\d+)?S)?)?$',
        "x-invalid-message": "'%s' is not a valid ISO 8601 duration."
        },

    "DurationRange": {
        "type": "object",
        "properties": {
            "lower": { "$ref": "#/pScheduler/Duration" },
            "upper": { "$ref": "#/pScheduler/Duration" }
        },
        "additionalProperties": False,
        "required": [ "lower", "upper" ]
    },

    "Email": { "type": "string", "format": "email" },

    "Float": {
        "type": "number"
    },

    "GeographicPosition": {
        "type": "string",
        # ISO 6709
        # Source:  https://svn.apache.org/repos/asf/abdera/abdera2/common/src/main/java/org/apache/abdera2/common/geo/IsoPosition.java
        "pattern": r'^(([+-]\d{2})(\d{2})?(\d{2})?(\.\d+)?)(([+-]\d{3})(\d{2})?(\d{2})?(\.\d+)?)([+-]\d+(\.\d+)?)?$'
        },

    "Host": {
        "anyOf": [
            { "$ref": "#/pScheduler/HostName" },
            { "$ref": "#/pScheduler/IPAddress" },
        ]
    },

    "HostName": {
        "type": "string",
        "format": "host-name"
        },

    "HostNamePort": {
        # Note that this will cover valid IPv4 addresses, too.
        "type": "string",
        "pattern": r'^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])(:[0-9]+)?$'
    },

    "Integer": { "type": "integer" },

    "IPAddress": {
        "oneOf": [
            { "type": "string", "format": "ipv4" },
            { "type": "string", "format": "ipv6" },
            ]
        },

    "IPv4": { "type": "string", "format": "ipv4" },

    "IPv6": { "type": "string", "format": "ipv6" },

    "IPv6RFC2732": {
        # IPv6 address with optional port, formatted per RFC 2732
        # Source: https://stackoverflow.com/a/17871737/180674
        "type": "string",
        "pattern": r'^\[(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))\](:[0-9]+)?$'
    },

    "IPv4CIDR": {
        "type": "string",
        # Source: http://blog.markhatton.co.uk/2011/03/15/regular-expressions-for-ip-addresses-cidr-ranges-and-hostnames
        "pattern":r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$'
        },

    "IPv6CIDR": {
        "type": "string",
        # Source: http://www.regexpal.com/93988
        "pattern": r'^s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3}))|:)))(%.+)?s*(\/([0-9]|[1-9][0-9]|1[0-1][0-9]|12[0-8]))$'
    },

    "IPCIDR": {
        "oneOf": [
            { "$ref": "#/pScheduler/IPv4CIDR" },
            { "$ref": "#/pScheduler/IPv6CIDR" },
        ]
    },

    "IPCIDRList": {
        "type": "array",
        "items": { "$ref": "#/pScheduler/IPCIDR" }
    },

    "Int8": {
        "type": "integer",
        "minimum": -128,
        "maximum": 127
    },

    "UInt8": {
        "type": "integer",
        "minimum": 0,
        "maximum": 255
    },

    "Int16": {
        "type": "integer",
        "minimum": -32768,
        "maximum": 32767
    },

    "UInt16": {
        "type": "integer",
        "minimum": 0,
        "maximum": 65535
    },

    "Int32": {
        "type": "integer",
        "minimum": -2147483648,
        "maximum": 2147483647
    },

    "UInt32": {
        "type": "integer",
        "minimum": 0,
        "maximum": 4294967295
    },

    "Int64": {
        "type": "integer",
        "minimum": -9223372036854775808,
        "maximum": 9223372036854775807
    },

    "UInt64": {
        "type": "integer",
        "minimum": 0,
        "maximum": 184446744073709551615
        },


    "IPPort": {
        "type": "integer",
        "minimum": 0,
        "maximum": 65535
        },
    
    "IPPortRange": {
        "type": "object",
        "properties": {
            "lower": { "$ref": "#/pScheduler/IPPort" },
            "upper": { "$ref": "#/pScheduler/IPPort" }
        },
        "additionalProperties": False,
        "required": [ "lower", "upper" ]
    },
    
    "IPTOS": {
        "type": "integer",
        "minimum": 0,
        "maximum": 255
        },

    "JQTransformSpecification": {
        "type": "object",
        "properties": {
            "script": { 
                "anyOf": [
                    { "$ref": "#/pScheduler/String" },
                    { "$ref": "#/pScheduler/StringList" },
                ]
            },
            "output-raw": { "$ref": "#/pScheduler/Boolean" },
            "args": { "$ref": "#/pScheduler/AnyJSON" }
        },
        "additionalProperties": False,
        "required": [ "script" ]
    },
    
    "Number": { "type": "number" },

    "Numeric": {
        "anyOf": [
            { "$ref": "#/pScheduler/Number" },
            { "$ref": "#/pScheduler/SINumber" },
            ]
    },

    "NumericRange": {
        "type": "object",
        "properties": {
            "lower": { "$ref": "#/pScheduler/Numeric" },
            "upper": { "$ref": "#/pScheduler/Numeric" }
        },
        "additionalProperties": False,
        "required": [ "lower", "upper" ]
    },

    "POSIXCronSpecification": {
        "type": "string",
        # POSIX-standard spec.  This was generated by
        # scripts/posix-cron-regex; see that for commentary.
        "pattern": r'^(\*|((([0-5]?\d)|(([0-5]?\d)-([0-5]?\d)))(,(([0-5]?\d)|(([0-5]?\d)-([0-5]?\d))))*))\s+(\*|(((([01]?\d)|2[0-3])|((([01]?\d)|2[0-3])-(([01]?\d)|2[0-3])))(,((([01]?\d)|2[0-3])|((([01]?\d)|2[0-3])-(([01]?\d)|2[0-3]))))*))\s+(\*|((((0?[1-9])|([12]\d)|(3[01]))|(((0?[1-9])|([12]\d)|(3[01]))-((0?[1-9])|([12]\d)|(3[01]))))(,(((0?[1-9])|([12]\d)|(3[01]))|(((0?[1-9])|([12]\d)|(3[01]))-((0?[1-9])|([12]\d)|(3[01])))))*))\s+(\*|((((0?[1-9])|(1[0-2]))|(((0?[1-9])|(1[0-2]))-((0?[1-9])|(1[0-2]))))(,(((0?[1-9])|(1[0-2]))|(((0?[1-9])|(1[0-2]))-((0?[1-9])|(1[0-2])))))*))\s+(\*|(([0-6]|([0-6]-[0-6]))(,([0-6]|([0-6]-[0-6])))*))$',
        "x-invalid-message": "'%s' is not a valid cron specification."
    },

    "Probability": {
        "type": "number",
        "minimum": 0.0,
        "maximum": 1.0
        },

    "ProbabilityRange": {
        "type": "object",
        "properties": {
            "lower": { "$ref": "#/pScheduler/Probability" },
            "upper": { "$ref": "#/pScheduler/Probability" }
        },
        "additionalProperties": False,
        "required": [ "lower", "upper" ]
    },

    "RetryPolicy": {
        "type": "array",
        "items": {"$ref": "#/pScheduler/RetryPolicyEntry" }
    },

    "RetryPolicyEntry": {
        "type": "object",
        "properties": {
            "attempts": {"$ref": "#/pScheduler/Cardinal" },
            "wait": {"$ref": "#/pScheduler/Duration" },
        },
        "additionalProperties": False,
        "required": [ "attempts", "wait" ]
    },


    "SINumber":  {
        "oneOf": [
            {
                "type": "string",
                "pattern": "^[0-9]+(\\.[0-9]+)?(\\s*[KkMmGgTtPpEeZzYy][Ii]?)?$"
            },
            {
                "type": "integer"
            }
        ]
    },

    # TODO: This should be subsumed by NumericRange,
    "SINumberRange": {
        "type": "object",
        "properties": {
            "lower": { "$ref": "#/pScheduler/SINumber" },
            "upper": { "$ref": "#/pScheduler/SINumber" }
        },
        "additionalProperties": False,
        "required": [ "lower", "upper" ]
    },

    "String": { "type": "string" },

    "StringList": {
        "type": "array",
        "items": { "$ref": "#/pScheduler/String" }
        },

    "StringMatch": {
        "type": "object",
        "properties": {
            "style": {
                "type": "string",
                "enum": [
                    "exact",
                    "contains",
                    "regex"
                    ],
            },
            "match": { "$ref": "#/pScheduler/String" },
            "case-insensitive": { "$ref": "#/pScheduler/Boolean" },
            "invert": { "$ref": "#/pScheduler/Boolean" },
        },
        "additionalProperties": False,
        "required": [ "style", "match" ]
    },

    "EnumMatch": {
        "type": "object",
        "properties": {
            "enumeration": { "type": "array",
                             "items": {
                                 "anyOf": [{ "type": "string" },
                                           { "$ref": "#/pScheduler/Number" }]
                              }
                           },
            "invert": { "$ref": "#/pScheduler/Boolean" },
        },
        "additionalProperties": False,
        "required": [ "enumeration" ]
    },

    "Timestamp": {
        "type": "string",
        # ISO 8601.  Source: https://gist.github.com/philipashlock/8830168
        "pattern": r'^([\+-]?\d{4}(?!\d{2}\b))((-?)((0[1-9]|1[0-2])(\3([12]\d|0[1-9]|3[01]))?|W([0-4]\d|5[0-2])(-?[1-7])?|(00[1-9]|0[1-9]\d|[12]\d{2}|3([0-5]\d|6[1-6])))([T\s]((([01]\d|2[0-3])((:?)[0-5]\d)?|24\:?00)([\.,]\d+(?!:))?)?(\17[0-5]\d([\.,]\d+)?)?([zZ]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)?)?)?$'
        },

    "TimestampAbsoluteRelative": {
        "oneOf" : [
            { "$ref": "#/pScheduler/Timestamp" },
            { "$ref": "#/pScheduler/Duration" },
            {
                "type": "string",
                # Same pattern as iso8601-duration, with '@' prepended
                "pattern": r'^@(R\d*/)?P(?:\d+(?:\.\d+)?Y)?(?:\d+(?:\.\d+)?M)?(?:\d+(?:\.\d+)?W)?(?:\d+(?:\.\d+)?D)?(?:T(?:\d+(?:\.\d+)?H)?(?:\d+(?:\.\d+)?M)?(?:\d+(?:\.\d+)?S)?)?$'
                }
            ]
        },

    "URL": { "type": "string", "format": "uri" },

    "URLHostPort": {
        # Any valid host/port pair as you'd find in a URI per RFC 2396
        "anyOf": [
            { "$ref": "#/pScheduler/HostNamePort" },
            { "$ref": "#/pScheduler/IPv6RFC2732" },
        ]

    },

    "UUID": {
        "type": "string",
        "pattern": r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$'
        },

    "Version": {
        "type": "string",
        "pattern": r'^[0-9]+(\.[0-9]+)*[A-Za-z0-9-+]*$'
        },


    #
    # Compound Types
    #

    "ArchiveSpecification_V1": {
        "type": "object",
        "properties": {
            "schema": {
                "type": "integer",
                "enum": [ 1 ]
            },
            "archiver": { "type": "string" },
            "data": { "$ref": "#/pScheduler/AnyJSON" },
            "transform": { "$ref": "#/pScheduler/JQTransformSpecification" },
            "ttl": { "$ref": "#/pScheduler/Duration" },
            },
        "additionalProperties": False,
        "required": [
            "archiver",
            "data",
            ]
        },

    "ArchiveSpecification_V2": {
        "type": "object",
        "properties": {
            "schema": {
                "type": "integer",
                "enum": [ 2 ]
            },
            "runs": {
                "type": "string",
                "enum": [
                    "all",
                    "succeeded",
                    "failed"
                    ]
            },
            "archiver": { "type": "string" },
            "data": { "$ref": "#/pScheduler/AnyJSON" },
            "transform": { "$ref": "#/pScheduler/JQTransformSpecification" },
            "ttl": { "$ref": "#/pScheduler/Duration" },
            "uri-host": { "$ref": "#/pScheduler/URLHostPort" }
            },
        "additionalProperties": False,
        "required": [
            "schema",
            "archiver",
            "data",
            ]
        },

    "ArchiveSpecification_V3": {
        "type": "object",
        "properties": {
            "schema": {
                "type": "integer",
                "enum": [ 3 ]
            },
            "runs": {
                "type": "string",
                "enum": [
                    "all",
                    "succeeded",
                    "failed"
                    ]
            },
            "label": { "type": "string" },
            "archiver": { "type": "string" },
            "data": { "$ref": "#/pScheduler/AnyJSON" },
            "transform": { "$ref": "#/pScheduler/JQTransformSpecification" },
            "ttl": { "$ref": "#/pScheduler/Duration" },
            "uri-host": { "$ref": "#/pScheduler/URLHostPort" }
            },
        "additionalProperties": False,
        "required": [
            "schema",
            "archiver",
            "data",
            ]
        },

    "ArchiveSpecification": {
        "oneOf": [
            { "$ref": "#/pScheduler/ArchiveSpecification_V1" },
            { "$ref": "#/pScheduler/ArchiveSpecification_V2" },
            { "$ref": "#/pScheduler/ArchiveSpecification_V3" }
            ]
        },


    "ContextSpecificationSingle": {
        "type": "object",
        "properties": {
            "context": { "type": "string" },
            "data": { "$ref": "#/pScheduler/AnyJSON" }
            },
        "additionalProperties": False,
        "required": [
            "context",
            "data"
            ]
        },

    "ContextSpecificationList": {
        "type": "array",
        "items": { "$ref": "#/pScheduler/ContextSpecificationSingle" },
    },

    "ContextSpecificationListList": {
        "type": "array",
        "items": { "$ref": "#/pScheduler/ContextSpecificationList" },
    },

    "ContextSpecification": {
        "type": "object",
        "properties": {
            "schema":   { "$ref": "#/pScheduler/Cardinal" },
            "contexts": { "$ref": "#/pScheduler/ContextSpecificationListList" }
            },
        "additionalProperties": False,
        "required": [
            "contexts"
            ]
        },


    "Maintainer": {
        "type": "object",
        "properties": {
            "name":  { "type": "string" },
            "email": { "$ref": "#/pScheduler/Email" },
            "href":  { "$ref": "#/pScheduler/URL" },
            },
        "additionalProperties": False,
        "required": [
            "name",
            ]
        },

    "NameVersion": {
        "type": "object",
        "properties": {
            "name":    { "type": "string" },
            "version": { "$ref": "#/pScheduler/Version" },
            },
        "additionalProperties": False,
        "required": [
            "name",
            "version",
            ]
        },

    "ParticipantResult": {
        "type": "object",
        "properties": {
            "participant": { "$ref": "#/pScheduler/Host" },
            "result":      { "$ref": "#/pScheduler/AnyJSON" },
            },
        "additionalProperties": False,
        "required": [
            "participant",
            "result",
            ]
        },

    "RunResult": {
        "type": "object",
        "properties": {
            "id":           { "$ref": "#/pScheduler/UUID" },
            "schedule":     { "$ref": "#/pScheduler/TimeRange" },
            "test":         { "$ref": "#/pScheduler/TestSpecification" },
            "tool":         { "$ref": "#/pScheduler/NameVersion" },
            "participants": {
                "type": "array",
                "items": { "$ref": "#/pScheduler/ParticipantResult" },
                },
            "result":       { "$ref": "#/pScheduler/AnyJSON" }
            },
        "additionalProperties": False,
        "required": [
            "id",
            "schedule",
            "test",
            "tool",
            "participants",
            "result",
            ]
        },

    "ScheduleSpecification_V1": {
        "type": "object",
        "properties": {
            "schema":   {
                "type": "integer",
                "enum": [ 1 ]
                },
            "start":    { "$ref": "#/pScheduler/TimestampAbsoluteRelative" },
            "slip":     { "$ref": "#/pScheduler/Duration" },
            "sliprand": { "$ref": "#/pScheduler/Boolean" },
            "repeat":   { "$ref": "#/pScheduler/Duration" },
            "until":    { "$ref": "#/pScheduler/TimestampAbsoluteRelative" },
            "max-runs": { "$ref": "#/pScheduler/Cardinal" },
            },
        "additionalProperties": False
        },

    "ScheduleSpecification_V2": {
        "type": "object",
        "properties": {
            "schema":   {
                "type": "integer",
                "enum": [ 2 ]
                },
            "start":    { "$ref": "#/pScheduler/TimestampAbsoluteRelative" },
            "slip":     { "$ref": "#/pScheduler/Duration" },
            "sliprand": { "$ref": "#/pScheduler/Boolean" },
            "repeat":   { "$ref": "#/pScheduler/Duration" },
            "repeat-cron": { "$ref": "#/pScheduler/POSIXCronSpecification" },
            "until":    { "$ref": "#/pScheduler/TimestampAbsoluteRelative" },
            "max-runs": { "$ref": "#/pScheduler/Cardinal" },
            },
        "required": [ "schema" ],
        "additionalProperties": False
        },

    "ScheduleSpecification": {
        "anyOf": [
            { "$ref": "#/pScheduler/ScheduleSpecification_V1" },
            { "$ref": "#/pScheduler/ScheduleSpecification_V2" }
            ]
        },


    # TODO: There are still some data types undefined, mainly because we cannot
    # find agents that will return such data types yet
    "SNMPNumericOID": {
        "type": "string",
        "pattern": r'^((\.\d)|\d)+(\.\d+)*$'
    },

    # must contain at least one letter to be considered alphanumeric
    "SNMPAlphaNumOID": {
        "type": "string",
        "pattern": r'[a-z][A-Z]*'
    },

    "SNMPResultOID": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "pattern": r'^ObjectIdentity$'
            },
            "value": { "$ref": "#/pScheduler/String" }
        },
        "additionalProperties": True,
        "required": [
            "type",
            "value"
        ]
    },

    "SNMPOID": {
        "anyOf": [
            { "$ref": "#/pScheduler/SNMPNumericOID" },
            { "$ref": "#/pScheduler/SNMPAlphaNumOID"},
            { "$ref": "#/pScheduler/SNMPResultOID"}
        ]
    },

    "SNMPInteger": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "pattern": r'^Integer$'
            },
            "value": { "$ref": "#/pScheduler/Integer" }
        },
        "additionalProperties": True,
        "required": [
            "type",
            "value"
        ]
    },

    "SNMPUnsigned32": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "pattern": r'^Unsigned32$'
            },
            "value": { "$ref": "#/pScheduler/UInt32"}
        },
        "additionalProperties": True,
        "required": [
            "type",
            "value"
        ]
    },

    "SNMPString": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "pattern": r'String$'
            },
            "value": { "$ref": "#/pScheduler/String"}
        },
        "additionalProperties": True,
        "required": [
            "type",
            "value"
        ]
    },

    "SNMPOpaque": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "pattern": r'^Opaque$'
            },
            "value": { "$ref": "#/pScheduler/String"}
        },
        "additionalProperties": True,
        "required": [
            "type",
            "value"
        ]
    },

    "SNMPIPAddress": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "pattern": r'^IpAddress$'
            },
            "value": { "$ref": "#/pScheduler/IPAddress"}
        },
        "additionalProperties": True,
        "required": [
            "type",
            "value"
        ]
    },

    "SNMPCounter32": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "pattern": r'^Counter32$'
            },
            "value": { "$ref": "#/pScheduler/UInt32"}
        },
        "additionalProperties": True,
        "required": [
            "type",
            "value"
        ]
    },

    "SNMPCounter64": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "pattern": r'^Counter64$'
            },
            "value": { "$ref": "#/pScheduler/UInt64"}
        },
        "additionalProperties": True,
        "required": [
            "type",
            "value"
        ]
    },

    "SNMPGauge32": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "pattern": r'^Gauge32$'
            },
            "value": { "$ref": "#/pScheduler/UInt32"}
        },
        "additionalProperties": True,
        "required": [
            "type",
            "value"
        ]
    },

    "SNMPTimeticks": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "pattern": r'^TimeTicks$'
            },
            "value": { "$ref": "#/pScheduler/Integer" }
        },
        "additionalProperties": True,
        "required": [
            "type",
            "value"
        ]
    },

    "SNMPBits": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "pattern": r'^Bits$'
            },
            "value": { "$ref": "#/pScheduler/String"},
        },
        "additionalProperties": True,
        "required": [
            "type",
            "value"
        ]
    },

    "SNMPOther": {
        "type": "object",
        "properties": {
            "type": { "$ref": "#/pScheduler/AnyJSON" },
            "value": { "$ref": "#/pScheduler/AnyJSON" }
        },
        "additionalProperties": True,
        "required": [
            "value"
        ]
    },

    "SNMPResult": {
        "anyOf": [
            { "$ref": "#/pScheduler/SNMPOID" },
            { "$ref": "#/pScheduler/SNMPInteger" },
            { "$ref": "#/pScheduler/SNMPUnsigned32" },
            { "$ref": "#/pScheduler/SNMPString" },
            { "$ref": "#/pScheduler/SNMPOpaque" },
            { "$ref": "#/pScheduler/SNMPIPAddress" },
            { "$ref": "#/pScheduler/SNMPCounter32" },
            { "$ref": "#/pScheduler/SNMPCounter64" },
            { "$ref": "#/pScheduler/SNMPGauge32" },
            { "$ref": "#/pScheduler/SNMPTimeticks" },
            { "$ref": "#/pScheduler/SNMPBits" },
            { "$ref": "#/pScheduler/SNMPOther" }
        ]
    },

    "SNMPResultList": {
        "type": "array",
        "items": { "$ref": "#/pScheduler/SNMPResult" }
    },

    "TaskSpecification_V1": {

        "type": "object",
        "properties": {
            "schema":   {
                "type": "integer",
                "enum": [ 1 ]
                },
            "lead-bind":{ "$ref": "#/pScheduler/Host" },
            "test":     { "$ref": "#/pScheduler/TestSpecification" },
            "tool":     { "$ref": "#/pScheduler/String" },
            "tools":    { "$ref": "#/pScheduler/StringList" },
            "schedule": { "$ref": "#/pScheduler/ScheduleSpecification" },
            "archives": {
                "type": "array",
                "items": { "$ref": "#/pScheduler/ArchiveSpecification" },
                },
            "reference": { "$ref": "#/pScheduler/AnyJSON" },
            "_key": { "$ref": "#/pScheduler/String" },
        },
        "additionalProperties": False,
        "required": [
            "test",
            ]
        },

    "TaskSpecification_V2": {
        "type": "object",
        "properties": {
            "schema":   {
                "type": "integer",
                "enum": [ 2 ]
                },
            "lead-bind":{ "$ref": "#/pScheduler/Host" },
            "test":     { "$ref": "#/pScheduler/TestSpecification" },
            "tool":     { "$ref": "#/pScheduler/String" },
            "tools":    { "$ref": "#/pScheduler/StringList" },
            "schedule": { "$ref": "#/pScheduler/ScheduleSpecification" },
            "archives": {
                "type": "array",
                "items": { "$ref": "#/pScheduler/ArchiveSpecification" },
                },
            "contexts": { "$ref": "#/pScheduler/ContextSpecification" },
            "reference": { "$ref": "#/pScheduler/AnyJSON" },
            "_key": { "$ref": "#/pScheduler/String" },
        },
        "additionalProperties": False,
        "required": [
            "schema",
            "test",
            ]
        },

    "TaskSpecification_V3": {
        "type": "object",
        "properties": {
            "schema":   {
                "type": "integer",
                "enum": [ 3 ]
                },
            "lead-bind":{ "$ref": "#/pScheduler/Host" },
            "test":     { "$ref": "#/pScheduler/TestSpecification" },
            "tool":     { "$ref": "#/pScheduler/String" },
            "tools":    { "$ref": "#/pScheduler/StringList" },
            "schedule": { "$ref": "#/pScheduler/ScheduleSpecification" },
            "priority": { "$ref": "#/pScheduler/Integer" },
            "archives": {
                "type": "array",
                "items": { "$ref": "#/pScheduler/ArchiveSpecification" },
                },
            "contexts": { "$ref": "#/pScheduler/ContextSpecification" },
            "reference": { "$ref": "#/pScheduler/AnyJSON" },
            "_key": { "$ref": "#/pScheduler/String" },
        },
        "additionalProperties": False,
        "required": [
            "schema",
            "test",
            ]
        },

    "TaskSpecification_V4": {
        "type": "object",
        "properties": {
            "schema":   {
                "type": "integer",
                "enum": [ 4 ]
                },
            "lead-bind":{ "$ref": "#/pScheduler/Host" },
            "test":     { "$ref": "#/pScheduler/TestSpecification" },
            "tool":     { "$ref": "#/pScheduler/String" },
            "tools":    { "$ref": "#/pScheduler/StringList" },
            "schedule": { "$ref": "#/pScheduler/ScheduleSpecification" },
            "priority": { "$ref": "#/pScheduler/Integer" },
            "archives": {
                "type": "array",
                "items": { "$ref": "#/pScheduler/ArchiveSpecification" },
                },
            "contexts": { "$ref": "#/pScheduler/ContextSpecification" },
            "reference": { "$ref": "#/pScheduler/AnyJSON" },
            "_key": { "$ref": "#/pScheduler/String" },
            "debug": { "$ref": "#/pScheduler/Boolean" },
        },
        "additionalProperties": False,
        "required": [
            "schema",
            "test",
            ]
        },

    "TaskSpecification": {
        "anyOf": [
            { "$ref": "#/pScheduler/TaskSpecification_V1" },
            { "$ref": "#/pScheduler/TaskSpecification_V2" },
            { "$ref": "#/pScheduler/TaskSpecification_V3" },
            { "$ref": "#/pScheduler/TaskSpecification_V4" }
            ]
        },


    "TestSpecification": {
        "type": "object",
        "properties": {
            "type": { "$ref": "#/pScheduler/String" },
            "spec": { "$ref": "#/pScheduler/AnyJSON" },
            },
        "additionalProperties": False,
        "required": [
            "type",
            "spec",
            ],
        },

    "TimeRange": {
        "type": "object",
        "properties": {
            "start": { "$ref": "#/pScheduler/Timestamp" },
            "end":   { "$ref": "#/pScheduler/Timestamp" },
            },
        "additionalProperties": False
        },




    #
    # Standard Values
    #
    # Note that these are lowercase with hyphens, matching the style
    # of the names used.
    #

    # TODO: Put this into the documentation
    "icmp-error": {
        "type": "string",
        "enum": [
            'net-unreachable',
            'host-unreachable',
            'protocol-unreachable',
            'port-unreachable',
            'fragmentation-needed-and-df-set',
            'source-route-failed',
            'destination-network-unknown',
            'destination-host-unknown',
            'source-host-isolated',
            'destination-network-administratively-prohibited',
            'destination-host-administratively-prohibited',
            'network-unreachable-for-type-of-service',
            'icmp-destination-host-unreachable-tos',
            'communication-administratively-prohibited',
            'host-precedence-violation',
            'precedence-cutoff-in-effect',
            ]
        },

    "ip-version": {
        "type": "integer",
        "enum": [ 4, 6 ]
        },

    "ip-version-list": {
        "type": "array",
        "items": { "$ref": "#/pScheduler/ip-version" },
        },


    #
    # Standard Limit Types
    #

    "Limit": {

        "Boolean": {
            "type": "object",
            "properties": {
                "description":  { "$ref": "#/pScheduler/String" },
                "match":        { "$ref": "#/pScheduler/Boolean" },
                "fail-message": { "$ref": "#/pScheduler/String" }
            },
            "additionalProperties": False,
            "required": [ "match" ]
        },

        "Cardinal": {
            "type": "object",
            "properties": {
                "description":  { "$ref": "#/pScheduler/String" },
                "range":        { "$ref": "#/pScheduler/CardinalRange" },
                "invert":       { "$ref": "#/pScheduler/Boolean" }
            },
            "additionalProperties": False,
            "required": [ "range" ]
        },

        "CardinalList": {
            "type": "object",
            "properties": {
                "description":  { "$ref": "#/pScheduler/String" },
                "match":        { "$ref": "#/pScheduler/CardinalList" },
                "invert":       { "$ref": "#/pScheduler/Boolean" }
            },
            "additionalProperties": False,
            "required": [ "match" ]

        },

        "CardinalZero": {
            "type": "object",
            "properties": {
                "description":  { "$ref": "#/pScheduler/String" },
                "range":        { "$ref": "#/pScheduler/CardinalZeroRange" },
                "invert":       { "$ref": "#/pScheduler/Boolean" }
            },
            "additionalProperties": False,
            "required": [ "range" ]
        },

        "CardinalZeroList": {
            "type": "object",
            "properties": {
                "description":  { "$ref": "#/pScheduler/String" },
                "match":        { "$ref": "#/pScheduler/CardinalZeroList" },
                "invert":       { "$ref": "#/pScheduler/Boolean" }
            },
            "additionalProperties": False,
            "required": [ "match" ]

        },

        "Duration": {
            "type": "object",
            "properties": {
                "description":  { "$ref": "#/pScheduler/String" },
                "range":        { "$ref": "#/pScheduler/DurationRange" },
                "invert":       { "$ref": "#/pScheduler/Boolean" }
            },
            "additionalProperties": False,
            "required": [ "range" ]
        },

        "SINumber": {
            "properties": {
                "description":  { "$ref": "#/pScheduler/String" },
                "range":        { "$ref": "#/pScheduler/SINumberRange" },
                "invert":       { "$ref": "#/pScheduler/Boolean" }
            },
            "additionalProperties": False,
            "required": [ "range" ]
        },

        "IPVersion": {
            "properties": {
                "description": { "$ref": "#/pScheduler/String" },
                "match":       { "$ref": "#/pScheduler/ip-version" },
                "invert":      { "$ref": "#/pScheduler/Boolean" }
            },
            "additionalProperties": False,
            "required": ["version"]  
        },

        "IPCIDRList": {
            "properties": {
                "description": { "$ref": "#/pScheduler/String" },
                "cidr":        { "$ref": "#/pScheduler/IPCIDRList" },
                "invert":      { "$ref": "#/pScheduler/Boolean" }
                }
        },

        "IPVersionList": {
            "properties": {
                "description": { "$ref": "#/pScheduler/String" },
                "enumeration": { "$ref": "#/pScheduler/ip-version-list"},
                "invert":      { "$ref": "#/pScheduler/Boolean" }
            },
            "additionalProperties": False,
            "required": ["enumeration"]  
        },

        "Probability": {
            "properties": {
                "description": { "$ref": "#/pScheduler/String" },
                "range":       { "$ref": "#/pScheduler/ProbabilityRange" },
                "invert":      { "$ref": "#/pScheduler/Boolean" }
            },
            "additionalProperties": False,
            "required": [ "range" ]
        },

        "String": {
            "type": "object",
            "properties": {
                "description":  { "$ref": "#/pScheduler/String" },
                "match":        { "$ref": "#/pScheduler/StringMatch" },
                "fail-message": { "$ref": "#/pScheduler/String" }
            },
            "additionalProperties": False,
            "required": [ "match" ]
        }

    },

    #
    # Standard Plugin Enumeration Types
    #

    "PluginEnumeration": {

        "Test": {
            "type": "object",
            "properties": {
                "schema":       { "$ref": "#/pScheduler/Cardinal" },
                "name":         { "$ref": "#/pScheduler/String" },
                "description":  { "$ref": "#/pScheduler/String" },
                "version":      { "$ref": "#/pScheduler/Version" },
                "maintainer":   { "$ref": "#/pScheduler/Maintainer" },
                "scheduling-class": { 
                    "type": "string",
                    "enum": [
                        "background",
                        "background-multi",
                        "exclusive",
                        "normal"
                    ]
                }
            },
            "additionalProperties": False,
            "required": [
                "name",
                "description",
                "version",
                "maintainer",
                "scheduling-class"
            ]
        },

        "Tool": {
            "type": "object",
            "properties": {
                "schema":       { "$ref": "#/pScheduler/Cardinal" },
                "name":         { "$ref": "#/pScheduler/String" },
                "description":  { "$ref": "#/pScheduler/String" },
                "version":      { "$ref": "#/pScheduler/Version" },
                "tests":        { "$ref": "#/pScheduler/StringList" },
                "preference":        { "$ref": "#/pScheduler/Integer" },
                "maintainer":   { "$ref": "#/pScheduler/Maintainer" },
                "scheduling-class": { 
                    "type": "string",
                    "enum": [
                        "background",
                        "background-multi",
                        "exclusive",
                        "normal"
                    ]
                }
            },
            "additionalProperties": False,
            "required": [
                "name",
                "description",
                "version",
                "tests",
                "preference",
                "maintainer"
            ]
        },

        "Archiver": {
            "type": "object",
            "properties": {
                "schema":       { "$ref": "#/pScheduler/Cardinal" },
                "name":         { "$ref": "#/pScheduler/String" },
                "description":  { "$ref": "#/pScheduler/String" },
                "version":      { "$ref": "#/pScheduler/Version" },
                "maintainer":   { "$ref": "#/pScheduler/Maintainer" }
            },
            "additionalProperties": False,
            "required": [
                "name",
                "description",
                "version",
                "maintainer"
            ]
        },

        "Context": {
            "type": "object",
            "properties": {
                "schema":       { "$ref": "#/pScheduler/Cardinal" },
                "name":         { "$ref": "#/pScheduler/String" },
                "description":  { "$ref": "#/pScheduler/String" },
                "version":      { "$ref": "#/pScheduler/Version" },
                "maintainer":   { "$ref": "#/pScheduler/Maintainer" }
            },
            "additionalProperties": False,
            "required": [
                "name",
                "description",
                "version",
                "maintainer"
            ]
        },


    }
}



__default_schema__ = {

    # TODO: Find out if this is downloaded or just a placeholder
    "$schema": "http://json-schema.org/draft-07/schema#",
    "id": "http://perfsonar.net/pScheduler/json_generic.json",
    "title": "pScheduler Generic Validation Schema",

    "type": "object",
    "additionalProperties": False,

    "pScheduler": __dictionary__
}




def json_validate(json, skeleton, max_schema=None):
    """Validate JSON against a jsonschema schema.

    The skeleton is a dictionary containing a partial,
    draft-07-compatible jsonschema schema, containing only the
    following:

        type         (array, boolean, integer, null, number, object, string)
        items        (Only when type is array)
        properties   (Only when type is object)
        additionalProperties  (Only when type is an object)
        required     Required items
        local        (Optional; see below.)
        $ref         (Optional; see below.)

    The optional 'local' element is a dictionary which may be used for
    any local definitions to be referenced from the items or
    properties sections.

    The standard pScheduler types are available for reference as
    "#/pScheduler/TypeName", where TypeName is a standard pScheduler
    type as defined in the "pScheduler JSON Style Guide and Type
    Dictionary" document."

    Schemas that want to refer to a single object in their local
    sections or something from the pScheduler can use "$ref":
    "#/path/to/definition" instead of type, items and properties as
    they would when defining a regular object.

    Tip:  If your schema needs to be allOf/anyOf/oneOf/not at the top,
    build it in local and use a $ref to refer to it.

    If max_schema is present and an integer, the JSON will be checked
    for having an integer "schema" value which is less than or equal
    to max_schema.

    The values returned are a tuple containing a boolean indicating
    whether or not the JSON was valid and a string containing any
    error messages if not.

    """

    # Validate what came in

    if not isinstance(json, dict):
        raise ValueError("JSON provided must be a dictionary.")

    if not isinstance(skeleton, dict):
        raise ValueError("Skeleton provided must be a dictionary.")

    if max_schema is not None:

        if not isinstance(max_schema, int):
            raise ValueError("Maximum schema provided must be an integer.")

        schema = json.get("schema", 1)

        if not isinstance(schema, int):
            return (False, "Schema value must be an integer.")

        if schema > max_schema:
            return (False,
                    "Schema version %d is not supported (highest is %d)." % (schema, max_schema))



    # Build up the schema from the dictionaries and user input.

    # A shallow copy is sufficient for this since we don't clobber the
    # innards.
    schema = copy.copy(__default_schema__)

    for element in [ 'type', 'items', 'properties', 'additionalProperties',
                     'required', 'local', '$ref' ]:
        if element in skeleton:
            schema[element] = skeleton[element]

    # Let this throw whatever it's going to throw, since schema errors
    # are problems wih the software, not the data.

    jsonschema.Draft7Validator.check_schema(schema)

    try:
        jsonschema.validate(json, schema,
                            format_checker=jsonschema.draft7_format_checker
        )
    except jsonschema.exceptions.ValidationError as ex:

        try:
            message = ex.schema["x-invalid-message"].replace("%s", ex.instance)
        except (KeyError, TypeError):
            message = ex.message

        path = "/".join([str(x) for x in ex.absolute_path])
        return (False, "At /%s: %s" % (path, message))

    return (True, 'OK')


# Test program

if __name__ == "__main__":

    sample = {
        "schema": 1,
        "when": "2015-06-12T13:48:19.234",
        "howlong": "PT10Mxx",
        "sendto": "bob@example.com",
        "x-factor": 3.14,
        "protocol": "udp",
        "ipv": 6,
        "ip": "fc80:dead:beef::",
#        "archspec": { "name": "foo", "data": None },
        }

    schema = {
        "local": {
            "protocol": {
                "type": "string",
                "enum": ['icmp', 'udp', 'tcp']
                }
            },
        "type": "object",
        "properties": {
            "schema":   { "$ref": "#/pScheduler/Cardinal" },
            "when":     { "$ref": "#/pScheduler/Timestamp" },
            "howlong":  { "$ref": "#/pScheduler/Duration" },
            "sendto":   { "$ref": "#/pScheduler/Email" },
            "ipv":      { "$ref": "#/pScheduler/ip-version" },
            "ip":       { "$ref": "#/pScheduler/IPAddress" },
            "protocol": { "$ref": "#/local/protocol" },
            "x-factor": { "type": "number" },
            "archspec": { "$ref": "#/pScheduler/ArchiveSpecification" },

            },
        "required": [ "sendto", "x-factor" ]
        }

    valid, message = json_validate(sample, schema)

    print(valid, message)



    text = {
        "schema": 2,
        "test": {
            "test": "rtt",
            "spec": {
                "dest": "www.notonthe.net"
            }
        },
        "archives": [
        ]
    }

    print(json_validate({"text": text}, {
        "type": "object",
        "properties": {
            "text": { "$ref": "#/pScheduler/TaskSpecification" }
        },
        "required": [ "text" ]
    }))
