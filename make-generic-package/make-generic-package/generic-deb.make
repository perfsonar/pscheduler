#
# Generic Makefile for Debian packagess
#
# To use this file, create a Makefile containing the following:
#
#     inclulde make/generic-deb.make
#
# Targets (Shortcuts in Parentheses):
#
#     build (b) - Build the RPM.  This is the default target.
#     clean (c) - Remove build by-products
#     install (i) - Install the RPM forcibly.  Must be run as a user
#                   that can do this.
#     rpmdump (r) - Dump contents of built RPMs.
#
# Other useful shortcut targets:
#
#     cb - Clean and build
#     cbr - Clean, build and rpmdump
#     cbi - Clean, build and install
#     cbic - Clean, build and install and forced re-clean
#     cbrc - Clean, build, rpmdump and forced re-clean
#
#
# To construct a tarball of your sources automatically:
#
#   - Name a subdirectory with the name of the product (e.g, foomatic)
#   - Specify a tarball in the source (e.g., Source0: foomatic-1.3.tar.gz)
#   - Set AUTO_TARBALL=1 in your makefile
#
#   NOTE:  The version number in the spec may not contain hyphens.
#

#
# NO USER-SERVICEABLE PARTS BELOW THIS LINE
#

default: build


# TODO: automagic tarball should be moved to a common file.


%:
	@echo "Nothing Debian is supported yet."
	@false


clean::
	rm -rf $(TO_CLEAN)
	find . -name '*~' | xargs rm -rf

# TODO: Convenient shorthands should be moved to a common file.
