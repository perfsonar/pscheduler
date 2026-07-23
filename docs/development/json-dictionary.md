# The pScheduler JSON Dictionary

The JSON dictionary is a compendium of commonly-used types and
structures in [JSON Schema](https://json-schema.org).

The dictionary can be retrieved from the command line of a system with
pScheduler installed by executing `pscheduler internal
json-dictionary`.

## Property Definitions

Validation for each property is defined in the standard JSON Schema way.

**NOTE:** The use of [JSON Schema's boolean schema
  combinators](https://json-schema.org/understanding-json-schema/reference/combining)
  (`allOf`, `anyOf`, `oneOf`, `not`) is discouraged for any property
  that may be displayed with a GUI generated from JSON Schema.  The
  recommended practice is to develop one property for each type (e.g.,
  `IPv4Address` and `IPv6Address`) and one that combines validation of
  those types into a `pattern` or something else suitable.


### JSON Schema Annotations

These [standard JSONSchema
annotations](https://json-schema.org/understanding-json-schema/reference/annotations)
are used in each definition:

 * `title` (Required) - A short, human-readable name for the property.

 * `description` (Optional) - A description of what the property
   represents.  Use of this property makes sense when a definition
   only ever has a single meaning (e.g., an `IPv6FlowLabel` is always
   that and a description of `IPv6 flow label` would be appropriate).
   In other cases, this property should be omitted (e.g., `Duration`
   means different things in differnt contexts).  This field in
   referring properties will override the dictionary.

 * `examples` (Optional but Recommended) - An array of examples of the
   property.  For user interfaces wanting to place a hint in text
   boxes, use of the first element in the array is recommended.  The
   `default` property is not used.


### pScheduler Extensions

pScheduler adds these extensions, all optional but recommended when
appropriate:

 * `x-description-append` - A string to be appended to a referring
   property's `description` as an explanation of that is valid for the
   type.  For example, if a referencing property has a `description`
   of `Run time.`, the appended text in the example below would result
   in `Run time.  This can be any valid ISO 8601 duration.`.

 * `x-invalid-message` - A message to be used when a proposed value
   for the property does not pass validation.

 * `x-info` - An array of links that can be followed for more
   information.  Each link is an object containing the following
   properties:
    * `title` - A human-readable title for the link.
    * `href` - A URL.


### Internal References

References to other properties within the dictionary should be
absolute (e.g., `"#/pScheduler/String'), rather than relative so any
dereferencing happens correctly.


## Complete Example

This is an example of a property definition taken from the dictionary.

```
"Duration": {
  "type": "string",
  "pattern": "...Regular Expression...",
  "title": "Duration",
  "examples": [ "PT10S", "PT45.67S", "PT1H30M", "P1D", "P2D3H37M" ],
  "x-description-append": "This can be any valid ISO 8601 duration.",
  "x-invalid-message": "Invalid ISO 8601 duration.",
  "x-info": [
    {
      "title": "ISO 8601 Durations",
      "href": "https://en.wikipedia.org/wiki/ISO_8601#Durations"
    }
  ]
}
```
