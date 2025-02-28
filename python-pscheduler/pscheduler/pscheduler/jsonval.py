"""
Functions for validating JSON against the pScheduler JSON and standard
values dictionaries
"""

import copy
import jsonschema
import pickle
import sys

# This is patched or filled in during the build process

__default_schema = {

    # TODO: Find out if this is downloaded or just a placeholder
    "$schema": "http://json-schema.org/draft-07/schema#",
    "id": "http://perfsonar.net/pScheduler/json_generic.json",
    "title": "pScheduler Generic Validation Schema",

    "type": "object",
    "additionalProperties": False,

    # A "pScheduler" pair will be added by json_validate()
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

    # Load the dictionary into the default schema if that hasn't
    # already happened.

    if 'pScheduler' not in __default_schema:
        with open('__DATADIR__/json-dictionary.pickled', 'rb') as pickled:
            __default_schema['pScheduler'] = pickle.load(pickled)

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
    schema = copy.copy(__default_schema)

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




def json_validate_from_standard_template(json, template):
    """
    Validate json from a standard template consisting of the following:

    {
      "local": {
          ... JSON Schema for locally-defined objects ...
      },
      "versions": {
        "1": {
           ... JSON Schema for version 1 ...
        },
        "2": {
           ... JSON Schema for version 2 ...
        }
      }
    }

    Return value is the same as for json_validate(), above.
    """

    # Build a temporary structure suitable for json_validate().  This
    # is done manually because using oneOf or anyOf results in error
    # messages that are difficult to decipher.

    schema = json.get("schema", 1)
    if not isinstance(schema, int):
        return ("False", "Schema must be an integer")

    try:
        json_schema = template["versions"][str(schema)]
    except KeyError:
        return (False, "Schema {} is not supported.".format(schema))

    temp_schema = {
        "local": template.get("local", {})
    }

    for field in [ "type", "items", "properties", "additionalProperties", "required" ]:
        try:
            temp_schema[field] = json_schema[field]
        except KeyError:
            pass  # Don't care if it's not there.

    return json_validate(json, temp_schema)



def json_standard_template_max_schema(template):
    """
    Determine the maximum schema in a standard template (see above)
    and make sure there are no gaps in the versions provided.
    """

    versions = 0
    max_version = 0

    for version in template.get("versions", {}):
        max_version = max(int(version), max_version)
        versions += 1

    if versions == 0 or versions != max_version:
        raise ValueError("Schema is missing versions")

    return max_version




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
