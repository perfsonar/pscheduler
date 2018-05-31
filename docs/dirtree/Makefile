# 
# Makefile for dirtree Package
#
#

NAME=dirtreei

default: build

$(NAME): $(NAME).zip
	unzip $<
TO_CLEAN += $(NAME)

build: $(NAME)
	cd $(NAME) && tex $(NAME).ins
	cp $(NAME)/$(NAME).sty $(NAME)/$(NAME).tex .
TO_CLEAN += $(NAME).sty $(NAME).tex


clean:
	rm -rf $(TO_CLEAN) *~
