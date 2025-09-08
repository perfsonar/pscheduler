#
# Makefile for Any Package
#

# Ethr leaves over a bunch of files and directories that are read-only
# and prevent 'clean' from building properly. This fixes that.
# Ignores errors if no unibuild-work.
clean::
	(find unibuild-work | xargs chmod +w) || true

include unibuild/unibuild.make
