# pScheduler - The perfSONAR Scheduler

pScheduler is the perfSONAR Scheduler, a system for the scheduling and
supervision of automated measurements and sending the results off for
storage.  It is a complete replacement for the Bandwidth Test
Controller (BWCTL), which has been part of perfSONAR since its early
days.  The core development team conducted an evaluation of BWCTL and
BWCTL2 (a re-implementation attempted in 2015) against the list of
features and additional sophistication demanded by the perfSONAR’s
users.  The result of that evaluation was a determination that a
clean-slate redesign and reimplementation was the best option to meet
the new requirements and enable future enhancements without running
afoul of BWCTL’s architectural limitations.

Among the features of the new software are:
 * Significantly-improved visibility into prior, current and scheduled future activities
 * Easy availability of diagnostic information
 * Full-featured, repeating testing for all measurement types baked into the core of the system
 * A more-powerful system for imposing policy-based limits on users
 * A REST API to make the software-based interfacing to perfSONAR easier
 * Standardized, documented data formats based on JavaScript Object Notation (JSON)
 * Hooks for supporting unusual use cases, such as measurements on GÉANT’s MD-VPN platform

The most significant of pScheduler’s new features is extensibility.  A
standard API has been defined for interfacing with implementations of
tests (types of measurements), tools (programs which make the
measurements) and archivers (programs to transfer measurement results
to various kinds long-term storage).  There have been many users
wanting to integrate less-than-mainstream applications with perfSONAR
but have been stymied by a lack of core development team resources.
This architecture will allow members of the community to participate
in development of new tests, tools and archivers with minimal
assistance from the core team.  The larger ecosystem of available
tools will help drive adoption perfSONAR in areas where it would not
have been possible previously.

## Building pScheduler

Documentation on building pScheuler is in the Developer's Guide, which
can be found in the docs directory.  This directory is not currently
part of the build proces and must be built manually.  (See the next
section.) The quickest way to build pScheduler is in the provided Docker
build environment. Run the following commands to build pScheduler:

```
docker-compose up --build -d
docker-compose exec -w /app pscheduler_build make
```

You can also enter the container for debugging purposes or to try pscheduler
after building with the command `docker-compose exec pscheduler_build bash`.
The pscheduler code can be found in `/app`. *Note this is not a shared directory so
changes to code in the container will not be reflected in the code outside the 
container.*


## Building the documentation

_There is a problem builing the documentation on CentOS 7 because
TeXLive was significantly changed and some of the packages we need
aren't as easily installed.  (TODO: Fix this.)_

There's a bit of a chicken-and-egg problem (TODO: fix this), so you'll
need a system with LaTeX to build the manual.

1. `yum -y install texlive-latex`
2. `cd docs`
3. `make`

This will produce PDFs of all documents.
