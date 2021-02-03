# Generic Makefile for RPM and Debian packages

This includable Makefile automatically builds packages for Red Hat-
and Debian-derived systems depending on the environment.

The sources, patches and packaging instructions live in a directory
called the _package directory_ that serves as the root of everything
for that package.  A typical build would consist of multiple package
directories built in dependency order.

## Installation

RPM systems require the following packages preinstalled:

 * TODO: Write this.

Debian systems require the following packages preinstalled:

 * TODO: Write this.

The package uses itself to do a build and install, so simply running
`make cbic` (clean, build, install, re-clean) in its package directory
will get the job done.


## Preparing The Package Directory

The package directory contains a number of files and subdirectories
that comprise everything needed to build the package.

### Makefile

For all packages, create a `Makefile` in the package directory
containing the following:

```
# Makefile for any package
inclulde make/generic-package.make
```


### Sources

Source code may be in the form of a tarball downloaded from another
source or a directory containing the sourc code.

#### Tarball

A tarball containing the sources for the package should be placed in
the package directory and named using the customary
_PACKAGE_-_VERSION_.tar.gz format (e.g., `foomatic-2.9.38.tar.gz`) .

Place the RPM spec and `debian` directory in the package directory
alongside the tarball.

For example:
```
ls -R foomatic
foomatic:
debian  foomatic-2.9.38.tar.gz  drop-in.spec  Makefile

foomatic/debian:
changelog  compat  control  copyright  rules  source

foomatic/debian/source:
format
```

#### Source Directory

For packages whose sources are developed locally (i.e., are not
distributed as tarballs from another source), the sources may be
placed in a subdirectory the package directory named for the package.

The Makefile will locate the RPM spec or `debian` directory within the
source directory if one exists.  Note that there must be exactly one
`.spec` file or `debian` directory within the source tree or the build
will fail.

For RPM specs, the `Source0` tag should be
`%{name}-%{version}.tar.gz`.  The Makefile will automatically create
the tarball as part of the packaging process.

A typical package directory using a source directory would be laid out
like this:

```
ls -R foomatic
foomatic/:
Makefile  foomatic

foomatic/foomatic:
debian  foomatic.1  foomatic.c  foomatic.spec  Makefile

foomatic/debian:
changelog  compat   control  copyright  patches  postinst
postrm     preinst  prerm    rules      source

foomatic/foomatic/debian/source:
format
```

### Patches

Files containing modifications to be made to the sources during the
build should be placed in the package directory, named so they will
sort into the order in which they should be applied.  For example:

```
foomatic-01-divide-by-zero.patch
foomatic-02-segfault.patch
```
#### Debian

The names of the patches should be listed in the
`debian/patches/series` file but not placed in the `debian/patches`
directory unless they are Debian-specific modifications.  The Makefile
will place them during the build.


#### RPM

The RPM spec must list the patches in the header section and apply
them in the proper order:

```
Patch0:  foomatic-01-divide-by-zero.patch
Patch1:  foomatic-02-segfault.patch
  ...
  %prep
  %setup -q -n %{name}-%{version}
  %patch0 -p1
  %patch1 -p1
```



## Building the Package

The package can be built by running `make` in the package directory.
The default behavior is to build the package, but there are several
useful targets available:


| Target | Shortcut | Description |
|--------|----------|-------------|
| `build` | `b` | Build the package.  This is the default target.  See note about `sudo` below.|
| `install` | `i` | Install the package forcibly.  See note about `sudo` below.|
| `dump` | `d` | Dump the contents of the built packages. |
| `clean` | `c` | Remove all by-products of the build process. |
| | `cb` | Clean and build. |
| | `cbd` | Clean, build and dump. |
| | `cbi` | Clean, build and install. |
| | `cbic` | Clean, build and install and forced re-clean. |
| | `cbdc` | Clean, build, dump and forced re-clean. |


**NOTE:** The `build` and `install` targets will use `sudo(8)` to
acquire superuser privileges required to install any build or runtime
dependencies.  It is recommended that this be enabled in a
frictionless mode (i.e., without having to interactively provide a
password) for maximum build throughput.

**NOTE:** The `r` (RPM dump), `cbr` (clean, build, RPM dump) and
`cbrc` (claen, build, RPM dump, clean) targets that were present in
older versions of this template are deprecated and have been mapped to
the same functions as `d`, `cbd` and `cbdc`.


## By-Products

The build process yields three by-products in the package directory:

`BUILD` - The directory where the build takes place.

`PRODUCTS` - Finished products (e.g., RPMs or DEBs).

`LOG` - A log of what transpired during the build process.
