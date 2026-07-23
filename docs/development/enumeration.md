# Plugin Enumeration

pScheduler plugins enumerate themselves to the system via the
`enumerate` method, which produces JSON on the standard output in a
set format.  Generally, that format is:

```
{
    ... Properties described in enumerate-skeleton.json ...
    "spec": {
        "jsonschema": { ... Contents of spec-jsonschema.json ... },
        "uischema":   { ... Contents of spec-uischema.json ... }
    },
    "result: {
        "jsonschema": { ... Contents of result-jsonschema.json ... }
    },
}
```

Notes:

 * The `spec` property is not present in enumerations for tool
   plugins.

 * The `result` property is present only in the enumerations for
   test plugins.

As part of the build process, files listed below containing JSON
Schema have any references (i.e., `{ "$ref": "#/pScheduler/Cardinal"
}`) replaced with the properties they reference.  Note that this
process is recursive, so references in referenced items will be
resolved properly.


## Plugin Files

### `Makefile`

The directory containing the plugin's source (e.g.,
`pscheduler-test-xxx/xxx`) should contain a `Makefile` that includes
one of the templates installed by the `pscheduler-plugin-makefiles`
package:

```
#
# Makefile for any TYPE class
#

include pscheduler/plugin-TYPE.make
```

Replace `TYPE` with one of `test`, `archive` or `context`.  There is
no `tool` template because tool plugins have very-simple enumerations,
but issue #1658 will add one.

The included template produces two files:

 * `enumerate.json` - A JSON file containing the full enumeration.

 * `enumerate` - An executable that dumps the enumeration to the
   standard output.


### `enumerate-skeleton.json`

This file is the skeletal enumeration for `test`, `archive` and
`context` plugins.  The enumerator for `tool` plugins is still the
simple format used prior to relese 5.3.0 and will probably remain that
way.

 * `schema` - Revision of the full enumeration format.  The
   currently-used version is `2`.

 * `name` - The name of the plugin in lowercase.  This is usually
   taken from the name of the directory where the source code lives.
   For example, if the file lives in
   `pscheduler-test-s3throughput/s3throughput`, this property should
   be `stockprice`.

 * `label` - A human-readable label for the plugin.  For the
   `s3throughput` test plugin, `S3 Throughput` would be a suitable
   value.

 * `description` - A human-readable description of the plugin, e.g.,
   `Measure S3 object service throughput`.

 * `version` - This field is not used to avoid leaking what version of
   pScheduler is installed.  Use `1.0`.

 * `maintainer` - A JSON object containing the following properties:

   * `name` - The name of the plugin's maintainer.  For
     project-maintained plugins, this should be `perfSONAR Development
     Team`.

   * `email` - A contact address for the maintainer.  For
     project-maintained plugins, this should be
     `perfsonar-developer@internet2.edu`.

   * `href` - A web site for the maintainer's organization.  For
     project-maintained plugins, this should be
     `https://www.perfsonar.net`.

 * `scheduling-class` - **For `test` plugins only**, the way tests
   using this plugin should be scheduled.  This must be one of
   `normal`, `background`, `background-multi` or `exclusive`.

 * `json-forms-compatible` - **For `test`, `archive` and `context`
   plugins only**, a boolean indicating whether or not programs that
   use JSON Forms to create data for plugins can do so for this
   plugin.  This is `false` for older plugins that have incompatible
   data structures and are bing phased out.

This is a fully-formed example for the `mtu` test plugin::

```
{
    "schema": 2,
    "name": "mtu",
    "label": "MTU",
    "description": "Measure Maximum Transmission Unit (MTU)",
    "version": "1.0",
    "maintainer": {
        "name": "perfSONAR Development Team",
        "email": "perfsonar-developer@internet2.edu",
        "href": "http://www.perfsonar.net"
    },
    "scheduling-class": "background",
    "json-forms-compatible": true
}
```


### `spec-jsonschema.json`

This file contains validators for a plugin's type-specific data, e.g.,
the parameters for a test.  Its overall arrangement is as follows:

```
{
    "local": { ... Local Definitions ...},

    "versions": [
        null,
        { ... JSONSchema for Version 1  ... },
        { ... JSONSchema for Version 2  ... },
        ...
        { ... JSONSchema for Version n  ... },
    ]
}
```


#### Local Definitions

The `local` property contains JSONSchema definitions of properties
unique to the spec for this plugin.  Its contents are made available
to all versions (see below) for reference as `#/local`.

This is a minimal example.  See the [pScheduler JSON Dictionary
description](json-dictionary.md) for details.

```
"local": {
    "protocol" : {
        "type": "string",
        "enum": [ "icmp", "tcp", "udp" ]     	
    },
    "small-positive": {
        "type": "integer",
        "maxValue": 100
    }
}
```

These could be referenced as `#/local/protocol` and
`#/local/small-positive`.

#### Versions

The `versions` property is an array of objects containing JSON Schema
validators for each version of the schema.  Each element in the array
maps to a schema number, so a schema of `2` would map to
`versions[2]`.

Note that:

 * Because there is no schema `0`, The first (zeroth) element in the
   array must always be `null`.

 * The validator for schema `1` must have the `schema` property
   present and set to a constant value of `1`.  Because the absence of
   a `schema` property is taken to mean `1`, the property **must not**
   appear in the list of `required` properties.

 * Validators for schema `2` and greater must also have the `schema`
   property present and set to a constant value matching the schema
   number.  The property **must** appear in the list of `required`
   properties.


The `pScheduler` (pScheduler JSON dictionary) and `local` (local
definitions; see above) namespaces are made available to the JSON
Schema in each version and may be accessed with a reference (e.g, `{
"$ref": "#/pScheduler/Duration" }`).

Here is a fully-formed example of the `versions` property:

```
"versions": [
    null,

    {
        "type": "object",
        "properties": {
            "schema":     { "$ref": "#/pScheduler/Schema", "const": 1 }
            "x-factor":   { "$ref": "#/local/small-positive" }
         },
         "additionalProperties": false,
         "required": [ "x-factor" ]
    },

    {
        "type": "object",
        "properties": {
            "schema":     { "$ref": "#/pScheduler/Schema", "const": 2 }
            "x-factor":   { "$ref": "#/local/small-positive" }
            "y-factor":   { "$ref": "#/pScheduler/CardinalZero" }
         },
         "additionalProperties": false,
         "required": [ "schema", "x-factor" ]
    }
]


### spec-uischema.json

This file contains [user interface
schema](https://jsonforms.io/docs/uischema) for use with [JSON
Forms](https://jsonforms.io).

Its structure is the same as `spec-jsonschema.json` but does not
include a `local` section because there are no references.


### result-jsonschema.json

This file defines a validator for the result of `test` plugins and
follows the same scheme as `spec-jsonschema.json`.


### `result-uischema.json`  (Nonexistent)

There is no `result-uischema.json` because results are validated and
presented but never edited by humans.
