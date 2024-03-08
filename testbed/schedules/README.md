# Testbed Schedules

When adding new repeat intervals:

Add one named for the time:

```
"PT30M": {               Named for the ISO interval
    "repeat": "PT30M",   Same as the name
    "slip": "PT15M",     Half the interval
    "sliprand": true     Allow random slip
}
```

Add a "strict" version:

```
"PT30S-strict": {        Named for the ISO interval + "-strict"
    "repeat": "PT30S",   Same as the name
    "slip": "PT30S",     Shorter of interval or PT3M
    "sliprand": false    No random slip
}
```
