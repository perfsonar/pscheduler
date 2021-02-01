# Generic Makefile for RPM and Debian packages

This includable Makefile automatically builds packages for Red Hat-
and Debian-derived systems.


## Using the Makefile

To use this file, create a `Makefile` containing the following:
```
inclulde make/generic-package.make
```

**TODO:** Need to format this.

To construct a tarball of your sources automatically:

  - Name a subdirectory with the name of the product (e.g, foomatic)
  - Specify a tarball in the source (e.g., Source0: foomatic-1.3.tar.gz)
  - Set AUTO_TARBALL=1 in your makefile

  NOTE:  The version number in the spec may not contain hyphens.




## Build Targets

| Target | Shortcut | Description |
|--------|----------|-------------|
| `build` | `b` | Build the package.  This is the default target. |
| `install` | `i` | Install the package forcibly.  This must be run as a user that can do this (i.e., `root`). |
| `dump` | `d` | Dump the contents of the built packages. |
| `clean` | `c` | Remove all by-products of the build process. |
| | `cb` | Clean and build. |
| | `cbd` | Clean, build and dump. |
| | `cbi` | Clean, build and install. |
| | `cbic` | Clean, build and install and forced re-clean. |
| | `cbdc` | Clean, build, dump and forced re-clean. |


**NOTE:** The `r` (RPM dump), `cbr` (clean, build, RPM dump) and
`cbrc` (claen, build, RPM dump, clean) targets that were present in
older versions of this template are deprecated and have been mapped to
the same functions as `d`, `cbd` and `cbdc`.
