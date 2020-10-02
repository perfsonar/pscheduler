#!/usr/bin/env python3
# Test program

import pscheduler
import validate

if __name__ == "__main__":

    sample = {
        "schema": 1,
        "succeeded": True,
        "record": [ ]
        }
    print(validate.result_is_valid( sample ))

    sample = {
        "schema": 1,
        "succeeded": True,
        "record": [ "" ]
        }
    print(validate.result_is_valid( sample ))

    sample = {
        "schema": 1,
        "succeeded": True,
        "record": "hostname.com"
        }
    print(validate.result_is_valid( sample ))

    sample = {
        "schema": 1,
        "succeeded": True,
        "record": [ "hostname.com" ]
        }
    print(validate.result_is_valid( sample ))

    sample = {
        "schema": 1,
        "succeeded": True,
        "record": [ "hostname.com", "over.yonder.org" ]
        }
    print(validate.result_is_valid( sample ))

    sample = {
        "schema": 1,
        "succeeded": True,
        "record": [ 1, "hostname.com", 2, "over.yonder.org" ]
        }
    print(validate.result_is_valid( sample ))

    sample = {
        "schema": 1,
        "succeeded": True,
        "record": [ [ 1, "hostname.com" ] ]
        }
    print(validate.result_is_valid( sample ))

    sample = {
        "schema": 1,
        "succeeded": True,
        "record": [ [ 1, "hostname.com" ] ]
        }
    print(validate.result_is_valid( sample ))

    sample = {
        "schema": 1,
        "succeeded": True,
        "record": [ [ 1, "hostname.com" ] ]
        }
    print(validate.result_is_valid( sample ))

    sample = {
        "schema": 1,
        "succeeded": True,
        "record": [ [ 1, "hostname.com" ] ]
        }
    print(validate.result_is_valid( sample ))

    sample = {
        "schema": 1,
        "succeeded": True,
        "record": [ "domain.com", "owner", 1, 2, 3, 4, 5, 6 ]
        }
    print(validate.result_is_valid( sample ))

    sample = {
        "schema": 1,
        "succeeded": True,
        "record": [ "domain.com", "owner", 1, 2, 3, 4, 5 ]
        }
    print(validate.result_is_valid( sample ))

    sample = {
        "schema": 1,
        "succeeded": True,
        "record": [ "domain.com", "owner", "1", "2", "3", "4", "5" ]
        }
    print(validate.result_is_valid( sample ))

    sample = {
        "schema": 1,
        "succeeded": True,
        "record": [ "txt" ]
        }
    print(validate.result_is_valid( sample ))

    sample = {
        "schema": 1,
        "succeeded": True,
        "record": [ "txt", "more text" ]
        }
    print(validate.result_is_valid( sample ))

    sample = {
        "schema": 1,
        "succeeded": True,
        "record": [ { "pref": 1, "mx" : "hostname.com" } ]
        }
    print(validate.result_is_valid( sample ))

    sample = {
        "schema": 1,
        "succeeded": True,
        "record": [ { "pref": 1, "mx" : "hostname.com" },
        { "pref": 2, "mx" : "somewhere.com" } ]
        }
    print(validate.result_is_valid( sample ))

