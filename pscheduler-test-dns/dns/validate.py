#
# Validator for "dns" Test
#

from pscheduler import json_validate

def spec_is_valid(json):
    schema = {
        "local": {
            "RecordType": {
		"type": "string",
		"enum": [ "a", "aaaa", "ns", "cname", "soa", "ptr", "mx", "txt" ]
	    }
	},
        "type": "object",
        "properties": {
            "schema":            { "$ref": "#/pScheduler/Cardinal" },
            "host":              { "$ref": "#/pScheduler/Host" },
            "host-node":         { "$ref": "#/pScheduler/Host" },
            "query":             { "$ref": "#/pScheduler/Host" },
            "record":            { "$ref": "#/local/RecordType" },
            "timeout":           { "$ref": "#/pScheduler/Duration" },
            "nameserver":        { "$ref": "#/pScheduler/Host" },
            },
        "required": [
            "query",
            "record"
            ]
        }
    return json_validate(json, schema)


def result_is_valid(json):
    schema = {
        "local": {

	    # https://tools.ietf.org/html/rfc1035#section-3.4.1
	    "AResult": {
		"type": "array",
		"items": { "$ref": "#/pScheduler/IPv4" },
		"minItems" : 1
	    },

	    # https://tools.ietf.org/html/rfc3596#section-2.2
	    "AAAAResult": {
		"type": "array",
		"items": { "$ref": "#/pScheduler/IPv6" },
		"minItems" : 1
	    },

	    # https://tools.ietf.org/html/rfc1035#section-3.3.1
	    "CNAMEResult": {
		"$ref": "#/pScheduler/Host"
	    },

	    # https://tools.ietf.org/html/rfc1035#section-3.3.9
	    "MXResult": {
		"type": "array",
		"items": {
		    "type": "object",
		    "properties" : {
			"pref": { "$ref": "#/pScheduler/Int16" },
			"mx": { "$ref": "#/pScheduler/Host" }
		    },
		    "required": [ "pref", "mx" ]
		},
		"minItems" : 1
	    },

	    # https://tools.ietf.org/html/rfc1035#section-3.3.11
	    "NSResult": {
		"type": "array",
		"items": { "$ref": "#/pScheduler/Host" },
		"minItems" : 1
	    },

	    # https://tools.ietf.org/html/rfc1035#section-3.3.12
	    "PTRResult": {
		"$ref": "#/pScheduler/Host"
	    },

	    # https://tools.ietf.org/html/rfc1035#section-3.3.14
	    "TXTResult": {
		"type": "array",
		"items": { "$ref": "#/pScheduler/String" },
		"minItems" : 1
	    },

	    # https://tools.ietf.org/html/rfc1035#section-3.3.13
	    "SOAResult": {
		"type": "object",
		"properties": {
		    "nameserver": { "$ref": "#/pScheduler/Host" },
		    "owner": { "$ref": "#/pScheduler/String" },
		    "serial": { "$ref": "#/pScheduler/UInt32" },
		    "refresh": { "$ref": "#/pScheduler/Int32" },
		    "retry": { "$ref": "#/pScheduler/Int32" },
		    "expire": { "$ref": "#/pScheduler/Int32" },
		    "minimum": { "$ref": "#/pScheduler/Int32" }
		},
		"required": [ "nameserver", "owner", "serial", "refresh",
			"retry", "expire", "minimum" ]
	    },

            "DNSRecord": {
		"anyOf": [
		    { "$ref": "#/local/AResult" },
		    { "$ref": "#/local/AAAAResult" },
		    { "$ref": "#/local/MXResult" },
		    { "$ref": "#/local/CNAMEResult" },
		    { "$ref": "#/local/NSResult" },
		    { "$ref": "#/local/SOAResult" },
		    { "$ref": "#/local/PTRResult" },
		    { "$ref": "#/local/TXTResult" },
		    ]
                },
	    },

	"type": "object",
        "properties": {
            "schema": { "$ref": "#/pScheduler/Cardinal" },
            "succeeded": { "$ref": "#/pScheduler/Boolean" },
            "time": { "$ref": "#/pScheduler/Duration" },
	    "record": { "$ref": "#/local/DNSRecord" }
            },
        "required": [ "succeeded" ]
        }
    return json_validate(json, schema)


def limit_is_valid(json):
    schema = {
        "type": "object",
        "properties": {
            "schema":            { "$ref": "#/pScheduler/Cardinal" },
            "host":              { "$ref": "#/pScheduler/Limit/String" },
            "host-node":         { "$ref": "#/pScheduler/Limit/String" },
            "query":             { "$ref": "#/pScheduler/Limit/String" },
            "record":		 { "$ref": "#/pScheduler/Limit/String" },
            "timeout":           { "$ref": "#/pScheduler/Limit/Duration" },
            "nameserver":        { "$ref": "#/pScheduler/Limit/String" },
            },
        "additionalProperties": False
    }
    return json_validate(json, schema)
