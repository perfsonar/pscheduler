#
# Functions for converting ISO 8601 values
#


def invalid_duration(value):
  error("Invalid ISO 8601 duration '\(value)'")
  ;


def duration_as_seconds(value):
  if (value | type) == "string" then
    # TODO: This should barf if the capture doesn't work.
    value
    | ascii_upcase
    | capture("^((P(((?<weeks>([0-9]+))W)?(?<days>([0-9]+))D)?(T((?<hours>([0-9]+))H)?((?<minutes>([0-9]+))M)?((?<seconds>([0-9]+([.][0-9]+)?))S)?)?)|(?<invalid>(.*)))$")
    | (if .invalid != null then invalid_duration(value) else . end)
    | del(.invalid)
    | map_values(if . == null then 0 else tonumber end)
    |   (.weeks * 604800)
      + (.days * 86400)
      + (.hours * 3600)
      + (.minutes * 60)
      + .seconds
  else
    invalid_duration(value)
  end
  ;



# Return an object with a timestamp's disassembled components
def timestamp_parsed(timestamp):
  timestamp
  | capture("^(
             (?<year>([0-9]{4,}))
             -(?<month>([0-9]{1,2}))
             -(?<day>([0-9]{1,2}))
             (T
               (?<hour>([0-9]{1,2}))
               :(?<minute>([0-9]{1,2}))
               (:(?<second>([0-9]{1,2})))?
               (
                (?<z>(Z))
                |((?<offset_hr>[-+][0-9]{2})(:(?<offset_min>[0-9]{2}))?)
               )?
             )?
            )|(?<invalid>.*)$"; "x")
  | if .invalid != null
    then error("Invalid timestamp '\(.invalid)'")
    else .
    end
  | if .z != null then .offset_hr = "0" else . end
  | if .z != null then .offset_min = "0" else . end
  | del(.z)
  | with_entries(select(.value != null ))
  | .
  ;
