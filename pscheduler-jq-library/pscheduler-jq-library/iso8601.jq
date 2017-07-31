#
# Functions for converting ISO 8601 values
#

def duration_as_seconds(value):
  if (value | type) == "string" then
    # TODO: This should barf if the capture doesn't work.
    value
    | ascii_upcase
    | capture("^P0|((?<weeks>([0-9]+))W)?((?<days>([0-9]+))D)?(T((?<hours>([0-9]+))H)?((?<minutes>([0-9]+))M)?((?<seconds>([0-9]+([.][0-9]+)?))S)?)?$")
    | map_values(if . != null then tonumber else 0 end)
    | (.weeks * 604800) + (.days * 86400) + (.hours * 3600) + (.minutes * 60) + .seconds
   else
       null
   end
;
