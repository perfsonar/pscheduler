#
# Makefile for pScheduler Documentation
#

default: build

LATEX=\
	developers-guide \
	json \
	misc \
	test-idle \
	test-simplestream


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
