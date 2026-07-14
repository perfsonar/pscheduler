# pScheduler Enumeration Simulator

The code in this directory builds a standalone Flask app that serves up.

# Build

This must be run on a working pScheduler server as it gets its data
from the pScheduler API.

From the top of this tree, run `make`.

The completed file, `enumerator`, is a standalone Python app with an
embedded Zip file that can be run anywhere.


## Example Test Data 

This was pulled from the API at `/pscheduler/tests/idle` and
annotated, so it's not valid JSON.

```
{
  "#": "What's in the file says schema 1.  This will be corrected",
  "#": "and won't break anything.",
  "schema": 2,

  "#": "Standard enumeration data used by pScheduler",
  "name": "idle",
  "version": "1.0",
  "maintainer": {
    "href": "http://www.perfsonar.net",
    "name": "perfSONAR Development Team",
    "email": "perfsonar-developer@internet2.edu"
  },
  "description": "Consume time in the background",
  "scheduling-class": "background",

  "#": "Added by the server",
  "href": "https://localhost/pscheduler/tests/idle",

  "#": "Newly-added spec enumeration.",
  "spec": {
    "jsonschema": {
      "#": "Each element in the array represents a schema number.  The",
      "#": "zeroth element is always null because there is no schema 0.",
      "versions": [
        null,
        { ... JSONSchema for Version 1 ... },
        { ... JSONSchema for Version 2 ... }
      ]
    },
    "uischema": {
      "#": "Each element in the array represents a schema number.  The",
      "#": "zeroth element is always null because there is no schema 0.",
      "versions": [
        null,
        { ... JSONSchema for Version 1 ... },
        { ... JSONSchema for Version 2 ... }
      ]
    }
  }
}
```

The parts you care about is going to be .spec.jsonschema.versions and
.spec.uischema.versions, which is are arrays.  Each element represents
a schema number.  The zeroth element is always `null` because there is
no schema zero.  If there is no `schema` in a proposed test spec, it
is safe to assume its value is `1`.  Essentially, you'll pull
`.spec.jsonschema.versions[N]`, where `N` is the schema number.

For the UI, using the latest schema version is recommended.  The fixup
mechanism (which we'll cover later) can knock the schema number down
to the lowest-required value.


## Notes

How to build a standalone Flask app:
https://stackoverflow.com/questions/53240082/how-to-bundle-python-flask-application-into-a-standalone-executable
