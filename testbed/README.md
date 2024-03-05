# pScheduler Test Bed Configuration

Scattered throughout the sources for the pScheduler plugins are files named `psconfig-testbed`.



# Tes

```
{
    "_meta": {
    },
    "addresses": {},
    "archives": {
    },
    "groups": {
    },
    "schedules": {
	"PT5M" {
	    "repeat": "PT5M",
	    "slip": "PT2M30S",
	    "sliprand": true
	}
    },
    "tasks": {
    },
    "tests": {
    }
}

## Naming

Anything added by a plugin package should be prefixed with its name,
e.g. `pscheduler-tool-iperf3-udp`.

## Schedules

Standard schedules are available

 * `PT30S`
 * `PT1M`
 * `PT5M`
 * `PT10M`
 * `PT15M`
 * `PT30M`
 * `PT1H`
 * `PT4H`
 * `PT6H`
 * `PT12H`
 * `P1D`

A plugin may define its own schedules

