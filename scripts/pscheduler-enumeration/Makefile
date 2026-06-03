#
# Makefile for enumerations
#

FILES := \
	tests \
	tools \
	archivers \
	contexts

JSONS := $(FILES:%=%.json)

TARBALL := pscheduler-enumeration-$(shell date +%Y%m%d%H%M%S).tar

default: $(TARBALL)


%.json: .FORCE
	curl -sk 'https://localhost/pscheduler/$(basename $@)?expanded&pretty' > "$@"


.FORCE::


$(TARBALL): $(JSONS) README.md
	tar cf "$@" $^
TO_CLEAN += pscheduler-enumeration-*.tar


build: $(JSONS)
TO_CLEAN += $(JSONS)

clean:
	rm -rf $(TO_CLEAN) *~
