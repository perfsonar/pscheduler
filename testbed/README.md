# pScheduler Test Bed Configuration



## Building the Configuration

 * Install the prerequisites:
   * Red Hat:  `dnf -y install make python3`
   * Debian:  `apt-get -y install make python3`

 * Run `make`

 * Find the ready-to-use mesh in `testbed.json`.


## Configuration Files


`skeleton/output.json` - Contains a skeletal version of a pSConfig
file and includes globally-significant data such as the administrator
information.  All other configuration is built atop this one.

`members/members` - Lists the hosts that will be part of the test bed.
Each entry consists of a FQDN and a label that will be translated into
an `address` entry in the finished pSConfig file.  The address entries
will be merged into groups as described below.

`schedules/intervals` - Lists the ISO 8601 durations that will be made
available as standard entries in the `schedules` section of the
pSConfig file.


## Plugin Configuration Files

Each plugin may, optionally, contribute tests and tasks to the
configuration by placing a file named `testbed.json` in its top-level
directory (e.g., `pscheduler-tool-iperf2/testbed.json`).  Note that
only directories for known plugin types (`archiver` , `context` ,
`test` or `tool`) will be probed for these files.

Inside the file


Identifiers for tests and tasks must be unique to avoid colliding with
those in other plugins.  The recommended convention is to use the full
name of the plugin package as a prefix, (e.g.,
`pscheduler-tool-iperf3-udp`).




Construction of the final `testbed.json` 

 * Each measurement will be sent to all of the archivers listed in the
   `archives` section.

A suitable sample for each type may be found in these plugins:

 * Test:  `pscheduler-test-idle/testbed.json`
 * Tool:  `pscheduler-tool-iperf3/testbed.json`
 * Archiver: `pscheduler-archiver-syslog/testbed.json`
 * Context:  `TODO:`

```
{
    "tasks": {
	"pscheduler-tool-iperf-tcp": {
	    "_meta": {
		"display-name": "Throughput - Iperf3 TCP"
	    },
	    "schedule": "PT4H",
	    "test": "pscheduler-tool-iperf3-tcp",
	    "tools": [ "iperf3" ]
	},
	"pscheduler-tool-iperf3-udp": {
	    "_meta": {
		"display-name": "Throughput - Iperf3 UDP"
	    },
	    "schedule": "PT4H",
	    "test": "pscheduler-tool-iperf3-udp",
	    "tools": [ "iperf3" ]
	}

    },
    "tests": {
	"pscheduler-tool-iperf3-tcp": {
	    "type": "throughput",
	    "spec": {
		"source": "{% address[0] %}",
		"dest": "{% address[1] %}",
		"duration": "PT20S"
	    }
	},
	"pscheduler-tool-iperf3-udp": {
	    "type": "throughput",
	    "spec": {
		"udp": true,
		"source": "{% address[0] %}",
		"dest": "{% address[1] %}",
		"duration": "PT20S"
	    }
	}	
    }
}
```


## Development Notes

Everything in this directory is designed to work on a minimal system
with no perfSONAR components intstalled.  Ergo, it is preferable to
write a Python script to process the data rather than using jq.
