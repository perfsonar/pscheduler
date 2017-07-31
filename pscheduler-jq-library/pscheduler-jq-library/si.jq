#
# SI Number Conversion Functions
#

def multiplier(prefix):
{
  "":   1,
  "k":  1000,
  "m":  1000000,
  "g":  1000000000,
  "t":  1000000000000,
  "p":  1000000000000000,
  "e":  1000000000000000000,
  "z":  1000000000000000000000,
  "y":  1000000000000000000000000,
  "ki": 1024,
  "mi": 1048576,
  "gi": 1073741824,
  "ti": 1099511627776,
  "pi": 1125899906842624,
  "ei": 1152921504606846976,
  "zi": 1180591620717411303424,
  "yi": 1208925819614629174706176
}[prefix];


def as_integer(value):
if (value | type) == "string"
then
  # TODO: This should barf if the capture doesn't work.
  value
    | ascii_downcase
    | capture("^(?<number>[0-9]+([.][0-9]+)?)(?<unit>([kmgtpezy]i?)?)$")
    | (.number|tonumber) * multiplier(.unit)
    | floor
else
  if (value | type) == "number"
  then
    value
  else
    # This should be an error.
    null
  end
end
;
