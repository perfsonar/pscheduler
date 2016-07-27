#
# Makefile for pScheduler Documentation
#

# Note for the future: These documents can be converted to other
# formats using Pandoc.  http://pandoc.org


default: build

# TODO: Re-add misc after figuring out where msc.sty went in CentOS 7.

LATEX=\
	archiver-syslog \
	developers-guide \
	json \
	limits \
	test-idle \
	test-rtt \
	test-simplestream \
	test-trace \
	values \



TEXES=$(LATEX:%=%.tex)
DVISS=$(LATEX:%=%.dvi)
PDFS=$(LATEX:%=%.pdf)


build: $(PDFS)
TO_CLEAN += $(PDFS)

%.pdf: %.dvi
	dvipdf $<


dirtree.sty dirtree.tex: dirtree
	make -C $<
	cp $</dirtree.tex $</dirtree.sty .
TO_CLEAN += dirtree.sty dirtree.tex


LATEX_OUTS=\
	aux \
	dvi \
	log \
	out \
	toc
# This is done twice to ensure the table of contents is right.
%.dvi: %.tex dirtree.sty pscheduler-tex.tex
	latex $<
	latex $<
TO_CLEAN += $(LATEX_OUTS:%=*.%)


#
# Clean
#

clean:
	make -C dirtree $@
	rm -rf $(TO_CLEAN) *~
